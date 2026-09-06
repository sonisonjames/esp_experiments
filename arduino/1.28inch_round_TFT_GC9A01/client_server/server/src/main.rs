use std::io::Write;
use std::net::{TcpListener, TcpStream};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "GC9A01 Server")]
#[command(about = "Send text or images to ESP32 display")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Send a text message
    Text {
        /// The text message to send
        message: String,
        /// Number of times to send the message
        #[arg(short, long, default_value = "1")]
        repeat: u32,
    },
    /// Send random words with random positions and colors
    Random {
        /// Number of times to send; 0 means keep sending
        #[arg(short, long, default_value = "0")]
        repeat: u32,
    },
    /// Generate and send a static cartoon image
    Image {
        /// Number of times to send the image
        #[arg(short, long, default_value = "1")]
        repeat: u32,
    },
}

fn rgb888_to_rgb565(r: u8, g: u8, b: u8) -> u16 {
    let r5 = (r as u16 >> 3) & 0x1f;
    let g6 = (g as u16 >> 2) & 0x3f;
    let b5 = (b as u16 >> 3) & 0x1f;
    (r5 << 11) | (g6 << 5) | b5
}

fn set_pixel(buf: &mut [u16], x: usize, y: usize, width: usize, height: usize, color: u16) {
    if x < width && y < height {
        let idx = y * width + x;
        buf[idx] = color;
    }
}

fn draw_circle(buf: &mut [u16], cx: i32, cy: i32, radius: i32, width: usize, height: usize, color: u16) {
    for y in (cy - radius)..=(cy + radius) {
        for x in (cx - radius)..=(cx + radius) {
            if x < 0 || x >= width as i32 || y < 0 || y >= height as i32 {
                continue;
            }

            let dx = x - cx;
            let dy = y - cy;
            if dx * dx + dy * dy <= radius * radius {
                set_pixel(buf, x as usize, y as usize, width, height, color);
            }
        }
    }
}

fn draw_rect(buf: &mut [u16], x: usize, y: usize, w: usize, h: usize, width: usize, height: usize, color: u16) {
    for yy in y..(y + h) {
        for xx in x..(x + w) {
            if xx < width && yy < height {
                set_pixel(buf, xx, yy, width, height, color);
            }
        }
    }
}

fn generate_cartoon(width: usize, height: usize) -> Vec<u8> {
    let pixel_count = width * height;
    let mut pixels: Vec<u16> = vec![0; pixel_count];

    // sky gradient
    for y in 0..height {
        let g = (50 + (y as f32 * 0.3) as i32).clamp(0, 255) as u8;
        for x in 0..width {
            let idx = y * width + x;
            pixels[idx] = rgb888_to_rgb565(100, g, 200);
        }
    }

    // ground
    draw_rect(&mut pixels, 0, height - height / 3, width, height / 3, width, height, rgb888_to_rgb565(100, 180, 80));

    // simple clouds
    let cloud_y = 15;
    draw_circle(&mut pixels, 30, cloud_y, 12, width, height, rgb888_to_rgb565(255, 255, 255));
    draw_circle(&mut pixels, 45, cloud_y + 2, 10, width, height, rgb888_to_rgb565(255, 255, 255));
    draw_circle(&mut pixels, width as i32 - 50, cloud_y, 14, width, height, rgb888_to_rgb565(255, 255, 255));
    draw_circle(&mut pixels, width as i32 - 35, cloud_y + 3, 11, width, height, rgb888_to_rgb565(255, 255, 255));

    // character: simple head
    let head_x = (width / 2) as i32;
    let head_y = (height / 2) as i32;
    draw_circle(&mut pixels, head_x, head_y, 18, width, height, rgb888_to_rgb565(240, 200, 160));

    // ears
    draw_circle(&mut pixels, head_x - 15, head_y - 15, 8, width, height, rgb888_to_rgb565(240, 200, 160));
    draw_circle(&mut pixels, head_x + 15, head_y - 15, 8, width, height, rgb888_to_rgb565(240, 200, 160));

    // eyes
    let eye_y = ((head_y - 5).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 10) as usize, eye_y, 5, 6, width, height, rgb888_to_rgb565(20, 20, 20));
    draw_rect(&mut pixels, (head_x + 5) as usize, eye_y, 5, 6, width, height, rgb888_to_rgb565(20, 20, 20));

    // mouth - smile
    let mouth_y = ((head_y + 8).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 7) as usize, mouth_y, 14, 3, width, height, rgb888_to_rgb565(220, 100, 100));

    // body
    let body_y = head_y + 22;
    let body_y_u = ((body_y).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 8) as usize, body_y_u, 16, 20, width, height, rgb888_to_rgb565(200, 80, 40));

    // arms
    let arm_y_u = ((body_y + 2).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 16) as usize, arm_y_u, 8, 12, width, height, rgb888_to_rgb565(240, 200, 160));
    draw_rect(&mut pixels, (head_x + 8) as usize, arm_y_u, 8, 12, width, height, rgb888_to_rgb565(240, 200, 160));

    // legs
    let leg_y_u = ((body_y + 20).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 6) as usize, leg_y_u, 4, 12, width, height, rgb888_to_rgb565(60, 40, 20));
    draw_rect(&mut pixels, (head_x + 2) as usize, leg_y_u, 4, 12, width, height, rgb888_to_rgb565(60, 40, 20));

    // feet
    let feet_y_u = ((body_y + 32).max(0) as usize).min(height - 1);
    draw_rect(&mut pixels, (head_x - 8) as usize, feet_y_u, 8, 3, width, height, rgb888_to_rgb565(40, 30, 20));
    draw_rect(&mut pixels, (head_x) as usize, feet_y_u, 8, 3, width, height, rgb888_to_rgb565(40, 30, 20));

    let mut bytes = Vec::with_capacity(pixel_count * 2);
    for p in pixels.iter() {
        let le = p.to_le_bytes();
        bytes.extend_from_slice(&le);
    }
    bytes
}

fn send_text(stream: &mut TcpStream, msg: &str, msg_id: u8, x: u16, y: u16, color: u16) -> std::io::Result<()> {
    let magic = [b'T', b'X', b'T', b'1'];
    let text_bytes = msg.as_bytes();
    let text_len = text_bytes.len() as u16;

    if text_bytes.is_empty() || text_bytes.len() > 64 {
        return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, "text must be 1-64 bytes"));
    }

    let mut header = [0u8; 14];
    header[0..4].copy_from_slice(&magic);
    header[4..6].copy_from_slice(&text_len.to_le_bytes());
    header[6] = msg_id;
    header[7] = 0;
    header[8..10].copy_from_slice(&x.to_le_bytes());
    header[10..12].copy_from_slice(&y.to_le_bytes());
    header[12..14].copy_from_slice(&color.to_le_bytes());

    stream.write_all(&header)?;
    stream.write_all(text_bytes)?;
    stream.flush()?;
    println!("sent text ({}): '{}' at ({}, {}), color 0x{:04X}", msg_id, msg, x, y, color);
    Ok(())
}

fn random_value(state: &mut u32, max: u16) -> u16 {
    *state = state.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
    (*state % max as u32) as u16
}

fn random_color(state: &mut u32) -> u16 {
    let red = 80 + random_value(state, 176) as u8;
    let green = 80 + random_value(state, 176) as u8;
    let blue = 80 + random_value(state, 176) as u8;
    rgb888_to_rgb565(red, green, blue)
}

fn send_image(stream: &mut TcpStream, msg_id: u8) -> std::io::Result<()> {
    let width: u16 = 240;
    let height: u16 = 240;
    
    println!("Generating cartoon: {}x{}", width, height);
    
    // Generate cartoon image
    let pixel_data = generate_cartoon(width as usize, height as usize);

    // Build header: IMG1 | width | height
    let magic = [b'I', b'M', b'G', b'1'];
    let mut header = [0u8; 8];
    header[0..4].copy_from_slice(&magic);
    header[4..6].copy_from_slice(&width.to_le_bytes());
    header[6..8].copy_from_slice(&height.to_le_bytes());

    // Send header
    stream.write_all(&header)?;
    stream.write_all(&pixel_data)?;
    stream.flush()?;
    println!("sent cartoon image ({}): {} bytes", msg_id, pixel_data.len());
    Ok(())
}

fn handle_text_client(mut stream: TcpStream, message: String, repeat: u32) {
    stream.set_nodelay(true).ok();
    for i in 0..repeat {
        if let Err(err) = send_text(&mut stream, &message, i as u8, 120, 120, rgb888_to_rgb565(255, 255, 255)) {
            eprintln!("stream error: {err}");
            break;
        }
        if repeat > 1 {
            std::thread::sleep(Duration::from_secs(5));
        }
    }
}

fn handle_random_client(mut stream: TcpStream, repeat: u32) {
    const WORDS: [&str; 15] = [
        "HELLO", "ESP32", "COLOR", "SPARK", "WAVE",
        "PIXEL", "ROUND", "TFT", "RANDOM", "BRIGHT",
        "BLOOM", "ORBIT", "SUNNY", "NOVA", "GLITCH",
    ];
    stream.set_nodelay(true).ok();
    let seed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .subsec_nanos();
    let mut state = seed;
    let mut message_count = 0u32;

    while repeat == 0 || message_count < repeat {
        let word = WORDS[random_value(&mut state, WORDS.len() as u16) as usize];
        let x = 45 + random_value(&mut state, 150);
        let y = 25 + random_value(&mut state, 190);
        let color = random_color(&mut state);

        if let Err(err) = send_text(&mut stream, word, (message_count % 256) as u8, x, y, color) {
            eprintln!("stream error: {err}");
            break;
        }
        message_count += 1;
        std::thread::sleep(Duration::from_secs(5));
    }
}

fn handle_image_client(mut stream: TcpStream, repeat: u32) {
    stream.set_nodelay(true).ok();
    for i in 0..repeat {
        if let Err(err) = send_image(&mut stream, i as u8) {
            eprintln!("stream error: {err}");
            break;
        }
        if repeat > 1 {
            std::thread::sleep(Duration::from_millis(500));
        }
    }
}

fn main() {
    let args = Args::parse();

    match args.command {
        Commands::Text { message, repeat } => {
            let listener = TcpListener::bind("0.0.0.0:9001").expect("failed to bind port 9001");
            println!("Listening on 0.0.0.0:9001");
            println!("Sending text message: '{}' (repeat: {})", message, repeat);
            
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        let msg = message.clone();
                        println!("Client connected: {}", stream.peer_addr().unwrap());
                        handle_text_client(stream, msg, repeat);
                    }
                    Err(e) => {
                        eprintln!("Connection error: {e}");
                    }
                }
            }
        }
        Commands::Random { repeat } => {
            let listener = TcpListener::bind("0.0.0.0:9001").expect("failed to bind port 9001");
            println!("Listening on 0.0.0.0:9001");
            println!("Sending random text, position, and color every 5 seconds (repeat: {})", repeat);

            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        println!("Client connected: {}", stream.peer_addr().unwrap());
                        handle_random_client(stream, repeat);
                    }
                    Err(e) => {
                        eprintln!("Connection error: {e}");
                    }
                }
            }
        }
        Commands::Image { repeat } => {
            let listener = TcpListener::bind("0.0.0.0:9001").expect("failed to bind port 9001");
            println!("Listening on 0.0.0.0:9001");
            println!("Sending cartoon image (repeat: {})", repeat);
            
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        println!("Client connected: {}", stream.peer_addr().unwrap());
                        handle_image_client(stream, repeat);
                    }
                    Err(e) => {
                        eprintln!("Connection error: {e}");
                    }
                }
            }
        }
    }
}

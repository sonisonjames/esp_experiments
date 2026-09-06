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

    // Fill the full panel with a simple dusk background.
    for y in 0..height {
        let red = (18 + (y as u32 * 18 / height as u32)) as u8;
        let green = (28 + (y as u32 * 22 / height as u32)) as u8;
        for x in 0..width {
            let idx = y * width + x;
            pixels[idx] = rgb888_to_rgb565(red, green, 65);
        }
    }

    let dark = rgb888_to_rgb565(20, 16, 25);
    let fur = rgb888_to_rgb565(75, 48, 38);
    let inner_ear = rgb888_to_rgb565(155, 82, 68);
    let muzzle = rgb888_to_rgb565(218, 164, 116);
    let shirt = rgb888_to_rgb565(40, 120, 170);
    let shoe = rgb888_to_rgb565(235, 190, 52);
    let white = rgb888_to_rgb565(245, 245, 235);

    // Original mouse-like character: large ears, round muzzle, bright shirt.
    let center_x = (width / 2) as i32;
    draw_circle(&mut pixels, center_x, 68, 55, width, height, fur);
    draw_circle(&mut pixels, center_x - 48, 38, 32, width, height, fur);
    draw_circle(&mut pixels, center_x + 48, 38, 32, width, height, fur);
    draw_circle(&mut pixels, center_x - 48, 38, 19, width, height, inner_ear);
    draw_circle(&mut pixels, center_x + 48, 38, 19, width, height, inner_ear);

    draw_circle(&mut pixels, center_x, 88, 34, width, height, muzzle);
    draw_circle(&mut pixels, center_x, 68, 9, width, height, dark);
    draw_circle(&mut pixels, center_x - 21, 63, 8, width, height, white);
    draw_circle(&mut pixels, center_x + 21, 63, 8, width, height, white);
    draw_circle(&mut pixels, center_x - 21, 63, 3, width, height, dark);
    draw_circle(&mut pixels, center_x + 21, 63, 3, width, height, dark);
    draw_circle(&mut pixels, center_x, 99, 5, width, height, dark);
    draw_rect(&mut pixels, (center_x - 22) as usize, 111, 44, 5, width, height, dark);

    // Body, arms, legs, and oversized shoes fill the lower half of the panel.
    draw_circle(&mut pixels, center_x, 163, 51, width, height, shirt);
    draw_rect(&mut pixels, (center_x - 44) as usize, 148, 88, 48, width, height, shirt);
    draw_rect(&mut pixels, (center_x - 76) as usize, 145, 30, 16, width, height, fur);
    draw_rect(&mut pixels, (center_x + 46) as usize, 145, 30, 16, width, height, fur);
    draw_circle(&mut pixels, center_x - 82, 153, 12, width, height, muzzle);
    draw_circle(&mut pixels, center_x + 82, 153, 12, width, height, muzzle);
    draw_rect(&mut pixels, (center_x - 28) as usize, 190, 18, 27, width, height, fur);
    draw_rect(&mut pixels, (center_x + 10) as usize, 190, 18, 27, width, height, fur);
    draw_circle(&mut pixels, center_x - 29, 219, 23, width, height, shoe);
    draw_circle(&mut pixels, center_x + 29, 219, 23, width, height, shoe);

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

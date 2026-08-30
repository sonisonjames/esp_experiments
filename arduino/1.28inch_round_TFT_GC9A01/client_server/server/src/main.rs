use std::io::Write;
use std::net::{TcpListener, TcpStream};
use std::time::Duration;

fn send_text(stream: &mut TcpStream, msg: &str, frame_index: u64) -> std::io::Result<()> {
    let magic = [b'T', b'X', b'T', b'1'];
    let text_bytes = msg.as_bytes();
    let text_len = text_bytes.len() as u16;

    let mut header = [0u8; 8];
    header[0..4].copy_from_slice(&magic);
    header[4..6].copy_from_slice(&text_len.to_le_bytes());
    header[6] = frame_index as u8;
    header[7] = 0;

    stream.write_all(&header)?;
    stream.write_all(text_bytes)?;
    stream.flush()?;
    println!("sent text: '{}'", msg);
    Ok(())
}

fn handle_client(mut stream: TcpStream) {
    stream.set_nodelay(true).ok();

    let messages = [
        "Hello TFT!",
        "Streaming text",
        "from Rust server",
        "to ESP32 display",
        "Line 5 test",
    ];

    let mut msg_index = 0u64;

    loop {
        if msg_index > 50 {
            break;
        }

        let msg = messages[(msg_index % (messages.len() as u64)) as usize];
        if let Err(err) = send_text(&mut stream, msg, msg_index) {
            eprintln!("stream error: {err}");
            break;
        }

        msg_index += 1;
        std::thread::sleep(Duration::from_millis(500));
    }
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:9001").expect("failed to bind port 9001");
    println!("Listening on 0.0.0.0:9001");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                println!("Client connected: {}", stream.peer_addr().unwrap());
                std::thread::spawn(move || {
                    handle_client(stream);
                });
            }
            Err(e) => {
                eprintln!("Connection error: {e}");
            }
        }
    }
}

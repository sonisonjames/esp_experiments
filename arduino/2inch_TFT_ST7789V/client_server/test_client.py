import serial
import time

'''
This is a test client script to send text messages to an ESP32 server
that displays them on a 2-inch TFT screen using the ST7789V driver.
The server is run using the test2.C program on the ESP32.
'''

# --- CONFIGURATION ---
SERIAL_PORT = 'COM6'  # Double check your COM port!
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for ESP32 to reboot after connection
    print("Connected to ESP32!")
except Exception as e:
    print(f"Error: {e}")
    exit()

while True:
    msg = input("Enter text to send to TFT (or 'exit'): ")

    if msg.lower() == 'exit':
        break

    # Send text with a newline character
    ser.write((msg + '\n').encode('utf-8'))

    # Wait for the ACK from ESP32
    ack = ser.readline().decode('utf-8').strip()
    if ack == "ACK":
        print("ESP32 received the message!")
    else:
        print("No response from ESP32.")

ser.close()
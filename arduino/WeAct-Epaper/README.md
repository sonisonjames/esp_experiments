# WeShare Docs
https://github.com/WeActStudio/WeActStudio.EpaperModule/tree/master

# Pinout Connection
| E-Paper Pin  | ESP32 Pin   | Notes               |
|--------------|-------------|---------------------|
| GND          | GND         | Ground              |
| VCC          | 3.3V        | Use 3.3V, not 5V |
| DIN/MOSI/SDA | D23(GPIO23) | SPI Data (MOSI)      |
| CLK/SCL      | D18(GPIO18) | SPI Clock (SCK)     |
| CS           | D13         | Chip Select         |
| DC           | D27         | Data / Command      |
| RST          | D26         | Reset               |
| BUSY         | D34         | Busy Signal         |
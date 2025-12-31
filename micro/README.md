# esp32-cambridge-transit-micro

ESP32-compatible Arduino code for the microcontroller connected to an e-ink display. This application is specifically implemented for a Firebeetle ESP32-E.

The device enters a deep sleep after initial update which can be exited via a button press. This conserves a huge amount of power allowing for a ~months between charges even with a very small 200-300mAh LiPo battery.

## Pin Configuration

| ESP32         | e-Paper Display |
| ------------- | --------------- |
| GPIO4         | Busy            |
| GPIO16        | RST             |
| GPIO17        | DC              |
| GPIO12        | CS              |
| GPIO18 (SCK)  | CLK             |
| GPIO23 (MOSI) | DIN             |
| GND           | GND             |
| 3.3V          | VCC             |

| ESP32  | Update Button |
| ------ | ------------- |
| GND.   | Pin 1         |
| GPIO25 | Pin 2         |

### Secrets

We need a few secret variables to run this project. These are defined in a hidden file at `src/secrets.h`. It should look like this and be filled out with the relevant info:

```c
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
#define API_BASE_URL "http://192.168.1.50:8000" // recommend assigning a static IP or using mDNS/self-hosted DNS
```

# esp32-cambridge-transit-micro

ESP32-compatible Arduino code for the microcontroller connected to an e-ink display. This application is specifically implemented for a Firebeetle ESP32-E with the following pinout:

```
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
```

`GPIO25` controls the wake mechnanism and will wake the device from deep sleep when pulled to `GND`.

### Secrets

We need a few secret variables to run this project. These are defined in a hidden file at `src/secrets.h`. It should look like this and be filled out with the relevant info:

```c
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
#define API_BASE_URL "http://192.168.1.50:8000"
```

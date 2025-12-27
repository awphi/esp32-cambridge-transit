# esp32-cambridge-transit-micro

ESP32-compatible Arduino code for the microcontroller connected to an e-ink display

### Secrets

We need a few secret variables to run this project. These are defined in a hidden file at `src/secrets.h`. It should look like this and be filled out with the relevant info:

```c
#define WIFI_SSID "..."
#define WIFI_PASSWORD "..."
#define API_BASE_URL "http://192.168.1.50:8000"
```

# esp32-cambridge-transit

Small ESP32-based project to build a real time transit dashboard for trains & buses near me in Cambridge, UK.

## Packages

This repo is composed of a few small packages:

`/micro` - ESP32-compatible Arduino code for the microcontroller connected to an e-ink display
`/api` - Small FastAPI-based aggregation API to provide a single, well-formatted endpoint for the ESP32 to fetch from for relevant data

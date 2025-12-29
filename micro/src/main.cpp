#include <Arduino.h>
#include <ArduinoJson.h>
#include <Fonts/FreeMonoBold9pt7b.h>
#include <GxEPD2_BW.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <secrets.h>

#include "GxEPD2_display_selection_new_style.h"

// total line height of 25 = 12 lines of text w/ display height of 300
#define LINE_PADDING_BOTTOM 7
#define LINE_HEIGHT (18 + LINE_PADDING_BOTTOM)

const int columnSpacingLength = 3;
const int transitColumnLengths[] = {3, 20, 7};
const int maxRowsPerSection = 5;
const size_t jsonDocSize = 8192;
StaticJsonDocument<jsonDocSize> transitDoc;
const unsigned long wifiConnectTimeoutMs = 15000;
const int maxFetchAttempts = 3;
const unsigned long fetchBackoffMs = 2000;

String rightPad(const String& str, char c, int len) {
  String output = "";
  for (int i = 0; i < len; i++) {
    output += c;
  }
  return str + output;
}

String ensureStringLength(const String& str, int len) {
  int n = str.length();
  if (n < len) {
    return rightPad(str, ' ', len - n);
  } else if (n > len) {
    return str.substring(0, len);
  }

  return str;
}

String formatTransitRow(const String& service, const String& dest,
                        const String& eta) {
  String rowText = ensureStringLength(service, transitColumnLengths[0]);
  rowText += rightPad("", ' ', columnSpacingLength);
  rowText += ensureStringLength(dest, transitColumnLengths[1]);
  rowText += rightPad("", ' ', columnSpacingLength);
  rowText += ensureStringLength(eta, transitColumnLengths[2]);
  return rowText;
}

void renderHeader(const String& str, int yOffset) {
  display.setCursor(0, yOffset - LINE_PADDING_BOTTOM);
  display.print(str);

  int topLineY = yOffset - LINE_HEIGHT;
  display.drawLine(0, yOffset, display.width() - 1, yOffset, GxEPD_BLACK);
  display.drawLine(0, topLineY, display.width() - 1, topLineY, GxEPD_BLACK);
}

void renderTransitRows(JsonArray departures, int yOffset) {
  int rowIndex = 0;
  int y = yOffset;

  for (JsonVariant row : departures) {
    if (rowIndex >= maxRowsPerSection) {
      break;
    }
    String service = row["service"] | "";
    String dest = row["dest"] | "";
    String eta = row["eta"] | "";
    String rowText = formatTransitRow(service, dest, eta);

    if (rowText.length() > 0) {
      display.setCursor(0, y - LINE_PADDING_BOTTOM);
      display.print(rowText);
      y += LINE_HEIGHT;
      rowIndex = rowIndex + 1;
    }
  }
}

void renderTransitSection(JsonObject info, int yOffset,
                          const char* fallbackTitle) {
  if (info.isNull()) {
    renderHeader(fallbackTitle, yOffset);
    return;
  }
  String title = info["title"] | fallbackTitle;
  renderHeader(title, yOffset);
  JsonArray departures = info["departures"].as<JsonArray>();
  if (!departures.isNull()) {
    renderTransitRows(departures, yOffset + LINE_HEIGHT);
  }
}

String buildApiUrl() {
  String baseUrl = String(API_BASE_URL);
  if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
    baseUrl = "http://" + baseUrl;
  }
  if (!baseUrl.endsWith("/")) {
    baseUrl += "/";
  }
  return baseUrl;
}

bool connectWifi() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFi.setSleep(true);
    return true;
  }

  Serial.printf("connecting to WiFi network: %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startMs = millis();
  while (WiFi.status() != WL_CONNECTED &&
         (millis() - startMs) < wifiConnectTimeoutMs) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected.");
    WiFi.setSleep(true);
    return true;
  } else {
    Serial.println("\nWiFi connect timeout.");
    return false;
  }
}

bool fetchTransitInfo(JsonDocument& doc) {
  String apiUrl = buildApiUrl();

  for (int attempt = 0; attempt < maxFetchAttempts; attempt++) {
    if (!connectWifi()) {
      delay(fetchBackoffMs * (attempt + 1));
      continue;
    }

    Serial.printf("Starting GET request: %s\n", apiUrl.c_str());
    WiFiClient client;
    HTTPClient http;
    if (http.begin(client, apiUrl)) {
      int httpCode = http.GET();
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        DeserializationError error = deserializeJson(doc, payload);
        if (error) {
          Serial.printf("JSON parse error: %s\n", error.c_str());
        } else {
          http.end();
          return true;
        }
      } else {
        Serial.printf("HTTP GET error: %s\n",
                      http.errorToString(httpCode).c_str());
      }
      http.end();
    } else {
      Serial.println("HTTP connection failed to initialize.");
    }

    delay(fetchBackoffMs * (attempt + 1));
  }

  return false;
}

void updateDisplay() {
  transitDoc.clear();
  bool hasData = fetchTransitInfo(transitDoc);
  JsonObject busInfo = transitDoc["bus_info"];
  JsonObject trainInfo = transitDoc["train_info"];

  if (!hasData) {
    Serial.println("No transit data available.");
    return;
  }

  display.setFullWindow();
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setCursor(0, 0);
    display.setTextSize(1);  // Adjust text size as needed

    renderTransitSection(busInfo, LINE_HEIGHT, "Buses");
    renderTransitSection(trainInfo, LINE_HEIGHT * (maxRowsPerSection + 2),
                         "Trains");

  } while (display.nextPage());
}

void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("initializing display...");
  display.init(115200);  // SPI baudrate
  display.setRotation(0);
  display.setFont(&FreeMonoBold9pt7b);

  connectWifi();

  updateDisplay();
}

void loop() {
  delay(60000);
  updateDisplay();
}

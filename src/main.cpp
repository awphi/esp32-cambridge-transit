#include <Arduino.h>
#include <Fonts/FreeMonoBold9pt7b.h>
#include <GxEPD2_BW.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <secrets.h>

#include "GxEPD2_display_selection_new_style.h"

// total line height of 25 = 12 lines of text w/ display height of 300
#define LINE_PADDING_BOTTOM 7
#define LINE_HEIGHT (18 + LINE_PADDING_BOTTOM)

const String url =
    "https://www.cambridgeshirebus.info/Popup_Content/WebDisplay/"
    "WebDisplay.aspx?stopRef=";

const int columnSpacingLength = 3;
const int busColumnLengths[] = {3, 20, 7};

String removeHTMLTags(const String& input) {
  String output = "";
  bool inTag = false;
  for (size_t i = 0; i < input.length(); i++) {
    char c = input.charAt(i);
    if (c == '<') {
      inTag = true;
      continue;
    }
    if (c == '>') {
      inTag = false;
      continue;
    }
    if (!inTag)
      output += c;
  }
  return output;
}

String extractTable(const String& html) {
  int tableStart = html.indexOf("<table class=\"rtiTable\"");
  if (tableStart == -1)
    return "";
  int tableEnd = html.indexOf("</table>", tableStart);
  if (tableEnd == -1)
    return "";
  // Include the closing tag in the substring:
  return html.substring(tableStart, tableEnd + 8);
}

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
    return str.substring(0, n);
  }

  return str;
}

void renderTableToDisplay(const String& tableHTML, int yOffset) {
  int currentIndex = 0;
  int rowIndex = 0;
  int y = yOffset;

  // Loop through each table row (<tr>...</tr>)
  while (rowIndex < 5) {
    int trStart = tableHTML.indexOf("<tr", currentIndex);
    if (trStart == -1) {
      break;
    }
    int trEnd = tableHTML.indexOf("</tr>", trStart);
    if (trEnd == -1) {
      break;
    }
    String trContent = tableHTML.substring(trStart, trEnd);

    // Parse out each cell (<td>...</td>) within the row.
    String rowText = "";
    int tdIndex = 0;
    int colIndex = 0;

    // only render first 3 non-empty columns
    while (colIndex < 3) {
      int tdStart = trContent.indexOf("<td", tdIndex);
      if (tdStart == -1)
        break;
      // Find the end of the <td ...> tag
      int tdTagEnd = trContent.indexOf(">", tdStart);
      if (tdTagEnd == -1)
        break;
      int tdEnd = trContent.indexOf("</td>", tdTagEnd);
      if (tdEnd == -1)
        break;

      String cellContent = trContent.substring(tdTagEnd + 1, tdEnd);
      cellContent = removeHTMLTags(cellContent);

      if (cellContent.length() > 0 && cellContent != "&nbsp;") {
        cellContent =
            ensureStringLength(cellContent, busColumnLengths[colIndex]);
        rowText += rightPad(cellContent, ' ', columnSpacingLength);
        colIndex = colIndex + 1;
      }

      tdIndex = tdEnd + 5;  // Move index past the closing </td>
    }

    if (rowText.length() > 0) {
      display.setCursor(0, y - LINE_PADDING_BOTTOM);
      display.print(rowText);
      y += LINE_HEIGHT;
      rowIndex = rowIndex + 1;
    }

    currentIndex = trEnd + 5;  // Move index past the closing </tr>
  }
}

void renderHeader(const String& str, int yOffset) {
  display.setCursor(0, yOffset - LINE_PADDING_BOTTOM);
  display.print(str);

  int topLineY = yOffset - LINE_HEIGHT;
  display.drawLine(0, yOffset, display.width() - 1, yOffset, GxEPD_BLACK);
  display.drawLine(0, topLineY, display.width() - 1, topLineY, GxEPD_BLACK);
}

String fetchBusData() {
  Serial.println("Starting HTTPS GET request...");

  // Create a secure Wi‑Fi client (disable certificate validation for
  // simplicity)
  WiFiClientSecure client;
  client.setInsecure();

  HTTPClient https;
  if (https.begin(client, url + BUS_STOP_REF)) {
    int httpCode = https.GET();
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        String payload = https.getString();
        Serial.println("Data fetched successfully.");
        String tableHTML = extractTable(payload);
        if (tableHTML != "") {
          return tableHTML;
        } else {
          Serial.println("No <table> element found in the HTML.");
        }
      } else {
        Serial.printf("HTTP GET error: %s\n",
                      https.errorToString(httpCode).c_str());
      }
    } else {
      Serial.printf("Unable to connect, error: %s\n",
                    https.errorToString(httpCode).c_str());
    }
    https.end();
  } else {
    Serial.println("HTTPS connection failed to initialize.");
  }

  return "";
}

void updateDisplay() {
  String busTableHTML = fetchBusData();

  display.setFullWindow();
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
    display.setCursor(0, 0);
    display.setTextSize(1);  // Adjust text size as needed

    renderHeader("Buses - Milton P&R", LINE_HEIGHT);
    renderTableToDisplay(busTableHTML, LINE_HEIGHT * 2);
  } while (display.nextPage());
}

void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("initializing display...");
  display.init(115200);  // SPI baudrate
  display.setRotation(0);
  display.setFont(&FreeMonoBold9pt7b);

  Serial.printf("connecting to WiFi network: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");

  updateDisplay();
}

void loop() {
  delay(60000);
  updateDisplay();
}

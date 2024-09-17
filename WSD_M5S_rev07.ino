/*
  Weather Station with BME280 & Datalogger
  Coder: Rogerio Alves <rogerio.acioli@hotmail.com.br>  
  Updated 2021-05-13
*/

//Includes Libraries 
#include <M5Stack.h> //Bibliotecas básicas do M5Stack
#include "M5StackUpdater.h"
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h> //libraries for the BME280 Sensor
#include <Adafruit_BME280.h>      //     ----->  BMP
#include "FS.h" //libraries for SD Card
#include <SD.h>
#include <WiFi.h> // Libraries to get time from NTP Server
#include <NTPClient.h>
#include <WiFiUdp.h>
//#include <esp_task_wdt.h> //WDT Libraries

// Network Credentials for NTP
const char* ssid     = "LOPES"; // Replace with your network credentials
const char* password = "m@i$r0g3r2018";
WiFiUDP ntpUDP; // Define NTP Client to get time
NTPClient timeClient(ntpUDP);

//Defines Sea Level Pressure
#define SDA 21  
#define SLC 22
#define ADR 0x77      //     ----->  BME  76
#define SEALEVELPRESSURE_HPA (1013.25)
#define SD_CS 5
//#define WDT_TIMEOUT 600 // define WDT TIMEOUT
Adafruit_BME280 bme; //I2C      //     ----->  BMP //Define a comunicação do sensor 

//Define variables
const int chipSelect = 4; //Define CS pin for the SD Card Module
String formattedDate;
String dayStamp;
String timeStamp;
String dataMessage;
char data[512];
int sensor = false;
unsigned long mtime = 0;
char response[2048];
long cnt=0;
float cor = 0;
float tmp = 0;
float pre = 0;
float hum = 0;
float alt = 0;
int period = 600000; //1000; //600000
unsigned long time_now = 0;
//char idWSD[] = "WSD01_000.txt";
//unsigned long last = 0; // WDT variable
//float i = 0; // WDT variable
//char filename[] = "0000000000000000";
char filename[] = "WSD_20210513.txt";
//char filename ;
//File myFile;

void handleRoot(){
  M5.Lcd.fillCircle(250, 20, 20, BLUE);
  Serial.println(cnt);

  if (!sensor) //Iniciando o sensor BME280
  {
    strcpy(data,"BME280 error !");  
  }
  else  
  {
    snprintf(data, sizeof(data),
      "Connect: %d <br>\
      Pressure: %.0f Pa<br>\
      Altutude: %.0f m<br>\
      Humidity: %.0f Percent<br>\
      Temperature: %.1f C<br>\
      ",cnt, pre,alt,hum,tmp
    );
  }

  if (cnt++ > 1000000)//1000000 - para 1 segundo e 600000000 para 10 minutos
    cnt = 0;
}

// Write to the SD card (DON'T MODIFY THIS FUNCTION)
void writeFile(fs::FS &fs, const char * path, const char * message) {
   
  Serial.printf("Writing file: %s\n", path);

  //File file = fs.open(path, FILE_WRITE);
  File file = fs.open(path, FILE_WRITE);
  
  if(!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  if(file.print(message)) {
    Serial.println("File written");
  } else {
    Serial.println("Write failed");
  }
  file.close();
}

// Append data to the SD card (DON'T MODIFY THIS FUNCTION)
void appendFile(fs::FS &fs, const char * path, const char * message) {
  Serial.printf("Appending to file: %s\n", path);


  //File file = fs.open(path, FILE_APPEND);
  File file = fs.open(path, FILE_APPEND);
  if(!file) {
    Serial.println("Failed to open file for appending");
    return;
  }
  if(file.print(message)) {
    Serial.println("Message appended");
  } else {
    Serial.println("Append failed");
  }
  file.close();

} 

void setup (){
  Serial.begin(115200);
  M5.begin();
  // Connect to Wi-Fi network with SSID and password
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");

  // Initialize a NTPClient to get time
  timeClient.begin();
  // Set offset time in seconds to adjust for your timezone, for example:
  // GMT +1 = 3600
  // GMT +8 = 28800
  // GMT -1 = -3600
  // GMT 0 = 0
  // GMT -3 = -10800
  timeClient.setTimeOffset(-10800); 

  while(!timeClient.update()) {
    timeClient.forceUpdate();
  }
  
  Serial.println("Welcome to the SD-Update !");
  Serial.print("M5Stack initializing...");
  
  Wire.begin();
  if(digitalRead(BUTTON_A_PIN) == 0) {
    Serial.println("Will Load menu binary");
    updateFromFS(SD);
    ESP.restart();
  }

  // Lcd display
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(10, 10);
  M5.Lcd.setTextColor(GREEN);
  M5.Lcd.setTextSize(3);
  M5.Lcd.printf("WSD MD-ITA");
  M5.Lcd.setTextColor(WHITE);

  // BME280
  Wire.begin(SDA,SLC);
  if (bme.begin(ADR)) 
    sensor = true; 

  mtime = millis();

  getTimeStamp();

  // If the data.txt file doesn't exist
  // Create a file on the SD card and write the data labels
  File file = SD.open("WSD_"+ filename + ".txt");
  if(!file) {
    Serial.println("File doens't exist");
    Serial.println("Creating file...");
             }
  else {
    Serial.println("File already exists");  
        }  
  file.close();


  M5.update();
  
  if (!sensor)
  {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.printf("BMP280 not ready");
    delay(2000);
    if (bme.begin(ADR)) 
      sensor = true; 
  }
  
  tmp = bme.readTemperature() - cor;
    pre = bme.readPressure();  
    hum = bme.readHumidity();      //     ----->  BMP
    alt = bme.readAltitude(SEALEVELPRESSURE_HPA);
    sprintf(data,"%.1f C", tmp);
    M5.Lcd.fillRect(10, 80, 200, 50, BLACK);
    M5.Lcd.setCursor(10, 80);
    M5.Lcd.printf(data); 
    sprintf(data,"%.0f Pa", pre);  
    M5.Lcd.fillRect(10, 130, 200, 50, BLACK);
    M5.Lcd.setCursor(10, 130);
    M5.Lcd.printf(data);   
    sprintf(data,"%.0f Percent",hum);
    M5.Lcd.fillRect(10, 180, 250, 50, BLACK);
    M5.Lcd.setCursor(10, 180);
    M5.Lcd.printf(data);

    //Nome conforme data
    //getFileName();
    //delay(3000);
    //createFileName()

    //Gravação dos dados no SD
    getTimeStamp();
    //fileName = "WSD_" + dayStamp.substring(0, 4) + dayStamp.substring(5, 7) + dayStamp.substring(8, 10) + ".txt";
    dataMessage = String(dayStamp) + "," + String(timeStamp) + "," + 
                  String(tmp) + "," + String(pre) + "," + String(hum) + "," +
                  String(alt) + "\r\n";
    //appendFile(SD, "/data.txt", dataMessage.c_str());
    appendFile(SD, "WSD_"+ filename + ".txt", dataMessage.c_str());

  /* Serial.println("Configuring WDT..."); //Set WDT
      esp_task_wdt_init(WDT_TIMEOUT, true); //enable panic so ESP32 restarts
      esp_task_wdt_add(NULL); //add current thread to WDT watch*/
}


void loop (){
   
  M5.update();
  if (!sensor)
  {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.printf("BMP280 not ready");
    delay(2000);
    if (bme.begin(ADR)) 
      sensor = true; 
  }
  
if ((millis() - mtime >= period) && sensor) //if ((millis() - mtime > 1000 || millis() - mtime <0)&& sensor)
  {
    tmp = bme.readTemperature() - cor;
    pre = bme.readPressure();  
    hum = bme.readHumidity();      //     ----->  BMP
    alt = bme.readAltitude(SEALEVELPRESSURE_HPA);
    sprintf(data,"%.1f C", tmp);
    M5.Lcd.fillRect(10, 80, 200, 50, BLACK);
    M5.Lcd.setCursor(10, 80);
    M5.Lcd.printf(data); 
    sprintf(data,"%.0f Pa", pre);  
    M5.Lcd.fillRect(10, 130, 200, 50, BLACK);
    M5.Lcd.setCursor(10, 130);
    M5.Lcd.printf(data);   
    sprintf(data,"%.0f Percent",hum);
    M5.Lcd.fillRect(10, 180, 250, 50, BLACK);
    M5.Lcd.setCursor(10, 180);
    M5.Lcd.printf(data);

    //Nome conforme data
    //getFileName();
    //delay(3000);
   // createFileName();

    //Gravação dos dados no SD
    getTimeStamp();
    //fileName = "WSD_" + dayStamp.substring(0, 4) + dayStamp.substring(5, 7) + dayStamp.substring(8, 10) + ".txt";
    dataMessage = String(dayStamp) + "," + String(timeStamp) + "," + 
                  String(tmp) + "," + String(pre) + "," + String(hum) + "," +
                  String(alt) + "\r\n";
     
    appendFile(SD, "WSD_"+ filename + ".txt", dataMessage.c_str());
    
    mtime = millis();
            
  } 

  if(millis() >= 86400000)
  {
    ESP.restart();
  }
  
  /*if (millis() - last >= 300000 && i < 288 ) { // resetting WDT every 2s, 5 times only
      Serial.println("Resetting WDT...");
      esp_task_wdt_reset();
      last = millis();
      i++;
      if (i == 288) {
        Serial.println("Stopping WDT reset. CPU should reboot in 3s");
      }
  }*/
}

void getTimeStamp() { 
  // The formattedDate comes with the following format: 2018-05-28T16:00:13Z
  formattedDate = timeClient.getFormattedDate();
  // Extract date
  int splitT = formattedDate.indexOf("T");
  dayStamp = formattedDate.substring(0, splitT);
  timeStamp = formattedDate.substring(splitT+1, formattedDate.length()-1);
  fileName = "WSD_" + dayStamp.substring(0, 4) + dayStamp.substring(5, 7) + dayStamp.substring(8, 10) + ".txt";
}

/*void getFileName(){
filename = dayStamp; //RTC.now();
filename[0] = (now.year()/1000)%10 + '0'; //To get 1st digit from year()
filename[1] = (now.year()/100)%10 + '0'; //To get 2nd digit from year()
filename[2] = (now.year()/10)%10 + '0'; //To get 3rd digit from year()
filename[3] = now.year()%10 + '0'; //To get 4th digit from year()
filename[4] = now.month()/10 + '0'; //To get 1st digit from month()
filename[5] = now.month()%10 + '0'; //To get 2nd digit from month()
filename[6] = now.day()/10 + '0'; //To get 1st digit from day()
filename[7] = now.day()%10 + '0'; //To get 2nd digit from day()
}*/

/*void createFileName(){
myFile = SD.open(filename, FILE_WRITE);
myFile.close();
}*/

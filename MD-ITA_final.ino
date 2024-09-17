/*
  Cosmic Watch Muons Detector - ITA

  Coder: Tiago M. Takaki <tiagomitsuo@gmail.com>
  Original Project: Spencer N. Axani <saxani@mit.edu>
  
  Libraries:
  1. SSD1306Ascii v1.3.0 -- Bill Greiman
  2. SDFat v1.0.8 -- Bill Greiman
  
  Updated 2019-10-25
*/

#include "SdFat.h"
#include "SSD1306Ascii.h"
#include "SSD1306AsciiAvrI2c.h"
#include <avr/wdt.h>



char idMD[] = "MD01M_000.txt";  //MD-Muons Detector | 00-ID | M-Master S-Slave | 000-Sequential filename
const int SIGNAL_THRESHOLD = 50; //ADC trigger to capture a signal from SiPM
const int RESET_THRESHOLD = 15; //ADC limit to avoid noise
const int COINCIDENCE_WINDOW = 30; //time (us) to notify slave that is a signal coincidence



volatile long int scount = 0L;  //sync counts

#define I2C_ADDRESS 0x3C
SSD1306AsciiAvrI2c oled;

SdFat SD;
SdFile dataFile;

void setup() {
  analogReference (EXTERNAL);
  ADCSRA &= ~(bit (ADPS0) | bit (ADPS1) | bit (ADPS2));  //clear prescaler
  ADCSRA |= bit (ADPS0) | bit (ADPS1);  //prescaler 8 (~150kS/s -> ~8.5us/S)

  //watchdog setup
  MCUSR &= ~(1<<WDRF);
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR = 1<<WDP0 | 1<<WDP3; //8" to reset
  WDTCSR |= _BV(WDIE);
  delay(10);

  pinMode(3, OUTPUT);
  PORTD = PORTD & B11110111; //turn led off
  
  if (idMD[4] == 'S') {
     pinMode(6, INPUT);
     
     pinMode(2, INPUT);
     attachInterrupt(digitalPinToInterrupt(2), syncCounts, RISING);
  }
  else{
     pinMode(6, OUTPUT);
     PORTD = PORTD & B10111111; //stop signal to slave
  }
  
  oled.begin(&Adafruit128x64, I2C_ADDRESS);
  oled.displayRemap(true);
  oled.setFont(lcd5x7);
  
  oled.clear();
  oled.setCursor(0, 0);
  oled.println(F(""));
  oled.println(F("     COSMIC WATCH"));
  oled.println(F(""));
  oled.println(F("    MUONS DETECTOR"));
  oled.println(F(""));
  oled.println(F(""));
  oled.println(F("         ITA"));
  
  if (!SD.begin()) {
    oled.clear();
    oled.println(F(""));
    oled.println(F(""));
    oled.println(F("    SD CARD FAILED"));
    oled.println(F(""));
    oled.println(F(""));
    oled.println(F("    OR NOT PRESENT"));
    
    PORTD = PORTD | B00001000;
    while (1);
  }
  
  for (uint8_t i = 1; i <= 99; i++) {
     int h = (i-i/1000*1000)/100;
     int t = (i-i/100*100)/10;
     int o = i%10;
    
     idMD[6] = h + '0';
     idMD[7] = t + '0';
     idMD[8] = o + '0';
    
     if (!SD.exists(idMD)) {
       dataFile.open(idMD, FILE_WRITE);
       break;
     }

     if (i == 99) {
       oled.clear();
       oled.println(F(""));
       oled.println(F(""));
       oled.println(F("   SD CARD IS FULL"));
       oled.println(F(""));
       oled.println(F(""));
       oled.println(F("    MAX FILES: 99"));
      
       PORTD = PORTD | B00001000;
 
       while (1);
     }
  }
     
  dataFile.println("Count;Time Stamp (ms);ADC (0-1023);Decay time (us);Dead time (ms);Temperature (C);Sync Count");
}

void loop() {
   unsigned long time_init = 0L;
   unsigned long time_end = 0L;
   unsigned long time_dead = 0L;
   unsigned long decay_time = 0L;        //decay time
   unsigned long dead_time = 0L;         //dead time
   unsigned long time_stamp = 0L;        //time stamp
   unsigned long init_stamp = millis();  //init time stamp
   long int count = 0L;                  //counts
   int adc = 0;                          //ADC SiPM peak (0-1023)
   float tempC = 25.0;                   //Temperature (°C)
   bool coincidence = true;

   //sync time stamp master and slave ???
   
   while (1) { //infinite loop
     wdt_reset();   

     adc = analogRead(0); //reads adc value of sensor

     if ((adc = analogRead(0)) > SIGNAL_THRESHOLD) {  //signal threshold
       time_init = micros();  //start decay time
       time_stamp = millis() - init_stamp;  //start time stamp
       
       if (idMD[4] == 'S') {
         if (PIND & (1<<PD6)) {
            PORTD = PORTD | B00001000; //turn led on
            coincidence = true;
         }
         else {
            coincidence = false;
         }
       }
       else {
         PORTD = PORTD | B01001000; //send signal to slave and turn led on

         delayMicroseconds(COINCIDENCE_WINDOW); //coincidence window
           
         PORTD = PORTD & B10111111; //stop signal to slave
       }

       if (coincidence) {
         while (analogRead(0) > RESET_THRESHOLD) { continue; }  //lock until voltage < reset threshold
         
         time_end = micros();  //stop decay time
         count++;
         tempC = (((analogRead(A3)+analogRead(A3))/2. * (3550./1024)) - 500.)/10. ;  //voltage calibrate
  
         decay_time = time_end - time_init;
         dead_time = millis() - time_dead - decay_time/1000;
  
         char bufferSD[40];
         sprintf(bufferSD, "%ld;%ld;%d;%ld;%ld;%d.%01d;%ld",  count, time_stamp, adc, decay_time, dead_time, (int)tempC, (int)(tempC*10)%10, scount);
         //if (coincidence) { dataFile.print("*"); }  //print all data but marking coincidence with *
         dataFile.println(bufferSD);
         //dataFile.flush();
         
         PORTD = PORTD & B11110111; //turn led off
         
         time_dead = millis();
       }
     }

     if ((millis() % 10000) == 0) {  //update display and flush SD each 10 seconds

        //temperature ???
        dataFile.flush();
        
        int hours = millis() / 1000 / 3600;
        int minutes = (millis() / 1000 / 60) % 60;
        //int seconds = (millis() / 1000) % 60;
        char hour_char[4];
        char min_char[4];
        //char sec_char[4];
        sprintf(hour_char, "%02d", hours);
        sprintf(min_char, "%02d", minutes);
        //sprintf(sec_char, "%02d", seconds);

        oled.clear();
        oled.setCursor(0, 0);
        oled.print(F("FILE:  "));
        oled.println(idMD);
        oled.println(F(""));
        oled.print(F("COUNT: "));
        oled.println(count);
        oled.println(F(""));
        oled.print(F("TIME:  "));
        oled.print(hour_char);
        oled.print(":");
        oled.println(min_char);
        oled.println(F(""));
        oled.print(F("RATE:  "));
        oled.print((count/(millis()/1000.)), 3);
        oled.print(F("   "));
        oled.print(tempC, 1);
        oled.print(F("*"));
        oled.print(F("C"));

        if (dataFile.getWriteError()) { //check if SD is ok
          oled.clear();
          oled.println(F(""));
          oled.println(F(""));
          oled.println(F("      FILE ERROR"));
          oled.println(F(""));
          oled.println(F(""));
          oled.println(F("      RESETING..."));
        
          PORTD = PORTD | B00001000;
          while(1);
       }

        if (millis() >= 86400000) {  //files with 24h of data
           dataFile.close();
           delay(2000);
          
           asm volatile ("  jmp 0"); 
        }
     }
   }
}

void syncCounts() {
  scount++;
}

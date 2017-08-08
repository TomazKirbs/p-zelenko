# coding=utf-8
# messprogramm.py
#------------------------------------------------------------

from Tkinter import *
import tkFont
import RPi.GPIO as GPIO
import os, sys, time, datetime, csv
 
# Global für vorhandene Temperatursensoren
tempSensorBezeichnung = [] #Liste mit den einzelnen Sensoren-Kennungen
tempSensorAnzahl = 0 #INT für die Anzahl der gelesenen Sensoren
tempSensorWert = [] #Liste mit den einzelnen Sensor-Werten
 
# Global für Programmstatus / 
programmStatus = 1 
 
def ds1820einlesen():
    global tempSensorBezeichnung, tempSensorAnzahl, programmStatus
    #Verzeichnisinhalt auslesen mit allen vorhandenen Sensorbezeichnungen 28-xxxx
    try:
        for x in os.listdir("/sys/bus/w1/devices"):
            if (x.split("-")[0] == "28") or (x.split("-")[0] == "10"):
                tempSensorBezeichnung.append(x)
                tempSensorAnzahl = tempSensorAnzahl + 1
    except:
        # Auslesefehler
        print ("Vrednosti ni mogoce prebrati.")
        programmStatus = 0
 
def ds1820auslesen():
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert, programmStatus
    x = 0
    try:
        # 1-wire Slave Dateien gem. der ermittelten Anzahl auslesen 
        while x < tempSensorAnzahl:
            dateiName = "/sys/bus/w1/devices/" + tempSensorBezeichnung[x] + "/w1_slave"
            file = open(dateiName)
            filecontent = file.read()
            file.close()
            # Temperaturwerte auslesen und konvertieren
            stringvalue = filecontent.split("\n")[1].split(" ")[9]
            sensorwert = (stringvalue[2:]) #/ 1000
            #temperatur = '%6.2f' % sensorwert #Sensor- bzw. Temperaturwert auf 2 Dezimalstellen formatiert
            tempSensorWert.insert(x,sensorwert) #Wert in Liste aktualisieren
            x = x + 1
    except:
        # Fehler bei Auslesung der Sensoren
        print ("Die Auslesung der DS1820 Sensoren war nicht möglich.")
        programmStatus = 0
 
#Programminitialisierung
ds1820einlesen() #Anzahl und Bezeichnungen der vorhandenen Temperatursensoren einlesen

danasnjidan = datetime.datetime.today()

dan = danasnjidan.strftime("%m/%d/%Y")

IzpisnaDatoteka = "/media/pi/USB DISK/Izpis + dan.csv" #Naslov datoteke za izpis

x = 0

with open(IzpisnaDatoteka, "a") as izpis:
    izpis.write("Datum:" + dan + "\n")
    izpis.write(",")
    while x < tempSensorAnzahl:
        izpis.write("Senzor" ";")
        x = x + 1
    izpis.write("\n")
    izpis.write("Cas,")
    x = 0
    while x < tempSensorAnzahl:
        izpis.write(tempSensorBezeichnung[x] + " ;")
        x = x + 1
    izpis.write("\n")
    #izpis.write("Datum:" + datetime.date() + "\n")
 
# Temperaturausgabe in Schleife
while programmStatus == 1:
    x = 0
    ds1820auslesen()
    
    tren_ura = datetime.datetime.now() #prebere trenuten čas
    ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
    
    with open(IzpisnaDatoteka, "a") as izpis:
        izpis.write(ura + " ;")
        while x < tempSensorAnzahl:
            izpis.write( tempSensorWert[x] + " ;")
            x = x + 1
        izpis.write("\n")
    x = 0
    print ("Sensorbezeichnung und Temperaturwert:")
    while x < tempSensorAnzahl:
        print (tempSensorBezeichnung[x] , " " , tempSensorWert[x] , " °C")
        x = x + 1
    time.sleep(.1)
    print ("\n")
   
# Programmende durch Veränderung des programmStatus
print ("Programm wurde beendet.")

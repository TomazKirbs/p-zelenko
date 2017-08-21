# coding=utf-8
# messprogramm.py
#ISKANJE POTI ZA AZURNI PRIKAZ TEMPERATUR 1.8.2017
#------------------------------------------------------------

from Tkinter import *
import Tkinter as tk
import tkFont
import RPi.GPIO as GPIO
import os, sys, time, datetime, csv, errno
from multiprocessing import Process, Value#Manager
 
# Temperaturausgabe in Schleife    

# Global für vorhandene Temperatursensoren
tempSensorBezeichnung = [] #Liste mit den einzelnen Sensoren-Kennungen
tempSensorAnzahl = 0 #INT für die Anzahl der gelesenen Sensoren
tempSensorWert = [] #Liste mit den einzelnen Sensor-Werten
skalirniFa = [] #Skalirni faktor a 
skalirniFb = [] #Skalirni faktor b
errorStat = 0
#IzpisDAN = {"nekaj"}


#temp1 = 0
#temp2 = 1
  
# Global für Programmstatus / 
#programmStatus = 1 
 
def ds1820einlesen():
    global tempSensorBezeichnung, tempSensorAnzahl, programmStat, errorStat
    #Verzeichnisinhalt auslesen mit allen vorhandenen Sensorbezeichnungen 28-xxxx
    try:
        for x in os.listdir("/sys/bus/w1/devices"):
            if (x.split("-")[0] == "28") or (x.split("-")[0] == "10"):
                tempSensorBezeichnung.append(x)
                tempSensorAnzahl = tempSensorAnzahl + 1
    except:
        # Auslesefehler
        print ("Vrednosti ni mogoce prebrati.")
        programmStat = 0
        errorStat = 1
    if programmStat == 1:

        jj=0
        # vpise naslov senzorja in začetne kalibracijske vrednosti v tabelo
        with open("CalibFile.csv", "w") as izpis:
            izpis.write( "Kalibracijske vrednosti: \n")
            for j in range(0, tempSensorAnzahl):

                jj = str(j)
                izpis.write( jj + ";" + tempSensorBezeichnung[j] + ";1;0 \n")
                
        
        
 
def ds1820auslesen():
    global tempSensorBezeichnung, tempSensorWert, tempSensorAnzahl, programmStat 
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
            sensorwert = float(stringvalue[2:])/ 1000
            temperatur = '%6.1f' % sensorwert #Sensor- bzw. Temperaturwert auf 1 Dezimalstellen formatiert
            tempSensorWert.insert(x,temperatur) #Wert in Liste aktualisieren
#            print (temperatur)
            x = x + 1
    except:
        # Fehler bei Auslesung der Sensoren
        print ("Vrednosti ni mogoce prebrati.")
        programmStat = 0
        errorStat = 1
 

    #Programminitialisierung
    

danasnjidan = datetime.datetime.today()

dan = danasnjidan.strftime("%m/%d/%Y")

NaslovIzpisneDatoteke = "/media/pi/USB DISK/" #Naslov datoteke za izpis


programmStat = 1 

def Func2(temp1, temp2, programmStatus, errorStatus, proc1, proc2):
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert, programmStatm, uraStart1, uraStart2
    
    programmStatus.value = 1
    programmStat = 1
    tempStart = float(  30.0)
    tempStop = float(30.0)
    tempPasterizacije = 35.0
    timeOFpaster = 5 # čas pasterizacije v minutah 
    
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

    try:
        file_handle = os.open('CalibFile.csv', flags)
    except OSError as e:
        if e.errno == errno.EEXIST:  # Failed as the file already exists.
            
            with open('CalibFile.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                next(csv_reader)
                l=0
                for row in csv_reader:
                    tempSensorAnzahlK, tempSensorBezeichnungK, skalirniFaK, skalirniFbK = row
 #                   print(row)
                    tempSensorBezeichnung.append(l)
#                    tempSensorAnzahl = tempSensorAnzahl + 1
                    skalirniFa.append(l)
                    skalirniFb.append(l)
                    tempSensorAnzahl = int(tempSensorAnzahlK)+1
                    tempSensorBezeichnung[l] = str(tempSensorBezeichnungK)
                    skalirniFa[l] = float(skalirniFaK)
                    skalirniFb[l] = float(skalirniFbK)
#                    print(tempSensorBezeichnung, tempSensorAnzahl, skalirniFa, skalirniFb)
                    l=l+1
            
            
        else:  # Something unexpected went wrong so reraise the exception.
            raise
    else:  # No exception, so the file must have been created successfully.
        ds1820einlesen() #Anzahl und Bezeichnungen der vorhandenen Temperatursensoren einlesen
    
    x = 0
    
    
    
    ds1820auslesen()
        
#        tsw0 = tempSensorWert[0]
#        tsw1 = tempSensorWert[1]
    
    endOFpaster1 = datetime.datetime.now()
    endOFpaster2 = datetime.datetime.now()
    uraStart1 = datetime.datetime.now()
    uraStart2 = datetime.datetime.now()   
    
    while programmStatus.value != 0:
        x = 0
        programmStatus.value = 1
#        tempSensorWert.lock()
        
        tsw0 = float(tempSensorWert[0])
        tsw1 = float(tempSensorWert[1])
                   
        if tsw0 >= tempStart:
            programmStatus.value = 2
            
            tren_ura = datetime.datetime.now() #prebere trenuten čas
            uraStart1 = tren_ura
#            endOFpaster1 = tren_ura + timeOFpaster
            ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
            IzpisDAN = tren_ura.strftime("Dan%d%m%Y_Ura%H%M%S") #formatira trenuten čas (čas kreirane datoteke)
    
            IzpisnaDatoteka1 = NaslovIzpisneDatoteke + "Kotel1_" + str(IzpisDAN) + ".csv" #formatira ime kreirane datoteke
        
            with open(IzpisnaDatoteka1, "a") as izpis:
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
            
        elif tsw1 >= tempStart:
            programmStatus.value = 3
            
            tren_ura = datetime.datetime.now() #prebere trenuten čas
            uraStart2 = tren_ura
#            endOFpaster2 = tren_ura + timeOFpaster
            ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
            IzpisDAN = tren_ura.strftime("Dan%d%m%Y_Ura%H%M%S") #formatira trenuten čas (čas kreirane datoteke)
    
            IzpisnaDatoteka2 = NaslovIzpisneDatoteke + "Kotel2_" + str(IzpisDAN) + ".csv" #formatira ime kreirane datoteke
        
        
            with open(IzpisnaDatoteka2, "a") as izpis:
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
            
        else:
            programmStatus.value = 1
#        tempSensorWert.relles()
        temp1.value = float(tempSensorWert[0])
        temp2.value = float(tempSensorWert[1])
        ds1820auslesen()
        time.sleep(.5) #zakasnitev med branjem vrednosti temperature
        
        while programmStatus.value == 2:
            tren_ura = datetime.datetime.now() #prebere trenuten čas
            ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
            with open(IzpisnaDatoteka1, "a") as izpis:
               izpis.write(ura + " ;")
               while x < tempSensorAnzahl:
                   izpis.write(tempSensorWert[x] + " ;")
                   x = x + 1
               izpis.write("\n")
               x = 0
               
            endOFpaster1 = tren_ura - uraStart1
            dmin1 = endOFpaster1.total_seconds()/60
            processProc1 = dmin1 *  100 / timeOFpaster
            processProc11 = int(round(processProc1))
            print (processProc11)
#            minOFpaster
            # posredovanje statusa napak za multiprocesno izmenjavo podatkov
            
            proc1.value = processProc11
            temp1.value = float(tempSensorWert[0])
            temp2.value = float(tempSensorWert[1])

            if errorStat == 1:  #Prepis napake za prikatz na GUI
                errorStatus.value = 1
            elif errorStat == 0:
                errorStatus.value = 0
            
            time.sleep(.5) #zakasnitev med branjem vrednosti temperature
            
            tsw0 = float(tempSensorWert[0])
            tsw1 = float(tempSensorWert[1])
            if tsw1 >= tempStart:
                programmStatus.value = 4
            
                tren_ura = datetime.datetime.now() #prebere trenuten čas
                uraStart2 = tren_ura
                ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
                IzpisDAN = tren_ura.strftime("Dan%d%m%Y_Ura%H%M%S") #formatira trenuten čas (čas kreirane datoteke)
    
                IzpisnaDatoteka2 = NaslovIzpisneDatoteke + "Kotel2_" + str(IzpisDAN) + ".csv" #formatira ime kreirane datoteke
        
        
                with open(IzpisnaDatoteka2, "a") as izpis:
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
            elif tsw0 <= tempStop and processProc11 > 99:
                programmStatus.value = 1
                print("koncano1")
                    
            ds1820auslesen()
            
        while programmStatus.value == 3:
            tren_ura = datetime.datetime.now() #prebere trenuten čas
            ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
            with open(IzpisnaDatoteka2, "a") as izpis:
               izpis.write(ura + " ;")
               while x < tempSensorAnzahl:
                   izpis.write(tempSensorWert[x] + " ;")
                   x = x + 1
               izpis.write("\n")
               x = 0
                          
            endOFpaster2 = tren_ura - uraStart2
            dmin2 = endOFpaster2.total_seconds()/60
            processProc2 = dmin2 *  100 / timeOFpaster
            processProc21 = int(round(processProc2))
            print (processProc21)

            # posredovanje statusa napak za multiprocesno izmenjavo podatkov
            proc2.value = processProc21
            temp1.value = float(tempSensorWert[0])
            temp2.value = float(tempSensorWert[1])

            if errorStat == 1:  #Prepis napake za prikatz na GUI
                errorStatus.value = 1
            elif errorStat == 0:
                errorStatus.value = 0
            
            time.sleep(.5) #zakasnitev med branjem vrednosti temperature
            
            tsw0 = float(tempSensorWert[0])
            tsw1 = float(tempSensorWert[1])
            if tsw0 >= tempStart:
                programmStatus.value = 4
            
                tren_ura = datetime.datetime.now() #prebere trenuten čas
                uraStart1 = tren_ura
#                endOFpaster1 = tren_ura + timeOFpaster
                ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
                IzpisDAN = tren_ura.strftime("Dan%d%m%Y_Ura%H%M%S") #formatira trenuten čas (čas kreirane datoteke)
    
                IzpisnaDatoteka1 = NaslovIzpisneDatoteke + "Kotel1_" + str(IzpisDAN) + ".csv" #formatira ime kreirane datoteke
        
        
                with open(IzpisnaDatoteka1, "a") as izpis:
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
            elif tsw1 <= tempStop and processProc21 > 99:
                programmStatus.value = 1
                    
            ds1820auslesen()
        
        while programmStatus.value == 4:
            tren_ura = datetime.datetime.now() #prebere trenuten čas
            ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
            with open(IzpisnaDatoteka1, "a") as izpis:
               izpis.write(ura + " ;")
               while x < tempSensorAnzahl:
                   izpis.write(tempSensorWert[x] + " ;")
                   x = x + 1
               izpis.write("\n")
               x = 0
            endOFpaster1 = tren_ura - uraStart1
            dmin1 = endOFpaster1.total_seconds()/60
            processProc1 = dmin1 *  100 / timeOFpaster
            processProc11 = int(round(processProc1))
            print (processProc11)
            
            
            with open(IzpisnaDatoteka2, "a") as izpis:
               izpis.write(ura + " ;")
               while x < tempSensorAnzahl:
                   izpis.write(tempSensorWert[x] + " ;")
                   x = x + 1
               izpis.write("\n")
               x = 0
            
            endOFpaster2 = tren_ura - uraStart2
            dmin2 = endOFpaster2.total_seconds()/60
            processProc2 = dmin2 *  100 / timeOFpaster
            processProc21 = int(round(processProc2))
            print (processProc21)

            # posredovanje statusa napak za multiprocesno izmenjavo podatkov
            proc1.value = processProc11
            proc2.value = processProc21
            temp1.value = float(tempSensorWert[0])
            temp2.value = float(tempSensorWert[1])

            if errorStat == 1:  #Prepis napake za prikatz na GUI
                errorStatus.value = 1
            elif errorStat == 0:
                errorStatus.value = 0
            
            time.sleep(.5) #zakasnitev med branjem vrednosti temperature
            
            tsw0 = float(tempSensorWert[0])
            tsw1 = float(tempSensorWert[1])
            if tsw1 <= tempStop and processProc21 > 99:
                programmStatus.value = 2
                
            elif tsw0 <= tempStop and processProc11 > 99:
                programmStatus.value = 3
                    
            ds1820auslesen()
            
        


def Func1(temp1, temp2, programmStatus, errorStatus, proc1, proc2):
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert
    
    temp11 = 0
    temp22 = 0
    temp1h = 31
    temp1l = 30
    temp2h = 31
    temp2l = 30
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(40, GPIO.OUT)
    GPIO.output(40, GPIO.LOW)
      

    class Prikaz(tk.Frame):
        def __init__(self, master=None):
            tk.Frame.__init__(self, master)
            self.master = master
            master.title("PRIKAZ TEMPERATUR")
            master.geometry('480x320')
            self.pack()
            self.Widgets()
            
        def Widgets(self):
            self.myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')
            self.tempFont = tkFont.Font(family = 'Helvetica', size = 40, weight = 'bold')
            
            self.time_now = tk.StringVar()                                 
            self.var1 = IntVar()            
            self.var2 = IntVar()
            self.proc1 = IntVar()            
            self.proc2 = IntVar()
            self.colour1 = StringVar()
            self.colour2 = StringVar()
            self.errors = tk.StringVar()
#            self.errors.set("Zagon prikazovalnika")
            
            self.UpdateVar()
            
            self.timeLabel = tk.Label(self, font = self.myFont)
            self.timeLabel.grid(row=0, columnspan=2)
            self.timeLabel["textvariable"] = self.time_now
            
            self.exitButton  = Button(self, text = "Exit", font = self.myFont, command = self.exitProgram, height =1 , width = 5, bg = "red") 
            self.exitButton.grid(row=1)
            
            self.kotel1Button  = Button(self, text = "Kotel 1", font = self.myFont, command = self.kotel1nast, height =1 , width = 5) 
            self.kotel1Button.grid(row=2)
            
            self.kotel2Button  = Button(self, text = "Kotel 2", font = self.myFont, command = self.kotel2nast, height =1 , width = 5) 
            self.kotel2Button.grid(row=2, column=1)
    
            self.temp1Label = Label(self, textvariable = self.var1, fg = "black", font = self.tempFont, height = 2, width = 5)
            self.temp1Label.grid(row=3)
            
            self.temp2Label = Label(self, textvariable = self.var2, fg = "black", font = self.tempFont, height = 2, width = 5)
            self.temp2Label.grid(row=3, column=1)
            
            self.proc1Label = Label(self, textvariable = self.proc1, font = self.myFont, height = 1, width = 5)
            self.proc1Label.grid(row=4)
            
            self.proc2Label = Label(self, textvariable = self.proc2, font = self.myFont, height = 1, width = 10)
            self.proc2Label.grid(row=4, column=1)
            
            self.errorLabel = tk.Label(self, font = self.myFont)
            self.errorLabel.grid(row=5, columnspan=2)
            self.errorLabel["textvariable"] = self.errors
            
            
        def UpdateVar(self):
            
            tren_ura = datetime.datetime.now()
            IzpisDAN = tren_ura.strftime("Datum: %d.%m.%Y Ura: %H:%M:%S")
            self.time_now.set(IzpisDAN)
            
            self.var1.set(str(temp1.value) + u"\u2103") #
            
            self.var2.set(str(temp2.value) + u"\u2103")
            
            self.proc1.set(str(proc1.value) + u"\u0025") #
            
            self.proc2.set(str(proc2.value) + u"\u0025")
            
            if errorStatus.value == 0:
                self.errors.set("Prikazovalnik deluje brez napak!")
            elif errorStatus.value == 1:
                self.errors.set("Vrednosti ni mogoce prebrati!")
#            self.temp1Label.config(fg = "black")
 #           self.temp2Label.config(fg = "black")
            
            
#            self.temp1Label.config(fg = "black")
            if programmStatus.value == 2 or programmStatus.value == 4:     
                if temp1h < temp1.value :
                    self.temp1Label.config(fg = "red")
                elif temp1l > temp1.value :
                    self.temp1Label.config(fg = "blue")
                else :
                    self.temp1Label.config(fg = "green")
                    
            
#            self.temp2Label.config(fg = "black")
            if programmStatus.value == 3 or programmStatus.value == 4:     
                if temp1h < temp2.value :
                    self.temp2Label.config(fg = "red")
                elif temp1l > temp2.value :
                    self.temp2Label.config(fg = "blue")
                else :
                    self.temp2Label.config(fg = "green")
                
            
            self.master.after(1000,self.UpdateVar)
            
            
        def exitProgram(self):

            print("Exit Button pressed")
    #        GPIO.cleanup()
            programmStatus.value = 0
            self.master.quit()
            
        def kotel1nast(self):
            pass
        
        def kotel2nast(self):
            pass
    

    root = tk.Tk()
    a = Prikaz(master=root)
    root.mainloop()

    # Programmende durch Veränderung des programmStatus
#    print ("Programm wurde beendet.")
    
if __name__=='__main__':
#    arr = Array('empSensorBezeichnung',' tempSensorWert')
#    manager = Manager()
    x = Value('d', 0.0)
    y = Value('d', 0.0)
    z = Value('i', 0)
    z1 = Value('i', 0)
    proc1 = Value('i', 0)
    proc2 = Value('i', 0)
#    time = Value( 'ctypes.c_char_p',"Datum: %d.%m.%Y Ura: %H:%M:%S")
    
    p1 = Process(target = Func1, args = (x, y, z, z1, proc1, proc2))
    p1.start()
#    p1.join()
     
    p2 = Process(target = Func2, args = (x, y, z, z1, proc1, proc2))
    p2.start()
#    p2.join()

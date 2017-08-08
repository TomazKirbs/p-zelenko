# coding=utf-8
# messprogramm.py
#ISKANJE POTI ZA AZURNI PRIKAZ TEMPERATUR 1.8.2017
#------------------------------------------------------------

from Tkinter import *
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

#temp1 = 0
#temp2 = 1

# Global für Programmstatus / 
#programmStatus = 1 
 
def ds1820einlesen():
    global tempSensorBezeichnung, tempSensorAnzahl, programmStat 
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
            sensorwert = (stringvalue[2:]) #/ 1000
            #temperatur = '%6.2f' % sensorwert #Sensor- bzw. Temperaturwert auf 2 Dezimalstellen formatiert
            tempSensorWert.insert(x,sensorwert) #Wert in Liste aktualisieren
            x = x + 1
    except:
        # Fehler bei Auslesung der Sensoren
        print ("Vrednosti ni mogoce prebrati.")
        programmStat = 0
 

    #Programminitialisierung
    

danasnjidan = datetime.datetime.today()

dan = danasnjidan.strftime("%m/%d/%Y")

NaslovIzpisneDatoteke = "/media/pi/USB DISK/" #Naslov datoteke za izpis


    #izpis.write("Datum:" + datetime.date() + "\n")

programmStat = 1 

def Func2(temp1, temp2, programmStatus):
    global tempSensorBezeichnung, tempSensorAnzahl, tempSensorWert, programmStat
    
    programmStatus.value = 1
    programmStat = 1
    
    
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
                    print(row)
                    tempSensorBezeichnung.append(l)
#                    tempSensorAnzahl = tempSensorAnzahl + 1
                    skalirniFa.append(l)
                    skalirniFb.append(l)
                    tempSensorAnzahl = int(tempSensorAnzahlK)+1
                    tempSensorBezeichnung[l] = str(tempSensorBezeichnungK)
                    skalirniFa[l] = float(skalirniFaK)
                    skalirniFb[l] = float(skalirniFbK)
                    print(tempSensorBezeichnung, tempSensorAnzahl, skalirniFa, skalirniFb)
                    l=l+1
            
            
        else:  # Something unexpected went wrong so reraise the exception.
            raise
    else:  # No exception, so the file must have been created successfully.
        ds1820einlesen() #Anzahl und Bezeichnungen der vorhandenen Temperatursensoren einlesen
    
    x = 0
    tren_ura = datetime.datetime.now() #prebere trenuten čas
    ura = tren_ura.strftime("%H:%M:%S") #formatira trenuten čas
    IzpisDAN = tren_ura.strftime("Dan%d%m%Y_Ura%H%M%S") #formatira trenuten čas
    
    
    IzpisnaDatoteka = NaslovIzpisneDatoteke + "Kotel1_" + str(IzpisDAN) + ".csv"
        
        
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
    
    while programmStatus.value == 1:
        x = 0
        ds1820auslesen()
    
#        IzpisnaDatoteka = 
   
        with open(IzpisnaDatoteka, "a") as izpis:
            izpis.write(ura + " ;")
            while x < tempSensorAnzahl:
                izpis.write(tempSensorWert[x] + " ;")
                x = x + 1
            izpis.write("\n")
            x = 0
            print ("Sensorbezeichnung und Temperaturwert:")
        while x < tempSensorAnzahl:
            print (tempSensorBezeichnung[x] , " " , tempSensorWert[x] , " °C")
            x = x + 1
        time.sleep(.9)
        print ("\n")
        temp1.value = float(tempSensorWert[0])/1000
        temp2.value = float(tempSensorWert[1])/1000



def Func1(temp1, temp2, programmStatus):
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
    
    win = Tk()
    myFont = tkFont.Font(family = 'Helvetica', size = 36, weight = 'bold')
    tempFont = tkFont.Font(family = 'Helvetica', size = 50, weight = 'bold')
    
#    rightButton["text"] = temp1.value
#    leftButton["text"] = temp2.value
    
    def right(): #osveževanje temperature
    	print("LED button pressed")
    	if temp11 != temp1.value :
    	    rightButton["text"] = temp1.value
    	if temp1h < temp1.value :
            rightButton["fg"] = "red"
        elif temp1l > temp1.value :
            rightButton["fg"] = "blue"
        else :
            rightButton["fg"] = "green"
    	win.after(1000,right)
    		
    def left():  #osveževanje temperature
    	if temp22 != temp2.value :
    	    leftButton["text"] = temp2.value
    	if temp2h < temp2.value :
            leftButton["fg"] = "red"
        elif temp2l > temp2.value :
            leftButton["fg"] = "blue"
        else :
            leftButton["fg"] = "green"
    	win.after(1000,left)

    def exitProgram():
	print("Exit Button pressed")
        GPIO.cleanup()
        programmStatus.value = 0
	win.quit()	

    win.title("PRIKAZ TEMPERATUR")
    win.geometry('480x320')
    testgit
    
#    var = StringVar()
#    self.var.set(str(temp2.value))
    
#    self.tempLabel = Label(win, text = self.var, font = myFont, height = 1, width = 5)
#    self.tempLabel.pack(side = TOP)

    exitButton  = Button(win, text = "Exit", font = myFont, command = exitProgram, height =1 , width = 5) 
    exitButton.pack(side = TOP)

    rightButton = Button(win, text = temp1.value, font = tempFont, command = right, height = 4, width =6 )
    rightButton.pack(side = RIGHT)

    leftButton = Button(win, text = temp2.value, font = tempFont, command = left, height = 4, width =7 )
    leftButton.pack(side = LEFT)

    mainloop()

    # Programmende durch Veränderung des programmStatus
    print ("Programm wurde beendet.")

''' def Func1(temp1, temp2, programmStatus):
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
    

    myFont = tkFont.Font(family = 'Helvetica', size = 36, weight = 'bold')
    tempFont = tkFont.Font(family = 'Helvetica', size = 50, weight = 'bold')


    class Application:
        def __init__(self, master):
            frame = Frame(master)
            frame.pack()
            
#        self.x = tk.IntVar()
 #       self.createWidgets()

#    rightButton["text"] = temp1.value
 #   leftButton["text"] = temp2.value
    
#    def right(): #osveževanje temperature
#    	print("LED button pressed")
#    	if temp11 != temp1.value :
#    	    rightButton["text"] = temp1.value
#    	if temp1h < temp1.value :
#            rightButton["fg"] = "red"
#        elif temp1l > temp1.value :
#            rightButton["fg"] = "blue"
#        else :
#            rightButton["fg"] = "green"
#    	win.after(1000,right)
    		
#    def left():  #osveževanje temperature
#    	if temp22 != temp2.value :
#    	    leftButton["text"] = temp2.value
#    	if temp2h < temp2.value :
#            leftButton["fg"] = "red"
#        elif temp2l > temp2.value :
#            leftButton["fg"] = "blue"
#        else :
#            leftButton["fg"] = "green"
#    	win.after(1000,left)
        def exitProgram(self):

            print("Exit Button pressed")
            GPIO.cleanup()
            programmStatus.value = 0
            frame.quit()	

 #   root.title("PRIKAZ TEMPERATUR")
 #   root.geometry('480x320')
    
#    var = StringVar()
#    self.var.set(temp2.value)
    
#    self.tempLabel = Label(win, text = self.var, font = myFont, height = 1, width = 5)
#    self.tempLabel.pack(side = TOP)

    root.exitButton  = Button(win, text = "Exit", font = myFont, command = self.exitProgram, height =1 , width = 5) 
    root.exitButton.pack(side = TOP)

#    rightButton = Button(win, text = temp1.value, font = tempFont, command = right, height = 4, width =6 )
#    rightButton.pack(side = RIGHT)

#    leftButton = Button(win, text = temp2.value, font = tempFont, command = left, height = 4, width =7 )
#    leftButton.pack(side = LEFT)
    root = tk.Tk()
    a = Aplication(root)
    root.mainloop()

    # Programmende durch Veränderung des programmStatus
    print ("Programm wurde beendet.")
 '''   
if __name__=='__main__':
#    arr = Array('empSensorBezeichnung',' tempSensorWert')
#    manager = Manager()
    x = Value('d', 0.0)
    y = Value('d', 0.0)
    z = Value('i', 0)
    
    p1 = Process(target = Func1, args = (x, y, z))
    p1.start()
#    p1.join()
     
    p2 = Process(target = Func2, args = (x, y, z))
    p2.start()
#    p2.join()

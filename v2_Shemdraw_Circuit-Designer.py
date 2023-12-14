# -*- coding: utf-8 -*-
"""
Created on Fri May 12 12:05:04 2023

v1.0

@author: tpantele
"""

    #############################################################################################################################################
    # ---- INFO zur Verwendung  von "CurrentLabelInline (Strompfeil)" und "CurrentLabel (Spannungspfeil)"                                       #
    #                                                                                                                                           #
    # +++ CurrentLabelInline (Strompfeil) +++                                                                                                   #
    # d += elm.CurrentLabelInline(direction='out', start=True).at(V).label('$I_5$', loc = "bottom")                                             #
    #                                                                                                                                           #
    #     direction = "in" / "out"                      --- Richtung des Strompfeils "zur" Quelle oder "weg" von Quelle                         #
    #     start = "True" / "False"                      --- Position des Strompfeils "links" von Quelle oder "rechts" von Quelle                #
    #     label(loc = "top", "bottom", "left", "right") --- Position des Labels                                                                 #
    #                                                                                                                                           #
    #                                                                                                                                           #
    # +++ CurrentLabel (Spannungspfeil) +++                                                                                                     #
    # d += elm.CurrentLabel(ofst=-0.75, length=1.5, top=True, reverse=False ).at(V).label('$U_0$', loc="top")                                   #
    #                                                                                                                                           #
    #     ofst = 0.75                       --- Legt ein Offset des Labels fest. "0.75" ist ein guter Richtwert                                 #
    #     length = 1.5                      --- Definiert die Länge des Pfeils. "1.5" ist ein guter Richtwert                                   #
    #     top = "True" / "False"            --- Legt fest, ob der Spannnungspfeil "über" oder "unter" die Quelle gelegt wird                    #
    #     reverse = "True" / False"         --- Legt fest, ob der Spannungspfeil von "rechts nach links" oder von "links nach rechts" zeigt     #
    #############################################################################################################################################


#### todo
"""
"length()" mit in ausgabe der elemente schreiben
löschen"backspace" löscht nicht den Eintrag bei "showelements"
Label "R" nicht in "Show elements" drin
theta nicht bei Dot (beeinflusst die position des labels?)
--delete crosshair (own function?)
"""


from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QLabel, QRadioButton, QComboBox, QTableWidget, QTableWidgetItem, QShortcut
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QKeySequence
import sys
from PyQt5.Qt import Qt


import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import *


import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# -- wird zur Erstellung von eigenen Schemdraw Zeichnungen verwendet
import numpy as np

gap = [np.nan, np.nan] 


### --------------------- Eigene Bauteilklassen
class VoltageSource(elm.Element2Term):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        radius = 0.5
        color = 'black'
        length = 3
    
        self.segments.append(Segment([[0, 0], [0, 0], [1, 0], [1, 0]]))
        self.segments.append(SegmentCircle([0.5, 0], 0.5))



class CurrentSource(elm.Element2Term):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        radius = 0.5
        color = 'black'
        

        self.segments.append(Segment([[0, 0], [0, 0], gap, [1, 0], [1, 0]]))
        self.segments.append(SegmentCircle([0.5, 0], 0.5))
        self.segments.append(Segment([[0.5, -0.5], [0.5, 0.5]], color))



class Crosshair(elm.Element):
    def __init__(self, *d, **kwargs):
        super().__init__(*d, **kwargs)
        
        line_len = 0.1
        
        self.segments.append(Segment([(0, 0), (line_len, line_len)], "red"))
        self.segments.append(Segment([(0, 0), (-line_len, line_len)], "red"))
        self.segments.append(Segment([(0, 0), (line_len, -line_len)], "red"))
        self.segments.append(Segment([(0, 0), (-line_len, -line_len)], "red"))


### --------------- Bauteilklassen Ende 




### --------------- GUI definieren
class UI(QDialog):       
    
    def __init__(self):
        super(UI, self).__init__()
        
        
        
        # Load the ui file
        uic.loadUi("Schemdraw_Circuit-Designer.ui", self)
        
        # Definde widgets
        self.button_start_circuit = self.findChild(QPushButton, "pushButton_start_circuit")
        self.button_show_elements = self.findChild(QPushButton, "pushButton_show_elements")
        #self.button_show_labels = self.findChild(QPushButton, "pushButton_show_labels")
        self.button_print = self.findChild(QPushButton, "pushButton_print")
        self.button_up = self.findChild(QPushButton, "pushButton_Up")
        self.button_down = self.findChild(QPushButton, "pushButton_Down")
        self.button_left = self.findChild(QPushButton, "pushButton_Left")
        self.button_right = self.findChild(QPushButton, "pushButton_Right")
        self.button_show_img = self.findChild(QPushButton, "pushButton_show_img")
        self.button_save_img = self.findChild(QPushButton, "pushButton_save_img")
        self.button_undo = self.findChild(QPushButton, "pushButton_undo")

        
        
        self.button_TEST = self.findChild(QPushButton, "pushButton_TEST")
        
        
        
        self.label_img = self.findChild(QLabel, "label")
        self.comboBox_elements = self.findChild(QComboBox, "comboBox_elements")
        self.tableWidget = self.findChild(QTableWidget, "tableWidget")
        
        
        
        # Define button functions
        self.button_start_circuit.clicked.connect(self.new_circuit)
        self.button_show_elements.clicked.connect(self.show_element_list)
        
        self.button_print.clicked.connect(self.printELementsToSchemdraw)
        self.button_show_img.clicked.connect(self.show_img)
        self.button_save_img.clicked.connect(self.save_img)
        
        # --- Direction in angle degree 
        # theta(0) = right()
        # theta(90) = up()
        # theta(180)=left()
        # theta(270) = down()
        self.button_right.clicked.connect(lambda: self.direction_clicked(0))
        self.button_up.clicked.connect(lambda: self.direction_clicked(90))
        self.button_left.clicked.connect(lambda: self.direction_clicked(180))
        self.button_down.clicked.connect(lambda: self.direction_clicked(270))
        
        self.button_undo.clicked.connect(self.removeElement)
        
        
        
        # --- Define shortcuts     
        self.button_up.setShortcut("up")
        self.button_down.setShortcut("down")
        self.button_left.setShortcut("left")
        self.button_right.setShortcut("right")
        
        
        
        self.elementTypesWithShortcuts_dict = {
            "r": "Resistor",
            "p": "Potentiometer",
            "c": "Capacitor",
            "i": "Inductor",
            "Diode": "xxxx",
            "l":"Line",
            "h": "Line (hidden)",
            "d": "Dot",
            "D": "Dot (Open)",
            "v": "Source: Voltage (DC)",
            "V": "Source: Voltage (AC)",
            "C": "Source: Current (DC)",
            "Source: Current (AC)": "xxxx"
            }
        
        
        
        self.elementTypes = [
            "Resistor",
            "Potentiometer",
            "Capacitor",
            "Inductor",
            "Diode",
            "Line",
            "Line (hidden)",
            "Dot",
            "Dot (Open)",
            "Source: Voltage (DC)",
            "Source: Voltage (AC)",
            "Source: Current (DC)",
            "Source: Current (AC)"
            ]
        
        
        
        self.elements2schemdraw_dict = {
            
            "Resistor": "elm.Resistor()",
            "Potentiometer": "elm.Potentiometer()",
            "Capacitor": "elm.Capacitor()",
            "Inductor": "elm.Inductor()",
            "Diode": "elm.Diode()",
            "Line": "elm.Line()",
            "Line (hidden)": "elm.Line().color(\"None\")",
            "Dot (Open)": "elm.Dot(open=True)",
            "Dot": "elm.Dot()",
            "Source: Voltage (DC)": "VoltageSource()",
            "Source: Voltage (AC)": "VoltageSource()",
            "Source: Current (DC)": "CurrentSource()",
            "Source: Current (AC)": "CurrentSource()"
            
            }
        
        
        self.elementTypes.sort()
        
        for i in range(len(self.elementTypes)):
            self.comboBox_elements.addItem(self.elementTypes[i])


        
        # Show the app
        self.show()
        
        
        
    
    
    def keyPressEvent(self, event):
        #if event.key() == Qt.Key_A:
        self.pressedKey = str(event.text())
        
        #print(self.pressedKey)
        if self.pressedKey in self.elementTypesWithShortcuts_dict:
            
            print(event.text())
            index = 0
            self.comboBox_elements.setItemText(index, self.elementTypesWithShortcuts_dict[event.text()])
            print(self.elementTypesWithShortcuts_dict[event.text()])
            
            # ---> Combobox soll auf Item gesetzt werden um Shortcuts zu verwenden zu können
            
    
    
    def show_element_list(self):
        
        print("Elements: ")
        for i in range(len(self.element_list_names)):
            
            print(self.element_list_names[i])
            

    
    def removeElement(self):
        print("Undo -- neu konfigurieren!")
        
    """  ---- Muss neu konfiguriert werden
        if "Resistor" in self.building_pattern_list[-1]:
            self.counter_R_elements = self.counter_R_elements - 1
        self.building_pattern_list.pop(-1)
        print(len(self.element_list_names))
        self.refresh()
    
    """
    
    
    # --- add Element
    def addElementToTable(self, selectedElement, direction, color, voltageArrow_activ, voltageArrow_direction, voltageArrow_offset, currentArrow_activ, currentArrow_direction, currentArrow_offset):
        self.selectedElement = selectedElement
        self.direction = direction
        self.color = color
        self.voltageArrow_activ = voltageArrow_activ
        self.voltageArrow_direction = voltageArrow_direction
        self.voltageArrow_offset = voltageArrow_offset
        self.currentArrow_activ = currentArrow_activ
        self.currentArrow_direction = currentArrow_direction
        self.currentArrow_offset = currentArrow_offset
        
        row_number = self.tableWidget.rowCount()
        
        
        self.tableWidget.insertRow(row_number)
        self.tableWidget.setItem(row_number, 0, QtWidgets.QTableWidgetItem(self.selectedElement))
        self.tableWidget.setItem(row_number, 1, QtWidgets.QTableWidgetItem(str(self.direction)))
        self.tableWidget.setItem(row_number, 2, QtWidgets.QTableWidgetItem(self.color))
        self.tableWidget.setItem(row_number, 3, QtWidgets.QTableWidgetItem(str(self.voltageArrow_activ)))
        self.tableWidget.setItem(row_number, 4, QtWidgets.QTableWidgetItem(str(self.voltageArrow_direction)))
        self.tableWidget.setItem(row_number, 5, QtWidgets.QTableWidgetItem(str(self.voltageArrow_offset)))
        self.tableWidget.setItem(row_number, 6, QtWidgets.QTableWidgetItem(str(self.currentArrow_activ)))
        self.tableWidget.setItem(row_number, 7, QtWidgets.QTableWidgetItem(str(self.currentArrow_direction)))
        self.tableWidget.setItem(row_number, 8, QtWidgets.QTableWidgetItem(str(self.currentArrow_offset)))
        
        row_number = row_number + 1
        
                
    
    def printELementsToSchemdraw(self):
        self.rowCount = self.tableWidget.rowCount()
        self.columnCount = self.tableWidget.columnCount()
        
        self.counter_R_elements = 1
        self.counter_U_elements = 1
        self.counter_I_elements = 1
        self.counter_C_elements = 1
        self.counter_L_elements = 1
        
        
        
        for row in range(self.rowCount):
                print(row, self.tableWidget.item(row,0).text(), self.tableWidget.item(row,1).text(), self.tableWidget.item(row,2).text(), self.tableWidget.item(row,3).text(), self.tableWidget.item(row,4).text(), self.tableWidget.item(row,5).text(), self.tableWidget.item(row,6).text())
        
        print("\n")
        
        with schemdraw.Drawing() as d:
            for row in range(self.rowCount):
                
                self.element_type = self.tableWidget.item(row,0).text()
                self.element_angle = float(self.tableWidget.item(row,1).text())
                self.color = self.tableWidget.item(row,2).text()
                self.voltageActiv = self.tableWidget.item(row,3).text()
                self.voltageDirection = self.tableWidget.item(row,4).text()
                self.voltageOffset = float(self.tableWidget.item(row,5).text())
                self.currentActiv = self.tableWidget.item(row,6).text()
                self.currentDirection = self.tableWidget.item(row,7).text()
                self.currentOffset = float(self.tableWidget.item(row,8).text())
                
    
                if self.element_type == "Resistor":
                    
                    d.add( R := (elm.Resistor().theta(self.element_angle).length(3).color(self.color).label("$R_"+str(self.counter_R_elements)+"$")))
                    self.counter_R_elements = self.counter_R_elements + 1
        
                
                    # Spannungspfeile
                    if self.voltageActiv == "1":
                        d.add(elm.CurrentLabel(length=1.5, reverse=True, ofst=self.voltageOffset, top=True).at(R).label("$U_"+str(self.counter_R_elements)+"$"))
                        
                    # Strompfeile
                    if self.currentActiv == "1":
                        d.add(elm.CurrentLabelInline(direction="out", start=False, ofst=self.currentOffset).at(R).label("$I_"+str(self.counter_R_elements)+"$"))
                        
        
        
    def direction_clicked(self, direction):
        self.direction = direction
        
        # Element aus Combobox nehmen und aus DIR suchen
        self.selectedElement = self.comboBox_elements.currentText()
        self.color = "black"
        
        if "hidden" in self.selectedElement:
            self.color = 'None'
            self.selectedElement = "Line"
            
        self.addElementToTable(self.selectedElement, self.direction, self.color, 0,0,0,0,0,0)
        self.printELementsToSchemdraw()

    
        
    def new_circuit(self):
        self.element_list.clear()
        
    
    def save_img(self, d):
        d.save(fname="test_automatic", dpi=120)
        print("IMG saved")
    
    def show_img(self):
        # Open Image
        self.pixmap = QPixmap("test_automatic.png")
        #self.pixmap = QPixmap("test1.png")
        
        self.label_img.setScaledContents(True)
        
        self.label_img.setPixmap(self.pixmap)

     


# Initialize the app
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
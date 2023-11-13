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


# Eigene Bauteilklassen
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
        
        #self.segments.append(Segment([(0, 0), (0, -fclen*1.41)]))
        self.segments.append(Segment([(0, 0), (line_len, line_len)], "red"))
        self.segments.append(Segment([(0, 0), (-line_len, line_len)], "red"))
        self.segments.append(Segment([(0, 0), (line_len, -line_len)], "red"))
        self.segments.append(Segment([(0, 0), (-line_len, -line_len)], "red"))



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class UI(QDialog):
    
    

    
    
    def __init__(self):
        super(UI, self).__init__()
        
        
        
        
        
        
        # Load the ui file
        uic.loadUi("Schemdraw_Circuit-Designer.ui", self)
        
        # Definde widgets
        self.button_start_circuit = self.findChild(QPushButton, "pushButton_start_circuit")
        self.button_show_elements = self.findChild(QPushButton, "pushButton_show_elements")
        #self.button_show_labels = self.findChild(QPushButton, "pushButton_show_labels")
        self.button_refresh = self.findChild(QPushButton, "pushButton_refresh")
        self.button_up = self.findChild(QPushButton, "pushButton_Up")
        self.button_down = self.findChild(QPushButton, "pushButton_Down")
        self.button_left = self.findChild(QPushButton, "pushButton_Left")
        self.button_right = self.findChild(QPushButton, "pushButton_Right")
        self.button_show_img = self.findChild(QPushButton, "pushButton_show_img")
        self.button_save_img = self.findChild(QPushButton, "pushButton_save_img")
        self.button_undo = self.findChild(QPushButton, "pushButton_undo")
        
        self.button_TEST = self.findChild(QPushButton, "pushButton_TEST")
        
        
        
        self.label_img = self.findChild(QLabel, "label")
        """
        self.radioButton_resistor = self.findChild(QRadioButton, "radioButton_Resistor")
        self.radioButton_line = self.findChild(QRadioButton, "radioButton_Line")
        self.radioButton_line_blank = self.findChild(QRadioButton, "radioButton_Line_blank")
        self.radioButton_capacitor = self.findChild(QRadioButton, "radioButton_Capacitor")
        self.radioButton_inductor = self.findChild(QRadioButton, "radioButton_Inductor")
        """
        
        self.comboBox_elements = self.findChild(QComboBox, "comboBox_elements")
        self.tableWidget = self.findChild(QTableWidget, "tableWidget_elements")
        
        
        
        # Define button functions
        self.button_start_circuit.clicked.connect(self.new_circuit)
        self.button_show_elements.clicked.connect(self.show_element_list)
        
        self.button_refresh.clicked.connect(self.refresh)
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
        
        
        #self.button_show_labels.clicked.connect(self.show_labels)
        self.button_undo.clicked.connect(self.removeElement)
        
        #self.button_TEST.clicked.connect(self.checkboxValue)
        
        
        # --- Define shortcuts
        #self.button_up = QShortcut(QKeySequence('up'),self)
        
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
            
            "Resistor": "elm.Resistor",
            "Potentiometer": "elm.Potentiometer()",
            "Capacitor": "elm.Capacitor()",
            "Inductor": "elm.Inductor()",
            "Diode": "elm.Diode()",
            "Line": "elm.Line()",
            "Line (hidden)": "elm.Line().color(\"None\")",
            "Dot (Open)": "elm.Dot(Open=True)",
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
        
        
        
        # Init
        self.element_list = []
        self.element_list_names = []
        self.current_label_list = []
        
        
        #self.generate_circuit()
        
        self.color = 'None'
        self.res_list = []
        self.res_names_list = []
        self.res_counter = 0
        self.check_R1 = False
        

      
        
        
        self.create_res_list()
        
        
        
        # building pattern
        self.building_pattern_list = []
        
        
    
    
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
            
    
    
    def test_method(self):
        print("Space shot!")
    
        
    def create_res_list(self):
        
        
        for i in range(1,30):
            self.res_list.append("R" + str(i))
            self.res_names_list.append("$R_" + str(i) + "$")
        
        #print(self.res_list)
    
    
    def show_element_list(self):
        
        for i in range(len(self.element_list_names)):
            
            print(self.element_list_names[i])
            

    
    def removeElement(self):
        if "Resistor" in self.building_pattern_list[-1]:
            self.counter_R_elements = self.counter_R_elements - 1
        self.building_pattern_list.pop()
        self.refresh()
    
    
    
    
    # --- add Element
    def addElementToList(self, selectedElement, direction, color):
        self.selectedElement = selectedElement
        self.direction = direction
        self.color = color
        
        print("Element: " + self.elements2schemdraw_dict[self.selectedElement])
        self.building_element(self.selectedElement, self.direction, self.color)
        
        
        
        self.element_list_names.append("d += " + self.elements2schemdraw_dict[self.selectedElement] + ".theta(" + str(self.direction) + ").color(\"" + self.color + "\")")
        
        
        
        
        """
        # Add Line (blank)
        elif self.radioButton_line_blank.isChecked() is True:
            self.building_element("Line", "up", "None")
            self.element_list_names.append("d += elm.Line().up().color('None')")     
        """
        
            
            
        #self.refresh()
        
    """
    def up_clicked(self):
        self.direction = "up"
       
    """
    
    def direction_clicked(self, direction):
        self.direction = direction
        
        # Element aus Combobox nehmen und aus DIR suchen
        self.selectedElement = self.comboBox_elements.currentText()
        print("SelectedItem: "+self.selectedElement)
        self.color = "black"
        
        if "hidden" in self.selectedElement:
            self.color = 'None'
            self.selectedElement = "Line"
            
        
      
        
        self.addElementToList(self.selectedElement, self.direction, self.color)
         
        self.refresh()
    
    
    
    def building_element(self, element_type, element_direction, element_color):
        
        if len(self.building_pattern_list) > 1:
            self.removeElement()
        
        self.building_pattern_list.append([element_type, element_direction, element_color])
        
        self.building_pattern_list.append(["Crosshair", "None", "red"])
        
        
    #self.building_pattern_list.append()
    
    def refresh(self):
            
        
        
        # --- Nummer für Bauelemente: z.B. Erster platzierter Widerstand soll R "1" sein und nicht R0
        self.counter_R_elements = 1
        self.counter_U_elements = 1
        self.counter_I_elements = 1
        self.counter_C_elements = 1
        self.counter_L_elements = 1
        #self.comboBox_elements.clear()
        
        
        
        
        
        with schemdraw.Drawing() as d:
            
            #self.new_counter = 0
            
            
            
            for i in range (len(self.building_pattern_list)):
                
                
                    
                ### -- Es wird der Text aus der Textbox genommen (ComboBox -- Resistor)
                
                self.degree_angle = self.building_pattern_list[i][1]
                
                
                # -- Startpunkt Crosshair
                
                
                # --- Resistor
                if "Resistor" in self.building_pattern_list[i][0]:
                    d.add(elm.Resistor().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]).label("$R_"+str(self.counter_R_elements)+"$"))
                    self.counter_R_elements = self.counter_R_elements + 1
                    
                    
                    
    
                    
                # --- Line    
                if "Line" in self.building_pattern_list[i][0]:
                    d.add(elm.Line().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]))
                    
                 
                    
                # --- Capacitor    
                # theta(0) = right(), theta(90) = up(), theta(180)=left(), theta(270) = down()
                # length(3) = standard length of element
                if "Capacitor" in self.building_pattern_list[i][0]:
                    d.add(elm.Capacitor().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]).label("$C_"+str(self.counter_C_elements)+"$"))
                    self.counter_C_elements = self.counter_C_elements + 1
                    
                  
                
                
                if "Inductor" in self.building_pattern_list[i][0]:
                    d.add(elm.Inductor().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]).label("$L_"+str(self.counter_L_elements)+"$"))
                    self.counter_L_elements = self.counter_L_elements + 1
                    
                
                
                
                
                if "Source: Voltage (DC)" in self.building_pattern_list[i][0]:
                    d.add(VoltageSource().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]).label("$U_"+str(self.counter_U_elements)+"$"))
                    self.counter_U_elements = self.counter_U_elements + 1
                    
                    
                  
                    
                if "Source: Current (DC)" in self.building_pattern_list[i][0]:
                    d.add(CurrentSource().theta(self.degree_angle).length(3).color(self.building_pattern_list[i][2]).label("$I_"+str(self.counter_I_elements)+"$"))
                    self.counter_I_elements = self.counter_I_elements + 1
                
                
                
                
                if "Dot" in self.building_pattern_list[i][0]:
                    d.add(elm.Dot().color(self.building_pattern_list[i][2]))

                    
                    
                if "Dot (Open)" in self.building_pattern_list[i][0]:
                    d.add(elm.Dot(open=True).color(self.building_pattern_list[i][2]))



                # --- Crosshair
                
                if "Crosshair" in self.building_pattern_list[i][0]:
                    d.add(Crosshair())

                
                
                
                
                
                # --- Testing things
                if self.check_R1 is True:
                    d += elm.CurrentLabel(top=False, ofst=.5, length=1).at(self.res_list[0]).label('$U_1$').color(self.color)
                    d += elm.CurrentLabelInline(direction='in').at(self.res_list[0]).label('$I_1$').color(self.color)
                    
                
                
                
                    
                
        
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
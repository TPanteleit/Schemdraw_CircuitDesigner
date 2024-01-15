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
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from io import BytesIO
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QKeySequence
import sys
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout


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

class ImageViewer(QDialog):
    
    def __init__(self, image_path):
        # Initialize the QDialog and set window properties
        super(ImageViewer, self).__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)  # Adjust dimensions as needed
        # Create a QLabel to display the image within the dialog
        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 10, 780, 580)  # Adjust dimensions as needed
        # Load and display the image
        self.load_and_display_image(image_path)

    def load_and_display_image(self, image_path):
        try:
            # Create a QPixmap from the provided image path
            pixmap = QPixmap(image_path)
            # Check if the QPixmap is valid
            if not pixmap.isNull():
                # Set the QPixmap to the QLabel and scale its contents
                self.image_label.setPixmap(pixmap)
                self.image_label.setScaledContents(True)
                # Show the dialog to display the image
                self.show()
            else:
                print("Invalid image file or format.")
        except Exception as e:
            # Handle exceptions that may occur during image loading
            print(f"Error loading image: {e}")

### --------------- Bauteilklassen Ende 



### --------------- GUI definieren
class UI(QDialog):       
    
    def __init__(self):
        super(UI, self).__init__()
        
        
        
        # Load the ui file
        uic.loadUi("v2_Schemdraw_Circuit-Designer.ui", self)
        
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
       # Initialize label_img here
        self.label_img = QLabel()
        self.label_img.setScaledContents(True)  # Set this if you want the image to scale

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
        # Get the row count of the table
        rowCount = self.tableWidget.rowCount()
        
        # Check if there are elements in the table
        if rowCount > 0:
            # Remove the last row from the table
            self.tableWidget.removeRow(rowCount - 1)
        
            # Remove the corresponding element from schemdraw
            self.printELementsToSchemdraw()

    
    
    # --- add Element
    def addElementToTable(self, selectedElement, direction, color, length, voltageArrow_activ, voltageArrow_direction, voltageArrow_offset, currentArrow_activ, currentArrow_direction, currentArrow_offset):
        
        self.selectedElement = selectedElement
        self.direction = direction
        self.color = color
        self.length= 3
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
        self.tableWidget.setItem(row_number, 3, QtWidgets.QTableWidgetItem(str(self.length)))

        # Create checkboxes for voltage arrows
        voltage_checkbox = QtWidgets.QCheckBox()
        # Set the initial state of the checkboxes based on the input values
        voltage_checkbox.setChecked(bool(int(self.voltageArrow_activ)))
        self.tableWidget.setCellWidget(row_number, 4, voltage_checkbox)


        self.tableWidget.setItem(row_number, 5, QtWidgets.QTableWidgetItem(str(self.voltageArrow_direction)))
        self.tableWidget.setItem(row_number, 6, QtWidgets.QTableWidgetItem(str(self.voltageArrow_offset)))
        
        # Create checkboxes for current arrows
        current_checkbox = QtWidgets.QCheckBox()
        # Set the initial state of the checkboxes based on the input values
        voltage_checkbox.setChecked(bool(int(self.currentArrow_activ)))
        self.tableWidget.setCellWidget(row_number, 7, current_checkbox)
        
        self.tableWidget.setItem(row_number, 8, QtWidgets.QTableWidgetItem(str(self.currentArrow_direction)))
        self.tableWidget.setItem(row_number, 9, QtWidgets.QTableWidgetItem(str(self.currentArrow_offset)))
        
        row_number = row_number + 1
        
                
    
    def printELementsToSchemdraw(self):
        self.rowCount = self.tableWidget.rowCount()
        self.columnCount = self.tableWidget.columnCount()
        
        self.counter_R_elements = 1
        self.counter_q_elements = 1
        self.counter_C_elements = 1
        self.counter_L_elements = 1
        
        
        
        for row in range(self.rowCount):
                print(row, self.tableWidget.item(row,0).text(), self.tableWidget.item(row,1).text(), self.tableWidget.item(row,2).text(), self.tableWidget.item(row,3).text(), self.tableWidget.cellWidget(row,4).isChecked(), self.tableWidget.item(row,5).text(), self.tableWidget.item(row,6).text(), self.tableWidget.cellWidget(row,7).isChecked())
        
        print("\n")
        
        with schemdraw.Drawing() as d:
            for row in range(self.rowCount):
                
                self.element_type = self.tableWidget.item(row,0).text()
                self.element_angle = float(self.tableWidget.item(row,1).text())
                self.color = self.tableWidget.item(row,2).text()
                self.length = float(self.tableWidget.item(row,3).text())
                self.voltageActiv = self.tableWidget.cellWidget(row, 4).isChecked()  # Use isChecked() for checkboxes
                self.voltageDirection = bool(int(self.tableWidget.item(row,5).text()))
                self.voltageOffset = float(self.tableWidget.item(row,6).text())
                self.currentActiv = self.tableWidget.cellWidget(row, 7).isChecked()  # Use isChecked() for checkboxes
                self.currentDirection = self.tableWidget.item(row,8).text()
                self.currentOffset = float(self.tableWidget.item(row,9).text())
                
                
                if self.element_type == "Resistor":
                    
                    self.counter_R_elements = self.counter_R_elements + 1
                    d.add( R := (elm.Resistor().theta(self.element_angle).length(self.length).color(self.color).label("$R_"+str(self.counter_R_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(R).label("$Ur_"+str(self.counter_R_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(R).label("$Ir_"+str(self.counter_R_elements-1)+"$"))
                 
                if self.element_type == "Capacitor":
                    
                    self.counter_C_elements = self.counter_C_elements + 1
                    d.add( C := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$C_"+str(self.counter_C_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(C).label("$Uc_"+str(self.counter_C_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(C).label("$Ic_"+str(self.counter_C_elements-1)+"$"))
                
                        
                if self.element_type == "Inductor":
                    
                    self.counter_L_elements = self.counter_L_elements + 1
                    d.add( L := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$L_"+str(self.counter_L_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(L).label("$UL_"+str(self.counter_L_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(R).label("$IL_"+str(self.counter_L_elements-1)+"$"))
               
                if self.element_type == "Source: Voltage (DC)":
                    
                    self.counter_q_elements = self.counter_q_elements + 1
                    d.add( U := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$Uq_"+str(self.counter_q_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(U).label("$Uq_"+str(self.counter_q_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(U).label("$Iq_"+str(self.counter_q_elements-1)+"$"))
               
                if self.element_type == "Source: Voltage (AC)":
                    
                    self.counter_q_elements = self.counter_q_elements + 1
                    d.add( UA := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$Uq_"+str(self.counter_q_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(UA).label("$Uq_"+str(self.counter_q_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(UA).label("$Iq_"+str(self.counter_q_elements-1)+"$"))
                
                
                if self.element_type == "Source: Current (DC)":
                    
                    self.counter_q_elements = self.counter_q_elements + 1
                    d.add( I := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$Iq_"+str(self.counter_q_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(I).label("$Uq_"+str(self.counter_q_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(I).label("$Iq_"+str(self.counter_q_elements-1)+"$"))
               
                if self.element_type == "Source: Current (AC)":
                    
                    self.counter_q_elements = self.counter_q_elements + 1
                    d.add( IA := (elm.Capacitor().theta(self.element_angle).length(self.length).color(self.color).label("$Iq_"+str(self.counter_q_elements-1)+"$")))
                    
                    # Spannungspfeile
                    if self.voltageActiv:
                        d.add(elm.CurrentLabel(length=1.5, reverse=self.voltageDirection, ofst=self.voltageOffset, top=False).at(IA).label("$Uq_"+str(self.counter_q_elements-1)+"$", loc='bottom'))
                        
                    # Strompfeile
                    if self.currentActiv:
                        d.add(elm.CurrentLabelInline(direction=self.currentDirection, start=False, ofst=self.currentOffset).at(IA).label("$Iq_"+str(self.counter_q_elements-1)+"$"))
               
                        
            
            # Add Crosshair element at the end
            d.add(Crosshair())
            
            return d
        
        
        
    def direction_clicked(self, direction):
        self.direction = direction
        
        # Element aus Combobox nehmen und aus DIR suchen
        self.selectedElement = self.comboBox_elements.currentText()
        self.color = "black"
        
        if "hidden" in self.selectedElement:
            self.color = 'None'
            self.selectedElement = "Line"
            
        self.addElementToTable(self.selectedElement, self.direction, self.color,0,0,0,0,0,'in',0)
        self.printELementsToSchemdraw()

    
        
    def new_circuit(self):
        self.element_list.clear()
        
    
    
    def save_img(self):
       
        # Get the schemdraw.Drawing instance from printELementsToSchemdraw
        d = self.printELementsToSchemdraw()
        # Open a file dialog to choose the path and file name
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Images (*.png)")
        # Check if the file dialog was accepted (user selected a file)
        if file_dialog.exec_():
            # Get the selected file path
            selected_file = file_dialog.selectedFiles()[0]
            # Save the image using schemdraw's save method
            d.save(fname=selected_file, dpi=120)
            print(f"Image saved at: {selected_file}")

    def show_img(self):
        # Create a QFileDialog to allow the user to select an image file
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.show_image_viewer(selected_file)

    def show_image_viewer(self, image_path):
        # Create an instance of the ImageViewer dialog to display the image
        image_viewer = ImageViewer(image_path)
        # Execute the dialog to show the image viewer
        image_viewer.exec_()




# Initialize the app
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
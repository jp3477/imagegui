# -*- coding: utf-8 -*- image_selector_logic.py
# File that contains function binding of gui elements

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
import image_selector
from os import path
import os
import dbHandler


db_name = "image_location.db"


class ImageSelector(QtGui.QMainWindow, image_selector.Ui_ImageLabeler):
    
  def __init__(self, parent=None):
      #Initial setup
      super(ImageSelector, self).__init__(parent)
      self.setupUi(self)
      self.actionOpen.triggered.connect(self.file_open)
      self.actionOpenDirectory.triggered.connect(self.directory_open)
      
      #Handle item click
      self.imageList.currentItemChanged.connect(self.on_image_select)
      self.image_filenames = []

      #Matplotlib Widget setup
      self.figure = plt.figure()
      
      self.canvas = FigureCanvas(self.figure)
      self.mplvl.addWidget(self.canvas)
      self.figure.canvas.mpl_connect('button_press_event', self.on_image_click)
      
      self.canvas.draw()
      #A file path composed of a file and its parent directory
      # Done this way to avoid name conflicts
      self.storedname = ""

      #Matplotlib interactive image settings
      self.handles_dict = {}
      self.typeColors = {"eye":"blue","nose":"red","shape":"green"}

      self.nextImageButton.clicked.connect(self.on_click_next_button)
      self.prevImageButton.clicked.connect(self.on_click_prev_button)

      #Set state of radio buttons
      self.set_radio_button_options()
     
      self.session = dbHandler.start_session(db_name)
      

      #Reveal window
      self.show()

  def draw_circles_by_type(self, storedname):
    #Find filename in db and plot stored types
    image = dbHandler.getImageByName(storedname, self.session)
    types = self.typeColors.keys() 
    locs = [dbHandler.getImageLocationByType(image, type, self.session) \
              for type in types]

    for loc in locs:
      if loc != None:
        color = self.typeColors[loc.type] 
        self.draw_circle(loc.x, loc.y, loc.type, color=color)


  def draw_circle(self, xd, yd, label, color='r'):
    #Plot a circle at coordinate
    self.destroy_handle(label)
    circle = plt.Circle((xd,yd), 5, color=color)
    self.ax.add_artist(circle)
    self.canvas.draw()
    self.handles_dict[label] = circle

    return circle


  def destroy_handle(self, name):
    #Remove an artist on figure
    if name in self.handles_dict:
      shape = self.handles_dict.pop(name)
      if shape in self.ax.get_children():
        try:
          shape.remove()
        except ValueError:
          print "some error removing", shape, name

  def destroy_all_handles(self):
    to_remove = self.handles_dict.keys()
    for name in to_remove:
      self.destroy_handle(name)

  def set_radio_button_options(self):
      #Intialize radio button listeners. More options can be added here
      def setType(type):
        self.selectedType = type
        
      
      self.eyesRadioButton.toggled.connect(lambda: setType("eye"))
      self.noseRadioButton.toggled.connect(lambda: setType("nose"))
      self.shapeRadioButton.toggled.connect(lambda: setType("shape"))


      #Eye button toggled by default
      self.eyesRadioButton.setChecked(True)
      self.selectedType = "eye"
 

  def file_open(self):
    #Open a file dialog box to select image
    filenames = QtGui.QFileDialog.getOpenFileNames(self, 'Open File',
        filter="*.png *.jpg *.jpeg")

    #try:
    for filename in filenames:
        
        pixmap = QtGui.QPixmap(filename)

        basename = path.basename(str(filename))
        label = (basename[:10] + '..') if len(basename) > 12 else basename

        itm = QListWidgetItem(label)
        itm.setIcon(QIcon(pixmap))
        

        self.imageList.addItem(itm)
        #Store the filenames in an array with same index as label in imageList
        self.image_filenames.append(str(filename))
        parent = path.basename(path.dirname(str(filename)))
        storedname = path.join(parent, basename)

        #Add new images to the db
        if dbHandler.getImageByName(storedname, self.session) == None:
            dbHandler.addImage(storedname, self.session)
    #except:
     #   pass

  
  def directory_open(self):
      # Open all contents in a selected directory
      dialog = QFileDialog(self)
      dialog.setFileMode(QFileDialog.Directory)
      dialog.setOption(QFileDialog.ShowDirsOnly, True)

      if dialog.exec_():
        for folder in dialog.selectedFiles():
          folder = str(folder)
          filenames = [f for f in os.listdir(folder) if path.isfile(path.join(folder, f))]
          
          for filename in filenames:
            #Only open image files
            if path.splitext(filename)[1] in [".png", ".jpeg", ".jpg"]:
              filename = path.join(folder, filename)

              pixmap = QtGui.QPixmap(filename)

              basename = path.basename(str(filename))
              label = (basename[:10] + '..') if len(basename) > 12 else basename

              itm = QListWidgetItem(label)
              itm.setIcon(QIcon(pixmap))


              self.imageList.addItem(itm)
              self.image_filenames.append(str(filename))

              parent = path.basename(path.dirname(str(filename)))
              storedname = path.join(parent, basename)

              #Add new images to the db
              if dbHandler.getImageByName(storedname, self.session) == None:
                dbHandler.addImage(storedname, self.session)

       


  def on_image_select(self):
      #Plot image on selection

      self.eyesRadioButton.setChecked(True)
      self.selectedType = "eye"

      lst = self.imageList
      currentItem = lst.currentItem()
      #print "%s clicked with index %d" % (currentItem.text(), lst.currentRow())
      filename = self.image_filenames[lst.currentRow()]


      arr = plt.imread(filename)

      self.ax = self.figure.add_subplot(111)
      self.ax.hold(False)
      self.ax.imshow(arr, cmap="gray")
      self.ax.set_axis_off()

      basename = path.basename(filename)
      self.ax.set_title(basename)
      # Putting this hear to make getting access this current basename easier
      parent = path.basename(path.dirname(str(filename)))
      self.storedname = path.join(parent, basename)
 

      #Read from Database
      self.draw_circles_by_type(self.storedname)
      
      self.canvas.draw()

  def on_click_next_button(self):
      #Select next image
      try:
        new_row = (self.imageList.currentRow() + 1) % self.imageList.count()
        self.imageList.setCurrentRow(new_row)
        self.on_image_select()
      except:
        pass

  def on_click_prev_button(self):
      #Select previous image
      try:
        new_row = self.imageList.currentRow() - 1 
        new_row = new_row if new_row >= 0 else self.imageList.count() - 1
        self.imageList.setCurrentRow(new_row)
        self.on_image_select()
      except:
        pass
        

  def on_image_click(self, event):
      #Get coordinates of an axes click
      click_data = {
        'button': event.button,
        'x': event.x, 'y': event.y,
        'xd': event.xdata, 'yd': event.ydata}

      #If click is within limits proceed
      if click_data['xd'] != None and click_data['yd'] != None:
          self.update_image(click_data['xd'], click_data['yd'], self.selectedType)
          

      #print 'x: {}, y: {}'.format(click_data['xd'], click_data['yd'])
 
  def update_image(self, x, y, type):
    #Either add new location to database or update existing loction. Then plot circle
    image = dbHandler.getImageByName(self.storedname, self.session)
    loc = dbHandler.getImageLocationByType(image,type, self.session)

    if loc == None:
      dbHandler.addLocation(x, y, type, image, self.session)
    else:
      loc.x = x
      loc.y = y
      self.session.commit()

    self.draw_circle(x, y, type, color=self.typeColors[type])


def run():
    app = QtGui.QApplication(sys.argv)
    GUI = ImageSelector()
    sys.exit(app.exec_())
    
run()




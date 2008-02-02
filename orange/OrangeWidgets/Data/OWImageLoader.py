"""
<name>ImageLoader</name>
<description>Reads in images of all kinds.</description>
<icon>icons/File.png</icon>
<contact>Thomas Wiecki (thomas.wiecki(@at@)gmail.com)</contact>
<priority>11</priority>
"""

#
# OWFile.py
# The File Widget
# A widget for opening orange data files
#
from __future__ import with_statement

import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI, string, os.path, user, sys

from os import listdir
from os.path import splitext
from scipy.stats import norm
from numpy import empty,zeros,ones,array,reshape,random,concatenate,min,max,sqrt,mean
from scipy import logspace
from scipy.misc import imread
from glob import glob
from sys import argv, exit
import pylab
import pickle
from PIL import Image
from subprocess import call
import os


#*******************
class ImageLoaderBase:
# Base class with all the functional
#*******************
    #=============
    def start(self, do_pickle=None):
    # Loads the Dataset and starts the training and testing methods
    #=============
        if do_pickle:
            with open("img.pickle", 'r') as fd_img:
                (self.imgs_train, self.imgs_valid) = pickle.load(fd_img)
            self.train(do_pickle='train.pickle')
            err_valid = self.valid(do_pickle='valid.pickle')
     
        else:
            (self.imgs_train, self.imgs_valid) = self.get_dataset()
            with open("img.pickle", 'w') as fd_img:
                pickle.dump((self.imgs_train, self.imgs_valid), fd_img)
            self.train()
            self.err_valid = self.valid()
     
        return self.err_valid

    #=================
    def load_one_image(self, file, flatten=True, resize=False):
    # Loads the image with filename 'file' and returns the PIL.Image object
    #=================
        try:
            print(file)
            im=Image.open(file)
            if resize:
                im = im.resize((160, 160), Image.ANTIALIAS)
            if flatten:
                im = im.convert('L')
        except IOError:
            print("Omitting: " + file)
        return (im)


    #==============
    def normalize(self, imgs, minimax = [None, None]):
    # Scales the input matrix to lay between 0 and 1 or minimax if supplied
    #==============
        if minimax[0]==None:
            minimax[0] = min(imgs)
        if minimax[1]==None:
            minimax[1] = max(imgs)

        normalized = (imgs-minimax[0])/(float(minimax[1]-minimax[0]))
        return (normalized, minimax)

    #==============
    def randperm(self,(seq)):
    # Randomly permutes the sequences in the seq tuple, however, 
    # every sequence gets permuted in the same order
    #==============
        l = list()
        perm = random.permutation(len(seq[0]))
        for i in seq:
            l.append(i[perm])
        return l

    #=================
    def get_fnames(self, dirs, flatten=True, formats=['.jpg','.gif','.bmp']):
    # Returns all the (filenames, labels, groups) of images in dirs, gets called by get_dataset
    #=================
        category = 0
        imgs = ()
        c_imgs = list()
        c_labels = list()
        category=0
        for dir in dirs:
            files = [file for file in glob(dir+'*') if splitext(file)[1] in formats]
            category+=1
            labels = []
            images = []
            imlist = []

            for file in files:
                ### Append
                images.append(file)
                labels.append(category)
            
            c_imgs.append(images)
            c_labels.append(labels)

        return (c_imgs, c_labels)

    #============
    def get_dataset(self):
    # Gets, splits, permutates and returns the dataset
    #============
        (imgs,labels) = self.get_fnames(['./AnimalDB/test_Targets/','./AnimalDB/test_Distractors/'])
        (x_train, y_train, x_valid, y_valid) = [array([]) for i in range(4)]

        for x,y in zip(imgs,labels,groups):
            # Permutate the sets
            (x1,y1) = self.randperm((array(x),array(y)))
     
            # Append them to the final matrix
            if len(x_train) == 0:
                x_train = x1
                y_train = y1
            else:
                x_train = concatenate((x_train, x1))
                y_train = concatenate((y_train, y1))


        # Clean up
        del x,y,x1,y1,imgs,labels

        (x_train, y_train) = self.randperm((x_train,y_train))

        (x_train,x_valid) = self.split(x_train)
        (y_train,y_valid) = self.split(y_train)

        return ((x_train, y_train), (x_valid, y_valid))

    #==============
    def split(self, imgs, size=None): #=round(imgs/2)):
    #==============
        if size==None:
            size=round(len(imgs)/2)
        return (imgs[0:size], imgs[size:len(imgs)])


class OWSubFile(OWWidget):
    settingsList=["recentFiles"]
    allFileWidgets = []

    def __init__(self, parent=None, signalManager = None, name = "File"):
#        import pycallgraph
#        pycallgraph.start_trace()         
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)
        OWSubFile.allFileWidgets.append(self)
        self.filename = ""

    def destroy(self, destroyWindow, destroySubWindows):
        OWSubFile.allFileWidgets.remove(self)
        OWWidget.destroy(self, destroyWindow, destroySubWindows)
#        pycallgraph.make_dot_graph('test.png')

    def activateLoadedSettings(self):
        # remove missing data set names
        self.recentFiles=filter(os.path.exists,self.recentFiles)
        self.setFileList()

        if len(self.recentFiles) > 0 and os.path.exists(self.recentFiles[0]):
            self.openFile(self.recentFiles[0])

        # connecting GUI to code
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)

    # user selected a file from the combo box
    def selectFile(self,n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(1)

        if len(self.recentFiles) > 0:
            self.setFileList()
            self.openFile(self.recentFiles[0])

    # user pressed the "..." button to manually select a file to load
    def browseFile(self, inDemos=0):
        "Display a FileDialog and select a file"
        if inDemos:
            import os
            try:
                import win32api, win32con
                t = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE\\Python\\PythonCore\\%i.%i\\PythonPath\\Orange" % sys.version_info[:2], 0, win32con.KEY_READ)
                t = win32api.RegQueryValueEx(t, "")[0]
                startfile = t[:t.find("orange")] + "orange\\doc\\datasets"
            except:
                startfile = ""

            if not startfile or not os.path.exists(startfile):
                d = OWGUI.__file__
                if d[-8:] == "OWGUI.py":
                    startfile = d[:-22] + "doc/datasets"
                elif d[-9:] == "OWGUI.pyc":
                    startfile = d[:-23] + "doc/datasets"

            if not startfile or not os.path.exists(startfile):
                d = os.getcwd()
                if d[-12:] == "OrangeCanvas":
                    startfile = d[:-12]+"doc/datasets"
                else:
                    if d[-1] not in ["/", "\\"]:
                        d+= "/"
                    startfile = d+"doc/datasets"

            if not os.path.exists(startfile):
                QMessageBox.information( None, "File", "Cannot find the directory with example data sets", QMessageBox.Ok + QMessageBox.Default)
                return
        else:
            if len(self.recentFiles) == 0 or self.recentFiles[0] == "(none)":
                if sys.platform == "darwin":
                    startfile = user.home
                else:
                    startfile="."
            else:
                startfile=self.recentFiles[0]

        filename = str(QFileDialog.getOpenFileName(self, 'Open Orange Data File', startfile, "",
        'Tab-delimited files (*.tab *.txt)\nC4.5 files (*.data)\nAssistant files (*.dat)\nRetis files (*.rda *.rdo)\nAll files(*.*)'))

        if filename == "": return
        if filename in self.recentFiles: self.recentFiles.remove(filename)
        self.recentFiles.insert(0, filename)
        self.setFileList()
        self.openFile(self.recentFiles[0])

    def setInfo(self, info):
        for (i, s) in enumerate(info):
            self.info[i].setText(s)

    # checks whether any file widget knows of any variable from the current domain
    def attributesOverlap(self, domain):
        for fw in OWSubFile.allFileWidgets:
            if fw != self and getattr(fw, "dataDomain", None):
                for var in domain:
                    if var in fw.dataDomain:
                        return True
        return False

    # Open a file, create data from it and send it over the data channel
    def openFileBase(self,fn, throughReload = 0, DK=None, DC=None):
        dontCheckStored = throughReload and self.resetDomain
        self.resetDomain = self.domain != None
        oldDomain = getattr(self, "dataDomain", None)
        if fn != "(none)":
            fileExt=lower(os.path.splitext(fn)[1])
            argdict = {"dontCheckStored": dontCheckStored, "use": self.domain}
            if fileExt in (".txt",".tab",".xls"):
                preloader, loader = orange.ExampleGenerator, orange.ExampleTable
                if DK:
                    argdict["DK"] = DK
                if DC:
                    argdict["DC"] = DC
            elif fileExt in (".c45",):
                preloader = loader = orange.C45ExampleGenerator
            else:
                return

            if dontCheckStored:
                data = loader(fn, **argdict)
            else:
                # Load; if the domain is the same and there is no other file widget which
                # uses any of the same attributes like this one, reload
                # If the loader for a particular format cannot load the examle generator
                # (i.e. if it always returns an example table), the data is loaded twice.
                data = preloader(fn, **argdict)
                if oldDomain == data.domain and not self.attributesOverlap(data.domain):
                    argdict["dontCheckStored"] = 1
                    data = loader(fn, **argdict)
                elif not isinstance(data, orange.ExampleTable):
                    data = loader(fn, **argdict)

            self.dataDomain = data.domain

            # update data info
            def sp(l):
                n = len(l)
                if n <> 1: return n, 's'
                else: return n, ''

            self.infoa.setText('%d example%s, ' % sp(data) + '%d attribute%s, ' % sp(data.domain.attributes) + '%d meta attribute%s.' % sp(data.domain.getmetas()))
            cl = data.domain.classVar
            if cl:
                if cl.varType == orange.VarTypes.Continuous:
                    self.infob.setText('Regression; Numerical class.')
                elif cl.varType == orange.VarTypes.Discrete:
                    self.infob.setText('Classification; Discrete class with %d value%s.' % sp(cl.values))
                else:
                    self.infob.setText("Class neither descrete nor continuous.")
            else:
                self.infob.setText('Classless domain')

            # make new data and send it
            fName = os.path.split(fn)[1]
            if "." in fName:
                data.name = string.join(string.split(fName, '.')[:-1], '.')
            else:
                data.name = fName
            self.send("Examples", data)
            self.send("Attribute Definitions", data.domain)
        else:
            self.send("Examples", None)
            self.send("Attribute Definitions", None)



class OWImageLoader(OWSubFile):
    def __init__(self,parent=None, signalManager = None):
        OWSubFile.__init__(self, parent, signalManager, "File")

        self.inputs = []
        self.outputs = [("Images as Numpy Array", ExampleTable), ("Images in PIL format", ExampleTable)]

        #set default settings
        self.recentFiles=["(none)"]
        self.domain = None
        #get settings from the ini file, if they exist
        self.loadSettings()
        self.test1 = ['blah','blub']
        self.test2 = ['blub', 'blah']
        buttonWidth = 1.5

        #GUI
        w = QWidget(self)
        self.controlArea.layout().addWidget(w)
        grid = QGridLayout()
        grid.setMargin(0)
        w.setLayout(grid)
        self.box = OWGUI.widgetBox(self.controlArea, box = "Data File", orientation = "horizontal")
        self.filecombo = OWGUI.comboBox(self.box, self, "filename")
        self.filecombo.setMinimumWidth(250)
 
        boxAvail = OWGUI.widgetBox(self, 'Available Attributes', addToLayout = 0)
        grid.addWidget(boxAvail, 0,0,3,1)

        self.inputAttributesList = OWGUI.listBox(boxAvail, self)

        vbAttr = OWGUI.widgetBox(self, addToLayout = 0)
        grid.addWidget(vbAttr, 0,1)
        self.attributesButtonUp = OWGUI.button(vbAttr, self, "Up", self.onButtonClick)
        self.attributesButtonUp.setMaximumWidth(buttonWidth)
        self.attributesButton = OWGUI.button(vbAttr, self, ">",self.onButtonClick)
        self.attributesButton.setMaximumWidth(buttonWidth)
        self.attributesButtonDown = OWGUI.button(vbAttr, self, "Down", self.onButtonClick)
        self.attributesButtonDown.setMaximumWidth(buttonWidth)

        self.inChange = False
        self.resize(400,480)


        # info
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, ' ')

        self.resize(150,100)

    # set the file combo box
    def setFileList(self):
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        else:
            self.filecombo.addItems([os.path.split(file)[1] for file in self.recentFiles])
        self.filecombo.addItem("Browse documentation data sets...")
        #self.filecombo.adjustSize() #doesn't work properly :(
        #self.filecombo.updateGeometry()

    def onButtonClick(self):
        pass

    def openFile(self,fn, throughReload = 0):
        self.openFileBase(fn, throughReload=throughReload)



if __name__ == "__main__":
    a=QApplication(sys.argv)
    owf=OWFile()
    owf.activateLoadedSettings()
    owf.show()
    sys.exit(a.exec_())
    owf.saveSettings()

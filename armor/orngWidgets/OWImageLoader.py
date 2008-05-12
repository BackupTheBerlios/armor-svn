"""
<name>ImageLoader</name>
<description>Reads in images of all kinds.</description>
<icon>icons/File.png</icon>
<contact>Thomas Wiecki (thomas.wiecki(@at@)gmail.com)</contact>
<priority>11</priority>
"""

#################################################################
#
# The class structure is as follows:
#
# OWImageSubLoader: Basic functionality like opening a file dialog
# OWImageLoader: The main GUI, inherits from OWImageSubLoader
#                and from ImageDataset as it is the logical
#                extension to this class
# ImageCategoryDlg: Edit individual categories, add files, display images
#               Inherits from OWImageSubLoader and from
#               ImageCategories as it is the logical extension of
#               that class



from OWWidget import *
import OWGUI 


import os
import os.path
import numpy
from armor.ImageDataset import *


class OWImageSubFile(OWWidget):
    settingsList=["recentFiles"]
    allFileWidgets = []

    def __init__(self, parent=None, signalManager = None, name = ""):
        OWWidget.__init__(self, parent, signalManager, name)
        OWImageSubFile.allFileWidgets.append(self)
        self.filename = ""
    
    def destroy(self, destroyWindow, destroySubWindows):
        #OWImageSubFile.allFileWidgets.remove(self)
        OWWidget.destroy(self, destroyWindow, destroySubWindows)

    def activateLoadedSettings(self):
        # remove missing data set names
        self.recentFiles=filter(os.path.exists,self.recentFiles)
        self.setFileList()

        if len(self.recentFiles) > 0 and os.path.exists(self.recentFiles[0]):
            self.openFile(self.recentFiles[0])

        # connecting GUI to code
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)


    def browseFile(self, filters=None, inDemos=0, dir=0, save=0):
        """Display a FileDialog and select an existing file, 
        or a dir (dir=1) or a new file (save=1).
        filters can be a list with all extensions to be displayed during browsing
        Returned is/are the selected item(s) with complete path."""
        if not filters:
            filters = ["All (*.*)"]

        dialog = QFileDialog()
        if dir == 0 and save == 0:
            dialog.setFileMode(QFileDialog.ExistingFiles)
        elif dir == 1 and save == 0:
            dialog.setFileMode(QFileDialog.Directory)
        elif dir == 0 and save == 1:
            dialog.setFileMode(QFileDialog.AnyFile)
        else:
            print "Incorrect mode." # TODO, throw an exception here

        dialog.setFilters(QStringList(filters))
        dialog.setViewMode(QFileDialog.List)

        if not dialog.exec_():
            return None

        selected = dialog.selectedFiles()

        return selected

    def setInfo(self, info):
        for (i, s) in enumerate(info):
            self.info[i].setText(s)

        
#*********************************************************
class OWImageLoader(OWImageSubFile, ImageDataset):
    """Class with a dialog to create your own image dataset.
    We only inherit all the functionality ImageDataset and
    provide a GUI to operate on the data structure. Because of
    this, every time changes are made to the dataset, 
    updateCategoryList gets called.""" 
#*********************************************************
    def __init__(self, parent=None, signalManager = None):
        OWImageSubFile.__init__(self, parent, signalManager, "Image Dataset")
        ImageDataset.__init__(self)

        self.inputs = []
        self.outputs = [("Images PIL", list), ("Attritube Definitions", orange.Domain)]

	self.useGenerator = True
	
        #set default settings
        self.recentFiles=["(none)"]
        self.domain = None
        #get settings from the ini file, if they exist
        self.loadSettings()
        buttonWidth = 1.5

        # Create the GUI
        self.dialogWidth = 250

        box = OWGUI.widgetBox(self.controlArea, 'Categories', addSpace = True, orientation=1)

        self.categoryList = OWGUI.listBox(box, self)
        self.connect(self.categoryList, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.editDataset)
        self.connect(self.categoryList, SIGNAL('itemEntered(QListWidgetItem *)'), self.editDataset)
        self.connect(self.categoryList, SIGNAL('itemSelectionChanged()'), self.selectionChanged)

        self.filecombo = OWGUI.comboBox(box, self, "Categories")
        self.filecombo.setMinimumWidth(self.dialogWidth)

        self.createNewButton = OWGUI.button(box, self, 'Create new category', callback = self.createNew, disabled=0, width=self.dialogWidth)
        self.addExistingButton = OWGUI.button(box, self, 'Add existing dataset', callback = self.addExisting, disabled=0, width=self.dialogWidth)
        self.removeSelectedButton = OWGUI.button(box, self, 'Remove selected category', callback = self.removeSelected, disabled=1, width=self.dialogWidth)
        self.saveDatasetButton = OWGUI.button(box, self, 'Save dataset', callback = self.saveDataset, disabled=0, width=self.dialogWidth)
        
        
	OWGUI.checkBox(box, self, "useGenerator", "Use lazy evaluation")
        self.resize(self.dialogWidth,480)


        # info
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.warnings = OWGUI.widgetLabel(box, '')


        self.adjustSize()

        self.applyButton = OWGUI.button(self.controlArea, self, 'Apply', callback = self.apply, disabled=0, width=self.dialogWidth)

	self.inChange = False

#====================================
    def sendData(self):
#====================================
        if len(self.categories) == 0:
	    return
	
        self.prepareSet()
        self.send("Images PIL", self.getData(useGenerator = self.useGenerator))
        
        
#==================================
    def addCategory(self, parent=None, name="", fnames=None, visible=False):
        """Overwrite addCategory function to use ImageCategoryDlg"""
#==================================
        if not fnames:
            fnames = []
        self.categories.append(ImageCategoryDlg(parent=self, name=name, fnames=fnames, visible=visible))
        self.updateCategoryList()

#==================================
    def editDataset(self, dataset):
        """Opens the edit dialog of the selected category"""
#==================================
        self.categories[self.categoryList.currentRow()].edit()

#==================================
    def selectionChanged(self):
        """Selection changed so there is a dataset present which _could_ be deleted,
        enable remove button"""
#==================================
        self.removeSelectedButton.setEnabled(1)

#==================================
    def addExisting(self):
        """Load an existing dataset from an xml file (special format)
        and add it to the dataset list"""
#==================================
        dataset_file = self.browseFile(filters=['Image Dataset (*.xml)','All files (*.*)'])
        if not dataset_file:
            return
        self.loadFromXML(str(dataset_file[0]))
        self.updateCategoryList()
        
#==================================
    def createNew(self):
        """Create a new dataset, a new dialog opens 
        where you can choose which files to include
        and what name the dataset should have"""
#==================================
        self.addCategory(parent = self, visible=True)
        
#==================================
    def removeSelected(self):
        """Remove dataset from the list of datasets"""
#==================================
        id = self.categoryList.currentRow() 
        self.delCategory(id)
        self.updateCategoryList()

#==================================
    def saveDataset(self):
        """Open a file dialog to select the filename and save the current datasets to the
        file in xml format"""
#==================================
        saveFile = str(self.browseFile(filters=['Image Dataset (*.xml)','All files (*.*)'], save=1)[0])
        if not saveFile:
            return
        self.saveToXML(saveFile)

#==================================
    def updateCategoryList(self):
#==================================
        # delete all items from the list
        self.categoryList.clear()
        for category in self.categories:
            self.categoryList.addItem(str(category.name))

	if len(self.categories) != 0:
	    self.infoa.setText('%i categories with a total of %i images' % (len(self.categories), sum([len(imgs.fnames) for imgs in self.categories])))
	    #self.infob.setText()
	else:
            self.infoa.setText("No data loaded")
#==================================
    def setFileList(self):
    # set the file combo box
#==================================
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(os.path.split(file)[1])
        self.filecombo.addItem("Browse documentation data sets...")
        #self.filecombo.adjustSize() #doesn't work properly :(
        self.filecombo.updateGeometry()

#==================================
    def apply(self):
    # User pressed apply button, hide the dialog (should we close here?)
#==================================
        self.sendData()
        self.setVisible(0)

#==================================
    def onButtonClick(self):
#==================================
        pass

#==================================
    def openFile(self,fn, throughReload = 0):
#==================================
        self.openFileBase(fn, throughReload=throughReload)

#==================================
    # user selected a file from the combo box
    def selectFile(self,n):
#==================================
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(inDemos=1)

        if len(self.recentFiles) > 0:
            self.setFileList()
            self.openFile(self.recentFiles[0])

#***********************************************************************
class ImageCategoryDlg(OWImageSubFile, ImageCategory):
# Dialog to create/edit a sinlge dataset.
# Here, the user can add single image files or a whole directory and give
# the dataset a name.
#***********************************************************************
#==================================
    def displayImage(self, WidgetItem):
#==================================
        img = self.loadOneImage(str(WidgetItem.text()))
        img.show()

#==================================
    def selectionChanged(self):
#==================================
        self.removeButton.setEnabled(1)

#==================================
    def removeFile(self):
#==================================
        row = self.widgetFileList.currentRow()
        self.delID(row)
        self.updateFileList()

#==================================
    # Called from the parent window, that the existing dataset should be edited
    def edit(self):
#==================================
        self.setVisible(1)

#==================================
    def browseImgFile(self):
#==================================
        fileList = self.browseFile(filters=['Image Files (*.jpg *.png *.gif *.bmp)','All files (*.*)'])
        if not fileList:
            return
        self.addFiles(fileList)
        self.updateFileList()

#==================================
    def browseImgDir(self):
#==================================
        dirName = self.browseFile(dir=1)
        if not dirName:
            return
        self.addDir(str(dirName[0]))
        self.updateFileList()

#==================================
    def apply(self):
#==================================
        self.emit(SIGNAL('updateParent'))
        
#==================================
    def ok(self):
#==================================
        self.emit(SIGNAL('updateParent'))
        self.setVisible(0)
    
#==================================
    def cancel(self):
#==================================
        self.setVisible(0)

#==================================
    def updateFileList(self):
#==================================
        self.widgetFileList.clear()
        self.widgetFileList.addItems(self.fnames)
        if self.widgetFileList.count() == 0:
            self.removeButton.setDisabled(0)


#==================================
    def __init__(self,parent=None, signalManager = None, name = "None", fnames = None, visible=True):
#==================================
        #get settings from the ini file, if they exist
        #self.loadSettings()
        if not fnames:
            fnames = []
        OWImageSubFile.__init__(self, parent, signalManager, "Category "+name)

        ImageCategory.__init__(self, name=name, fnames=fnames)
       
        #set default settings
        self.domain = None
        #GUI
        self.dialogWidth = 250
        buttonWidth = 1.5
        self.recentFiles=["(none)"]
        
        box = OWGUI.widgetBox(self.controlArea, 'Dataset', addSpace = True, orientation=1)
        OWGUI.lineEdit(box, self, "name", "Name of dataset: ", orientation="horizontal", tooltip="The name of the dataset used throughout the training")

        self.widgetFileList = OWGUI.listBox(box, self)
        self.connect(self.widgetFileList, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.displayImage)
        self.connect(self.widgetFileList, SIGNAL('itemEntered(QListWidgetItem *)'), self.displayImage)
        self.connect(self.widgetFileList, SIGNAL('itemSelectionChanged()'), self.selectionChanged)
        self.connect(self, SIGNAL('updateParent'), parent.updateCategoryList)
        #OWGUI.connectControl(self.widgetFileList, self, None, self.displayImage, "itemDoubleClicked(*QListWidgetItem)", None, None)

        self.fileButton = OWGUI.button(box, self, 'Add file(s)', callback = self.browseImgFile, disabled=0, width=self.dialogWidth)
        self.dirButton = OWGUI.button(box, self, 'Add directory', callback = self.browseImgDir, disabled=0, width=self.dialogWidth)
        self.removeButton = OWGUI.button(box, self, 'Remove selected file', callback = self.removeFile, disabled=1, width=self.dialogWidth)
        self.applyButton = OWGUI.button(self.controlArea, self, 'Apply', callback = self.apply, disabled=0, width=self.dialogWidth)        
        self.inChange = False
        self.resize(self.dialogWidth,300)

        # Add the filenames to the widgetFileList
        self.widgetFileList.addItems(self.fnames)
        if visible:
            self.show()

if __name__ == "__main__":
    a=QApplication(sys.argv)
    owf=OWImageLoader()
    owf.activateLoadedSettings()
    owf.show()
    sys.exit(a.exec_())
    owf.saveSettings()

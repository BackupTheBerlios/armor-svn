

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
#                and from OWImageDataset as it is the logical
#                extension to this class
# OWImageGroupDlg: Edit individual groups, add files, display images
#               Inherits from OWImageSubLoader and from
#               OWImageGroups as it is the logical extension of
#               that class



from OWWidget import *
import OWGUI 


import os
import os.path
import numpy
from OWImageDataset import *


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
        if inDemos:
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
class OWImageLoader(OWImageSubFile, OWImageDataset):
    """Class with a dialog to create your own image dataset.
    We only inherit all the functionality OWImageDataset and
    provide a GUI to operate on the data structure. Because of
    this, every time changes are made to the dataset, 
    updateGroupList gets called.""" 
#*********************************************************
    def __init__(self, parent=None, signalManager = None):
        OWImageSubFile.__init__(self, parent, signalManager, "Image Dataset")
        OWImageDataset.__init__(self)

        self.inputs = []
        self.outputs = [("Images as Numpy Array", numpy.array), ("Images in PIL format", list)]

	self.useGenerator = True
	
        #set default settings
        self.recentFiles=["(none)"]
        self.domain = None
        #get settings from the ini file, if they exist
        self.loadSettings()
        buttonWidth = 1.5

        # Create the GUI
        self.dialogWidth = 250

        box = OWGUI.widgetBox(self.controlArea, 'Groups', addSpace = True, orientation=1)

        self.groupList = OWGUI.listBox(box, self)
        self.connect(self.groupList, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.editDataset)
        self.connect(self.groupList, SIGNAL('itemEntered(QListWidgetItem *)'), self.editDataset)
        self.connect(self.groupList, SIGNAL('itemSelectionChanged()'), self.selectionChanged)

        self.filecombo = OWGUI.comboBox(box, self, "Groups")
        self.filecombo.setMinimumWidth(self.dialogWidth)

        self.createNewButton = OWGUI.button(box, self, 'Create new group', callback = self.createNew, disabled=0, width=self.dialogWidth)
        self.addExistingButton = OWGUI.button(box, self, 'Add existing dataset', callback = self.addExisting, disabled=0, width=self.dialogWidth)
        self.removeSelectedButton = OWGUI.button(box, self, 'Remove selected group', callback = self.removeSelected, disabled=1, width=self.dialogWidth)
        self.saveDatasetButton = OWGUI.button(box, self, 'Save dataset', callback = self.saveDataset, disabled=0, width=self.dialogWidth)
        
        
	OWGUI.checkBox(wbS, self, "useGenerator", "Use lazy evaluation")
        self.resize(self.dialogWidth,480)


        # info
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.warnings = OWGUI.widgetLabel(box, '')

	OWGUI.checkBox(wbS, self, "useGenerator", "Use lazy evaluation")

        self.adjustSize()

        self.applyButton = OWGUI.button(self.controlArea, self, 'Apply', callback = self.apply, disabled=0, width=self.dialogWidth)

	self.inChange = False

#====================================
    def sendData(self):
#====================================
        self.prepareSet()
	if self.useGenerator:
	    data = self.iterator
	else:
	    self.createArray()
	    data = self.allImages
        self.send(data)
        
        
#==================================
    def addGroup(self, parent=None, name="", fnames=None, visible=True):
        """Overwrite addGroup function to use OWImageGroupDlg"""
#==================================
        if not fnames:
            fnames = []
        self.groups.append(OWImageGroupDlg(parent=self, name=name, fnames=fnames, visible=visible))
        self.updateGroupList()

#==================================
    def editDataset(self, dataset):
        """Opens the edit dialog of the selected group"""
#==================================
        self.groups[self.groupList.currentRow()].edit()

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
        dataset_file = self.browseFile(filters=['Image Database (*.xml)','All files (*.*)'])
        if not dataset_file:
            return
        self.loadFromXML(str(dataset_file[0]))
        self.updateGroupList()
        
#==================================
    def createNew(self):
        """Create a new dataset, a new dialog opens 
        where you can choose which files to include
        and what name the dataset should have"""
#==================================
        self.addGroup(parent = self, visible=True)
        
#==================================
    def removeSelected(self):
        """Remove dataset from the list of datasets"""
#==================================
        id = self.groupList.currentRow() 
        self.delGroup(id)
        self.updateGroupList()

#==================================
    def saveDataset(self):
        """Open a file dialog to select the filename and save the current datasets to the
        file in xml format"""
#==================================
        saveFile = str(self.browseFile(filters=['Image Database (*.xml)','All files (*.*)'], save=1)[0])
        if not saveFile:
            return
        self.saveToXML(saveFile)

#==================================
    def updateGroupList(self):
#==================================
        # delete all items from the list
        self.groupList.clear()
        for group in self.groups:
            self.groupList.addItem(group.name)

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
class OWImageGroupDlg(OWImageSubFile, OWImageGroup):
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
        OWImageSubFile.__init__(self, parent, signalManager, "Group "+name)

        OWImageGroup.__init__(self, name=name, fnames=fnames)
       
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
        self.connect(self, SIGNAL('updateParent'), parent.updateGroupList)
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

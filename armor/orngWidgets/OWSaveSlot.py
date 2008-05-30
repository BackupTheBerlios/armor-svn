"""
<name>SaveSlot</name>
<description>Save a slot to a file.</description>
<icon>icons/Save.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>3</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor
from armor.SeqContainer import SeqContainer as SeqContainer
class OWSaveSlot(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", SeqContainer, self.setData)]
        self.outputs = []

        self.useGenerator = armor.useGenerator
        
        # Settings
        self.name = name
        self.loadSettings()

	self.fname = None
        self.slot = None
	
        wbN = OWGUI.widgetBox(self.controlArea, "SaveSlot settings")
	
        #OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "Save to...", callback = self.browseFile, disabled=0)

        self.resize(100,150)

    def browseFile(self, filters=None):
        """Display a FileDialog and select an existing file, 
        or a dir (dir=1) or a new file (save=1).
        filters can be a list with all extensions to be displayed during browsing
        Returned is/are the selected item(s) with complete path."""
        if not filters:
            filters = ["All (*.*)"]

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)

        dialog.setFilters(QStringList(filters))
        dialog.setViewMode(QFileDialog.List)

        if not dialog.exec_():
            return None

        selected = dialog.selectedFiles()

        self.fname = str(selected[0])
	self.setData(self.slot)

    def setData(self,slot):
	self.slot = slot
        if self.slot is None or self.fname is None:
            return
        armor.saveSlots(self.fname, outputSlot=slot)

	# Create orange.ExampleTable
	#histoList = []
	#histoContainer = self.kmeans.getData()
	#for d in histoContainer:
	#    histoList.append(list(d[0]) + [str(d[1])])
	    
        #domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(self.kmeans.dataHistogram[0][0]))] + [orange.EnumVariable("class", values = orange.StringList([str(x) for x in histoContainer.classes]))])
        #from PyQt4 import QtCore; QtCore.pyqtRemoveInputHook()
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()

        #self.histograms = orange.ExampleTable(domain, histoList)
        #self.send("Histograms", self.histograms)
	

def main():
    a=QApplication(sys.argv)
    ows=OWKmeans()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

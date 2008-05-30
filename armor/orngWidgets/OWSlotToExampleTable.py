"""
<name>ListToExampleTable</name>
<description>Converts a List/Generator to ExampleTable.</description>
<icon>icons/DataTable.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from armor.SeqContainer import SeqContainer as SeqContainer
import orange

class OWSlotToExampleTable(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='ListToExampleTable'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("SeqContainer", SeqContainer, self.setData), ("Labels", SeqContainer, self.setLabels)]
        self.outputs = [("Table", ExampleTable)]

        # Settings
        self.name = name
        self.loadSettings()

        self.data = None                    # input data set
        self.labels = None
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,250)


    def setLabels(self, slot):
	if slot is None:
            return
        self.labels = slot
        if self.data is not None:
            self.createExampleTable()
            
    def setData(self, slot):
	if slot is None:
            return
        self.data = slot
	if self.labels is None:
	    return
	#self.data.registerGroup(armor.groupCounter)
	#armor.groupCounter += 1
        if self.labels is not None:
            self.createExampleTable()
            
    def createExampleTable(self):
        # Create orange.ExampleTable
        datalabels = []
        data = list(self.data)
        labels = list(self.labels)
        
        for vec,label in zip(data, labels):
            datalabels.append(list(vec) + [str(label)])
            
        domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(data[0]))] + [orange.EnumVariable("class", values = orange.StringList([str(x) for x in self.labels.container.classes]))])
        #from PyQt4 import QtCore; QtCore.pyqtRemoveInputHook()
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()

        orngTable = orange.ExampleTable(domain, datalabels)
        self.send("Table", orngTable)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
 
    

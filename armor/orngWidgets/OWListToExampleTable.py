"""
<name>ListToExampleTable</name>
<description>Converts a List/Generator to ExampleTable.</description>
<icon>icons/kNearestNeighbours.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception

class OWListToExampleTable(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='ListToExampleTable'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", list, self.setData)]
        self.outputs = [("ExampleTable", ExampleTable)]

        # Settings
        self.name = name
        self.loadSettings()

        self.data = None                    # input data set

        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,250)


    def setData(self, inputData):

        if not inputData:
            pass
        
        self.inputData = inputData
        dataList = []
        inputIDs = []

        # Create ExampleTable
        for data in self.inputData:
            dataList.append(data)

        QtCore.pyqtRemoveInputHook()
        from IPython.Debugger import Tracer; debug_here = Tracer()
        debug_here()
        
        domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(dataList))] + ["class"])
        exampleTable = orange.ExampleTable(domain, dataList)
        
        self.send("ExampleTable", exampleTable)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

    
    

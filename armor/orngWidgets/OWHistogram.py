"""
<name>Histogram</name>
<description>Compute Histograms.</description>
<icon>icons/Rank.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor.histogram
from armor.SeqContainer import SeqContainer as SeqContainer

class OWHistogram(OWWidget):
    settingsList = ["bins"]

    def __init__(self, parent=None, signalManager = None, name='histogram'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", SeqContainer, self.setData)]
        self.outputs = [("Histogram", SeqContainer)] # , ("Histograms", ExampleTable)]

        self.useGenerator = True
        
        # Settings
        self.name = name
        self.loadSettings()

	self.bins = 200
        
        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "kMeans Settings")
        OWGUI.spin(wbN, self, "bins", 1, 100000, 100, None, "Number of bins  ", orientation="horizontal")

        OWGUI.separator(self.controlArea)
        
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,150)


    def setData(self,slot):
        if not slot:
            return
        self.histogram = armor.histogram.histogram(self.bins)
	self.histogram.inputSlot.registerInput(slot)
        self.send("Histogram", self.histogram.outputSlot)

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
    ows=OWHistogram()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

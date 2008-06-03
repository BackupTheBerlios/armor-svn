"""
<name>Histogram</name>
<description>Compute Histograms.</description>
<icon>icons/Rank.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>20</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor
import armor.Histogram
from armor.SeqContainer import SeqContainer as SeqContainer

class OWHistogram(OWWidget):
    settingsList = ['bins', 'useLazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='Histogram'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", SeqContainer, self.setData)]
        self.outputs = [("Histogram", SeqContainer)] # , ("Histograms", ExampleTable)]

        self.useLazyEvaluation = armor.useLazyEvaluation
        
        # Settings
        self.name = name
	self.Histogram = None
	
        self.loadSettings()

	self.bins = 200
        
        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Histogram Settings")
        OWGUI.spin(wbN, self, "bins", 1, 100000, 100, None, "Number of bins  ", orientation="horizontal")

        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
	if armor.applySettings(self.settingsList, self, obj=self.Histogram):
	    self.sendData()
	
    def setData(self,slot):
        if slot is None:
            return

	if self.Histogram is None:
	    self.Histogram = armor.Histogram.Histogram(self.bins)
	    self.Histogram.InputSlot.registerInput(slot)
	    
	self.sendData()

    def sendData(self):
	self.send("Histogram", self.Histogram.OutputSlot)
	
	# Create orange.ExampleTable
	#histoList = []
	#histoContainer = self.kmeans.getData()
	#for d in histoContainer:
	#    histoList.append(list(d[0]) + [str(d[1])])
	    
        #domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(self.kmeans.dataHistogram[0][0]))] + [orange.EnumVariable("class", values = orange.StringList([str(x) for x in histoContainer.classes]))])
        #from PyQt4 import QtCore; QtCore.pyqtRemoveInputHook()
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()

        #self.Histograms = orange.ExampleTable(domain, histoList)
        #self.send("Histograms", self.Histograms)
	

def main():
    a=QApplication(sys.argv)
    ows=OWHistogram()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

"""
<name>Quantize</name>
<description>Return the closest cluster center.</description>
<icon>icons/MDS.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>15</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor.quantize
from armor.SeqContainer import SeqContainer as SeqContainer

class OWQuantize(OWWidget):
    settingsList = ['useLazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Codebook", SeqContainer, self.setCodebook), ("Data", SeqContainer, self.setData)]
        self.outputs = [("Clusters", SeqContainer)]

        self.useLazyEvaluation = armor.useLazyEvaluation
        
        # Settings
        self.name = name
        self.loadSettings()
                
        wbN = OWGUI.widgetBox(self.controlArea, "kMeans Settings")
#        OWGUI.spin(wbN, self, "numClusters", 1, 100000, 100, None, "Number of clusters   ", orientation="horizontal")
#        OWGUI.spin(wbN, self, "maxiter", 0, 100000, 1, None, "Maximum number of iterations", orientation="horizontal")
#        OWGUI.spin(wbN, self, "numruns", 0, 100000, 1, None, "Number of runs ", orientation="horizontal")

        OWGUI.separator(self.controlArea)
        
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,150)

	self.quantize = armor.quantize.quantize(useLazyEvaluation=self.useLazyEvaluation)


    def setData(self,slot):
        if not slot:
            return
	if self.quantize.InputSlotVec.senderSlot is None or self.quantize.InputSlotVec.senderSlot() is None:
	    self.quantize.InputSlotVec.registerInput(slot)
        self.send("Clusters", self.quantize.OutputSlot)

    def setCodebook(self, slot):
	if not slot:
	    return
	if self.quantize.InputSlotCodebook.senderSlot is None or self.quantize.InputSlotCodebook.senderSlot() is None:
	    self.quantize.InputSlotCodebook.registerInput(slot)
	self.send("Clusters", self.quantize.OutputSlot)
	
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
    ows=OWQuantize()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

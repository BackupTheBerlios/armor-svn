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
import armor.cluster
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
                
        wbN = OWGUI.widgetBox(self.controlArea, "Quantization settings")

        
        OWGUI.checkBox(wbN, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)

        self.quantize = armor.cluster.quantize(useLazyEvaluation=self.useLazyEvaluation)

    def applySettings(self):
        armor.applySettings(self.settingsList, self, obj=self.quantize)

    def setData(self,slot):
        if not slot:
            return

        self.quantize.InputSlotVec.registerInput(slot)
        self.send("Clusters", self.quantize.OutputSlot)

    def setCodebook(self, slot):
        if not slot:
            return

        self.quantize.InputSlotCodebook.registerInput(slot)
        self.send("Clusters", self.quantize.OutputSlot)
        
        

def main():
    a=QApplication(sys.argv)
    ows=OWQuantize()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

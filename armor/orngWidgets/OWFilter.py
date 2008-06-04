"""
<name>Filter</name>
<description>Apply a filter to the images.</description>
<icon>icons/unknown.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>7</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
import armor
import armor.smooth
from armor.SeqContainer import SeqContainer as SeqContainer

class OWFilter(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='filter'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", SeqContainer, self.setData)]
        self.outputs = [("Filtered Images PIL", SeqContainer)]

        self.useLazyEvaluation = armor.useLazyEvaluation
        
        # Settings
        self.name = name
        self.filter = None
        
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Filter Settings")

        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,250)


    def applySettings(self):
        changed = False
        
        if self.filter is not None:
            if self.sift.useLazyEvaluation != self.useLazyEvaluation:
                self.sift.useLazyEvaluation = self.useLazyEvaluation
                changed = True
                
            if armor.applySettings(self.settingsList, self, self.filter):
                changed = True

            if changed:
                self.sendData()

    def sendData(self):
        self.send("Filtered Images PIL", self.filter.outputSlot)
        
    def setData(self, slot):
        if not slot:
            return
        if self.filter is None:
            self.filter = armor.smooth.Smooth(useLazyEvaluation=self.useLazyEvaluation)

            self.filter.InputSlot.registerInput(slot)

        self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

"""
<name>Normalize</name>
<description>Normalize input data by different distance measurements.</description>
<icon>icons/unknown.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>13</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
import armor
import armor.normalize
from armor.SeqContainer import SeqContainer as SeqContainer

class OWNormalize(OWWidget):
    settingsList = ['normtype']

    def __init__(self, parent=None, signalManager = None, name='filter'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Unnormalized Data", SeqContainer, self.setData)]
        self.outputs = [("Normalized Data", SeqContainer)]

        self.useLazyEvaluation = armor.useLazyEvaluation
        
        # Settings
        self.name = name
	self.normalize = None
        self.normtype = 1
	self.normtypes = ['bin', 'L1', 'L2', 'whiten', 'bias', 'crop', 'log']
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Normalization Settings")
        self.filecombo = OWGUI.comboBoxWithCaption(wbN, self, "normtype", "Normalize type: ", items=self.normtypes, valueType = int)

        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
	if self.normalize:
	    # Because Normalize defines different input slots
	    # depending on the normalization type we have to create a
	    # new object here
	    if self.normalize.normtype != self.normtypes[self.normtype]:
		# Save old slot
		backup_slot = self.normalize.inputSlot.senderSlot()
		self.normalize = None
		self.setData(backup_slot)
        
    def sendData(self):
        self.send("Normalized Data", self.normalize.outputSlot)
        
    def setData(self, slot):
        if not slot:
            return
        if self.normalize is None:
            self.normalize = armor.normalize.Normalize(normtype=self.normtypes[self.normtype], useLazyEvaluation=self.useLazyEvaluation)

	self.normalize.inputSlot.registerInput(slot)

        self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWNormalize()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
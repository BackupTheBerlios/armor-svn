"""
<name>Sift</name>
<description>Scale invariant feature transform.</description>
<icon>icons/kNearestNeighbours.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor
import armor.sift
from armor.SeqContainer import SeqContainer as SeqContainer

class OWSift(OWWidget):
    settingsList = ["Octave", "Levels", "First Octave", "PeakThresh", "EdgeThresh", "Orientations"]

    def __init__(self, parent=None, signalManager = None, name='sift'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", SeqContainer, self.setData)]
        self.outputs = [("Descriptors", SeqContainer)]

        self.useGenerator = armor.useGenerator
        
        # Settings
        self.name = 'sift'
        self.loadSettings()

        self.Octave = 6
        self.Levels = 3
        self.FirstOctave = 0
        self.PeakThresh = 0
        self.EdgeThresh = 10
        self.Orientations = 0
        
        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Sift Settings")
        OWGUI.spin(wbN, self, "Octave", -1, 8, 1, None, "Octaves   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "Levels", 1, 8, 1, None, "Levels   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "FirstOctave", 0, 8, 1, None, "First Octave ", orientation="horizontal")
        OWGUI.spin(wbN, self, "PeakThresh", -1, 8, 1, None, "PeakThresh", orientation="horizontal")
        OWGUI.spin(wbN, self, "EdgeThresh", -1, 8, 1, None, "EdgeThresh", orientation="horizontal")                
        OWGUI.checkBox(wbN, self, "Orientations", "Force computation of orientations")
        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useGenerator", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,250)


    def setData(self, slot):
        if not slot:
            return
	self.sift = armor.sift.siftObj(Octave=self.Octave, Levels=self.Levels, FirstOctave=self.FirstOctave, PeakThresh=self.PeakThresh, EdgeThresh=self.EdgeThresh, Orientations=self.Orientations, useGenerator=self.useGenerator)
	self.sift.inputSlot.registerInput(slot)

	self.send("Descriptors", self.sift.outputSlot)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

    
    

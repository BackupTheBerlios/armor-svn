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

class OWSift(OWWidget):
    settingsList = ["Octave", "Levels", "First Octave", "PeakThresh", "EdgeThresh", "Orientations"]

    def __init__(self, parent=None, signalManager = None, name='sift'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", list, self.setData)]
        self.outputs = [("Descriptors", list)]

        self.useGenerator = False
        
        # Settings
        self.name = 'sift'
        self.loadSettings()

        self.Octave = -1
        self.Levels = 3
        self.FirstOctave = 0
        self.PeakThresh = -1
        self.EdgeThresh = -1
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


    def setData(self,data):
        if not data:
            return
	print data
        self.data = data
        self.sift = armor.sift(images=data, Octave=self.Octave, Levels=self.Levels, FirstOctave=self.FirstOctave, PeakThresh=self.PeakThresh, EdgeThresh=self.EdgeThresh, Orientations=self.Orientations)
	# Copy the generator so different widgets get different generators
	output = self.sift.getData(useGenerator=self.useGenerator)
	self.send("Descriptors", output)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

    
    

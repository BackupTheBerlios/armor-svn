"""
<name>Sift2</name>
<description>Scale invariant feature transform by Rob Hess.</description>
<icon>icons/kNearestNeighbours.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor.sift2
from armor.SeqContainer import SeqContainer as SeqContainer

class OWSift2(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='sift2'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", list, self.setData)]
        self.outputs = [("Descriptors", list)]

        self.useLazyEvaluation = False
        
        # Settings
        self.name = 'sift2'
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Sift Settings")
        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,150)


    def setData(self,data):
        if not data:
            return
	print data
        self.data = data
        self.sift = armor.sift2.sift2(imgContainer=data)
	# Copy the generator so different widgets get different generators
	output = self.sift.getData(useLazyEvaluation=self.useLazyEvaluation)
	self.send("Descriptors", output)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

    
    

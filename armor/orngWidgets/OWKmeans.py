"""
<name>KMeans</name>
<description>KMeans Clustering.</description>
<icon>icons/KMeans.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import armor

class OWKmeans(OWWidget):
    settingsList = ["numClusters", "maxiter", "numruns"]

    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", list, self.setData)]
        self.outputs = [("Cluster Centers", list), ("Histograms", ExampleTable)]

        self.useGenerator = True
        
        # Settings
        self.name = name
        self.loadSettings()

        self.numClusters = 20
        self.maxiter = 0
        self.numruns = 1
        
        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "kMeans Settings")
        OWGUI.spin(wbN, self, "numClusters", 1, 100000, 100, None, "Number of clusters   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "maxiter", 0, 100000, 1, None, "Maximum number of iterations", orientation="horizontal")
        OWGUI.spin(wbN, self, "numruns", 0, 100000, 1, None, "First Octave ", orientation="horizontal")

        OWGUI.separator(self.controlArea)
        
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,150)


    def setData(self,data):
        if not data:
            pass
        self.data = data
        self.kmeans = armor.kmeans(data, numClusters = self.numClusters, maxiter = self.maxiter, numruns = self.numruns)
        self.send("Cluster Centers", self.kmeans.clusters)

	# Create orange.ExampleTable
	histoList = []
	histoContainer = self.kmeans.getData()
	for d in histoContainer:
	    histoList.append(list(d[0]) + [str(d[1])])
	    
        domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(self.kmeans.dataHistogram[0][0]))] + [orange.EnumVariable("class", values = orange.StringList([str(x) for x in histoContainer.classes]))])
        #from PyQt4 import QtCore; QtCore.pyqtRemoveInputHook()
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()

        self.histograms = orange.ExampleTable(domain, histoList)
        self.send("Histograms", self.histograms)
	

def main():
    a=QApplication(sys.argv)
    ows=OWKmeans()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    

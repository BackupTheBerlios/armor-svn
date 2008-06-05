from numpy import array,ndarray,float32,loadtxt,float
import subprocess, os
import armor.slot
import armor.datatypes
import armor

binPath = os.path.join(armor.__path__[0],'..', 'bin')
regcovexec = os.path.join(binPath, 'regcovextract')
output = os.path.join(binPath, 'output.txt')
imgfile = os.path.join(binPath, 'img.png')
features = ['regcov', 'regcov_image', 'lbp', 'color', 'edge']

class Feature(object):
    def __init__(self, featureType, useLazyEvaluation=armor.useLazyEvaluation, **kwargs):
        if featureType in features:
            self.featureType = featureType
        else:
            raise NotImplementedError, "Feature Type %s not implemented" % featureType
        
        self.kwargs = kwargs
        self.useLazyEvaluation = useLazyEvaluation
        
        
        # Define types
        self.inputType = armor.datatypes.ImageType(format=["PIL"])
        self.outputType = armor.datatypes.VectorType(shape='nestedarray')

        # Define slots
        self.inputSlot = armor.slot.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
        self.outputSlot = armor.slot.OutputSlot(name='Sift Descriptors',
                                                outputType=self.outputType,
                                                inputSlot=self.inputSlot,
                                                processFunc=armor.weakmethod(self, 'process'),
                                                slotType='sequential',
                                                useLazyEvaluation=self.useLazyEvaluation)

    def process(self, img):
        if armor.verbosity > 0:
            print "Extracting feature: %s..." % self.featureType

        # Save Image to file
        savePIL(imgfile, img)
        # Run the extractor
        callExtractor(self.featureType, imgfile, output)
        # Read the descriptors
        return loadDescr(output)
        
def callExtractor(featureType, inputImg, outputFile):
    retcode = subprocess.call([regcovexec,'--type', featureType, '--image', inputImg, '--output', outputFile], shell=False)
    return retcode

def loadDescr(fname):
    #converters = {}
    #converters.fromkeys(range(100), numpy.float)
    #return loadtxt(fname, converters=converters)

    X = []
    
    try:
        fd = open(fname, 'r')
        for line in fd:
            values = [float(x) for x in line.split(' ')]
            X.append(values)
            
    finally:
        del fd

    return array(X)

def savePIL(fname, img):
    img.save(fname)
    

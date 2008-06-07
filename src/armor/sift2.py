from numpy import array,ndarray,float32,loadtxt,float
import subprocess, os
import armor.slot
import armor.datatypes
import armor

binPath = os.path.join(armor.__path__[0], 'bin')
siftexec = os.path.join(binPath, 'siftfeat')
output = os.path.join(binPath, 'output.txt')
imgfile = os.path.join(binPath, 'img.png')

class Sift(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation, **kwargs):
        self.useLazyEvaluation = useLazyEvaluation
        self.kwargs = kwargs

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
            print "Extracting features: sift (Rob Hess' implementation)..."

        # Save Image to file
        savePIL(imgfile, img)
        # Run the extractor
        callExtractor(imgfile, output)
        # Read the descriptors
        return loadDescr(output)[1]


def savePIL(fname, img):
    img.save(fname)
    
def callExtractor(inputImg, outputFile):
    subprocess.call([siftexec, '-x', '-o', outputFile, inputImg])
    
    
def loadDescr(fname):
    f = open(fname,'rb')
    f.readline() #skip the first line
    xlist = []
    ylist = []
    while(1):
        x = f.readline()[0:-1].split()
        y = []
        for i in xrange(7):
            y = y + [int(x) for x in f.readline()[1:-1].split()]
        xlist.append(x)
        ylist.append(y)
        #depending on file mode use tell to get file position
        pos = f.tell()
        if f.read(1)=="":
            f.close()
            break
        f.seek(pos)
    return (xlist, ylist)


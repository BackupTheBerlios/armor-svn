from numpy import array,ndarray,float32,loadtxt,float
import subprocess, os
import armor.slots
import armor


class Nowozin(object):
    binPath = os.path.join(armor.__path__[0], 'bin')
    regcovexec = os.path.join(binPath, 'regcovextract')
    output = os.path.join(binPath, 'output.txt')
    imgfile = os.path.join(binPath, 'img.png')
    features = ['regcov', 'regcov_image', 'lbp', 'color', 'edge']

    def __init__(self, featureType, useLazyEvaluation=armor.useLazyEvaluation, **kwargs):
        if featureType in Nowozin.features:
            self.featureType = featureType
        else:
            raise NotImplementedError, "Feature Type %s not implemented" % featureType
        
        self.kwargs = kwargs
        self.useLazyEvaluation = useLazyEvaluation
        
        
        # Define types
        self.inputType = armor.slots.ImageType(format=["PIL"])
        self.outputType = armor.slots.VectorType(shape='nestedarray')

        # Define slots
        self.inputSlot = armor.slots.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
        self.outputSlot = armor.slots.OutputSlot(name='Sift Descriptors',
                                                outputType=self.outputType,
                                                inputSlot=self.inputSlot,
                                                processFunc=armor.weakmethod(self, 'process'),
                                                slotType='sequential',
                                                useLazyEvaluation=self.useLazyEvaluation)

    def process(self, img):
        if armor.verbosity > 0:
            print "Extracting feature: %s..." % self.featureType

        # Save Image to file
        img.save(Nowozin.imgfile)
        # Run the extractor
        self.callExtractor(self.featureType, Nowozin.imgfile, Nowozin.output)
        # Read the descriptors
        return self.loadDescr(Nowozin.output)
        

    def callExtractor(self, featureType, inputImg, outputFile):
        retcode = subprocess.call([Nowozin.regcovexec,'--type', featureType, '--image', inputImg, '--output', outputFile], shell=False)
        return retcode

    def loadDescr(self, fname):
        X = []
        
        try:
            fd = open(fname, 'r')
            for line in fd:
                values = [float(x) for x in line.split(' ')]
                X.append(values)
                
        finally:
            del fd

        return array(X)


class SiftRobHess(object):
    binPath = os.path.join(armor.__path__[0], 'bin')
    siftexec = os.path.join(binPath, 'siftfeat')
    output = os.path.join(binPath, 'output.txt')
    imgfile = os.path.join(binPath, 'img.png')

    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation, **kwargs):
        self.useLazyEvaluation = useLazyEvaluation
        self.kwargs = kwargs

        # Define types
        self.inputType = armor.slots.ImageType(format=["PIL"])
        self.outputType = armor.slots.VectorType(shape='nestedarray')

        # Define slots
        self.inputSlot = armor.slots.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
        self.outputSlot = armor.slots.OutputSlot(name='Sift Descriptors',
                                                outputType=self.outputType,
                                                inputSlot=self.inputSlot,
                                                processFunc=armor.weakmethod(self, 'process'),
                                                slotType='sequential',
                                                useLazyEvaluation=self.useLazyEvaluation)

    def process(self, img):
        if armor.verbosity > 0:
            print "Extracting features: sift (Rob Hess' implementation)..."

        # Save Image to file
        img.save(SiftRobHess.imgfile)
        # Run the extractor
        self.callExtractor(SiftRobHess.imgfile, SiftRobHess.output)
        # Read the descriptors
        descr = self.loadDescr(SiftRobHess.output)[1]
        if armor.verbosity > 1:
            print array(descr).shape
        return descr


    def callExtractor(self, inputImg, outputFile):
        subprocess.call([SiftRobHess.siftexec, '-x', '-o', outputFile, inputImg])
    
    
    def loadDescr(self, fname):
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

    

class SiftValedi(object):
    """ SIFT  Scale-invariant feature transform
    (F,D) = sift(I) where computes the SIFT frames (keypoints) F and 
    the SIFT descriptors D of the image I. I is a gray-scale image in 
    single precision. Each column of F is a feature frame and has the 
    format [X;Y;S;TH], where X,Y is the (fractional) center of the frame, 
    S is the scale and TH is the orientation (in radians).
    Each column of D is the descriptor of the corresponding frame in F. A
    descriptor is a 128-dimensional vector.
    """
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation, **kwargs):
        self.kwargs = kwargs
        self.useLazyEvaluation = useLazyEvaluation

        # Define types
        self.inputType = armor.slots.ImageType(format=["PIL"], color_space=["gray"])
        self.outputType = armor.slots.VectorType(shape='nestedarray')

        # Define slots
        self.inputSlot = armor.slots.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
        self.outputSlot = armor.slots.OutputSlot(name='Sift Descriptors',
                                                outputType=self.outputType,
                                                inputSlot=self.inputSlot,
                                                processFunc=armor.weakmethod(self, 'process'),
                                                slotType='sequential',
                                                useLazyEvaluation=self.useLazyEvaluation)

    def process(self, img):
        if armor.verbosity > 0:
            print "Computing sift-descriptors (Valedi implementation)..."
        descr = sift(array(img, dtype=float32), **self.kwargs)[1]
        if armor.verbosity >= 2:
            print (len(descr), len(descr[0]))
        return descr
    

        
def sift(*args, **kwargs):
    """ SIFT  Scale-invariant feature transform
    (F,D) = sift(I) where computes the SIFT frames (keypoints) F and 
    the SIFT descriptors D of the image I. I is a gray-scale image in 
    single precision. Each column of F is a feature frame and has the 
    format [X;Y;S;TH], where X,Y is the (fractional) center of the frame, 
    S is the scale and TH is the orientation (in radians).
    Each column of D is the descriptor of the corresponding frame in F. A
    descriptor is a 128-dimensional vector.
    
    sift(I, option=value, ...) accepts the following options
    
    Octaves
    Set the number of octave of the DoG scale space.
    
    Levels
    Set the number of levels per octave of the DoG scale space.
    
    FirstOctave
    Set the index of the first octave of the DoG scale space.
    
    PeakThresh
    Set the peak selection threshold.
    
    EdgeThresh
    Set the non-edge selection threshold.
    
    NormThresh
    Set the minimum l2-norm of the descriptor before
    normalization. Descriptors below the threshold are set to zero.

    Frames
    Set the frames to use (bypass the detector).

    Orientations
    Force the computation of the oritentations of the frames
    even if the option 'Frames' is being used.
        
    Verbose
    Be verbose (may be repeated)."""

    import _sift
    
    # Type checking, all other type checking is done inside the c function
    assert type(kwargs.get('Octave')) is type(0) or type(kwargs.get('Octave')) is type(None), \
           "'Octave' must be an integer"
    assert type(kwargs.get('Levels')) is type(0) or type(kwargs.get('Levels')) is type(None), \
           "'Levels' must be an integer"
    assert type(kwargs.get('FirstOctave')) is type(0) or type(kwargs.get('FirstOctave')) is type(None), \
           "'FirstOctave' must be an integer"
    assert type(kwargs.get('Orientations')) is type(0) or type(kwargs.get('Orientations')) is type(None), \
           "'Orientations' must be an integer"
    return _sift.sift(*args, **kwargs)

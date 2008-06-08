from numpy import array,median,std,mean,log,concatenate,sum,reshape,sqrt,dot,exp,diag
from ctypes import c_double
import armor
import armor.slots


class Transform(object):
    def __init__(self, transtype, kernel=None, useLazyEvaluation=armor.useLazyEvaluation):
        self.transtype = transtype
        if self.transtype not in ['PCA','KPCA', 'LLE', 'none']:
            raise NotImplementedError, "No operation mode specified"

        if kernel is None:
            self.kernel = 'gaussian_kernel'
        elif kernel not in ['linear_kernel', 'gaussian_kernel', 'chi2_kernel']:
            raise NotImplementedError, "Wrong kernel chosen"
        else:
            self.kernel = kernel
        

        self.inputTypeData = armor.slots.VectorType(shape=['flatarray'], bulk=True)
        self.inputTypeLabels = armor.slots.VectorType(name=['labels'], shape=['flatlist'])
        
        self.outputType = armor.slots.VectorType(shape='flatarray')

        self.inputSlotData = armor.slots.InputSlot(name='untransformed',
                                                   acceptsType=self.inputTypeData)

        self.inputSlotLabels = armor.slots.InputSlot(name='labels',
                                                     acceptsType=self.inputTypeLabels)

        self.outputSlot = armor.slots.OutputSlot(name='transformed',
                                                 outputType=self.outputType,
                                                 useLazyEvaluation=useLazyEvaluation,
                                                 iterator=armor.weakmethod(self, 'iterator'))

    def iterator(self):
        # Pool data
        data = array(list(self.inputSlotData))
        labels = list(self.inputSlotLabels)

        if armor.verbosity>0:
            print "Transforming: %s with kernel: %s..." % (self.transtype, self.kernel)

        try:
            X = transform(data, self.transtype, len(labels), len(self.inputSlotLabels.senderSlot().container.classes), self.kernel)
        except AssertionError:
            raise AssertionError, "Not enough features!"

        for i in X:
            yield i
            
    def transform(self, data):
        return transform(array(data), self.transtype)

# The following code was kindly provided by Christoph Lampert
# (christoph.lampert@tuebingen.mpg.de) and comes under the
# Apache-License


# define some convenient kernels 

def transform(Xarray, proctype, num_examples, num_components, kernel='gaussian_kernel'):
    """Process data using the specified methods: 'PCA', 'KPCA' (kernel-PCA), 
       'LLE' (laplacian eigenmaps), 'none'"""
    from arpack.speigs import ARPACK_eigs as eigs
    if proctype=='PCA':
        Kmatrix = linear_kernel(Xarray)
        centeredKmatrix = centered(Kmatrix)
        val, vec = eigs(lambda x: dot(centeredKmatrix,x), num_examples, num_components, which='LM')
        vec *= sqrt(val) # equivalent to projecting data to EVs
        return vec

    elif proctype=='KPCA':
        # "kernel-K-means" (similar to Laplacian-based spectral clustering)
        Kmatrix = centered( eval(kernel)(Xarray) )
        val, vec = eigs(lambda x: dot(Kmatrix,x), num_examples, num_components, which='LM')
        vec *= sqrt(val) # equivalent to projecting data to EVs
        return vec

    elif proctype=='LLE':
        # Spectral Clustering in the Ng/Jordan formulation
        Kmatrix = eval(kernel)(Xarray)
        Lmatrix = Kmatrix-diag(diag(Kmatrix))
        Dsqrtmatrix = sqrt(sum(Lmatrix,axis=0))
        Lmatrix *= 1./ascolumn(Dsqrtmatrix)  # multiplies from left because of shape
        Lmatrix *= 1./asrow(Dsqrtmatrix)  # multiplies from right because of shape
        Lmatrix = 0.5*(Lmatrix+Lmatrix.T) # symmetrize, although it should be symmetric already
        val, vec = eigs(lambda x: dot(Lmatrix,x), num_examples, num_components, which='LR')
        vec *= ascolumn(Dsqrtmatrix)
        return vec

    else: # 'none'
        return Xarray


class Normalize(object):
    def __init__(self, normtype, useLazyEvaluation=armor.useLazyEvaluation):
        self.normtype = normtype
        if self.normtype in ['bin', 'L1','L2']:
            self.sequential = False
        elif self.normtype in ['whiten', 'bias', 'crop', 'log', 'none']:
            self.sequential = True
        else:
            raise ValueError, "No operation mode specified"

        if self.sequential:
            self.inputType = armor.slots.VectorType(shape=['flatarray'])
        else:
            self.inputType = armor.slots.VectorType(shape=['flatarray'], bulk=True)

        self.outputType = armor.slots.VectorType(shape='flatarray')

        self.inputSlot = armor.slots.InputSlot(name='unnormalized',
                                               acceptsType=self.inputType)
        if self.sequential:
            self.outputSlot = armor.slots.OutputSlot(name='normalized',
                                                     inputSlot=self.inputSlot,
                                                     slotType='sequential',
                                                     processFunc=armor.weakmethod(self, 'normalize_seq'),
                                                     outputType=self.outputType,
                                                     useLazyEvaluation=useLazyEvaluation)
        else:
            self.outputSlot = armor.slots.OutputSlot(name='normalized',
                                                     inputSlot=self.inputSlot,
                                                     slotType='bulk',
                                                     processFunc=armor.weakmethod(self, 'normalize_bulk'),
                                                     outputType=self.outputType,
                                                     useLazyEvaluation=useLazyEvaluation)
                                                
            
        

        

    # The following code was kindly provided by Christoph Lampert
    # (christoph.lampert@tuebingen.mpg.de) and comes under the
    # Apache-License.

    def normalize_seq(self, data):
        if armor.verbosity>0:
            print "Normalizing %s..." % self.normtype
        Xnorm = array(data, dtype=c_double)

        if self.normtype=='whiten':
            Xnorm = Xnorm-mean(Xnorm,axis=0)
            Xscale = std(Xnorm,axis=0)
            Xnorm[Xnorm==0.]=1.
            Xnorm = Xnorm/Xscale
        elif self.normtype=='bias':
            Xnorm += 1  # pre-processing to normalization
        elif self.normtype=='crop':
            crop_thresh=0.1
            Xnorm[Xnorm>crop_thresh] = crop_thresh # pre-processing to normalization
        elif self.normtype=='log':
            Xnorm = log(Xnorm+1.)
        return Xnorm

    def normalize_bulk(self, data):
        if armor.verbosity>0:
            print "Normalizing %s..." % self.normtype

        Xnorm = array(data, dtype=c_double)
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()
        if self.normtype=='bin':
            Xscale = mean(Xnorm) # median is usually better than mean
            Xnorm = 1.*(Xnorm>Xscale)
        elif self.normtype=='L1':
            Xscale = ascolumn( sum(abs(Xnorm),axis=1) )
            Xscale[Xscale==0]=1.
            Xnorm = Xnorm/Xscale
        elif self.normtype=='L2':
            Xscale = ascolumn( sqrt(sum(Xnorm**2,axis=1)) )
            Xscale[Xscale==0]=1.
            Xnorm = Xnorm/Xscale
        return Xnorm


def normalize_data(Xlist, operation=None, operations=None):
    """Normalize data using the specified methods: 'bin'arize, 'L1', 'L2', 'whiten'ing, 
       'bias' (adds 1 to every entry), 'none'
       L1 and L2 are per-sample operations, binarization and whitening are per feature operations"""

    if operation:
        operations = [operation]


    Xtmp = []
    for Xi in Xlist:
        Xnorm = array(Xi,c_double)
        for normtype in operations:
            if normtype=='bin':
                Xscale = median(Xnorm) # median is usually better than mean
                Xnorm = 1.*(Xnorm>Xscale)
            elif normtype=='L1':
                Xscale = ascolumn( sum(abs(Xnorm),axis=1) )
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='L2':
                Xscale = ascolumn( sqrt(sum(Xnorm**2,axis=1)) )
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='whiten':
                Xnorm = Xi-mean(Xnorm,axis=0)
                Xscale = std(Xnorm,axis=0)
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='bias':
                Xnorm += 1  # pre-processing to normalization
            elif normtype=='crop':
                crop_thresh=0.1
                Xnorm[Xnorm>crop_thresh] = crop_thresh # pre-processing to normalization
            elif normtype=='log':
                Xnorm = log(Xnorm+1.)
            else:
                pass
        Xtmp.append(Xnorm)
    return array(concatenate(Xtmp,axis=1), c_double) # contiguous array


#########################
# Convenience functions #
#########################

def linear_kernel(Xarray):
    Kmatrix = array( dot(Xarray,Xarray.T), c_double)
    return Kmatrix

def chi2_kernel(Xarray):
    from chi2 import chi2_kernel as chi2
    Kmatrix,meanK = chi2( array(Xarray,c_double) )
    return Kmatrix

def gaussian_kernel(Xarray):
    xsq = array([ dot(x,x.T) for x in Xarray], c_double)
    Kmatrix = asrow(xsq) -2*dot(Xarray,Xarray.T) + ascolumn(xsq) 
    Kmatrix = exp(-0.5*Kmatrix/median(Kmatrix)) # default bandwidth
    return Kmatrix

def ascolumn(X):
    """Reshape data into (n x 1) column vector"""
    return reshape(X, (-1,1))

def asrow(X):
    """Reshape data into (1 x n) row vector"""
    return reshape(X, (1,-1))
    
def centered(M):
    """Center a kernel matrix"""
    return M - asrow(mean(M,axis=0)) - ascolumn(mean(M,axis=1)) + mean(M)

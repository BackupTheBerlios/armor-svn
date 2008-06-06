from numpy import array,median,std,mean,log,concatenate,sum,reshape,sqrt,dot
from ctypes import c_double
import armor
import armor.datatypes
import armor.slot


class Transform(object):
    def __init__(self, transtype, useLazyEvaluation=armor.useLazyEvaluation):
        self.transtype = transtype
        if self.transtype not in ['PCA','KPCA', 'LLE']:
            raise ValueError, "No operation mode specified"

	self.inputType = armor.datatypes.VectorType(shape=['flatarray'], bulk=True)

        self.outputType = armor.datatypes.VectorType(shape='flatarray')

        self.inputSlot = armor.slot.InputSlot(name='untransformed',
                                              acceptsType=self.inputType)

	self.outputSlot = armor.slot.OutputSlot(name='transformed',
						inputSlot=self.inputSlot,
						slotType='bulk',
						processFunc=armor.weakmethod(self, 'transform'),
						outputType=self.outputType,
						useLazyEvaluation=useLazyEvaluation)

    def transform(self, data):
	if armor.verbosity>0:
	    print "Transforming: %s..." % self.transtype
	return transform(array(data), self.transtype)

# The following code was kindly provided by Christoph Lampert
# (christoph.lampert@tuebingen.mpg.de) and comes under the
# Apache-License


# define some convenient kernels 

def transform(Xarray, proctype):
    """Process data using the specified methods: 'PCA', 'KPCA' (kernel-PCA), 
       'LLE' (laplacian eigenmaps), 'none'"""
    from arpack.speigs import ARPACK_eigs as eigs
    if proctype=='PCA':
        Kmatrix = linear_kernel(Xarray)
        centeredKmatrix = centered(Kmatrix)
        val, vec = eigs(lambda x: dot(centeredKmatrix,x), num_examples, num_components, which='LM')
        vec *= sqrt(val) # equivalent to projecting data to EVs
        return vec

    elif proctype.startswith('KPCA'):
        # "kernel-K-means" (similar to Laplacian-based spectral clustering)
        try:
            kernel=proctype.split('-')[1]+'_kernel'
	except IndexError:
	    kernel='gaussian_kernel'
	Kmatrix = centered( eval(kernel)(Xarray) )
        val, vec = eigs(lambda x: dot(Kmatrix,x), num_examples, num_components, which='LM')
        vec *= sqrt(val) # equivalent to projecting data to EVs
        return vec

    elif proctype.startswith('LLE'):
        # Spectral Clustering in the Ng/Jordan formulation
        try:
            kernel=proctype.split('-')[1]+'_kernel'
	except IndexError:
	    kernel='gaussian_kernel'
        
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

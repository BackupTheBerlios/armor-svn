from __future__ import division
import numpy
import numpy as np
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
        if self.normtype=='none':
            return data

        if armor.verbosity>0:
            print "Normalizing %s..." % self.normtype
        Xnorm = array(data)

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

        Xnorm = array(data)
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



class Fft2(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):
        self.inputType = armor.slots.ImageType(format=['PIL'], color_space=['gray'])
        self.outputType = armor.slots.VectorType(shape='flatarray')

        self.inputSlot = armor.slots.InputSlot(name='unnormalized',
                                               acceptsType=self.inputType)

        self.outputSlot = armor.slots.OutputSlot(name='normalized',
                                                 inputSlot=self.inputSlot,
                                                 slotType='sequential',
                                                 processFunc=armor.weakmethod(self, 'fft2'),
                                                 outputType=self.outputType,
                                                 useLazyEvaluation=useLazyEvaluation)

    def fft2(self, img):
        import scipy.fftpack, numpy
        from PIL import Image
        
        if armor.verbosity > 0:
            print "Computing fft2 of image..."
        img = img.resize((256,256), Image.ANTIALIAS)
        x = numpy.array(img)
        x = x-mean(x)
        fft = numpy.power(numpy.abs(scipy.fftpack.fft2(x)), 2)
        fft_shifted = scipy.fftpack.fftshift(fft)
        fft_normalized = fft_shifted/numpy.var(fft_shifted)
        (size_x, size_y) = fft_normalized.shape
        return fft_normalized[:size_x/2, :]

class FFt2TransformToGauss(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):
        self.inputTypeData = armor.slots.VectorType(shape=['flatarray'])
        self.inputTypeLabels = armor.slots.VectorType(name=['labels'], shape=['flatlist'])
        
        self.outputType = armor.slots.VectorType(shape='flatarray')

        self.inputSlotData = armor.slots.InputSlot(name='untransformed',
                                                   acceptsType=self.inputTypeData)

        self.inputSlotLabels = armor.slots.InputSlot(name='labels',
                                                     acceptsType=self.inputTypeLabels)

        self.outputSlot = armor.slots.OutputSlot(name='transformed',
                                                 outputType=self.outputType,
                                                 useLazyEvaluation=useLazyEvaluation,
						 slotType='sequential',
                                                 iterator=armor.weakmethod(self, 'iterator'))

	self.x, self.y = np.mgrid[-.5:.5:256j, -.5:.5:256j]
	
    def iterator(self):
	pass

    # The following function was taken from the GIST code of (c) Antonia Torralba
    # and converted from Matlab to Python by Thomas Wiecki.
    def createGabor(self, orients, size):
	"""
	% G = createGabor(numberOfOrientationsPerScale, n);
	%
	% Precomputes filter transfer functions. All computations are done on the
	% Fourier domain. 
	%
	% If you call this function without output arguments it will show the
	% tiling of the Fourier domain.
	%
	% Input
	%     numberOfOrientationsPerScale = vector that contains the number of
	%                                orientations at each scale (from HF to BF)
	%     n = imagesize (square images)
	%
	% output
	% G = transfer functions for a jet of gabor filters
	"""
	Nscales = len(orients)
	Nfilters = np.sum(orients)

	l=0
	param = np.empty((Nfilters, 4))
	for i in xrange(Nscales):
	    for j in xrange(orients[i]):
		param[l,:]=[.35, .3/(1.85**i), 16*orients[i]**2/32.**2, np.pi/(orients[i])*j]
		l=l+1

	# Frequencies:
	fx, fy = np.mgrid[-size/2:size/2, -size/2:size/2]
	fr = np.fft.fftshift(np.sqrt(np.power(fx,2)+np.power(fy,2)))
	t = np.fft.fftshift(np.angle(fx + fy*np.complex(0,1)))


	# Transfer functions:
	G = np.zeros((size, size, Nfilters))
	for i in xrange(Nfilters-1):
	    tr=t+param[i,3]
	    tr=tr + 2*np.pi*(tr< -(np.pi)) - 2*np.pi*(tr > np.pi)
	    G[:,:,i]=np.exp( -10*param[i,0]*np.power((fr/size/param[i,1]-1),2) - 2*param[i,2]*np.pi*np.power(tr,2) )

	return G

    def gistGabor(self, img, w, G):
	"""
	% Input:
	%   img = input image (it can be a block: [nrows, ncols, c, Nimages])
	%   w = number of windows (w*w)
	%   G = precomputed transfer functions
	%
	% Output:
	%   g: are the global features = [Nfeatures Nimages], 
	%                    Nfeatures = w*w*Nfilters*c
	"""
	if img.ndim==2:
	    c = 1 
	    N = 1

	if img.ndim==3:
	    (nrows, ncols, c) = img.shape
	    N = c

	if img.ndim==4:
	    (nrows, ncols, c, N) = img.shape
	    img = reshape(img, (nrows, ncols, c*N))
	    N = c*N


	(n, n, Nfilters) = G.shape
	W = w**2
	g = np.zeros((W*Nfilters, N))

	img = np.fft.fft2(img)
	k=0
	for n in xrange(Nfilters):
	    filt = G[:,:,n]
	    print filt.shape
	    filtered = img * filt.resize((filt.shape[0], filt.shape[1], N))
	    ig = np.abs(np.fft.ifft2(filtered))
	    #pl.imshow(ig)
	    v = self.downN(ig, w)
	    print filtered.shape
	    print v.shape
	    print W
	    print N
	    g[k:k+W-1,:] = v.reshape((W, N))
	    k = k + W

	if c == 3:
	    # If the input was a color image, then reshape 'g' so that one column
	    # is one images output:
	    g = g.reshape((g.shape[0]*3, g.shape[1]/3))

	return g

    def downN(self, x, N):
	"""
	% 
	% averaging over non-overlapping square image blocks
	%
	% Input
	%   x = [nrows ncols nchanels]
	% Output
	%   y = [N N nchanels]
	"""
	nx = np.fix(np.linspace(0,x.shape[0],N))
	ny = np.fix(np.linspace(0,x.shape[1],N))
	y  = np.zeros((N, N, x.shape[2]))
	for xx in xrange(N):
	    for yy in xrange(N):
		v = np.mean(x[nx[xx]:nx[xx], ny[yy]:ny[yy],:])
		y[xx,yy,:] = v.flatten()

	return y

    def G(self, f_x, f_y, f_0, sigma_x, sigma_y):
	return np.exp( -np.power(f_y,2) / sigma_y**2 ) * (np.exp( -np.power(f_x-f_0,2)/sigma_x**2 ) + np.exp( np.power(f_x+f_0,2)/sigma_x**2) )
    
class Average(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):
        self.inputTypeData = armor.slots.VectorType(shape=['flatarray'])
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
        import pylab, numpy
        # Pool data
        data = array(list(self.inputSlotData))
        classes = self.inputSlotLabels.senderSlot().container.classes
        labels = array(list(self.inputSlotLabels))


        animal_idx = data[labels==classes[0],:,:]
        bgrnd_idx = data[labels==classes[1],:,:]
        del data
        
        animal_mean = numpy.mean(animal_idx, axis=0)
        bgrnd_mean = numpy.mean(bgrnd_idx, axis=0)
        pylab.figure(1)
        pylab.imshow(numpy.log(animal_mean))
        pylab.title('Animals - Mean')
        pylab.figure(2)
        pylab.imshow(numpy.log(bgrnd_mean))
        pylab.title('Background - Mean')
        
        animal_var = numpy.var(animal_idx, axis=0)
        bgrnd_var = numpy.var(bgrnd_idx, axis=0)
        pylab.figure(3)
        pylab.imshow(numpy.log(animal_var))
        pylab.title('Animals - Variance')
        pylab.figure(4)
        pylab.imshow(numpy.log(bgrnd_var))
        pylab.title('Background - Variance')

        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()
       
        mean_diff = numpy.abs(animal_mean - bgrnd_mean)
        var_diff = numpy.abs(animal_var - bgrnd_var)

        mean_mult = numpy.log(mean_diff)
        mean_norm = (mean_mult - numpy.min(mean_mult)) / (numpy.max(mean_mult)-numpy.min(mean_mult))
        var_mult = numpy.log(numpy.abs(animal_var * bgrnd_var))
        var_norm = (var_mult - numpy.min(var_mult)) / (numpy.max(var_mult)-numpy.min(var_mult))
        why_diff = mean_norm / var_norm
        why_diff[why_diff == numpy.Inf] = 1.0
        pylab.figure(5)
        pylab.imshow(numpy.log(mean_diff))
        pylab.title('Difference - Mean')
        pylab.figure(6)
        pylab.imshow(numpy.log(var_diff))
        pylab.title('Difference - Variance')
        pylab.figure(7)
        pylab.imshow(why_diff)
        pylab.title('Difference - Special')

        animal_row = reshape(animal_idx, (animal_idx.shape[0], -1))
        bgrnd_row = reshape(bgrnd_idx, (bgrnd_idx.shape[0], -1))
        
        animal_mean_feat = numpy.dot(animal_row, asrow(mean_diff).T)
        bgrnd_mean_feat = numpy.dot(bgrnd_row, asrow(mean_diff).T)
        animal_var_feat = numpy.dot(animal_row, asrow(var_diff).T)
        bgrnd_var_feat = numpy.dot(bgrnd_row, asrow(var_diff).T)
        animal_why_feat = numpy.dot(animal_row, asrow(var_diff).T)
        bgrnd_why_feat = numpy.dot(bgrnd_row, asrow(var_diff).T)



        animal_feat = numpy.vstack((animal_mean_feat.T, animal_var_feat.T)) #  animal_why_feat))
        bgrnd_feat = numpy.vstack((bgrnd_mean_feat.T, bgrnd_var_feat.T)) #, bgrnd_why_feat))
        
        pylab.figure(8)
        pylab.plot(animal_feat[0], animal_feat[1], '+b', label='_nolegend_')
        pylab.plot(bgrnd_feat[0], bgrnd_feat[1], 'xr', label='_nolegend_')
        pylab.title('Animal feat Vs Background feat')
        
        pylab.show()

        yield animal_feat
        

    def normalize(self, x):
        return (x - numpy.min(x)) / (numpy.max(x) - numpy.min(x))
    

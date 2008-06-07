import mpi_kmeans
import numpy
import armor.slots
import armor
from ctypes import c_double
from scipy import cluster

class Kmeans(object):
    """Class to perform kmeans clustering on input data (e.g. descriptors).
    Returns a codebook.
    For performance reasons we use the kmeans implementation of Peter Gehler
    (pgehler@tuebingen.mpg.de, URL: http://mloss.org/software/view/48/)

    Default is lazy, so the clustering will only be performed when the codebook
    gets accessed."""
    def __init__(self, numClusters, maxiter=2000, numruns=200, useLazyEvaluation=armor.useLazyEvaluation):
        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns
	self.useLazyEvaluation = useLazyEvaluation
	
	# Define some types
	inputType = armor.slots.VectorType(shape=['flatarray'])
	outputType = armor.slots.VectorType(name='codebook', shape='flatarray')

	self.inputSlot = armor.slots.InputSlot(name='vectors', acceptsType = inputType, bulk=True, useLazyEvaluation=useLazyEvaluation)
	
	self.outputSlot = armor.slots.OutputSlot(name='codebook',
						inputSlot = self.InputSlot,
						slotType = 'bulk',
						processFunc = armor.weakmethod(self, 'process'),
						outputType = outputType,
						useLazyEvaluation= self.useLazyEvaluation)
	
    def process(self, data):
	# Perform KMeans clustering
	if armor.verbosity > 0:
	    print "Performing kmeans clustering with k=%i..." % self.numClusters
	self.codebook, self.dist, self.labels = mpi_kmeans.kmeans(numpy.array(data, dtype=c_double), self.numClusters, self.maxiter, self.numruns)

	return self.codebook



class Quantize(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):

        self.useLazyEvaluation = useLazyEvaluation

        # Define types
        inputTypeVec = armor.slots.VectorType(shape=['nestedlist', 'nestedarray'])
        inputTypeCodebook = armor.slots.VectorType(name=['codebook'], shape=['flatarray'])
        
        outputType = armor.slots.VectorType(shape='flatarray')

        # Define slots
        self.inputSlotVec = armor.slots.InputSlot(name='vectors',
                                                  acceptsType=inputTypeVec)

        self.inputSlotCodebook = armor.slots.InputSlot(name='codebook',
                                                       acceptsType=inputTypeCodebook)
        
        self.outputSlot = armor.slots.OutputSlot(name='cluster',
                                                 outputType=outputType,
                                                 iterator=armor.weakmethod(self, 'quantize'),
                                                 useLazyEvaluation=self.useLazyEvaluation)

    def quantize(self):
        # Get data from codebook slot
        codebook = numpy.array(list(self.inputSlotCodebook))

        # Sequentiall get data from vector slot
        for features in self.inputSlotVec:
            if armor.verbosity > 0:
                print ("Quantizing... Codebook shape: %i,%i Vector Shape: %i,%i " % (codebook.shape[0], codebook.shape[1], features.shape[0], features.shape[1]))
            clusters = cluster.vq.vq(features, codebook)[0]
            yield clusters




#    def quantize(self):
#	self.dataClusters = []
#	
#	for vecs in self.data:
#	    dataCluster = cluster.vq.vq(vecs[0], self.clusters)
#	    self.dataClusters.append((dataCluster[0], vecs[1]))

    #==============
#    def Histogram(self):
#    #==============
#       self.dataHistogram = []

#	for (dataCluster, classID) in self.dataClusters:
#	    histo = npy.Histogram(dataCluster, bins = self.numClusters)
#	    self.dataHistogram.append((histo[0], classID))

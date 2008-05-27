import mpi_kmeans
import numpy
import armor.slot
import armor.datatypes
import armor

class kmeansObj(object):
    """Class to perform kmeans clustering on input data (e.g. descriptors).
    Returns a codebook.
    For performance reasons we use the kmeans implementation of Peter Gehler
    (pgehler@tuebingen.mpg.de, URL: http://mloss.org/software/view/48/)

    Default is lazy, so the clustering will only be performed when it gets
    accessed."""
    def __init__(self, numClusters, maxiter=0, numruns=1, useGenerator=armor.useGenerator):
        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns

	self.inputType = armor.datatypes.VectorType(shape=['flatarray'])
	self.outputType = armor.datatypes.VectorType(shape='flatarray')

	self.inputSlot = armor.slot.inputSlot(name='vectors', acceptsType = self.inputType, bulk=True)
	
	self.outputSlot = armor.slot.outputSlot(name='codebook',
						input = self.inputSlot,
						slotType = 'bulk',
						processFunc = self.process)
	
    def process(self, data):
	# Perform KMeans clustering
	if armor.verbosity > 0:
	    print "Performing kmeans clustering..."
	self.codebook, self.dist, self.labels = mpi_kmeans.kmeans(numpy.array(data).T, self.numClusters, self.maxiter, self.numruns)

	return self.codebook
	    
#    def quantize(self):
#	self.dataClusters = []
#	
#	for vecs in self.data:
#	    dataCluster = cluster.vq.vq(vecs[0], self.clusters)
#	    self.dataClusters.append((dataCluster[0], vecs[1]))

    #==============
#    def histogram(self):
#    #==============
#       self.dataHistogram = []

#	for (dataCluster, classID) in self.dataClusters:
#	    histo = npy.histogram(dataCluster, bins = self.numClusters)
#	    self.dataHistogram.append((histo[0], classID))

import mpi_kmeans
import types
import numpy as npy
from scipy import cluster
import armor.SeqContainer

class kmeans(object):
    def __init__(self, input, numClusters, maxiter=0, numruns=1):
	self.input = input
        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns

	self.runKmeans()
	self.quantize()
	del self.data
	self.histogram()

    def getData(self):
	return armor.SeqContainer.SeqContainer(self.dataHistogram, classes=self.input.classes, useGenerator=False)
    
    def runKmeans(self):
	# For the clustering we need the data without labels and 
        
	self.data = list(self.input)

	# Also, remove the labels
	data = [x[0] for x in self.data]

	# Flatten the list (if we get descriptors, we get a list of 2-D arrays)
	if isinstance(data, types.ListType):
	    if isinstance(data[0], npy.ndarray):
		data = npy.concatenate(data)

	# Perform KMeans clustering
	self.clusters, self.dist, self.labels = mpi_kmeans.kmeans(data, self.numClusters, self.maxiter, self.numruns)
	    
    def quantize(self):
	self.dataClusters = []
	
	for vecs in self.data:
	    dataCluster = cluster.vq.vq(vecs[0], self.clusters)
	    self.dataClusters.append((dataCluster[0], vecs[1]))

    #==============
    def histogram(self):
    #==============
        self.dataHistogram = []

	for (dataCluster, classID) in self.dataClusters:
	    histo = npy.histogram(dataCluster, bins = self.numClusters)
	    self.dataHistogram.append((histo[0], classID))

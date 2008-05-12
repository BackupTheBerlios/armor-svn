import unittest
import armor
import armor.tests
import numpy
import os.path

class testAll(unittest.TestCase):
    def setUp(self):
	self.path = armor.tests.__path__[0]
	self.imgDataset = armor.ImageDataset()
	self.imgDataset.loadFromXML(os.path.join(self.path, 'test_valid.xml'))


    def testGenerator(self):
	sft = armor.sift(self.imgDataset.getData(useGenerator=True))
        km = armor.kmeans(sft.getData(useGenerator=True), 3)
	data = list(km.getData())
	self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
	#for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
	#    self.assertTrue(all(x[0] == y))
	
    def testList(self):
	sft = armor.sift(self.imgDataset.getData())
	km = armor.kmeans(sft.getData(), 3)
	data = list(km.getData())
	self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
	#TODO: Call kmeans with fixed start vectors
	#for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
	#    self.assertTrue(all(x[0] == y))

suite = unittest.TestLoader().loadTestsFromTestCase(testAll)
unittest.TextTestRunner(verbosity=3).run(suite)
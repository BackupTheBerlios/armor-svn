import numpy, PIL.Image
import armor.sift
import unittest

class TestSift(unittest.TestCase):
    def setUp(self):
	self.path = armor.tests.__path__[0]
	self.imgDataset = armor.ImageDataset()
	self.imgDataset.loadFromXML(self.path + '/test_valid.xml')

	
    def testSiftGenerator(self):
	#TODO: Check if values are correct descriptors
	self.sft = armor.sift(self.imgDataset.getData(useGenerator=True), Verbose=1)
	list(self.sft.getData(useGenerator=True))

    def testSiftList(self):
	self.sft = armor.sift(self.imgDataset.getData(), Verbose=1)
	self.sft.getData(useGenerator=False)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSift)
unittest.TextTestRunner(verbosity=3).run(suite)
	

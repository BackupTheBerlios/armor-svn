import numpy, PIL.Image
import armor.sift
import armor.ImageDataset
import unittest
import os.path
import armor.tests

class TestSift(unittest.TestCase):
    def setUp(self):
	self.path = armor.tests.__path__[0]
	self.imgDataset = armor.ImageDataset.ImageDataset()
	self.imgDataset.loadFromXML(os.path.join(self.path, 'test_valid.xml'))

	
    def testSiftGenerator(self):
	#TODO: Check if values are correct descriptors
	self.sft = armor.sift(self.imgDataset.outContainer, Verbose=1)
	list(self.sft.outContainer)

    def testSiftList(self):
	self.sft = armor.sift.siftObj(self.imgDataset.outContainer, Verbose=1)
	list(self.sft.outContainer)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSift)
unittest.TextTestRunner(verbosity=3).run(suite)
	

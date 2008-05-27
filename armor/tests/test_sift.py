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
	self.imgDataset.prepare()
	
    def testSiftGenerator(self):
	#TODO: Check if values are correct descriptors
	self.sft = armor.sift.siftObj(Verbose=1)
	self.sft.inputSlot.registerInput(self.imgDataset.outputSlot)
	list(self.sft.outputSlot)

    def testSiftList(self):
	self.sft = armor.sift.siftObj(Verbose=1)
	self.sft.inputSlot.registerInput(self.imgDataset.outputSlot)
	list(self.sft.outputSlot)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSift)
unittest.TextTestRunner(verbosity=3).run(suite)
	

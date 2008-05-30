import unittest
import armor.ImageDataset
import armor.sift
import armor.kmeans
import armor.quantize
import armor.tests
import armor.histogram

import armor
import numpy
import os.path
import gc

class testAll(unittest.TestCase):
    def setUp(self):
	self.path = armor.tests.__path__[0]
	self.imgDataset = armor.ImageDataset.ImageDataset()
	self.imgDataset.loadFromXML(os.path.join(self.path, 'test_valid.xml'))
	self.imgDataset.prepare()

    def testGenerator(self):
	#from IPython.Debugger import Tracer; debug_here = Tracer()
	#debug_here()

	sft = armor.sift.siftObj()
        km = armor.kmeans.kmeansObj(3)
	qt = armor.quantize.quantize()
	hg = armor.histogram.histogram(3)
	
	sft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
	km.inputSlot.registerInput(sft.outputSlot)
	qt.inputSlotCodebook.registerInput(km.outputSlot)
	qt.inputSlotVec.registerInput(sft.outputSlot)
	hg.inputSlot.registerInput(qt.outputSlot)
	
	print list(hg.outputSlot)
	del sft
	self.assertRaises(AttributeError, list(hg.outputSlot))
#	del km
#	self.assertRaises(AttributeError, list(hg.outputSlot))
	
#	armor.saveSlots([km.outputSlot], 'kmeansSlot.pickle')
#	kmSlots = armor.loadSlots('kmeansSlot.pickle')
#	assert (list(km.outputSlot), list(kmSlots['codebook']))
#	print list(km.outputSlot)[0].shape


	#self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
	#for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
	#    self.assertTrue(all(x[0] == y))
	
#     def testList(self):
# 	sft = armor.sift(self.imgDataset.getData())
# 	km = armor.kmeans(sft.getData(), 3)
# 	data = list(km.getData())
# 	self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
	#TODO: Call kmeans with fixed start vectors
	#for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
	#    self.assertTrue(all(x[0] == y))

suite = unittest.TestLoader().loadTestsFromTestCase(testAll)
unittest.TextTestRunner(verbosity=3).run(suite)

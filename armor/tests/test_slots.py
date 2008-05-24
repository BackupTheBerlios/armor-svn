import unittest
import armor
import armor.slot
import armor.datatypes

class TestTypes(unittest.TestCase):
    def setUp(self):
	self.sequence = range(10)

    def setSlotsNoConversion(self):
	self.outType1 = armor.datatypes.ImageType(format='PIL', color_space='RGB')
	self.inType2 = armor.datatypes.ImageType(format=['PIL'], color_space=['RGB'])
	self.outType2 = armor.datatypes.VectorType(shape='nestedlist')

	self.slotSend = armor.slot.slot('sender',
				   iterator=self.iterator,
				   outputType=self.outType1)
				   
	self.slotRecv = armor.slot.slot('receiver',
				   processFunc=self.process,
				   inputType=self.inType2,
				   outputType=self.outType2)

    def setSlotsConversion(self):
	self.outType1 = armor.datatypes.ImageType(format='PIL', color_space='RGB')
	self.inType2 = armor.datatypes.ImageType(format=['PIL'], color_space=['gray'])
	self.outType2 = armor.datatypes.VectorType(shape='nestedlist')

	self.slotSend = armor.slot.slot('sender',
				   iterator=self.iterator,
				   outputType=self.outType1)
				   
	self.slotRecv = armor.slot.slot('receiver',
				   processFunc=self.process,
				   inputType=self.inType2,
				   outputType=self.outType2)
	
    def testSlotConnectNoConversion(self):
	self.setSlotsNoConversion()
	self.slotRecv.registerInput(self.slotSend)
	self.assertEqual([i.__name__ for i in self.slotRecv.processFuncs], ['process'])
	
    def testSlotConnectConversion(self):
	self.setSlotsConversion()
	self.slotRecv.registerInput(self.slotSend)
	self.assertEqual([i.__name__ for i in self.slotRecv.processFuncs], ['convert_RGB_to_gray', 'process'])

    def testIterating(self):
	self.setSlotsNoConversion()
	self.slotRecv.registerInput(self.slotSend)
	self.assertEqual([i for i in self.slotRecv], range(10))


	
    def process(self, item):
	return item

    def iterator(self):
	for i in xrange(10):
	    yield i

suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)

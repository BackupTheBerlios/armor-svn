import armor.datatypes
import unittest
import PIL.Image
import numpy

class TestTypes(unittest.TestCase):
    def setUp(self):
	pass

    def testConvertRGB(self):
	a = armor.datatypes.ImageType(format=['PIL'], color_space=['gray'], symmetrical=False)
	b = armor.datatypes.ImageType(format='PIL', color_space='RGB', symmetrical=False)
	self.assertEqual(a.compatible(b)[0].__name__, 'convert_RGB_to_gray')

    def testIncompatibleType(self):
	a = armor.datatypes.ImageType(format=['PIL'], color_space=['RGB'], symmetrical=False)
	b = armor.datatypes.VectorType(format='PIL', color_space='gray', symmetrical=False)
	assert a.compatible(b) is False

    def testIncompatibleAttr(self):
	a = armor.datatypes.ImageType(format=['PIL'], color_space=['RGB'], symmetrical=False)
	b = armor.datatypes.ImageType(format='PIL', color_space='gray', symmetrical=False)
	assert a.compatible(b) is False	

    def testNestedVectorToFlat(self):
	a = armor.datatypes.VectorType(shape=['flatarray'])
	b = armor.datatypes.VectorType(shape='nestedlist')
	self.assertEqual(a.compatible(b)[0].__name__, 'convert_nestedlist_to_flatarray')


suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)

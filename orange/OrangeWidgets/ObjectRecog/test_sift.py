import numpy, PIL.Image
import _sift

x = PIL.Image.open('lena.pgm')
x = numpy.array(x.convert('L'), dtype=numpy.float32)
z = numpy.array(x.T).copy()
print z.dtype
print z
y = _sift.sift(z, Verbose=1)

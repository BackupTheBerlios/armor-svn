import sys
import os
import platform

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

try:
    import numpy
    import scipy
    import PIL
except:
    print "You need to have numpy, scipy and PIL installed."
    
import glob

siftModule = Extension('_sift',
		       language = 'c++',
		       sources = glob.glob('src/vlfeat/vl/*.c') + ['src/vlfeat/python/sift.c'],
		       extra_compile_args=['-g', '-pedantic', '-Wall', '-std=c89', '-O3' ,'-Wno-unused-function', '-Wno-long-long', '-D__LITTLE_ENDIAN__', '-std=c99'],
		       include_dirs = [numpy.get_include(), 'src/vlfeat'],
		       extra_link_args = ['-lm'])

kmeansModule = Extension('libmpikmeans',
		       language = 'c++',
		       sources = ['src/mpi_kmeans/mpi_kmeans.cxx'],
		       extra_compile_args=['-Wl,-soname=libmpikmeans.so','-Wall', '-O3'])


setup (name = 'armor',
       version = '0.1',
       description = 'Object Recognition Toolkit for Orange',
       author = 'Thomas V. Wiecki',
       author_email = 'thomas.wiecki@gmail.com',
       url = 'http://www.python.org/doc/current/ext/building.html',
       long_description = '''...''',
       ext_modules = [siftModule, kmeansModule],
       packages = ['armor', 'armor.orngWidgets', 'armor.tests'],
       package_dir={'': 'src'},
       include_package_data = True,
       #install_requires=['setuptools', 'numpy >= 1.0', 'scipy >= 0.5', 'PIL >= 1.1.6'],
       test_suite = "armor.tests.test_all",
       zip_safe = False
       )


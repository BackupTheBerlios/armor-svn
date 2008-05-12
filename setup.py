import sys
import os
import platform

scriptName = sys.argv[0]

if not (scriptName == "setup.py" and os.path.exists("armor")):
	print """
Please start the installation from the directory above "armor" by executing
"python setup.py build" 
"python setup.py test"
"python setup.py install"
"""
	exit(1)
	

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension
try:
    import numpy
    import scipy
    import PIL
except:
    print "You need to have numpy, scipy an PIL installed."
    
import glob

siftModule = Extension('_sift',
		       language = 'c++',
		       sources = glob.glob('source/vlfeat/vl/*.c') + ['source/vlfeat/python/sift.c'],
		       extra_compile_args=['-g', '-pedantic', '-Wall', '-std=c89', '-O3' ,'-Wno-unused-function', '-Wno-long-long', '-D__LITTLE_ENDIAN__', '-std=c99'],
		       include_dirs = [numpy.get_include(), 'source/vlfeat'],
		       extra_link_args = ['-lm'])

kmeansModule = Extension('libmpikmeans',
		       language = 'c++',
		       sources = ['source/mpi_kmeans/mpi_kmeans.cxx'],
		       extra_compile_args=['-Wl,-soname=libmpikmeans.so','-Wall', '-O3'])

setup (name = 'Armor',
       version = '0.1',
       description = 'Object Recognition Toolkit for Orange',
       author = 'Thomas V. Wiecki',
       author_email = 'thomas.wiecki@gmail.com',
       url = 'http://www.python.org/doc/current/ext/building.html',
       long_description = '''...''',
       ext_modules = [siftModule, kmeansModule],
       packages = ['armor', 'armor.orngWidgets', 'armor.tests'],
       include_package_data = True,
       test_suite = "armor.tests.test_all",
       zip_safe = False
#       install_requires = ['numpy >= 1.0', 'scipy >= 0.5', 'PIL >= 1.1.6']
       )

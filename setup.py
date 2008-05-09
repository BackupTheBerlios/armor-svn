from setuptools import setup, Extension
import numpy
import glob

siftModule = Extension('_sift',
		       language = 'c++',
		       sources = glob.glob('source/vlfeat/vl/*.c') + ['source/vlfeat/python/sift.c'],
		       extra_compile_args=['-g', '-pedantic', '-Wall', '-std=c89', '-O0' ,'-Wno-unused-function', '-Wno-long-long', '-D__LITTLE_ENDIAN__', '-std=c99'],
		       include_dirs = [numpy.get_include(), 'vlfeat'],
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
       packages = ['armor'],
#       package_dir={'armor': 'armor'},
       pymodules = ['orngWidgets/*.py']
       package_data={'armor': ['orngWidgets/*.py']}
       )

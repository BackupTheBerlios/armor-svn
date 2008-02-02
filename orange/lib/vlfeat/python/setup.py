from distutils.core import setup, Extension
import numpy
module1 = Extension('_sift',
                    define_macros = [('MAJOR_VERSION', '0'),
                                     ('MINOR_VERSION', '1')],
                    include_dirs = ['..',numpy.get_include()],
                    #libraries = ['tcl83'],
                    #library_dirs = ['/usr/local/lib'],
                    sources = ['sift.c'],
		    extra_link_args = ['../bin/glx/objs/sift.o','../bin/glx/objs/imop.o']
		    )

setup (name = 'Sift',
       version = '1.0',
       description = 'This is a demo package',
       author = 'Thomas V. Wiecki',
       author_email = 'thomas.wiecki@gmail.com',
       url = 'http://www.python.org/doc/current/ext/building.html',
       long_description = '''
This is really just a demo package.
''',
       ext_modules = [module1])

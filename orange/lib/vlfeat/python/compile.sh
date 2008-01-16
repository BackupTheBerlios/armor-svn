gcc -DLINUX -I.. -I/usr/lib/python2.5/site-packages/numpy/core/include/numpy/ -pedantic -Wall -std=c99 -g -O0 -c sift.c -o _sift.o
gcc -lpython2.5 -shared _sift.o ../bin/glx/objs/*.o -o _sift.so

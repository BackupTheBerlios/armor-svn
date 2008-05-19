from subprocess import call
import armor.prototypes

class sift2(armor.prototypes.SeqProcessor):
    def __init__(self, images, useGenerator=True, **kwargs):
        armor.prototypes.SeqProcessor.__init__(self, images, useGenerator)
        self.kwargs = kwargs

    def preprocess(self, img):
        img.save('tmp.pgm')
        return img
    
    def process(self, img):
        call(['./siftfeat', '-x', '-o', 'tmp.out', 'tmp.pgm'])
        return('tmp.out')
    
    def postprocess(self, fname = 'tmp.out'):
        f = open(fname,'rb')
        f.readline() #skip the first line
        xlist = []
        ylist = []
        while(1):
            x = f.readline()[0:-1].split()
            y = []
            for i in range(7):
                y = y + [int(x) for x in f.readline()[1:-1].split()]
            xlist.append(x)
            ylist.append(y)
#depending on file mode use tell to get file position
            pos = f.tell()
            if f.read(1)=="":
                f.close()
                break
            f.seek(pos)
        return (xlist, ylist)


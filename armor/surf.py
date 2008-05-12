from subprocess import call
import armor.SeqContainer

class surf(object):
    def __init__(self, imgContainer, **kwargs):
        self.imgContainer = imgContainer
        self.kwargs = kwargs

    def iterator(self):
        for img in self.imgContainer:
            self.runAlgorithm(img[0], **self.kwargs)
            yield (self.readDescrFile()[1], img[1])
        #self.imgContainer.reset()

    def getData(self, useGenerator=True):
	return armor.SeqContainer(self.iterator, classes=self.imgContainer.classes, useGenerator=useGenerator)

    def runAlgorithm(self, img, **kwargs):
        img.save('tmp.pgm')
        call(['./siftfeat', '-x', '-o', 'tmp.out', 'tmp.pgm'])

    def readDescrFile(self, fname = 'tmp.out'):
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


import OWImageDataset
import sift
import kmeans

def test():
    owi = OWImageDataset.OWImageDataset()
    owi.loadFromXML('test.xml')
    owi.prepareSet()
    sft = sift.sift(owi.iterator)
    sft.createDescr()
    
    km = kmeans.kmeans(sft.iterator, 3)
    km.quantize()

    km.histogram()
    
    return km.dataHistogram
    
    

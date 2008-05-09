import armor

def test():
    owi = armor.ImageDataset()
    owi.loadFromXML('test_valid.xml')
#    owi.prepareSet()
    sft = armor.sift(owi.getData(useGenerator=True))
    
    km = armor.kmeans(sft.getData(useGenerator=True), 3)
    
    return km.getData()

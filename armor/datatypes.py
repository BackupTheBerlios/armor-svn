import types

class basetype(object):
    def __init__(self, **kwargs):
        self.dataType = kwargs
        self.attributes = {}
        self.conversions = {}
	
    def __iter__(self):
        return iter(self.dataType)

    def __getitem__(self, item):
        return self.dataType[item]
    
    def compatible(self, toType):
	if toType.__class__ is not self.__class__:
            return False

        convertable = False
        conversionFunc = []
        
        for key in toType:
            # If key is not present, we assume compatibility
            if key not in self:
                continue
            
            # Convert self[key] to list if needed
            selfkey = self[key] if isinstance(self[key], type([])) else [self[key]]
            
            if toType[key] in selfkey:
                continue # Compatible

            # Can we convert?
            for attr in selfkey:
                for conversion in self.conversions[key]:
                    if conversion[0] == toType[key] and conversion[1] == attr:
                        conversionFunc.append(conversion[2])
                        convertable = True
                        break
                if convertable:
                    break
            if convertable:
                convertable=False
                continue
                
            # If we are here, we are not compatible and can not convert
            return False

        # For now we disable multiple conversions as it is not really clear
        # on what the order should be etc and may cause weird behavior
        if len(conversionFunc) > 1:
            return False
        
        return conversionFunc
            
        
class ImageType(basetype):
    from PIL import Image
    def __init__(self, **kwargs):
        super(ImageType, self).__init__(**kwargs)
        
        self.attributes = {'format': ['PIL', 'vigra'],
                          'color_space': ['gray', 'RGB'],
                          'symmetrical': [False, True]
                           }

        self.conversions = {'format': [('PIL', 'vigra', self.convert_PIL_to_vigra)],
                            'color_space': [('RGB', 'gray', self.convert_RGB_to_gray)],
                            'symmetrical' : []
                            }

    def convert_PIL_to_vigra(self, image):
        raise NotImplemented, "Vigra support not yet implemented"
    
    def convert_RGB_to_gray(self, image):
        image = image.convert('L')
        return image


class VectorType(basetype):
    from numpy import array, concatenate

    def __init__(self, **kwargs):
        super(VectorType, self).__init__(**kwargs)

        self.attributes = {'shape': ['nestedlist', 'nestedarray', 'flatarray', 'flatlist'],
                           'length': [type(1)]
                           }

        self.conversions = {'shape': [('nestedlist', 'flatarray', self.convert_nestedlist_to_flatarray),
                                       ('nestedarray', 'flatarray', self.convert_nestedlist_to_flatarray)],
                            'length': []
                            }

    def convert_nestedlist_to_flatarray(self, lst):
        return concatenate(lst)



	
    

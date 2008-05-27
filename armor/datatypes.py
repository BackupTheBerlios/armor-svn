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

	compatible = True
        convert = True
	
        for key in toType:
            # If key is not present, we assume compatibility
            if key not in self.dataType:
                continue

            if toType[key] in self.dataType[key]:
                continue # Compatible

	    compatible = False

	if compatible:
	    return []

	# Can we convert?
        for conversion in self.conversions:
	    for key in conversion:
		if key == 'function':
		    continue
		for inType in self.dataType[key]:
		    if conversion[key][0] != toType[key] and conversion[key][1] != inType:
			convert = False
		    
		if convert:
		    return [conversion['function']]
		convert = True

	# No
	return False
            
        
class ImageType(basetype):
    from PIL import Image
    from numpy import array
    
    def __init__(self, **kwargs):
        super(ImageType, self).__init__(**kwargs)
        
        self.attributes = {'format': ['PIL', 'numpy'],
                          'color_space': ['gray', 'RGB']
                           }

        self.conversions = [{'format': ('PIL', 'PIL'),
			     'color_space': ('RGB', 'gray'),
			     'function': self.convert_PIL_RGB_to_PIL_gray},
			    {'format': ('PIL', 'numpy'),
			     'color_space': ('RGB', 'RGB'),
			     'function': self.convert_PIL_RGB_to_numpy_RGB},
			    {'format': ('PIL', 'numpy'),
			     'color_space': ('RGB', 'gray'),
			     'function': self.convert_PIL_RGB_to_numpy_gray}
			    ]
			    
    
    def convert_PIL_RGB_to_PIL_gray(self, image):
        image = image.convert('L')
        return image

    def convert_PIL_RGB_to_numpy_RGB(self, image):
	return array(image)

    def convert_PIL_RGB_to_numpy_gray(self, image):
	return array(self.convert_PIL_RGB_to_PIL_gray(image))

class VectorType(basetype):
    def __init__(self, **kwargs):
        super(VectorType, self).__init__(**kwargs)

        self.attributes = {'shape': ['nestedlist', 'nestedarray', 'flatarray', 'flatlist'],
                           'length': [type(1)]
                           }

        self.conversions = [{'shape': ('nestedlist', 'flatarray'),
			     'function': self.convert_nestedlist_to_flatarray},
			    {'shape': ('nestedarray', 'flatarray'),
			     'function': self.convert_nestedlist_to_flatarray}
			    ]

    def convert_nestedlist_to_flatarray(self, lst):
	from numpy import concatenate
        return concatenate(lst)



	
    

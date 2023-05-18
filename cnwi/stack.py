from typing import Union
import ee

from . import rf


class ImageStack(ee.Image):
    def __init__(self, *args):
        super().__init__(ee.Image.cat(args=args), None)
    
    def classifiy(self, model: Union[ee.Classifier, rf.RandomForestModel]) -> ee.Image:
        if isinstance(model, rf.RandomForestModel):
            pass
        else:
            clfd = self.classifiy(model).unit8()
        return clfd
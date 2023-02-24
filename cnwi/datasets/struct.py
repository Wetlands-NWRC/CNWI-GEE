from typing import Iterable, Union


import ee

class ImageList:
    def __init__(self, images: Iterable[Union[str, ee.Image]]) -> None:
        if not isinstance(images, list):
            self.imgs = list(images)
        else:
            self.imgs = images
    
    def __len__(self):
        return len(self.imgs)
    
    def __getitem__(self, value):
        return self.imgs[value]
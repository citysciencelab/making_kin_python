from enum import Enum
import numpy as np
import imageio
from PIL import Image, ImageOps

o = [
    {"a": 12},
    {"a": 13},
    {"a": 14},
    {"a": 15}
]

for e in o:
    if e["a"] == 13:
        print("found")
        break
    print(e["a"])

# im = imageio.imread("./data/jakarta_fake.png")
# im_2 = Image.open("./data/jakarta_fake.png")
# im_2 = im_2.convert("RGB")
# tuple = (128,128)
# print(np.array(im_2)[tuple])


class Bar(Enum):
    MEIN = "dum"
    ATTR = "dam"

for v in Bar:
    print(v)

# class SomeClass():
#     def __init__(self, someFunc=None, newProp = "foo") -> None:
#         # funcType = type(SomeClass.someFunc)
#         # self.someFunc = funcType(someFunc, self, SomeClass)
#         self.someFunc = someFunc.__get__(self, SomeClass)
#         setattr(self, "foo", 42)
#         setattr(self, Bar.ATTR.value, 42)

#     def someFunc(self):
#         pass

# def myFunc(self):
#     print("new func")

# instance = SomeClass(someFunc=myFunc)

# instance.someFunc()
# print(instance.foo)
# print(instance.dam)

# s = "some string with {} value".format(instance.dam)
# print(s)


from PIL import Image
from typing import Self, TypeAlias
from pyfunc.datafunc import tuple_max, tuple_min
import logging

l = logging.getLogger()

vec2:TypeAlias = tuple[int,int]

class gif_frame:
    def __init__(self, image:Image.Image | None=None) -> None:
        self.images: list[tuple[Image.Image, vec2]] = []
        if image is not None:
            self.addimage(image)
        
    def addimage(self, img:Image.Image, pos:vec2=(0,0)) -> None:
        self.images.append((img, pos))

    def addgifframe(self, img:Self, pos:vec2=(0,0)) -> None:
        for frame,(x,y) in img.images:
            self.addimage(frame, (x+pos[0],y+pos[1]))
    
    def exportframe(self) -> Image.Image:
        copy = Image.new("RGBA", (4096, 4096)) # i don't like hard limits # like what if someone makes a 100 block tall recipe? # what then?
        for i, pos in self.images:
            copy.alpha_composite(i, pos)
        copy = copy.crop(copy.getbbox())
        return copy
    
    def getsize(self) -> vec2:
        return tuple_max((0, 0),*[
            (im.width + x, im.height + y)
            for im,(x,y) in
            self.images
        ])

def copygifframe(f:gif_frame) -> gif_frame:
    f2 = gif_frame()
    f2.addgifframe(f)
    return f2

class gif:
    def __init__(self, defaultbg: tuple[int, int, int]):
        self.cursor = (0, 0)
        self.framelist: list[gif_frame] = []
        self.defaultbg: tuple[int, int, int] = defaultbg
    
    def addframe(self, image:Image.Image | None=None) -> None:
        self.framelist.append(gif_frame(image))
    
    def movecursor(self, x:int=0, y:int=0) -> None:
        self.cursor = (self.cursor[0] + x, self.cursor[1] + y)
    
    def setcursor(self, x:int | None=None, y:int | None=None) -> None:
        x = x if x is not None else self.cursor[0]
        y = y if y is not None else self.cursor[1]
        self.cursor = (x, y)
        
    def addgifframes(self, giflist:list[Image.Image], pos:vec2 | None=None, movecursor:bool=True) -> Self:
        pos = pos or self.cursor
        if len(self.framelist) == 0:
            self.addframe()
        # print(f"GIF adding img at pos {pos}")
        # but consider: loops of different lengths multiply to their LCM
        ogiflist=[*giflist]
        oframelist=[*self.framelist]
        while len(self.framelist) != len(giflist):
            print(len(self.framelist),len(giflist))
            if len(self.framelist) > len(giflist):
                l.debug("Adding giflist")
                giflist += [*ogiflist]
            elif len(self.framelist) < len(giflist):
                l.debug("Adding framelist")
                self.framelist += [copygifframe(f) for f in oframelist]

        maxdm = (0, 0)
        for gifframe, selfframe in zip(giflist, self.framelist):
            if selfframe is None: return
            selfframe.addimage(gifframe, pos)
            maxdm = tuple_max(maxdm, gifframe.size)
        if movecursor: self.movecursor(x=maxdm[0], y=maxdm[1])
        return self
        
    def addgif(self, newgif:Self, pos:vec2=(0, 0)) -> Self: # ignore the background of newgif
        print(f"GIF adding gif at pos {pos}")
        if len(self.framelist) == 0:
            self.addframe()
        giflist = newgif.framelist
        ogiflist=[*giflist]
        oframelist=[*self.framelist]
        while len(self.framelist) != len(giflist):
            print(len(self.framelist),len(giflist))
            if len(self.framelist) > len(giflist):
                l.debug("Adding giflist")
                giflist += [*ogiflist]
            elif len(self.framelist) < len(giflist):
                l.debug("Adding framelist")
                self.framelist += [copygifframe(f) for f in oframelist]
        for i in range(len(giflist)):
            gifframe, selfframe = newgif.framelist[i], self.framelist[i]
            if selfframe is None: return
            selfframe.addgifframe(gifframe, pos)
        return self
            
        
    def addimageframes(self, image:Image.Image, pos:vec2 | None=None, movecursor:bool=True) -> Self:
        pos = pos or self.cursor
        if len(self.framelist) == 0:
            self.addframe()
        for f in self.framelist:
            f.addimage(image, pos)
        # print(f"GIF adding img at pos {pos}")
        # for i in self.framelist:
        #     i.addimage(image, pos)
        if movecursor: self.movecursor(x=image.size[0], y=image.size[1])
        return self
    
    def export(self, pth:str="cache/exported.gif", duration:float=1000, apng:bool=False) -> None:
        framel = []
        for f in self.framelist:
            im = f.exportframe()
            bge = Image.new("RGBA", im.size, self.defaultbg)
            bge.alpha_composite(im)
            framel.append(bge)
        # for i,fi in enumerate(framel):
        #     fi.save(pth+f'-{i}.png', format="PNG")
        framel[0].save(pth, format="GIF", save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
        if apng:
            framel[0].save(pth.replace(".gif", ".apng"), save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
    
    def getsize(self) -> vec2:
        return tuple_max((0, 0),*[f.getsize() for f in self.framelist])

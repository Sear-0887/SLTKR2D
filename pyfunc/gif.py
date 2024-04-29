from PIL import Image
from pyfunc.datafunc import tuple_max, tuple_min
import logging

l = logging.getLogger()

class gif_frame:
    def __init__(self, image:Image.Image | None=None) -> None:
        self.images: list[tuple[Image.Image, tuple[int, int]]] = []
        self.addimage(image or Image.new("RGBA", (0, 0)))
        
    def addimage(self, img=None, pos=(0,0)):
        self.images.append((img, pos))
    
    def exportframe(self):
        copy = Image.new("RGBA", (4096, 4096))
        for i, pos in self.images:
            copy.alpha_composite(i, pos)
        copy = copy.crop(copy.getbbox())
        return copy

class gif:
    def __init__(self, defaultbg: tuple[int, int, int]):
        self.cursor = (0, 0)
        self.perimage = []
        self.framelist: list[gif_frame] = []
        self.defaultbg: tuple[int, int, int] = defaultbg
    
    def addframe(self, image=None):
        self.framelist.append(gif_frame(image))
    
    def movecursor(self, x=0, y=0):
        self.cursor = tuple(map(sum, zip(self.cursor, (x, y))))
    
    def setcursor(self, x=None, y=None):
        x = x if x is not None else self.cursor[0]
        y = y if y is not None else self.cursor[1]
        self.cursor = (x, y)
        
    def addgifframes(self, giflist, pos=None, movecursor=True):
        pos = pos or self.cursor
        if len(self.framelist) == 0:
            self.addframe()
        # print(f"GIF adding img at pos {pos}")
        ogiflist=giflist
        oframelist=self.framelist
        while len(self.framelist) != len(giflist):
            if len(self.framelist) > len(giflist):
                l.debug("Adding giflist")
                giflist += ogiflist
            elif len(self.framelist) < len(giflist):
                l.debug("Adding framelist")
                self.framelist += oframelist

        maxdm = (0, 0)
        for gifframe, selfframe in zip(giflist, self.framelist):
            if selfframe is None: return
            selfframe.addimage(gifframe, pos)
            maxdm = tuple_max(maxdm, gifframe.size)
        if movecursor: self.movecursor(x=maxdm[0], y=maxdm[1])
        return self
            
        
    def addimageframes(self, image, pos=None, movecursor=True):
        pos = pos or self.cursor
        if len(self.framelist) == 0:
            self.addframe()
        self.perimage.append((image, pos))
        # print(f"GIF adding img at pos {pos}")
        # for i in self.framelist:
        #     i.addimage(image, pos)
        if movecursor: self.movecursor(x=image.size[0], y=image.size[1])
        return self
    
    def export(self, pth="cache/exported.gif", duration=1000, apng=False):
        framel = []
        for f in self.framelist:
            for perim, pos in self.perimage:
                f.addimage(perim, pos)
            im = f.exportframe()
            bge = Image.new("RGBA", im.size, self.defaultbg)
            bge.alpha_composite(im)
            framel.append(bge)
        framel[0].save(pth, format="GIF", save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
        if apng:
            framel[0].save(pth.replace(".gif", ".apng"), save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
    
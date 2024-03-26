from PIL import Image, ImageSequence
from pyfunc.block import defaultblock

def tuple_max(*tuples) -> tuple[int]:
    rt = []
    _itr = zip(*tuples)
    for p in _itr:
        rt.append(max(p))
    return tuple(rt)

class gif_frame:
    def __init__(self, image=None, bg=None, dm=(0, 0)):
        self.Dimension = dm
        self.images: list[tuple[Image.Image, tuple[int, int]]] = []
        self.Background: tuple[int, int, int] = bg or (0, 0, 0)
        self.addimage(image or Image.new("RGBA", (0, 0), bg))
        
    def addimage(self, img=None, pos=(0,0)):
        self.Dimension = tuple_max(map(sum, zip(pos, img.size)), self.Dimension)
        img = img or Image.new("RGBA", self.Dimension, self.Background)
        self.images.append((img, pos))
        self.extendFrameDimension()
        return self
        
    def extendFrameDimension(self):
        for ind, frmdt in enumerate(self.images):
            i, pos = frmdt
            self.Dimension = tuple_max(map(sum, zip(pos, i.size)), self.Dimension)
            img = Image.new("RGBA", self.Dimension)
            img.alpha_composite(i)
            self.images[ind] = (img, pos)
            ...
    
    def exportframe(self):
        copy = Image.new("RGBA", self.Dimension, self.Background)
        for i, pos in self.images:
            copy.alpha_composite(i, pos)
        return copy

class gif:
    def __init__(self, defaultbg):
        self.Dimension = (0, 0)
        self.longestFrameLength = 0
        self.framelist: list[gif_frame] = []
        self.defaultbg: tuple[int, int, int] = defaultbg
    
    def addframe(self, image=None):
        image = image or Image.new("RGBA", self.Dimension)
        self.framelist.append(gif_frame(image, self.defaultbg, self.Dimension))
        for frm in self.framelist:
            frm.extendFrameDimension()
        ...
        
    def addgifframes(self, image, pos=(0, 0)):
        print(f"GIF adding img at pos {pos}")
        giflist = image
        if len(self.framelist) < len(giflist):
            for _ in range( len(giflist) - len(self.framelist) ):
                self.addframe()
        for i in range(len(giflist)):
            gifframe, selfframe = giflist[i], self.framelist[i]
            if selfframe is None: return
            selfframe.addimage(gifframe, pos)
        return self
            
    def addimageframes(self, image, pos=(0, 0)):
        print(f"GIF adding img at pos {pos}")
        for i in self.framelist:
            i.addimage(image, pos)
        return self
    def export(self, pth="cache/exported.gif", duration=1000):
        framel = [f.exportframe() for f in self.framelist]
        framel[0].save(pth, format="GIF", save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
            
    
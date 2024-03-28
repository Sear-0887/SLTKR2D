from PIL import Image

def tuple_max(*tuples) -> tuple[int]:
    return tuple(map(max, zip(*tuples)))
def tuple_min(*tuples) -> tuple[int]:
    return tuple(map(min, zip(*tuples)))

class gif_frame:
    def __init__(self, image=None):
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
    def __init__(self, defaultbg):
        self.framelist: list[gif_frame] = []
        self.defaultbg: tuple[int, int, int] = defaultbg
    
    def addframe(self, image=None):
        self.framelist.append(gif_frame(image))
        
    def addgifframes(self, giflist, pos=(0, 0)):
        print(f"GIF adding img at pos {pos}")
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
        framel = []
        for f in self.framelist:
            im = f.exportframe()
            bge = Image.new("RGBA", im.size, self.defaultbg)
            bge.alpha_composite(im)
            framel.append(bge)
        framel[0].save(pth, format="GIF", save_all=True, append_images=framel[1:], loop=0, disposal=2, duration=duration)
            
    
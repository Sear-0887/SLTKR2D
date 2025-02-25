from PIL import Image
from typing import Self, TypeAlias
from pyfunc.datafunc import tuple_max, tuple_min
import logging

l = logging.getLogger()

vec2: TypeAlias = tuple[int,int]

class GifFrame:
    imagesData: list[tuple[Image.Image, vec2]]
    def __init__(self, image: Image.Image | None = None) -> None:
        self.imagesData = []
        if image is not None:
            self.addImage(image)
        
    def addImage(self, image: Image.Image, pos: vec2 = (0, 0)) -> None:
        self.imagesData.append((image, pos))

    def addImagesFromFrame(self, frame: Self, start: vec2 = (0, 0)) -> None:
        for frame, (x, y) in frame.imagesData:
            self.addImage(frame, (x + start[0],y + start[1]))
    
    def export(self) -> Image.Image:
        base = Image.new("RGBA", (4096, 4096))
        for i, pos in self.imagesData:
            base.alpha_composite(i, pos)
        base = base.crop(base.getbbox())
        return base
    
    def getSize(self) -> vec2:
        return tuple_max((0, 0), *[
            (im.width + x, im.height + y)
            for im, (x,y) in
            self.imagesData
        ])

def copyGifFrame(f: GifFrame) -> GifFrame: # This will duplicate the frame
    copy = GifFrame()
    copy.addImagesFromFrame(f)
    return copy

class GIF:
    def __init__(self, defaultbg: tuple[int, int, int]):
        self.cursor = (0, 0)
        self.frames: list[GifFrame] = []
        self.defaultBG: tuple[int, int, int] = defaultbg
    
    def addFrameFromImage(self, image: Image.Image | None = None) -> None:
        self.frames.append(GifFrame(image))
    
    def moveCursor(self, x: int = 0, y: int = 0) -> None:
        self.cursor = (self.cursor[0] + x, self.cursor[1] + y)
    
    def setCursor(self, x:int | None=None, y:int | None=None) -> None:
        x = x if x is not None else self.cursor[0]
        y = y if y is not None else self.cursor[1]
        self.cursor = (x, y)
        
    def mergeImagesToFrames(self, images: list[Image.Image], pos: vec2 | None = None, moveCursor: bool = True) -> Self:
        pos = pos or self.cursor
        if len(self.frames) == 0:
            self.addFrameFromImage()
        # print(f"GIF adding img at pos {pos}")
        # but consider: loops of different lengths multiply to their LCM
        gifList_original = [*images]
        frameList_original = [*self.frames]
        
        # Expand images and self.frames to the length of lcm(len(images), len(self.frames))
        # Expanding only loops the original
        while len(self.frames) != len(images):
            print(len(self.frames), len(images))
            if len(self.frames) > len(images):
                l.debug("Adding giflist")
                images += gifList_original
            elif len(self.frames) < len(images):
                l.debug("Adding framelist")
                self.frames += [copyGifFrame(f) for f in frameList_original]

        maxSize = (0, 0)
        for image, selfFrame in zip(images, self.frames):
            if selfFrame is None: return
            selfFrame.addImage(image, pos)
            maxSize = tuple_max(maxSize, image.size)
        if moveCursor: self.moveCursor(x=maxSize[0], y=maxSize[1])
        return self
        
    def mergeTwoGif(self, newgif: Self, pos: vec2 = (0, 0)) -> Self: # ignore the background of newgif
        l.debug(f"GIF adding gif at pos {pos}")
        if len(self.frames) == 0:
            self.addFrameFromImage()

        gifList = newgif.frames
        gifList_original = [*gifList]
        frameList_original = [*self.frames]

        # Expand images and self.frames to the length of lcm(len(images), len(self.frames))
        # Expanding only loops the original
        while len(self.frames) != len(gifList):
            print(len(self.frames),len(gifList))
            if len(self.frames) > len(gifList):
                l.debug("Adding giflist")
                gifList += [*gifList_original]
            elif len(self.frames) < len(gifList):
                l.debug("Adding framelist")
                self.frames += [copyGifFrame(f) for f in frameList_original]
        for i in range(len(gifList)):
            gifFrame, selfFrame = newgif.frames[i], self.frames[i]
            if selfFrame is None: return
            selfFrame.addImagesFromFrame(gifFrame, pos)
        return self
            
        
    def addImageOnAllFrames(self, image: Image.Image, pos: vec2 | None = None, moveCursor:bool=True) -> Self:
        pos = pos or self.cursor
        if len(self.frames) == 0:
            self.addFrameFromImage()
        for f in self.frames:
            f.addImage(image, pos)
        # print(f"GIF adding img at pos {pos}")
        # for i in self.framelist:
        #     i.addimage(image, pos)
        if moveCursor: self.moveCursor(x=image.size[0], y=image.size[1])
        return self
    
    def export(self, pth: str = "cache/exported.gif", duration: float = 1000, apng: bool = False) -> None:
        exportedFrames = []
        for frame in self.frames:
            frameImage = frame.export()
            background = Image.new("RGBA", frameImage.size, self.defaultBG) # Potential Bug? Unsure
            background.alpha_composite(frameImage)
            exportedFrames.append(background)
        exportedFrames[0].save(pth, format="GIF", save_all=True, append_images=exportedFrames[1:], loop=0, disposal=2, duration=duration)
        if apng:
            exportedFrames[0].save(pth.replace(".gif", ".apng"), save_all=True, append_images=exportedFrames[1:], loop=0, disposal=2, duration=duration)
    
    def getSize(self) -> vec2:
        return tuple_max((0, 0), *[frame.getSize() for frame in self.frames])

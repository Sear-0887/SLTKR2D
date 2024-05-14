import PIL.Image, PIL.ImageChops
import logging
import pyfunc.smp as smp
import os
from pyfunc.lang import cfg
import functools
import collections
import re
import typing
import numpy as np
from pyfunc.assetload import blockinfos, assetinit

l = logging.getLogger()
assetinit()

rimlights:dict[int, np.ndarray] = {}

vec3:typing.TypeAlias = tuple[float, float, float]

def clamp(a:np.ndarray) -> np.ndarray:
	return np.fmin(np.fmax(a, 0.0), 1.0) # overflow error

def dot(normal:np.ndarray, light:vec3) -> np.ndarray:
	return np.einsum('ijk,k->ij',normal,light)

def diffuse(normal:np.ndarray, light:vec3) -> np.ndarray:
	return np.fmax(dot(normal, light), 0.0)

def quarter_rotate(v:vec3, r:int) -> vec3:
	match r:
		case 0:
			return v
		case 1:
			return (-v[1], v[0], v[2])
		case 2:
			return (-v[0], -v[1], v[2])
		case 3:
			return (v[1], -v[0], v[2])
	raise ValueError('bad rotate')

def calc_diffuse_ambient_light(lightdir:vec3, normal:np.ndarray) -> np.ndarray:
	# calculate diffuse light
	light_diffuse = diffuse(normal, lightdir)
	return light_diffuse * 0.5 + 0.5

def calc_highlights(lightdir:vec3, normal:np.ndarray, rimlight:np.ndarray) -> np.ndarray:
	lightdir2 = (lightdir[0], lightdir[1], 0)
	intensity:np.ndarray = dot(normal, lightdir2) # how much the normal faces toward the light
	s0,s1 = intensity.shape
	highlights = np.empty((s0,s1,3))
	for i in range(s0):
		for j in range(s1):
			pixel = rimlight[int(255 * clamp((intensity[i, j] + 1) / 2))]
			highlights[i, j] = tuple(c * 0.3 for c in pixel)
	return highlights

fullbright_lightdir = (-0.5, 1.0, 1.0)

def apply_normalmap(albedo:PIL.Image.Image, normal:PIL.Image.Image | None, rotation:int, block_id:int, flip:bool) -> PIL.Image.Image:
	# rotate the light so when the block is rotated back the light is in the right direction
	lightdir:vec3 = quarter_rotate(fullbright_lightdir, rotation);

	light:np.ndarray

	normal_array:np.ndarray

	if normal is None:
		s0,s1 = albedo.size
		normal_array = np.full((s0,s1,3),(0.5,0.5,0.5))
	else:
		normal_array = np.asarray(normal) / 255 * 2 - 1
		normal_array = normal_array / np.atleast_3d(np.linalg.norm(normal_array, axis = 2))
		normal_array = normal_array[:, :, :3]
		# shape (any, any, 3)

	if flip: # flip_uv_x
		normal_array[:, :, 0] = -normal_array[:, :, 0]

	normal_array[:, :, 1] = -normal_array[:, :, 1]

	light = calc_diffuse_ambient_light(lightdir, normal_array)
	light = np.array([light, light, light])
	light = np.moveaxis(light, 0, 2)
	light = clamp(light)
	light = light * 255
	light = light.astype('uint8')
	lightim:PIL.Image.Image = PIL.Image.fromarray(light)

	alpha:PIL.Image.Image = albedo.getchannel('A')
	color:PIL.Image.Image = albedo.convert('RGB')
	diffused:PIL.Image.Image = PIL.ImageChops.multiply(color, lightim)
	out:PIL.Image.Image
	out = diffused

	if block_id in rimlights:
		highlights:np.ndarray = calc_highlights(lightdir, normal_array, rimlights[block_id]);
		highlights = clamp(highlights)
		highlights = highlights * 255
		highlights = highlights.astype('uint8')
		highlightsim:PIL.Image.Image = PIL.Image.fromarray(highlights)
		out = PIL.ImageChops.add(out,highlightsim)
			
	out.putalpha(alpha)

	return out

#welded=top,left,bottom,right
#rotate= 0    1    2      3

class WeldSide(typing.TypedDict):
	weld:bool
	wire:bool
	platform:bool
	frame:bool

WeldSides: typing.TypeAlias = tuple[WeldSide,WeldSide,WeldSide,WeldSide]
WeldSideIn: typing.TypeAlias = WeldSide | bool
WeldSidesIn: typing.TypeAlias = tuple[WeldSideIn,WeldSideIn,WeldSideIn,WeldSideIn]

class ImageBit:
	im:PIL.Image.Image
	normal:PIL.Image.Image | None
	x:int
	y:int
	w:int
	h:int
	flip:bool
	rotation:int
	block_id:int

	def __init__(self,im:tuple[PIL.Image.Image,PIL.Image.Image | None] | typing.Self,x:int=0,y:int=0,w:int=16,h:int=16,block_id:int | None = None) -> None:
		# the dimensions of the part of the image to use
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		if isinstance(im,ImageBit):
			# gonna just assume x,y,w,h stays inside the image
			self.x += im.x
			self.y += im.y
			block_id = im.block_id
			im = im.im, im.normal
		if block_id is None:
			raise ValueError('no block id given/inherited')
		self.block_id = block_id
		self.im, self.normal = im
		# rotation
		self.flip = False # first
		self.rotation = 0 # second

	def rotate(self,r:int,flip:bool=False) -> None:
		if flip:
			self.rotation = -self.rotation % 4
			self.flip = not self.flip
		self.rotation += r

	def getim(self) -> PIL.Image.Image:
		albedo = self.im.crop((self.x, self.y, self.x + self.w, self.y + self.h))
		if self.normal is not None:
			normal = self.normal.crop((self.x, self.y, self.x + self.w, self.y + self.h))
		else:
			normal = None

		im = apply_normalmap(albedo, normal, self.rotation, self.block_id, self.flip)
		# i have to calculate the diffuse and "rimlight"
		# self.flip = flip_uv_x
		# self.rotate = either rotation or (3 - rotation)
		if self.flip:
			im = im.transpose(PIL.Image.FLIP_LEFT_RIGHT)
		match self.rotation:
			case 1:
				im = im.transpose(PIL.Image.ROTATE_270)
			case 2:
				im = im.transpose(PIL.Image.ROTATE_180)
			case 3:
				im = im.transpose(PIL.Image.ROTATE_90)
		return im

class Image:
	ims:list[tuple[tuple[float, float], ImageBit]] # centers

	def __init__(self) -> None:
		self.ims=[]

	def addimagebit(self, im:ImageBit, x:float=0, y:float=0) -> None:
		x += im.w / 2
		y += im.h / 2
		self.ims.append(((x, y), im))

	def addimage(self, im:typing.Self, x:float=0, y:float=0) -> None:
		for (ix, iy), oim in im.ims:
			self.ims.append(((ix + x, iy + y), oim))

	def rotate(self, r:int, flip:bool=False, center:tuple[int, int]=(8, 8)) -> None:
		x, y = center
		for i, ((ix, iy), im) in enumerate(self.ims):
			im.rotate(r, flip)
			dx = ix - x
			dy = iy - y
			dx, dy = rotatexy(dx, dy, r, flip)
			self.ims[i]=((x + dx, y + dy), self.ims[i][1])

	def getdims(self) -> tuple[int,int]:
		mx:float = 0
		my:float = 0
		for (x, y), im in self.ims:
			w, h = rotatexy(im.w, im.h, im.rotation, im.flip)
			mx = max(mx, x + w / 2)
			my = max(my, y + h / 2)
		return (int(mx),int(my))

	def genimage(self,w:int | None=None,h:int | None=None) -> PIL.Image.Image:
		defaultw, defaulth = self.getdims()
		if w is None:
			w = defaultw
		if h is None:
			h = defaulth
		out=PIL.Image.new('RGBA',(w,h),(0,0,0,0))
		for (x, y), im in self.ims:
			pim = im.getim()
			out.alpha_composite(pim, (int(x - pim.width / 2), int(y - pim.height / 2)))
		return out

class BlockData(typing.TypedDict):
	type:str
	rotate:typing.NotRequired[int]
	weld:typing.NotRequired[WeldSides]
	data:typing.NotRequired[str]
	offsetx:typing.NotRequired[int]
	offsety:typing.NotRequired[int]
	overlayoffsetx:typing.NotRequired[int]
	overlayoffsety:typing.NotRequired[int]
	sizex:typing.NotRequired[int]
	sizey:typing.NotRequired[int]

BlockDataIn: typing.TypeAlias = BlockData | str | tuple | list

class BlockDesc(typing.TypedDict):
	wired:bool
	datafilters:list[typing.Callable[[BlockData], BlockData]]
	layers:list[typing.Callable[[BlockData], Image]]

def rotatexy(x:float, y:float, r:int, flip:bool) -> tuple[float,float]:
	if flip:
		x = -x
	if r == 0:
		x, y =  x,  y
	if r == 1:
		x, y = -y,  x
	if r == 2:
		x, y = -x, -y
	if r == 3:
		x, y =  y, -x
	return x, y

blockpaths={}
pthblocktexture = cfg("localGame.texture.texturePathFile")
with open(pthblocktexture) as f:
	data=smp.getsmpvalue(f.read())
for name,texture in data.items():
	blockpaths[name] = texture
	if 'rimlight' in texture:
		rimlight = PIL.Image.open(os.path.join(cfg("localGame.texture.texturePathFolder"),blockpaths[name]['rimlight'])).convert('RGB')
		rimlight_array:np.ndarray = np.asarray(rimlight)[0]
		l.debug(f'{name} has a rimlight wth shape {rimlight_array.shape}')
		rimlights[blockinfos[name]['id']] = rimlight_array

@functools.cache
def getblockims(block:str) -> tuple[PIL.Image.Image,PIL.Image.Image | None]:
	try:
		normal = PIL.Image.open(os.path.join(cfg("localGame.texture.texturePathFolder"),blockpaths[block]['normal'])).convert('RGBA')
	except FileNotFoundError:
		normal = None
	return (
		PIL.Image.open(os.path.join(cfg("localGame.texture.texturePathFolder"),blockpaths[block]['albedo'])).convert('RGBA'),
		normal,
	)

def getblocksbyattr(attr:str) -> list[str]:
	return [b for b,data in blockinfos.items() if attr in data['attributes']]

def getblocksbynotattr(attr:str) -> list[str]:
	return [b for b,data in blockinfos.items() if attr not in data['attributes']]

# wire components on a wafer
wafertypes=[
	"accelerometer","capacitor","diode",
	"galvanometer","latch","matcher",
	"potentiometer","sensor","transistor",
	"cascade","counter"
]
# wafer components that have an output side
outputtypes=[
	"diode",
	"galvanometer","latch",
	"potentiometer","transistor",
	"cascade","counter"
]
# wire components on a frame
wiretypes=[
	"detector","port","toggler","trigger"
]
# all blocks that connect to wire
wiredtypes=getblocksbyattr("wire_connect")
# blocks that only face one direction
norotatetypes=getblocksbynotattr("rotatable")
# blocks that only face two directions
twowaytypes=getblocksbyattr("symmetrical")
frametypes=wiretypes+['frame','wire']

def iswelded(side:WeldSide) -> bool:
	return side['weld']

def iswired(side:WeldSide) -> bool:
	return side['wire']

def isframe(side:WeldSide) -> bool:
	return side['frame']

def platformx(side:WeldSide) -> int:
	if side['platform']:
		return 2
	return int(side['weld'])

def makeweldside(side:WeldSideIn) -> WeldSide:
	if isinstance(side,dict):
		return side
	return {'weld':side,'wire':False,'platform':False,'frame':False}

weldedside = makeweldside(True)
unweldedside = makeweldside(False)

def setplatformside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['platform']=True
	return side

def setframeside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['frame']=True
	return side

def setwireside(side:WeldSide,other:bool) -> WeldSide:
	if side['weld'] and other:
		side['wire']=True
	return side

def blockdesc() -> BlockDesc:
	return {
		'wired':False, # does this block connect to wires beside it?
		'datafilters':[], # change the block data (norotate)
		'layers':[] # the layers of the block (actuator/any wire component)
	}

def norotatefilter(data:BlockData) -> BlockData:
	data={**data}
	data['rotate']=0
	return data

def twowayfilter(data:BlockData) -> BlockData:
	data={**data}
	if data['rotate']==1:
		data['rotate']=3
	if data['rotate']==2:
		data['rotate']=0
	return data

@functools.cache
def _getblocktexture(block:str,offsetx:int,offsety:int,sizex:int,sizey:int) -> ImageBit:
	im1, im2 = getblockims(block)
	return ImageBit((im1,im2),offsetx,offsety,offsetx+sizex,offsety+sizey,blockinfos[block]['id'])

def getblocktexture(data:BlockData) -> ImageBit:
	block=data['type']
	offsetx=data.get('offsetx',0) or 0
	offsety=data.get('offsety',0) or 0
	sizex=data.get('sizex',32) or 32
	sizey=data.get('sizey',32) or 32
	return _getblocktexture(block,offsetx,offsety,sizex,sizey)

def drawblocktexture(image:ImageBit,weld:WeldSides) -> Image:
	top,left,bottom,right=weld
	im = Image()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			im.addimagebit(ImageBit(image,x+16*iswelded(xside),y+16*iswelded(yside),8,8),x,y)
	return im

def defaultblock(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture(data)
	welded=rotatewelded(welded,rotate)
	im=drawblocktexture(image,welded)
	im=rotateblockib(im,rotate)
	return im

def overlay(data:BlockData) -> Image:
	rotate=data['rotate']
	im=getblocktexture({
		**data,
		'offsetx':data.get('overlayoffsetx',0),
		'offsety':data.get('overlayoffsety',0),
		'sizex':16,
		'sizey':16,
	})
	im2 = Image()
	im2.addimagebit(ImageBit(im,0,0,16,16),0,0)
	im2=rotateoverlayib(im2,rotate)
	return im2

def wafer(data:BlockData) -> Image:
	return defaultblock({**data,'type':'wafer'})

def frame(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture({'type':'frame','sizex':64})
	top,left,bottom,right=rotatewelded(welded,rotate)
	im = Image()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			if isframe(xside) or isframe(yside):
				offset=32 # frames have different welding to each other
			else:
				offset=0
			im.addimagebit(ImageBit(image,x+offset+16*iswelded(xside),y+16*iswelded(yside),8,8),x,y)
	im=rotateblockib(im,rotate)
	return im

def wiretop(data:BlockData) -> Image:
	if data['type'] in outputtypes:
		welded=data['weld']
		rotate=data['rotate']
		top,_,_,_=rotatewelded(welded,rotate) # different texture by if the output is connected
		data={**data,'offsety':data.get('offsety',0)+16*iswired(top)}
	return overlay(data)

def wire(data:BlockData) -> Image:
	welded=data['weld']
	if 'data' in data:
		bdata=re.fullmatch('(?P<state>on|off)',data['data'])
		if bdata is None:
			raise ValueError('bad value format')
		offset=32 if bdata['state']=='on' else 0
	else:
		offset=0
	image=getblocktexture({'type':'wire','offsetx':offset})
	top,left,bottom,right=welded
	im = Image()
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			im.addimagebit(ImageBit(image,x+16*iswired(xside),y+16*iswired(yside),8,8),x,y)
	return im

def actuator(data:BlockData) -> Image:
	welded=data['weld']
	rotate=data['rotate']
	top,left,bottom,right=rotatewelded(welded,rotate)
	weld1=weldedside,left,bottom,right
	weld2=top,unweldedside,weldedside,unweldedside
	im1 = defaultblock({**data,'type':'actuator_base','weld':weld1,'rotate':0})
	im2 = defaultblock({**data,'type':'actuator_head','weld':weld2,'rotate':0})
	im = Image()
	im.addimage(im1,0,0)
	im.addimage(im2,0,0)
	im=rotateblockib(im,rotate)
	return im

def platform(data:BlockData) -> Image:
	_,left,_,right=data['weld']
	image=getblocktexture({**data,'sizex':48})
	y=0
	if left==0 and right==1 or left==1 and right==0 or left==0 and right==0:
		y=16
	im = Image()
	for x,xside in [(0,left),(8,right)]:
		im.addimagebit(ImageBit(image,x+16*platformx(xside),y,8,16),x,y)
	return im

def wirecomponent(data:BlockData) -> BlockData:
	if 'data' in data:
		typ=data['type']
		if typ in ["port","accelerometer","matcher","detector","toggler","trigger"]:
			# instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['state'] or 'off'
		elif typ=="capacitor":
			# non instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ in ["diode","galvanometer","latch","transistor"]:
			# column 1 off
			# column 2 on
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<outstate>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsetx']=16 if bdata['outstate']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ=="potentiometer": # the rest have a setting
			pass
		elif typ=="sensor":
			pass
		elif typ=="cascade":
			# delay, in, out
			bdata=re.fullmatch('(?P<delay>[1-7])(?P<instate>on|off)?(?P<state>on|off)',data['data'])
			if bdata is None:
				raise ValueError('bad value format')
			data['overlayoffsetx']=16*(2*(int(bdata['delay'])-1)+(bdata['state']=='on'))
	return data

def counterfilter(data:BlockData) -> BlockData:
	raise NotImplemented

def counter(data:BlockData) -> Image:
	raise NotImplemented

def wiresetting(data:BlockData) -> Image:
	raise NotImplemented

blocktypes:collections.defaultdict[str,BlockDesc]=collections.defaultdict(blockdesc)

for t in norotatetypes:
	blocktypes[t]['datafilters'].append(norotatefilter)

for t in twowaytypes:
	blocktypes[t]['datafilters'].append(twowayfilter)

for t in wiretypes+wafertypes+['wire','wire_board']:
	blocktypes[t]['wired']=True

for block in blockpaths:
	blocktypes[block]['layers']=[defaultblock]

if 'player_pilot_chair_controls' in blocktypes: # not a real block
	del blocktypes['player_pilot_chair_controls']

blocktypes['actuator']['layers']=[actuator]
blocktypes['platform']['layers']=[platform]

for t in wafertypes:
	blocktypes[t]['layers']=[wafer,wire,wiretop]
	blocktypes[t]['datafilters'].append(wirecomponent)

for t in wiretypes:
	blocktypes[t]['layers']=[frame,wire,wiretop]
	blocktypes[t]['datafilters'].append(wirecomponent)

for t in ["potentiometer","sensor"]:
	blocktypes[t]['layers']=[frame,wire,wiretop,wiresetting]

blocktypes['counter']['datafilters'].append(counterfilter)
blocktypes['counter']['layers']=[wafer,wire,counter]

blocktypes['wire_board']['layers']=[wafer,wire]
blocktypes['wire']['layers']=[frame,wire]
blocktypes['frame']['layers']=[frame]

# rotate an image of a block by rotate
def rotateblockib(im:Image,rotate:int) -> Image:
	if rotate==0:
		pass
	if rotate==3:
		im.rotate(1)
	if rotate==1:
		im.rotate(3,True)
	if rotate==2:
		im.rotate(2,True)
	return im

# rotate an overlay (like galvanometer) by rotate
def rotateoverlayib(im:Image,rotate:int) -> Image:
	if rotate==0:
		pass
	if rotate==3:
		im.rotate(1)
	if rotate==1:
		im.rotate(3)
	if rotate==2:
		im.rotate(2)
	return im

# rotate the welds so they are in the right place when rotated by rotateblock
def rotatewelded(welded:WeldSides,rotate:int) -> WeldSides:
	if rotate==0:
		return welded
	idxs:tuple[int,int,int,int]
	if rotate==3:
		idxs = (3, 0, 1, 2)
	elif rotate==1:
		idxs = (1, 0, 3, 2)
	elif rotate==2:
		idxs = (2, 1, 0, 3)
	else:
		raise ValueError(f'bad rotate {rotate}')
	return ( # mypy dumb
		welded[idxs[0]],
		welded[idxs[1]],
		welded[idxs[2]],
		welded[idxs[3]],
	)

# convert blocks into a standardized format
# for easy processing
def normalize(block:BlockDataIn) -> BlockData:
	weld:WeldSidesIn
	if block is None:
		typ = 'air'
		rotate = 0
		weld = (True,True,True,True)
	elif isinstance(block,str):
		typ = block
		rotate = 0
		weld = (True,True,True,True)
	elif isinstance(block,(tuple,list)):
		b = dict(zip(["type","rotate","weld"],block))
		typ = b.get('type') or 'air'
		rotate = b.get('rotate') or 0
		weld = b.get('weld') or (True,True,True,True)
	else:
		typ = block.get('type') or 'air'
		rotate = block.get('rotate') or 0
		weld = block.get('weld') or (True,True,True,True)
	weld2=tuple(makeweldside(w) for w in weld)
	assert len(weld2)==4
	typ = typ.lower()
	if typ == 'nic':
		typ = 'air'
	return {
		"type":typ,
		"rotate":rotate,
		"weld":weld2,
	}

# get a block from a grid
# if the coordinates are outside the grid, return air
def get(vss:list[list[BlockData]],xi:int,yi:int) -> BlockData:
	if xi<0 or yi<0 or yi>=len(vss):
		return normalize("air");
	vs=vss[yi]
	if(xi>=len(vs)):
		return normalize("air");
	return vs[xi]

bottomtypes=['cap','flower_magenta','flower_yellow','grass','motor','pedestal','spikes'] # Only Bottom
topbottomtypes=['actuator_head','wire_spool','telewall'] # Only Top / Bottom
sidestypes=['combiner','extractor','injector','platform'] # no Top / Bottom
notoptypes=['arc_furnace','beam_core','collector','creator','destroyer','dismantler','magnet','manipulator','mantler','teleportore','summonore']

# can this block weld on this side?
def canweld(side:str,block:BlockData) -> bool:
	sides = blockinfos[block['type']]['weldablesides']
	i={'top':0,'bottom':2,'left':1,'right':3}[side]+4-block['rotate']
	i=i%4
	return sides[i] and iswelded(block['weld'][{'top':0,'bottom':2,'left':1,'right':3}[side]])

# the main method
# blocks is a grid of blocks
# autoweld makes it weld all possible unspecified welds
# autoweld=False makes welds not autocorrect (for rendering roody structures)
def makeimage(blocks:list[list[BlockDataIn]],autoweld:bool=True) -> PIL.Image.Image:
	xsize=max(map(len,blocks))
	ysize=len(blocks)

	newblocks=[[normalize("air") for _ in range(xsize)] for _ in range(ysize)]
	for yi,line in enumerate(blocks):
		for xi,block in enumerate(line):
			block=normalize(block)
			newblocks[yi][xi]=block

	im=Image()
	for xi in range(xsize):
		for yi in range(ysize):
			block=get(newblocks,xi,yi)
			if block['type']=='air':
				continue
			if autoweld:
				weldright=canweld('right',block) and canweld('left',get(newblocks,xi+1,yi))
				weldleft=canweld('left',block) and canweld('right',get(newblocks,xi-1,yi))
				weldbottom=canweld('bottom',block) and canweld('top',get(newblocks,xi,yi+1))
				weldtop=canweld('top',block) and canweld('bottom',get(newblocks,xi,yi-1))
				block['weld']=(
					makeweldside(block['weld'][0] and weldtop),
					makeweldside(block['weld'][1] and weldleft),
					makeweldside(block['weld'][2] and weldbottom),
					makeweldside(block['weld'][3] and weldright),
				)
			if block['type']=='platform': # special case
				# check if sides are platform
				block['weld']=(
					block['weld'][0],
					setplatformside(block['weld'][1],get(newblocks,xi-1,yi)['type']!='platform'),
					block['weld'][2],
					setplatformside(block['weld'][3],get(newblocks,xi+1,yi)['type']!='platform'),
				)
			if block['type'] in frametypes: # special case
				# check if sides are frame base
				block['weld']=(
					setframeside(block['weld'][0],get(newblocks,xi,yi-1)['type'] in frametypes),
					setframeside(block['weld'][1],get(newblocks,xi-1,yi)['type'] in frametypes),
					setframeside(block['weld'][2],get(newblocks,xi,yi+1)['type'] in frametypes),
					setframeside(block['weld'][3],get(newblocks,xi+1,yi)['type'] in frametypes),
				)
			blocktype=blocktypes[block['type']]
			if blocktype['wired']:
				# check if sides are wired
				block['weld']=(
					setwireside(block['weld'][0],get(newblocks,xi,yi-1)['type'] in wiredtypes),
					setwireside(block['weld'][1],get(newblocks,xi-1,yi)['type'] in wiredtypes),
					setwireside(block['weld'][2],get(newblocks,xi,yi+1)['type'] in wiredtypes),
					setwireside(block['weld'][3],get(newblocks,xi+1,yi)['type'] in wiredtypes),
				)
			for datafilter in blocktype['datafilters']:
				block=datafilter(block)
			for layer in blocktype['layers']:
				bim = layer(block)
				im.addimage(bim,xi*16,yi*16) # paste the block
	return im.genimage(xsize * 16,ysize * 16)
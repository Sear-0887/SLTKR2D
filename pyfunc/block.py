import PIL.Image
import pyfunc.smp as smp
import os
from pyfunc.lang import cfg
import functools
import collections
import re

#welded=top,left,bottom,right
#rotate= 0    1    2      3

class ImageBit:
	def __init__(self,im,x=0,y=0,w=16,h=16):
		self.im = im
		# the dimensions of the part of the image to use
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		# rotation
		self.flip = False # first
		self.rotate = 0 # second

	def rotate(self,r,flip=False):
		if flip:
			self.rotate = -self.rotate % 4
			self.flip = not self.flip
		self.rotate += r

class Image:
	ims:list[tuple[tuple[float, float], ImageBit]] # centers

	def __init__(self):
		self.ims=[]

	def addimagebit(self, im:ImageBit, x=0, y=0):
		x += im.w / 2
		y += im.h / 2
		ims.append(((x, y), im))

	def addimage(self, im:"Image", x=0, y=0):
		for (ix, iy), im in im.ims:
			ims.append(((ix + x, iy + y), im))

	def rotate(self, r, flip=False):
		for i, ((x, y), im) in enumerate(self.ims):
			im.rotate(r, flip)
			if r == 0:
				x, y =  x,  y
			if r == 1:
				x, y = -y,  x
			if r == 2:
				x, y = -x, -y
			if r == 3:
				x, y =  y, -x
			self.ims[i][0]=x, y

blockpaths={}
pthblocktexture = cfg("localGame.texture.texturePathFile")
with open(pthblocktexture) as f:
  data=smp.getsmpvalue(f.read())
for name,texture in data.items():
  blockpaths[name] = texture

@functools.cache
def getblockim(block):
	return PIL.Image.open(os.path.join(cfg("localGame.texture.texturePathFolder"),blockpaths[block])).convert('RGBA')

def getblockdata(data):
	return {'data':data}

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
wiredtypes=[
	'actuator','motor','telewall','injector','pedestal',
	'actuator_base','display',"lamp",'combiner',
	'arc_furnace','extractor','beam_core','creator',
	'destroyer','dismantler','magnet','manipulator',
	'mantler','wire','wire_board'
]+wafertypes+wiretypes
# unweldable blocks
noweldtypes=[
	"copper_ore","iron_ore","pulp","sand","silicon","spawner","air","sawdust"
]
# blocks that only face one direction
norotatetypes=[
	'pedestal','dirt','sediment','stone','rubber',
	'leaf_maple','iron_vein','iron_bar','iron_plate',
	'cast_iron','copper_vein','copper_bar','frame',
	'toggler','capacitor','inductor','roller',
	'dynamic_roller','chair','chair_pilot','display',
	'core_ore','raw_core','mass_core','refined_core',
	'catalyst_core','command_block','boundary',
	'spawner','calcium_bar','water','foam','oxide',
	'soul_core','adobe','peltmellow','glass',
	'glass_cyan','glass_magenta','glass_yellow',
	'grass','flower_magenta','flower_yellow','residue',
	'ice','compressed_stone','wafer'
]+noweldtypes
noweldtypes.append('telecross') # literally the only rotatable but unweldable block
# blocks that only face two directions
twowaytypes=[
	"wire_spool",'log_maple','log_pine',"mirror"
]
frametypes=wiretypes+['frame','wire']

def iswelded(side):
	if isinstance(side,bool):
		return side
	return side['weld']

def iswired(side):
	return side['wire']

def isframe(side):
	return side['frame']

def platformx(side):
	if side['platform']:
		return 2
	return int(side['weld'])

def makeweldside(side):
	return {'weld':side,'wire':False,'platform':False,'frame':False,'id':id(side)}

def setplatformside(side,other):
	if side['weld'] and other:
		side['platform']=True
	return side

def setframeside(side,other):
	if side['weld'] and other:
		side['frame']=True
	return side

def setwireside(side,other):
	if side['weld'] and other:
		side['wire']=True
	return side

def blockdesc():
	return {
		'wired':False, # does this block connect to wires beside it?
		'datafilters':[], # change the block data (noweld/norotate)
		'layers':[] # the layers of the block (actuator/any wire component)
	}

def noweldfilter(data):
	data={**data}
	data['weld']=[False,False,False,False]
	return data

def norotatefilter(data):
	data={**data}
	data['rotate']=0
	return data

def twowayfilter(data):
	data={**data}
	if data['rotate']==1:
		data['rotate']=3
	if data['rotate']==2:
		data['rotate']=0
	return data

@functools.cache
def _getblocktexture(block,offsetx,offsety,sizex,sizey):
	return getblockim(block).crop((offsetx,offsety,offsetx+sizex,offsety+sizey)).convert('RGBA')

def getblocktexture(data):
	block=data['type']
	offsetx=data.get('offsetx',0)
	offsety=data.get('offsety',0)
	sizex=data.get('sizex',32)
	sizey=data.get('sizey',32)
	return _getblocktexture(block,offsetx,offsety,sizex,sizey)

def drawblocktexture(image,weld):
	top,left,bottom,right=weld
	im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			im.alpha_composite(image.crop((x+16*iswelded(xside),y+16*iswelded(yside),x+16*iswelded(xside)+8,y+16*iswelded(yside)+8)),(x,y))
	return im

def defaultblock(data):
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture(data)
	welded=rotatewelded(welded,rotate)
	im=drawblocktexture(image,welded)
	im=rotateblock(im,rotate)
	return im

def overlay(data):
	rotate=data['rotate']
	image=getblocktexture({
		**data,
		'offsetx':data.get('overlayoffsetx',0),
		'offsety':data.get('overlayoffsety',0),
		'sizex':16,
		'sizey':16
	})
	im=rotateoverlay(image,rotate)
	return im

def wafer(data):
	return defaultblock({**data,'type':'wafer'})

def frame(data):
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture({'type':'frame','sizex':64})
	top,left,bottom,right=rotatewelded(welded,rotate)
	im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			if isframe(xside) or isframe(yside):
				offset=32 # frames have different welding to each other
			else:
				offset=0
			im.alpha_composite(image.crop((x+offset+16*iswelded(xside),y+16*iswelded(yside),x+offset+16*iswelded(xside)+8,y+16*iswelded(yside)+8)),(x,y))
	im=rotateblock(im,rotate)
	return im

def wiretop(data):
	if data['type'] in outputtypes:
		welded=data['weld']
		rotate=data['rotate']
		top,_,_,_=rotatewelded(welded,rotate) # different texture by if the output is connected
		data={**data,'offsety':data.get('offsety',0)+16*iswired(top)}
	return overlay(data)

def wire(data):
	welded=data['weld']
	if data['data'] is not None:
		bdata=re.fullmatch('(?P<state>on|off)',data['data']).groupdict()
		offset=32 if bdata['state']=='on' else 0
	else:
		offset=0
	image=getblocktexture({'type':'wire','offsetx':offset})
	top,left,bottom,right=welded
	im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			im.alpha_composite(image.crop((x+16*iswired(xside),y+16*iswired(yside),x+16*iswired(xside)+8,y+16*iswired(yside)+8)),(x,y))
	return im

def actuator(data):
	welded=data['weld']
	rotate=data['rotate']
	im1=getblocktexture({'type':'actuator_base'})
	im2=getblocktexture({'type':'actuator_head'})
	top,left,bottom,right=rotatewelded(welded,rotate)
	weld1=True,left,bottom,right
	weld2=top,False,True,False
	im=drawblocktexture(im1,weld1)
	im.alpha_composite(drawblocktexture(im2,weld2),(0,0))
	im=rotateblock(im,rotate)
	return im

def platform(data):
	_,left,_,right=data['weld']
	im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
	image=getblocktexture({**data,'sizex':48})
	y=0
	if left==0 and right==1 or left==1 and right==0 or left==0 and right==0:
		y=16
	for x,xside in [(0,left),(8,right)]:
		im.alpha_composite(image.crop((x+16*platformx(xside),y,x+16*platformx(xside)+8,y+16)),(x,0))
	return im

def wirecomponent(data):
	if data['data'] is not None:
		typ=data['type']
		if typ in ["port","accelerometer","matcher","detector","toggler","trigger"]:
			# instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<state>on|off)',data['data']).groupdict()
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['state'] or 'off'
		elif typ=="capacitor":
			# non instantaneous
			# top off bottom on texture
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<state>on|off)',data['data']).groupdict()
			data['overlayoffsety']=16 if bdata['state']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ in ["diode","galvanometer","latch","transistor"]:
			# column 1 off
			# column 2 on
			bdata=re.fullmatch('(?P<instate>on|off)?(?P<outstate>on|off)',data['data']).groupdict()
			data['overlayoffsetx']=16 if bdata['outstate']=='on' else 0
			data['data']=bdata['instate'] or 'off'
		elif typ=="potentiometer": # the rest have a setting
			pass
		elif typ=="sensor":
			pass
		elif typ=="cascade":
			# delay, in, out
			bdata=re.fullmatch('(?P<delay>[1-7])(?P<instate>on|off)?(?P<state>on|off)',data['data']).groupdict()
			data['overlayoffsetx']=16*(2*(int(bdata['delay'])-1)+(bdata['state']=='on'))
	return data

def counterfilter(data):
	pass

def counter(data):
	pass

def wiresetting(data):
	pass

blocktypes=collections.defaultdict(blockdesc)

for t in noweldtypes:
	blocktypes[t]['datafilters'].append(noweldfilter)

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
	blocktypes[t]['datafilters']=[wirecomponent]

for t in wiretypes:
	blocktypes[t]['layers']=[frame,wire,wiretop]
	blocktypes[t]['datafilters']=[wirecomponent]

for t in ["potentiometer","sensor"]:
	blocktypes[t]['layers']=[frame,wire,wiretop,wiresetting]

blocktypes[t]['datafilters']=[counterfilter]
blocktypes['counter']['layers']=[wafer,wire,counter]

blocktypes['wire_board']['layers']=[wafer,wire]
blocktypes['wire']['layers']=[frame,wire]
blocktypes['frame']['layers']=[frame]

# rotate an image of a block by rotate
def rotateblock(im,rotate):
	if rotate==0:
		return im
	if rotate==3:
		return im.transpose(PIL.Image.ROTATE_270)
	if rotate==1:
		return im.transpose(PIL.Image.TRANSPOSE)
	if rotate==2:
		return im.transpose(PIL.Image.FLIP_TOP_BOTTOM)

# rotate an overlay (like galvanometer) by rotate
def rotateoverlay(im,rotate):
	if rotate==0:
		return im
	if rotate==3:
		return im.transpose(PIL.Image.ROTATE_270)
	if rotate==1:
		return im.transpose(PIL.Image.ROTATE_90)
	if rotate==2:
		return im.transpose(PIL.Image.ROTATE_180)

# rotate the welds so they are in the right place when rotated by rotateblock
def rotatewelded(welded,rotate):
	if rotate==0:
		return welded
	if rotate==3:
		return [welded[i] for i in [3,0,1,2]]
	if rotate==1:
		return [welded[i] for i in [1,0,3,2]]
	if rotate==2:
		return [welded[i] for i in [2,1,0,3]]

# convert blocks into a standardized format
# for easy processing
def normalize(block):
	if block is None:
		return {"type":'air',"rotate":0,"weld":'all'}
	if type(block)==str:
		return {"type":block,"rotate":0,"weld":"all"}
	if type(block) in [tuple,list]:
		out={"type":'air',"rotate":0,"weld":'all'}
		out.update(dict(zip(["type","rotate","weld"],block)))
		return out
	out={"type":'air',"rotate":0,"weld":'all'}
	out.update(block)
	return out

# get a block from a grid
# if the coordinates are outside the grid, return air
def get(vss,xi,yi):
	if xi<0 or yi<0 or yi>=len(vss):
		return normalize("air");
	vs=vss[yi]
	if(xi>=len(vs)):
		return normalize("air");
	return vs[xi]

# can this block weld on this side?
def canweld(side,block):
	if block['type'] in noweldtypes:
		return False
	elif block['type'] in ['cap','flower_magenta','flower_yellow','grass','motor','pedestal','spikes']: # Only Bottom
		sides=[False,False,True,False]
	elif block['type'] in ['actuator_head','wire_spool','telewall']: # Only Top / Bottom
		sides=[True,False,True,False]
	elif block['type'] in ['combiner','extractor','injector','platform']: # no Top / Bottom
		sides=[False,True,False,True]
	elif block['type'] in ['arc_furnace','beam_core','collector','creator','destroyer','dismantler','magnet','manipulator','mantler','teleportore','summonore']: 
		sides=[False,True,True,True]
	else:
		sides=[True,True,True,True]
	i={'top':0,'bottom':2,'left':1,'right':3}[side]+4-block['rotate']
	i=i%4
	return sides[i] and iswelded(block['weld'][{'top':0,'bottom':2,'left':1,'right':3}[side]])

# the main method
# blocks is a grid of blocks
# autoweld makes it weld all possible unspecified welds
# autoweld=False makes welds not autocorrect (for rendering roody structures)
def makeimage(blocks,autoweld=True):
	xsize=max(map(len,blocks))
	ysize=len(blocks)

	newblocks=[[normalize("air") for _ in range(xsize)] for _ in range(ysize)]
	for yi,line in enumerate(blocks):
		for xi,block in enumerate(line):
			block=normalize(block)
			newblocks[yi][xi]=block

	im=PIL.Image.new('RGBA',(16*xsize,16*ysize),(0,0,0,0))
	for xi in range(xsize):
		for yi in range(ysize):
			block=get(newblocks,xi,yi)
			if block['type']=='air':
				continue
			if block['weld']=='all':
				block['weld']=[True,True,True,True]
			if autoweld:
				weldright=canweld('right',block) and canweld('left',get(newblocks,xi+1,yi))
				weldleft=canweld('left',block) and canweld('right',get(newblocks,xi-1,yi))
				weldbottom=canweld('bottom',block) and canweld('top',get(newblocks,xi,yi+1))
				weldtop=canweld('top',block) and canweld('bottom',get(newblocks,xi,yi-1))
				block['weld']=[
					b and w for b,w in
					zip(
						block['weld'],
						[weldtop,weldleft,weldbottom,weldright]
					)
				]
				for i,b,w in zip(
					range(4),
					block['weld'],
					[weldtop,weldleft,weldbottom,weldright]
				):
					print(f'welded side {i} not allowed on {block}\n'*(not w and b),end='')
			block['weld']=[makeweldside(w) for w in block['weld']]
			if block['type']=='platform': # special case
				# check if sides are platform
				block['weld'][1]=setplatformside(block['weld'][1],get(newblocks,xi-1,yi)['type']!='platform')
				block['weld'][3]=setplatformside(block['weld'][3],get(newblocks,xi+1,yi)['type']!='platform')
			if block['type'] in frametypes: # special case
				# check if sides are frame base
				block['weld'][0]=setframeside(block['weld'][0],get(newblocks,xi,yi-1)['type'] in frametypes)
				block['weld'][1]=setframeside(block['weld'][1],get(newblocks,xi-1,yi)['type'] in frametypes)
				block['weld'][2]=setframeside(block['weld'][2],get(newblocks,xi,yi+1)['type'] in frametypes)
				block['weld'][3]=setframeside(block['weld'][3],get(newblocks,xi+1,yi)['type'] in frametypes)
			blocktype=blocktypes[block['type']]
			if blocktype['wired']:
				# check if sides are wired
				block['weld'][0]=setwireside(block['weld'][0],get(newblocks,xi,yi-1)['type'] in wiredtypes)
				block['weld'][1]=setwireside(block['weld'][1],get(newblocks,xi-1,yi)['type'] in wiredtypes)
				block['weld'][2]=setwireside(block['weld'][2],get(newblocks,xi,yi+1)['type'] in wiredtypes)
				block['weld'][3]=setwireside(block['weld'][3],get(newblocks,xi+1,yi)['type'] in wiredtypes)
			for datafilter in blocktype['datafilters']:
				block=datafilter(block)
			for layer in blocktype['layers']:
				im.alpha_composite(layer(block),(xi*16,yi*16)) # paste the block
	return im
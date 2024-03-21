import PIL.Image
import pyfunc.smp as smp
import os
from pyfunc.lang import cfg
import functools
import collections

#welded=top,left,bottom,right
#rotate= 0    1    2      3

bsize=128

blockpaths={}
pthblocktexture = cfg("localGame.texture.texturePathFile")
with open(pthblocktexture) as f:
  data=smp.getsmpvalue(f.read())
for name,texture in data.items():
  blockpaths[name] = texture

@functools.cache
def getblockim(block):
	return PIL.Image.open(os.path.join(cfg("localGame.texture.texturePathFolder"),blockpaths[block]))

def getblockdata(data):
	return {'data':data}

# https://stackoverflow.com/a/13054570
class Block:
	# a class that i'm mot sure i need
	# maybe replace with functions?
	# has a draw(welds,direction) method
	# with all the special cases, i'm not sure classes is easier
	cache = []

	@classmethod
	def __getCache(cls, key):
		for k,v in cls.cache:
			if k==key:
				return v
		return None
	def __new__(cls, *args, **kwargs):
		existing = cls.__getCache([args,kwargs])
		if existing is not None:
			return existing
		block = super(Block, cls).__new__(cls)
		cls.cache.append([[str(cls),args,kwargs],block])
		return block

# wire components on a wafer
wafertypes=[
	"accelerometer","capacitor","diode",
	"galvanometer","latch","matcher",
	"potentiometer","sensor","transistor","wire_board"
]
# wire components on a frame
wiretypes=[
	"detector","port","toggler","trigger","wire"
]
# all blocks that connect to wire
wiredtypes=[
	'actuator','motor','telewall','injector','pedestal',
	'actuator_base','display',"lamp",'combiner',
	'arc_furnace','extractor','beam_core','creator',
	'destroyer','dismantler','magnet','manipulator',
	'mantler'
]+wafertypes+wiretypes
# unweldable blocks
noweldtypes=[
	"copper_ore","iron_ore","pulp","sand","silicon","spawner","air"
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
	'ice','compressed_stone'
]+noweldtypes
noweldtypes.append('telecross') # literally the only rotatable but unweldable block
# blocks that only face two directions
twowaytypes=[
	"wire_spool",'log_maple','log_pine',"mirror"
]

def blockdesc():
	return {
		'wired':False, # does this block connect to wires beside it?
		'platform':False, # does this block detect platforms beside it?
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

def getblocktexture(data):
	block=data['type']
	offsetx=data.get('offsetx',0)
	offsety=data.get('offsety',0)
	return getblockim(block).crop((offsetx,offsety,offsetx+32,offsety+32)).convert('RGBA')

def defaultblock(data):
	welded=data['weld']
	rotate=data['rotate']
	image=getblocktexture(data)
	top,left,bottom,right=rotatewelded(welded,rotate)
	im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
	for x,xside in [(0,left),(8,right)]:
		for y,yside in [(0,top),(8,bottom)]:
			im.alpha_composite(image.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
	im=rotateblock(im,rotate)
	return im.resize((bsize,bsize),PIL.Image.NEAREST)

def wafer(data):
	return defaultblock({'type':'wafer'})

def wire(data):
	return defaultblock({'type':'wire'})

def wiretop(data):
	pass

def actuatorhead(data):
	pass

def actuatorbase(data):
	pass

blocktypes=collections.defaultdict(blockdesc)

for t in noweldtypes:
	blocktypes[t]['datafilters'].append(noweldfilter)

for t in norotatetypes:
	blocktypes[t]['datafilters'].append(norotatefilter)

for t in twowaytypes:
	blocktypes[t]['datafilters'].append(twowayfilter)

for t in wiretypes:
	blocktypes[t]['wired']=True

for block in blockpaths:
	blocktypes[block]['layers']=[defaultblock]

blocktypes['actuator']['layers']=[actuatorhead,actuatorbase]

for t in wafertypes:
	blocktypes[t]['layers']=[wafer,wiretop]

for t in wiretypes:
	blocktypes[t]['layers']=[wire,wiretop]

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

# mirror and wood
# 2 rotations instead of 4
class TwoSideBlock(Block):
	def __init__(self,block,offset=0):
		self.image=getblockim(block).crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,rotate=0):
		if rotate==1:
			rotate=3
		if rotate==2:
			rotate=0
		top,left,bottom,right=rotatewelded(welded,rotate)
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.image.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		im=rotateblock(im,rotate)
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# sand
# unweldable
class NoWeldBlock(Block):
	def __init__(self,block):
		self.image=getblockim(block).crop((0,0,16,16)).convert('RGBA')

	def draw(self,_,__=0):
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		im.alpha_composite(self.image.crop((0,0,16,16)))
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# literally just telecross
class TelecrossBlock(Block):
	def __init__(self):
		self.image=getblockim('telecross').crop((0,0,16,16)).convert('RGBA')

	def draw(self,_,rotate=0):
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		im.alpha_composite(self.image.crop((0,0,16,16)))
		im=rotateblock(im,rotate)
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# all wire components (transistor, latch, etc)
class WaferBlock(Block):
	def __init__(self,top,base='wafer',offset=0):
		self.wafer=getblockim(base).crop((0,0,32,32)).convert('RGBA')
		self.wire=getblockim('wire').crop((offset,0,offset+32,32)).convert('RGBA')
		self.image=getblockim(top).crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,rotate=0,offset=(0,0)):
		top,left,bottom,right=welded
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.wafer.crop((x+16*(xside>0),y+16*(yside>0),x+16*(xside>0)+8,y+16*(yside>0)+8)),(x,y))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.wire.crop((x+16*(xside//2+offset[0]),y+16*(yside//2+offset[1]),x+16*(xside//2+offset[0])+8,y+16*(yside//2+offset[1])+8)),(x,y))
		im.alpha_composite(self.image.crop((16*offset[0],16*offset[1],16*(offset[0]+1),16*(offset[1]+1))).rotate(90*rotate))
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# wire board and wire
class WireBlock(Block):
	def __init__(self,base,offset=0):
		self.wafer=getblockim(base).crop((0,0,32,32)).convert('RGBA')
		self.image=getblockim('wire').crop((offset,0,offset+32,32)).convert('RGBA')

	def draw(self,welded,_=0,offset=(0,0)):
		top,left,bottom,right=welded
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.wafer.crop((x+16*(xside>0),y+16*(yside>0),x+16*(xside>0)+8,y+16*(yside>0)+8)),(x,y))
		for x,xside in [(0,left),(8,right)]:
			for y,yside in [(0,top),(8,bottom)]:
				im.alpha_composite(self.image.crop((x+16*(xside//2+offset[0]),y+16*(yside//2+offset[1]),x+16*(xside//2+offset[0])+8,y+16*(yside//2+offset[1])+8)),(x,y))
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# platform
class PlatformBlock(Block):
	def __init__(self):
		self.image=getblockim('platform').convert('RGBA')

	def draw(self,welded,_,offset=(0,0)):
		_,left,_,right=welded
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		y=0
		if left==0 and right==1 or left==1 and right==0 or left==0 and right==0:
			y=16
		for x,xside in [(0,left),(8,right)]:
			im.alpha_composite(self.image.crop((x+16*xside,y,x+16*xside+8,y+16)),(x,0))
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

# actuator
class ActuatorBlock(Block):
	def __init__(self,offset=0):
		self.base=getblockim('actuator_base').crop((0,0,32,32)).convert('RGBA')
		self.head=getblockim('actuator_head').crop((0,0,32,32)).convert('RGBA')

	def draw(self,welded,rotate=0):
		headtop,baseleft,basebottom,baseright=rotatewelded(welded,rotate)
		basetop,headleft,headbottom,headright=[True,False,True,False]
		im=PIL.Image.new('RGBA',(16,16),(0,0,0,0))
		for x,xside in [(0,headleft),(8,headright)]:
			for y,yside in [(0,headtop),(8,headbottom)]:
				im.alpha_composite(self.head.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		for x,xside in [(0,baseleft),(8,baseright)]:
			for y,yside in [(0,basetop),(8,basebottom)]:
				im.alpha_composite(self.base.crop((x+16*xside,y+16*yside,x+16*xside+8,y+16*yside+8)),(x,y))
		im=rotateblock(im,rotate)
		return im.resize((bsize,bsize),PIL.Image.NEAREST)

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
	elif block['type'] in ['cap','flower_magenta','flower_yellow','grass','motor','pedestal','spikes']:
		sides=[False,False,True,False]
	elif block['type'] in ['actuator_head','wire_spool','telewall']:# no sides
		sides=[True,False,True,False]
	elif block['type'] in ['combiner','extractor','injector','platform']: # no top/bottom
		sides=[False,True,False,True]
	elif block['type'] in ['arc_furnace','beam_core','collector','creator','destroyer','dismantler','magnet','manipulator','mantler','teleportore']: # no top
		sides=[False,True,True,True]
	else:
		sides=[True,True,True,True]
	i={'top':0,'bottom':2,'left':1,'right':3}[side]+4-block['rotate']
	i=i%4
	return sides[i] and block['weld'][{'top':0,'bottom':2,'left':1,'right':3}[side]]

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

	im=PIL.Image.new('RGBA',(bsize*xsize,bsize*ysize),(0,0,0,0))
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
					'''
			if block['type']=='wire':
				b=WireBlock('frame')
			elif block['type']=='wire_board':
				b=WireBlock('wafer')
			elif block['type'] in wafertypes:
				b=WaferBlock(block['type'])
			elif block['type'] in wiretypes:
				b=WaferBlock(block['type'],'frame')
			elif block['type'] in twowaytypes:
				b=TwoSideBlock(block['type'])
			elif block['type'] in norotatetypes:
				b=NoRotateBlock(block['type'])
			elif block['type'] in noweldtypes:
				b=NoWeldBlock(block['type'])
			elif block['type']=='platform': # special case
				# check if sides are platform
				block['weld'][1]=block['weld'][1] and (2 if get(newblocks,xi-1,yi)['type']!='platform' else True)
				block['weld'][3]=block['weld'][3] and (2 if get(newblocks,xi+1,yi)['type']!='platform' else True)
				b=PlatformBlock()
			elif block['type']=='actuator':
				b=ActuatorBlock()
			elif block['type']=='telecross':
				b=TelecrossBlock()
			else:
				b=NormalBlock(block['type'])
			if block['type'] in wiretypes+wafertypes:
				# check if sides are wired
				block['weld'][0]=block['weld'][0] and (2 if get(newblocks,xi,yi-1)['type'] in wiredtypes else True)
				block['weld'][1]=block['weld'][1] and (2 if get(newblocks,xi-1,yi)['type'] in wiredtypes else True)
				block['weld'][2]=block['weld'][2] and (2 if get(newblocks,xi,yi+1)['type'] in wiredtypes else True)
				block['weld'][3]=block['weld'][3] and (2 if get(newblocks,xi+1,yi)['type'] in wiredtypes else True)
			if block['data'] is not None:
				bim=b.draw(block['weld'],block['rotate'],data=getblockdata(block['data']))
			else:
				bim=b.draw(block['weld'],block['rotate'])
				'''
			blocktype=blocktypes[block['type']]
			for datafilter in blocktype['datafilters']:
				block=datafilter(block)
			for layer in blocktype['layers']:
				im.alpha_composite(layer(block),(xi*bsize,yi*bsize)) # paste the block
	return im
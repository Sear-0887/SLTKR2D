from pyfunc.block import makeimage

im = makeimage([
	['iron_bar','air',{'type':'iron_bar','rotate':1}],
	[],
	[
		{'type':'actuator_head','rotate':0},
		{'type':'actuator_head','rotate':1},
		{'type':'actuator_head','rotate':2},
		{'type':'actuator_head','rotate':3},
	],
	[],
	[
		{'type':'frame','rotate':0},
		{'type':'frame','rotate':1},
		{'type':'frame','rotate':2},
		{'type':'actuator_head','rotate':3},
	]
])

im.show()
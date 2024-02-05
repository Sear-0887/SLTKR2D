wafertypes = [
"accelerometer",
"capacitor", "diode",
"galvanometer", "latch",
"matcher","potentiometer",
"sensor","transistor",
"wire_board"
]

frametypes = [
    "detector","port",
    "toggler","trigger",
    "wire"
]

wiredtypes=['actuator','motor',
'telewall','injector',
'pedestal','actuator_base',
'display',"lamp",'combiner',
'arc_furnace','extractor',
'beam_core','creator',
'destroyer','dismantler',
'magnet','manipulator',
'mantler']+wafertypes+frametypes # that connect to wires
twowaytypes=["wire_spool",'wood',"mirror"]


#weld
weldspr = {
    "0000": [
        "copper_ore", "iron_ore", "pulp", "sand", "silicon", "spawner", "telecross", "air", "prism"
    ],
    "0100": [
        'cap','flower_magenta','flower_yellow','grass','motor','pedestal','spikes',"pedestal","summonore"
    ],
    "0101": [
        'actuator_head','wire_spool','telewall'
    ],
    "1010": [
        'combiner','extractor','injector','platform'
    ],
    "1110":[
        'arc_furnace','beam_core','collector','creator','destroyer','dismantler','magnet','manipulator','mantler','teleportore'
    ]
}
# 16n, 32e, 64s, 128n

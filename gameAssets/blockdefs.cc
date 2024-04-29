BLOCK_DEF(air             , collision::none, atb::dungeon_replaceable, 0b0000, 0), \
\
    BLOCK_DEF(dirt            , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 50), \
    BLOCK_DEF(sediment        , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 50), \
    BLOCK_DEF(stone           , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 50), \
\
    BLOCK_DEF(sand            , collision::buildable | collision::solid, atb::dust | atb::dungeon_replaceable, 0b0000, 50), \
    BLOCK_DEF(pulp            , collision::buildable | collision::solid, atb::dust, 0b0000, 50), \
    BLOCK_DEF(rubber          , collision::buildable | collision::solid, atb::none, 0b1111, 40), \
    BLOCK_DEF(cap             , collision::buildable | collision::solid, atb::rotatable, 0b0100, 75), \
    BLOCK_DEF(silicon         , collision::buildable | collision::solid, atb::none, 0b0000, 50), \
    BLOCK_DEF(wafer           , collision::buildable | collision::solid, atb::none, 0b1111, 50), \
\
    BLOCK_DEF(log_maple       , collision::buildable | collision::solid, atb::rotatable | atb::symmetrical | atb::dungeon_replaceable, 0b1111, 50), \
    BLOCK_DEF(leaf_maple      , collision::buildable, atb::dungeon_replaceable, 0b1111, 20), \
\
    BLOCK_DEF(iron_vein       , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 150), \
    BLOCK_DEF(iron_ore        , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b0000, 50), \
    BLOCK_DEF(iron_bar        , collision::buildable | collision::solid, atb::none, 0b1111, 50), \
    BLOCK_DEF(iron_plate      , collision::buildable | collision::solid, atb::none, 0b1111, 30), \
    BLOCK_DEF(cast_iron       , collision::buildable | collision::solid, atb::none, 0b1111, 80), \
\
    BLOCK_DEF(copper_vein     , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 150), \
    BLOCK_DEF(copper_ore      , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b0000,  50), \
    BLOCK_DEF(copper_bar      , collision::buildable | collision::solid, atb::none, 0b1111, 50), \
    BLOCK_DEF(wire_spool      , collision::buildable | collision::solid, atb::rotatable | atb::symmetrical, 0b0101, 50), \
\
    BLOCK_DEF(frame           , collision::buildable, atb::none, 0b1111, 30), \
\
    BLOCK_DEF(wire            , collision::buildable, atb::wire_draw | atb::wire_connect | atb::is_wire, 0b1111, 30), \
    BLOCK_DEF(wire_board      , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::is_wire, 0b1111, 30), \
    BLOCK_DEF(port            , collision::buildable, atb::wire_draw | atb::wire_connect | atb::rotatable | atb::is_wire, 0b1110, 30), \
\
    BLOCK_DEF(toggler         , collision::buildable | collision::interactable, atb::wire_draw | atb::wire_connect, 0b1111, 30), \
    BLOCK_DEF(detector        , collision::buildable | collision::trigger, atb::wire_draw | atb::wire_connect | atb::is_wire, 0b1111, 50), \
    BLOCK_DEF(sensor          , collision::buildable | collision::solid | collision::interactable, atb::wire_draw | atb::wire_connect | atb::rotatable | atb::unweld_listener, 0b1111, 50), \
    BLOCK_DEF(accelerometer   , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::rotatable | atb::symmetrical, 0b1111, 50), \
\
    BLOCK_DEF(capacitor       , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge, 0b1111, 50), \
    BLOCK_DEF(diode           , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(potentiometer   , collision::buildable | collision::solid | collision::interactable, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(transistor      , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(cascade         , collision::buildable | collision::solid | collision::interactable, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(galvanometer    , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(latch           , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
    BLOCK_DEF(inductor        , collision::buildable | collision::solid, atb::wire_connect, 0b1111, 50), \
\
    BLOCK_DEF(platform        , collision::buildable | collision::solid, atb::assymetric_nonrotatable, 0b1010, 30), \
\
    BLOCK_DEF(actuator        , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::xtruder, 0b1111, 50), \
    BLOCK_DEF(actuator_base   , collision::buildable | collision::solid, atb::rotatable | atb::wire_connect, 0b1111, 50), \
    BLOCK_DEF(actuator_head   , collision::buildable | collision::solid, atb::rotatable, 0b0101, 50), \
    BLOCK_DEF(roller          , collision::buildable | collision::solid | collision::interactable, atb::wire_connect, 0b1111, 50), \
    BLOCK_DEF(dynamic_roller  , collision::buildable | collision::solid | collision::interactable, atb::wire_connect, 0b1111, 50), \
    BLOCK_DEF(magnet          , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable, 0b1110, 50), \
    BLOCK_DEF(motor           , collision::buildable | collision::solid | collision::interactable, atb::wire_connect | atb::rotatable | atb::machine, 0b0100, 50), \
    BLOCK_DEF(manipulator     , collision::buildable | collision::solid, atb::rotatable | atb::unweld_listener | atb::wire_connect, 0b1110, 50), \
\
    BLOCK_DEF(combiner        , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::machine | atb::xtruder, 0b1010, 50), \
    BLOCK_DEF(mantler         , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::unweld_listener, 0b1110, 50), \
    BLOCK_DEF(dismantler      , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::machine | atb::unweld_listener, 0b1110, 50), \
    BLOCK_DEF(destroyer       , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::machine, 0b1110, 50), \
    BLOCK_DEF(extractor       , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::machine | atb::xtruder, 0b1010, 50), \
    BLOCK_DEF(arc_furnace     , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::machine, 0b1110, 50), \
\
    BLOCK_DEF(chair           , collision::buildable, atb::none, 0b1111, 50), \
    BLOCK_DEF(chair_pilot     , collision::buildable, atb::wire_connect, 0b1111, 50), \
\
    BLOCK_DEF(display         , collision::buildable | collision::interactable, atb::wire_connect, 0b1111, 50), \
\
    BLOCK_DEF(core_ore        , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 100), \
    BLOCK_DEF(raw_core        , collision::buildable | collision::solid, atb::none, 0b1111, 100), \
    BLOCK_DEF(mass_core       , collision::buildable | collision::solid, atb::none, 0b1111, 100), \
    BLOCK_DEF(force_core      , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable, 0b1111, 100), \
    BLOCK_DEF(refined_core    , collision::buildable | collision::solid, atb::stationary, 0b1111, 100), \
    BLOCK_DEF(beam_core       , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable, 0b1111, 100), \
    BLOCK_DEF(catalyst_core   , collision::buildable | collision::solid, atb::none, 0b1111, 100), \
    BLOCK_DEF(teleportore     , collision::buildable | collision::solid, atb::rotatable | atb::unweld_listener | atb::wire_connect, 0b1110, 75), \
\
    BLOCK_DEF(command_block   , collision::solid | collision::interactable, atb::wire_connect | atb::dynamic_data | atb::weldable_with_cheats, 0b0000, 100), \
    BLOCK_DEF(boundary        , collision::solid, atb::stationary | atb::weldable_with_cheats, 0b0000, 100), \
    BLOCK_DEF(creator         , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable | atb::xtruder, 0b1110, 50), \
    BLOCK_DEF(spawner         , collision::solid, atb::stationary | atb::dynamic_data, 0b0000, 100), \
\
    BLOCK_DEF(calcium_bar     , collision::buildable | collision::solid, atb::none, 0b1111, 50), \
    BLOCK_DEF(spikes          , collision::buildable | collision::solid, atb::rotatable, 0b0100, 50), \
\
    BLOCK_DEF(water           , collision::buildable | collision::entity_swim | collision::entity_slow, atb::dungeon_replaceable, 0b0000, 0),\
    BLOCK_DEF(foam            , collision::buildable | collision::solid, atb::none, 0b1111, 30),\
    BLOCK_DEF(oxide           , collision::buildable | collision::solid, atb::none, 0b1111, 50),\
\
    BLOCK_DEF(soul_core       , collision::buildable | collision::solid, atb::none, 0b1111, 100),\
    BLOCK_DEF(adobe           , collision::buildable | collision::solid, atb::none, 0b1111, 50),\
    BLOCK_DEF(peltmellow      , collision::buildable | collision::solid, atb::none, 0b1111, 50),\
    BLOCK_DEF(glass           , collision::buildable | collision::solid, atb::glass, 0b1111, 30),\
    BLOCK_DEF(lamp            , collision::buildable, atb::rotatable | atb::wire_connect, 0b0100, 75), \
\
    BLOCK_DEF(collector       , collision::buildable | collision::solid, atb::rotatable, 0b1110, 50), \
    BLOCK_DEF(trigger         , collision::buildable, atb::wire_draw | atb::wire_connect | atb::rotatable | atb::unweld_listener, 0b1110, 50), \
    BLOCK_DEF(matcher         , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::rotatable | atb::unweld_listener | atb::symmetrical, 0b1010, 50), \
\
    BLOCK_DEF(telewall        , collision::buildable | collision::solid, atb::rotatable | atb::unweld_listener | atb::wire_connect, 0b1010, 75), \
    BLOCK_DEF(telecross       , collision::buildable | collision::solid, atb::rotatable | atb::unweld_listener, 0b0000, 75), \
\
    BLOCK_DEF(mirror          , collision::buildable, atb::rotatable | atb::symmetrical, 0b1111, 30), \
    BLOCK_DEF(glass_cyan      , collision::buildable | collision::solid, atb::glass, 0b1111, 30),\
    BLOCK_DEF(glass_magenta   , collision::buildable | collision::solid, atb::glass, 0b1111, 30),\
    BLOCK_DEF(glass_yellow    , collision::buildable | collision::solid, atb::glass, 0b1111, 30),\
\
    BLOCK_DEF(grass           , collision::buildable, atb::crushable_detail | atb::dungeon_replaceable, 0b0000, 50),\
    BLOCK_DEF(flower_magenta  , collision::buildable, atb::crushable_detail | atb::dungeon_replaceable, 0b0000, 50),\
    BLOCK_DEF(flower_yellow   , collision::buildable, atb::crushable_detail | atb::dungeon_replaceable, 0b0000, 50),\
    BLOCK_DEF(residue         , collision::buildable | collision::entity_swim, atb::dungeon_replaceable, 0b1111, 30),\
\
    BLOCK_DEF(injector        , collision::buildable | collision::solid, atb::rotatable | atb::machine | atb::wire_connect, 0b1010, 50),\
    BLOCK_DEF(rail_core       , collision::buildable | collision::solid, atb::rotatable | atb::symmetrical, 0b1111, 100),\
\
    BLOCK_DEF(ice             , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 30),\
    BLOCK_DEF(compressed_stone, collision::buildable | collision::solid, atb::none, 0b1111, 100),\
\
    BLOCK_DEF(pedestal        , collision::buildable | collision::solid, atb::wire_connect | atb::assymetric_nonrotatable, 0b0100, 50),\
    BLOCK_DEF(summonore       , collision::buildable | collision::solid | collision::interactable, atb::wire_connect | atb::rotatable, 0b1110, 50),\
\
    BLOCK_DEF(counter         , collision::buildable | collision::solid | collision::interactable, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50), \
\
    BLOCK_DEF(log_pine        , collision::buildable | collision::solid, atb::rotatable | atb::symmetrical | atb::dungeon_replaceable, 0b1111, 50), \
    BLOCK_DEF(leaf_pine       , collision::buildable, atb::dungeon_replaceable, 0b1111, 20), \
    BLOCK_DEF(sawdust         , collision::buildable | collision::solid, atb::dust, 0b0000, 50), \
    BLOCK_DEF(snow            , collision::buildable | collision::entity_slow, atb::crushable_detail | atb::dungeon_replaceable, 0b0000, 50), \
\
    BLOCK_DEF(prism           , collision::buildable | collision::interactable | collision::solid, atb::none, 0b0000, 30), \
\
    BLOCK_DEF(slime           , collision::buildable | collision::solid, atb::none, 0b1111, 50), \
    BLOCK_DEF(slime_ice       , collision::buildable | collision::solid, atb::rotatable, 0b1111, 50), \
\
    BLOCK_DEF(chert           , collision::buildable | collision::solid, atb::dungeon_replaceable, 0b1111, 75), \
    BLOCK_DEF(compressed_chert, collision::buildable | collision::solid, atb::none, 0b1111, 100), \
    BLOCK_DEF(spark_catcher   , collision::buildable | collision::solid | collision::trigger, atb::wire_connect, 0b1111, 50), \
    BLOCK_DEF(spark_emitter   , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable, 0b1110, 50), \
    BLOCK_DEF(bomb_emitter    , collision::buildable | collision::solid, atb::wire_connect | atb::rotatable, 0b1110, 50), \
\
    BLOCK_DEF(divider         , collision::buildable | collision::solid, atb::wire_draw | atb::wire_connect | atb::next_charge | atb::rotatable, 0b1111, 50)

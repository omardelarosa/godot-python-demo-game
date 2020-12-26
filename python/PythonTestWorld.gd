extends Spatial

var Constants = preload('res://Config/Constants.gd')
var CharBase = preload('res://Characters/Basics/CharacterBase.tscn')

var noise = OpenSimplexNoise.new()
var BLUE_TILE = 1
var GRASS_TILE = 0

onready var pyb = $PyBridge
onready var terrain_grid = $TerrainGrid
onready var meta_grid = $MetaGrid
onready var characters_container = $CharactersContainer
onready var cam = $Camera

var game_state : Dictionary

var char_id_to_idx = {}

func grid_to_position_list(grid):
    var positions = grid.get_used_cells()
    if not positions:
        return []
    else:
        return positions

# Called when the node enters the scene tree for the first time.
func _ready():
    init_game()

func make_procedural_grid(rows, cols, target_grid: GridMap):
    # Configure
    noise.seed = randi()
    noise.octaves = 4
    noise.period = 20.0
    noise.persistence = 0.8

    var positions = []

    var height_range = 8
    var height_offset = -4

    target_grid.clear()

    for x in rows:
        for z in cols:
            var y = noise.get_noise_2d(x, z)
            var h = int(y * height_range) + height_offset
            var pos = Vector3(x,h,z)
            positions.push_back(pos)
            target_grid.set_cell_item(x, h, z, GRASS_TILE)

    return positions

func character_node_name_from_id(id: String):
    return 'Character_' + id

func init_game():

    make_procedural_grid(32, 32, terrain_grid)

    var terrain_grid_positions = grid_to_position_list(terrain_grid)
    var meta_grid_positions = grid_to_position_list(meta_grid)


    # Bind events
    pyb.connect(Constants.EVENT_PLAYER_MOVE_SUCCESS, self, "_handle_player_move_success")
    pyb.connect(Constants.EVENT_PLAYER_MOVE_FAILED, self, "_handle_player_move_failed")
    pyb.connect(Constants.EVENT_GAME_STATE_READY, self, "_handle_game_state_ready")

    # Registers a grid, a meta grid and self to the game manger
    print("setting up!", pyb)
    pyb.setup({ 'grid': terrain_grid_positions, 'num_characters_per_team': 3, 'num_teams': 2 })


func _handle_game_state_ready():
    
    # Place characters
    game_state = pyb.state()
    print('game_state is ready: ')
    
    # clear existing character nodes
    for c in characters_container.get_children():
        characters_container.remove_child(c)

    var selected_char_node
    var idx = 0
    for c in game_state['characters']:
        var char_node : CharacterBase = CharBase.instance()
        var cid = c['id']
        char_node.name = character_node_name_from_id(c['id']) # use name and ID for 
        characters_container.add_child(char_node)
        char_node.set_grid(terrain_grid)
        char_node.state = c
        char_id_to_idx[c['id']] = idx
        idx += 1

    draw_board()
    

func _handle_player_move_success(a: Vector3, b: Vector3):
#    print("player_success: ", a, b)
    draw_board()

func _handle_player_move_failed(a: Vector3, b: Vector3):
#    print("player_failed: ", a, b)
    draw_board()

func draw_board():
    # get board:  grids + character positions
    game_state = pyb.state()
    var selected_character_data = game_state['selected_character']
    var player_pos = selected_character_data['position']
    var _meta_grid = game_state['meta_grid']
    meta_grid.clear()

    for item in _meta_grid:
        var vec = item[0]
        var tile = item[1]
        meta_grid.set_cell_item(vec.x, vec.y, vec.z, tile)

    var char_node = null
    for c in game_state['characters']:
        var c_node = characters_container.get_child(char_id_to_idx[c['id']])
        c_node.set_state(c)
        if c['id'] == game_state['selected_character']['id']:
            c_node.activate_camera()

func _process(delta):
    if game_state and "selected_character" in game_state:
        if Input.is_action_just_pressed("ui_left"):
            pyb.notify(Constants.EVENT_REQUEST_PLAYER_MOVE, Vector3.LEFT)
        if Input.is_action_just_pressed("ui_right"):
            pyb.notify(Constants.EVENT_REQUEST_PLAYER_MOVE, Vector3.RIGHT)
        if Input.is_action_just_pressed("ui_up"):
            pyb.notify(Constants.EVENT_REQUEST_PLAYER_MOVE, Vector3.FORWARD)
        if Input.is_action_just_pressed("ui_down"):
            pyb.notify(Constants.EVENT_REQUEST_PLAYER_MOVE, Vector3.BACK)
        if Input.is_action_just_pressed("pointer_click") or Input.is_action_just_pressed("ui_accept"):
            pyb.notify(Constants.EVENT_REQUEST_END_TURN)
    else:
        if Input.is_action_just_pressed("ui_left"):
            pyb.notify(Constants.EVENT_REQUEST_CURSOR_MOVE, Vector3.LEFT)
        if Input.is_action_just_pressed("ui_right"):
            pyb.notify(Constants.EVENT_REQUEST_CURSOR_MOVE, Vector3.RIGHT)
        if Input.is_action_just_pressed("ui_up"):
            pyb.notify(Constants.EVENT_REQUEST_CURSOR_MOVE, Vector3.FORWARD)
        if Input.is_action_just_pressed("ui_down"):
            pyb.notify(Constants.EVENT_REQUEST_CURSOR_MOVE, Vector3.BACK)
        if Input.is_action_just_pressed("pointer_click") or Input.is_action_just_pressed("ui_accept"):
            pyb.notify(Constants.EVENT_CURSOR_SELECT)

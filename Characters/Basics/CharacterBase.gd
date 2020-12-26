extends Spatial
class_name CharacterBase

const DEFAULT_CHARACTER_BASE_STATE_DICT = {
    'id': '',
    'hit_points': 1,
    'name': 'Unnamed Character',
    'position': Vector3.ZERO,
    'last_position': Vector3.ZERO
}

export(Dictionary) var state = DEFAULT_CHARACTER_BASE_STATE_DICT setget set_state

onready var cam = $CharacterBaseCam

var is_selected = false
var grid: GridMap = null

func set_grid(_grid):
    grid = _grid

func set_state(_next_state):
    print('Updating character state: ', _next_state)
    state = _next_state
    if grid:
        # move if necessary
        move_char_to(state['position'], grid)

func set_camera():
    cam = $CharacterBaseCam

func activate_camera():
    print('activating camera')
    if cam:
        print('camera present')
        cam.current = true
    else:
        print('no camera!')

func grid_to_world_pos(grid_pos, _grid: GridMap):
    var reference_grid: GridMap
    if _grid != null:
        reference_grid = _grid
    else:
        reference_grid = grid
    return reference_grid.map_to_world(grid_pos.x, grid_pos.y, grid_pos.z)

func move_char_to(_grid_pos: Vector3, _grid: GridMap):
    var _world_pos = grid_to_world_pos(_grid_pos, _grid)
    var t = global_transform
    global_transform.origin = Vector3(_world_pos.x, _world_pos.y, _world_pos.z)

# Called when the node enters the scene tree for the first time.
func _ready():
    pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
    pass

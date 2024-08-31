# Entity States # should be different from animation indexes
STATE_IDLE                  = 1
STATE_MOVING                = 2
STATE_ATTACKING             = 3

## State Flags
STATE_FLAG_MOVING           = 1 << 0 # 1st bit
STATE_FLAG_ATTACKING        = 1 << 1 # 2nd bit
STATE_FLAG_DEFENDING        = 1 << 2 # 3rd bit

## animation indexes
ANIMATION_IDLE              = 1
ANIMATION_WALKING           = 2
ANIMATION_BASE_ATTACK       = 3
ANIMATION_SPECIAL_ATTACK    = 3

# Entity Dirrections
LEFT                        = 11
RIGHT                       = 12
UP                          = 13
DOWN                        = 14
UP_LEFT                     = 15
UP_RIGHT                    = 16
DOWN_LEFT                   = 17
DOWN_RIGHT                  = 18

# Characters
CHARACTER_WIZART            = "069b2uri"

# Sprite Types/All Types
TYPE_ENTITY                 = "entity"
CONFIG_TYPE                 = "type"
CONFIG_DATA                 = "data"

# Entity Config Data
ENTITY_CONFIG_NAME          = "name"
ENTITY_CONFIG_ENTITY_ID     = "entity_id"
ENTITY_CONFIG_SPEED         = "speed"

SPRITE_SHEET_CONFIG         = "sprite_sheet_config"
SPRITE_SHEET_PATH           = "sprite_sheet_path"
SPRITE_SHEET_WIDTH          = "width"
SPRITE_SHEET_HEIGHT         = "height"
SPRITE_SHEET_ROWS           = "rows"
SPRITE_SHEET_COLUMNS        = "columns"
SPRITE_SHEET_CELL_WIDTH     = "cell_width"
SPRITE_SHEET_CELL_HEIGHT    = "cell_height"

ANIMATIONS_PATH             = "animations_path"
ANIMATIONS_CONFIG           = "animations_config"
ANIMATIONS_FPS              = "fps"
ANIMATIONS_ANIMATIONS       = "animations"

ANIMATIONS_INFO_ROW         = "row"
ANIMATIONS_INFO_LENGTH      = "length"
ANIMATIONS_IDLE             = "idle"
ANIMATIONS_WALK             = "walk"
# Should be an array of attacks (length 1 if only one)
ANIMATIONS_BASE_ATTACK      = "base_attack"

# Loading States
LOADING_STATE_PENDING       = "pending"
LOADING_STATE_LOADING       = "loading"
LOADING_STATE_INTERRUPT     = "interrupted"
LOADING_STATE_ERROR         = "error"
LOADING_STATE_DONE          = "done"

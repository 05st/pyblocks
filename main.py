# LIBRARY IMPORTS #
import pygame

# LOCAL MODULES #
import game
import graphics
import shared
import blocks

GAME_INSTANCE = game.Game()

# UI VARIABLES AND FUNCTIONS #
# using a single dictionary and function makes implementing UI easier
toggleables = {
    "d_menu": False,
    "d_vars": True,
    "d_cont": False,
    "d_tutr": True,
    "d_prob": False,
}
def toggle(x):
    if x in toggleables:
        toggleables[x] = not toggleables[x]

temp_instances = [getattr(blocks, block_class)() for block_class in shared.INSERT_OPTIONS]
insert_buttons = [(block.label, block.color) for block in temp_instances]
insert_menu_ps = [] # contains position and size of insert menu buttons for click detection

# using a dictionary allows me to not use a thousand elif statements
input_map = {
    pygame.K_x: (GAME_INSTANCE.clear, []),
    pygame.K_v: (toggle, ["d_vars"]),
    pygame.K_c: (toggle, ["d_cont"]),
    pygame.K_t: (toggle, ["d_tutr"]),
    pygame.K_TAB: (toggle, ["d_prob"]),
    pygame.K_SPACE: (toggle, ["d_menu"]),
    pygame.K_RETURN: (GAME_INSTANCE.run, []),
    pygame.K_LEFT: (GAME_INSTANCE.inc_level, [-1]),
    pygame.K_RIGHT: (GAME_INSTANCE.inc_level, [1]),
}

def insert_menu_detection(pos):
    global insert_menu_ps
    for i, btn_ps in enumerate(insert_menu_ps):
        if shared.check_collision(btn_ps[0], btn_ps[1], pos):
            toggleables["d_menu"] = False
            GAME_INSTANCE.begin_place(shared.INSERT_OPTIONS[i])

# GAME LOOP #
closed = False
while not closed:
    for event in pygame.event.get(): # catch any events
        if event.type == pygame.QUIT:
            closed = True
        elif event.type == pygame.KEYDOWN:
            if GAME_INSTANCE.typing:
                GAME_INSTANCE.handle_typing(event)
            elif event.key in input_map:
                input_map[event.key][0](*input_map[event.key][1]) # calls the function associated with the key code
        elif event.type == pygame.MOUSEBUTTONDOWN and not GAME_INSTANCE.typing: # any mouse inputs should be ignored if typing
            pos = pygame.mouse.get_pos()
            if event.button == 1: # LMB
                if toggleables["d_menu"]: # if insert menu is open, check if any buttons were clicked
                    insert_menu_detection(pos)
                else:
                    target = GAME_INSTANCE.identify_block(pos)
                    if pygame.key.get_pressed()[pygame.K_LSHIFT] : # cloning block feature
                        GAME_INSTANCE.clone(target)
                    else:
                        GAME_INSTANCE.begin_typing(target, pos) # will try to begin typing
                        if not GAME_INSTANCE.typing: # if not interacting with a FieldBlock
                            (GAME_INSTANCE.end_place if GAME_INSTANCE.placing else GAME_INSTANCE.begin_move)(target, pos)
            elif event.button == 3 and not toggleables["d_menu"]: # RMB
                GAME_INSTANCE.delete_block(pos)

    tasks = GAME_INSTANCE.global_blocks[:]

    # update ghost
    if GAME_INSTANCE.placing:
        mx, my = pygame.mouse.get_pos()
        sx, sy = GAME_INSTANCE.ghost.size
        GAME_INSTANCE.ghost.pos = (mx - sx // 2, my - sy // 2)
        tasks.append(GAME_INSTANCE.ghost)

    # render everything
    graphics.prepare() # clears screen
    graphics.render(tasks) # renders block_defs
    graphics.display_level(GAME_INSTANCE.level) # displays level
    # render toggleables
    if toggleables["d_vars"]: graphics.display_vars(blocks.global_vars)
    if toggleables["d_prob"]: graphics.display_problem(shared.LEVEL_DATA[GAME_INSTANCE.level][0])
    if toggleables["d_menu"]: insert_menu_ps = graphics.display_insert_menu(insert_buttons)
    if toggleables["d_cont"]: graphics.display_controls()
    if toggleables["d_tutr"]: graphics.display_tutorial()
    graphics.finish() # update display

pygame.quit() # properly clean up


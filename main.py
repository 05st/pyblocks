import pygame
import copy

import graphics
import blocks
import utility

global_blocks = []

typing = False
closed = False
placing = False

# starts the game, execute all start blocks
def run_game():
    for root in global_blocks:
        if isinstance(root, blocks.StartBlock):
            root.execute()

ghost = None
def begin_place(block_type):
    global placing, ghost
    if not placing:
        ghost = getattr(blocks, block_type)()
        ghost.opacity = 128
        placing = True

def end_place(ident, pos):
    global placing, ghost, global_blocks
    if placing:
        placing = False
        ghost.opacity = 255
        if ident:
            if isinstance(ident, blocks.SlotBlock):
                if not ident.fill_slot(ghost, pos):
                    ident.add_child(ghost)
            else:
                ident.add_child(ghost)
        else:
            global_blocks.append(ghost)
        del ghost

def begin_move(ident, pos):
    global placing, ghost, global_blocks
    if not placing and ident:
        ghost = ident
        delete_block(pos, global_blocks)
        ghost.opacity = 128
        ghost.valid_parent = ghost.default_valid_parent # incase it's moving out of a slot
        placing = True

# another recursive search, children first; needed to handle BlockSlot separately
def delete_block_slot(pos, slots):
    for i, slot in slots.items():
        if isinstance(slot, blocks.SlotBlock):
            if delete_block_slot(pos, slot.slots):
                return True
        if utility.check_collision(slot.pos, slot.size, pos):
            del slots[i]
            return True
    return False

# recursively search for block, similar to identify_block
def delete_block(pos, roots):
    for i in range(len(roots)): # since we want to modify the list, we cant do "for x in roots"
        status = delete_block(pos, roots[i].children)
        if isinstance(roots[i], blocks.SlotBlock):
            status = delete_block_slot(pos, roots[i].slots)
        if status: return True
        if utility.check_collision(roots[i].pos, roots[i].size, pos):
            del roots[i]
            return True
    return False

insert_menu = False
def toggle_insert():
    global insert_menu
    insert_menu = not insert_menu

def begin_typing(ident, pos):
    global typing, field_block
    if ident and isinstance(ident, blocks.FieldBlock) and utility.check_collision(ident.field_ps[0], ident.field_ps[1], pos):
        typing = True
        field_block = ident
 
# using a dictionary allows me to not use a thousand elif statements
# (not that i needed to in the first place)
input_map = {
    pygame.K_1: (begin_place, ["StartBlock"]),
    pygame.K_2: (begin_place, ["NumBlock"]),
    pygame.K_3: (begin_place, ["PrintBlock"]),
    pygame.K_4: (begin_place, ["AddBlock"]),
    pygame.K_5: (begin_place, ["SubBlock"]),
    pygame.K_6: (begin_place, ["MulBlock"]),
    pygame.K_7: (begin_place, ["DivBlock"]),
    pygame.K_8: (begin_place, ["ModBlock"]),
    pygame.K_SPACE: (toggle_insert, []),
    pygame.K_RETURN: (run_game, []),
}

# probably not the best place to organize these lists
insert_options = ["StartBlock", "NumBlock", "PrintBlock", "AddBlock", "SubBlock", "MulBlock", "DivBlock", "ModBlock"]
temp_instances = [getattr(blocks, block_class)() for block_class in insert_options]
insert_buttons = [(block.label, block.color) for block in temp_instances]
insert_menu_ps = []

# game loop
field_block = None
while not closed:
    for event in pygame.event.get(): # catch any events
        if event.type == pygame.QUIT:
            closed = True
        elif event.type == pygame.KEYDOWN:
            # TODO: move fieldblock stuff to separate functions
            if typing:
                # i had to implement my own text input, since pygame didn't support
                if event.key == pygame.K_RETURN:
                    typing = False
                    field_block.validate()
                    field_block = None
                elif event.key == pygame.K_BACKSPACE:
                    field_block.field = field_block.field[:-1]
                else:
                    field_block.field += event.unicode
            elif event.key in input_map:
                input_map[event.key][0](*input_map[event.key][1])
        elif event.type == pygame.MOUSEBUTTONDOWN and not typing: # any mouse inputs should be ignored if typing
            pos = pygame.mouse.get_pos()
            if event.button == 1: # LMB
                if insert_menu: # if insert menu is open, check if any buttons were clicked
                    for i, btn_ps in enumerate(insert_menu_ps):
                        if utility.check_collision(btn_ps[0], btn_ps[1], pos):
                            insert_menu = False
                            begin_place(insert_options[i])
                else:
                    ident = utility.identify_block(pos, global_blocks)
                    begin_typing(ident, pos) # will try to begin typing
                    if not typing: # if not interacting with a FieldBlock
                        (end_place if placing else begin_move)(ident, pos)
            if event.button == 3 and not insert_menu: # RMB
                delete_block(pos, global_blocks)

    tasks = global_blocks[:] # to send to renderer
    # update ghost
    if placing:
        mx, my = pygame.mouse.get_pos()
        ghost.pos = (mx - ghost.size[0] // 2, my - ghost.size[1] // 2)
        tasks.append(ghost)

    graphics.prepare()
    graphics.render(tasks)
    if insert_menu:
        insert_menu_ps = graphics.insert_menu(insert_buttons)
    graphics.finish()

pygame.quit()


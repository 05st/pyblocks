import pygame

import graphics
import blocks
import utility

global_blocks = [
    blocks.BaseBlock("test", (255, 0, 0), pos = (250, 0), children = [
        blocks.BaseBlock("child", (0, 0, 255), pos = (250, 200), children = [
            blocks.StartBlock(),
        ]),
        blocks.StartBlock(),
    ]),
    blocks.SlotBlock("test2", (0, 255, 0), 2, slots = {
        0: blocks.StartBlock(),
        1: blocks.SlotBlock("test3", (0, 0, 255), 2, slots = {0: blocks.StartBlock()})
    }),
]

placing = False
ghost = None
def begin_place(block_type):
    global placing, ghost
    if not placing:
        ghost = getattr(blocks, block_type)()
        placing = True

def end_place():
    global placing, ghost, global_blocks
    if placing:
        placing = False
        pos = pygame.mouse.get_pos()
        parent = utility.identify_block(pos, global_blocks)
        ghost.opacity = 255
        if parent:
            if isinstance(parent, blocks.SlotBlock):
                if not parent.fill_slot(ghost, pos):
                    parent.add_child(ghost)
            else:
                parent.add_child(ghost)
        else:
            global_blocks.append(ghost)
        del ghost

def begin_move():
    global placing, ghost, global_blocks
    if not placing:
        pos = pygame.mouse.get_pos()
        ghost = utility.identify_block(pos, global_blocks)
        if ghost != None:
            delete_block(pos, global_blocks)
            ghost.opacity = 128
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

input_map = {
    pygame.K_1: (begin_place, ["StartBlock"]),
    pygame.K_2: (begin_place, ["StartBlock"]),
}

# game loop
closed = False
while not closed:
    for event in pygame.event.get(): # catch any events
        if event.type == pygame.QUIT:
            closed = True
        elif event.type == pygame.KEYDOWN:
            if event.key in input_map:
                input_map[event.key][0](*input_map[event.key][1])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # LMB
                (end_place if placing else begin_move)()
            if event.button == 3: # RMB
                delete_block(pygame.mouse.get_pos(), global_blocks)

    tasks = global_blocks[:] # to send to renderer
    # update ghost
    if placing:
        mx, my = pygame.mouse.get_pos()
        ghost.pos = (mx - ghost.size[0] // 2, my - ghost.size[1] // 2)
        tasks.append(ghost)

    graphics.render(tasks)

pygame.quit()


import pygame

import graphics
import blocks

global_blocks = [
    blocks.ParentBlock("test", (255, 0, 0), children = [
        blocks.BaseBlock("child", (0, 0, 255), pos = (200, 200))
    ])
]

placing = False
ghost = None
def begin_place(block_type):
    global placing, ghost
    if not placing:
        ghost = getattr(blocks, block_type)("test", (255, 0, 0), opacity = 128)
        placing = True

def end_place():
    global placing, ghost
    if placing:
        placing = False
        ghost.opacity = 255
        global_blocks.append(ghost)
        del ghost

def begin_move():
    pass

input_map = {
    pygame.K_1: (begin_place, ["BaseBlock"]),
    pygame.K_2: (begin_place, ["ParentBlock"]),
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

    tasks = global_blocks[:] # to send to renderer
    # update ghost
    if placing:
        mx, my = pygame.mouse.get_pos()
        ghost.pos = (mx - ghost.size[0] // 2, my - ghost.size[1] // 2)
        tasks.append(ghost)

    graphics.render(tasks)

pygame.quit()


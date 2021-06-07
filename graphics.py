import pygame
import blocks

display = pygame.display.set_mode((1280, 720))
pygame.font.init()
font = pygame.font.SysFont("Arial", 25)

# to be called once per frame
def render(tasks):
    display.fill((0, 0, 0)) # black background

    while tasks:
        block = tasks.pop(0)

        # render text onto a surface
        text_surf = font.render(block.label, True, (255, 255, 255))

        # calculate width
        width = text_surf.get_rect().width + 10
        if isinstance(block, blocks.SlotBlock):
            width += block.slots_count * block.size[1] + 5 * (block.slots_count - 1)
        block.size = (width, block.size[1])

        # create main surface
        block_surf = pygame.Surface(block.size)
        block_surf.fill(block.color)
        block_surf.set_alpha(block.opacity)

        # handle SlotBlocks
        if isinstance(block, blocks.SlotBlock):
            for i in range(block.slots_count):
                slot_surf = pygame.Surface((block.size[1],)*2)
                slot_surf.fill((255, 255, 255))
                block_surf.blit(slot_surf, (text_surf.get_rect().width + 10 + i * (block.size[1] + 5), 0))

        # blit surfaces
        block_surf.blit(text_surf, (5, block.size[1] // 2 - text_surf.get_rect().height // 2))
        display.blit(block_surf, block.pos)

        # handle children
        cur_height = block.size[1]
        for i, child in enumerate(block.children):
            child.pos = (block.pos[0] + 20, block.pos[1] + cur_height) # indent size is 20px
            cur_height += child.abs_height()
        
        tasks += block.children[:]

    pygame.display.update() # update display


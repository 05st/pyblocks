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
        
        # create main surface
        block_surf = pygame.Surface(block.size)
        block_surf.fill(block.color)
        block_surf.set_alpha(block.opacity)

        # render text onto a surface
        text_surf = font.render(block.label, True, (255, 255, 255))

        # blit surfaces
        block_surf.blit(text_surf, (5, block.size[1] // 2 - text_surf.get_rect().height // 2))
        display.blit(block_surf, block.pos)
        
        if isinstance(block, blocks.ParentBlock):
            tasks += block.children[:]

    pygame.display.update() # update display


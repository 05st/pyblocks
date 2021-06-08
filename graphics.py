import pygame
import blocks

display = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("PyBlocks")
pygame.font.init()
font = pygame.font.SysFont("Arial", 25)

# to be called once per frame
def render(tasks):
    display.fill((0, 0, 0)) # black background

    while tasks: # while tasks is not empty
        block = tasks.pop()

        # render text onto a surface
        text_surf = font.render(block.label, True, (255, 255, 255))

        # calculate width
        # REDO: move handling from below up here
        width = text_surf.get_rect().width + 10
        if isinstance(block, blocks.SlotBlock): # account for slots
            width += block.slots_count * block.size[1] + 5 * (block.slots_count - 1)
            for item in block.slots.values():
                width -= block.size[1]
                width += item.size[0]
        elif isinstance(block, blocks.FieldBlock):
            text_temp = font.render(block.field, True, (0, 0, 0))
            width += text_temp.get_rect().width + 10
        block.size = (width, block.size[1])

        # create main surface
        block_surf = pygame.Surface(block.size)
        block_surf.fill(block.color)
        block_surf.set_alpha(block.opacity)

        # handle SlotBlocks
        if isinstance(block, blocks.SlotBlock):
            cur_width = text_surf.get_rect().width + 10
            for i in range(block.slots_count):
                slot_surf = pygame.Surface((block.size[1],)*2)
                slot_surf.fill((236, 240, 241))#(255, 255, 255))
                slot_pos = (cur_width + i * 5, 0)
                block_surf.blit(slot_surf, slot_pos)
                block.slots_pos[i] = (block.pos[0] + slot_pos[0], block.pos[1] + slot_pos[1])
                if i in block.slots:
                    block.slots[i].pos = block.slots_pos[i]
                    tasks.append(block.slots[i])
                    cur_width += block.slots[i].size[0]
                else:
                    cur_width += block.size[1]

        # handle FieldBlocks
        elif isinstance(block, blocks.FieldBlock):
            field_text_surf = font.render(block.field, True, (0, 0, 0))
            field_surf = pygame.Surface((field_text_surf.get_rect().width + 10, block.size[1]))
            field_surf.fill((236, 240, 241))#(255, 255, 255))
            field_surf.blit(field_text_surf, (5, block.size[1] // 2 - field_text_surf.get_rect().height // 2))
            block_surf.blit(field_surf, (text_surf.get_rect().width + 10, 0))

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


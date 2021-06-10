import pygame

import blocks
import utility

display = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("PyBlocks")
pygame.font.init()
font = pygame.font.SysFont(pygame.font.get_default_font(), 25)

# DIALOG CODE #
# create_dialog for reusability
def create_dialog(lines, size = (600, 600)):
    surface = pygame.Surface(size)
    surface.fill((236, 240, 241))
    ww, wh = pygame.display.get_surface().get_size()
    pos = (ww // 2 - size[0] // 2, wh // 2 - size[1] // 2)
    for i, elem in enumerate(lines):
        text = font.render(elem, True, (0, 0, 0))
        surface.blit(text, (5, 5 + i * 25))
    display.blit(surface, pos)

# i prefer using lambda when the function would only be 2 lines
display_problem = lambda problem_text: create_dialog(utility.wrap_text(problem_text), (600, 100))
    
tutorial_text = """
    PyBlocks is a game where the objective is to solve certain problems with interactive code. [BREAK]
    To view the current problem, press TAB. Solutions are verified by checking if value stored inside the 'goal' variable is correct.
    [BREAK] [BREAK]
    Clicking on top of a block when placing adds it as a child. [BREAK]
    Code that you want to run at the start should be placed under 'Start' blocks. They are the entry point; first blocks executed.
    Only 'Start', 'If', 'While', and 'Function' blocks can have children.
    [BREAK] [BREAK]
    There are blocks for values, like 'Num' or 'Text' where you provide input, or blocks like 'True' and 'False'.
    Some blocks have slots, like operators. The 'Add' block has 2 slots for example. 'Print' block prints to the console window.
    [BREAK] [BREAK]
    To define and assign variables, use the 'Set' block.
    It has 2 slots, the first slot is for a 'Var' block (the variable you want to set) and the second slot is for any value to set the variable to.
    Once set, run the code by pressing ENTER and the value should appear on the top right. (Make sure Variable Display is toggled!)
    [BREAK] [BREAK]
    To call a 'Function' block, use the 'Call' block with the name of the function in the field.
    [BREAK] [BREAK]
    Press T to toggle this tutorial. Press C to view all of the controls.
    [BREAK]
    Press SPACE to begin inserting blocks!
"""
display_tutorial = lambda: create_dialog(utility.wrap_text(tutorial_text), (600, 648))

controls_elems = [
    "LMB: Move/Place/Interact", "RMB: Delete",
    "LSHIFT + LMB: Clone",
    "X: Clear",
    "V: Toggle Variable Display",
    "C: Show Controls",
    "T: Show Tutorial",
    "SPACE: Insert Menu",
    "ENTER: Run Code",
    "TAB: View Problem",
    "LEFT ARROW: Previous Level",
    "RIGHT ARROW: Next Level",
]
display_controls = lambda: create_dialog(controls_elems)

def display_vars(global_vars):
    count = 0
    for label, val in global_vars.items():
        surf = font.render(f"{label}: {str(val)}", True, (255, 255, 255))
        display.blit(surf, (0, count * 25))
        count += 1

# returns list of pos and sizes for btns so main module can handle click detection
# takes in list of tuples for button data
def display_insert_menu(btn_datas):
    surface = pygame.Surface((600, 600))
    surface.fill((236, 240, 241))

    ps = []

    # center in window
    ww, wh = pygame.display.get_surface().get_size()
    spos = (ww // 2 - 300, wh // 2 - 300)

    cur_width = 5
    cur_height = 5
    for btn_data in btn_datas:
        btn_text = font.render(btn_data[0], True, (255, 255, 255))
        text_rect = btn_text.get_rect()
        btn_surf = pygame.Surface((text_rect.width + 10, 40))

        # wrapping container functionality
        if cur_width + text_rect.width + 10 > 600:
            cur_width = 5
            cur_height += 45

        btn_surf.fill(btn_data[1])
        btn_surf.blit(btn_text, (5, 10))
        pos = (cur_width, cur_height)
        surface.blit(btn_surf, pos)
        btn_rect = btn_surf.get_rect()

        cur_width += btn_rect.width + 5
        ps.append(((pos[0] + spos[0], pos[1] + spos[1]), (btn_rect.width, btn_rect.height)))

    display.blit(surface, spos)

    return ps

def prepare():
    display.fill((0, 0, 0)) # black background

def finish():
    pygame.display.update() # update display

# to be called once per frame
def render(tasks):

    while tasks: # while tasks is not empty
        block = tasks.pop()

        # render text onto a surface
        text_surf = font.render(block.label, True, (255, 255, 255))

        # calculate width
        # TODO: move handling from below up here
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
            field_size = (field_text_surf.get_rect().width + 10, block.size[1])
            field_surf = pygame.Surface(field_size)
            field_surf.fill((236, 240, 241))#(255, 255, 255))
            field_surf.blit(field_text_surf, (5, block.size[1] // 2 - field_text_surf.get_rect().height // 2))
            block.field_ps = ((text_surf.get_rect().width + 10 + block.pos[0], block.pos[1]), field_size)
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



# game.py contains the class definition for the main Game class

# LIBRARY IMPORTS #
import pygame
import copy

# LOCAL MODULES #
import blocks as block_defs # 'blocks' is too valuable of a variable name to use on a module
import shared

class Game:
    # constructor, initialize all variables
    def __init__(self):
        self.global_blocks = []
        self.level = 1

        self.ghost = None
        self.field_block = None

        self.typing = False
        self.placing = False

    # increments level by n
    def inc_level(self, n):
        self.level = shared.clamp(self.level + n, 1, len(shared.LEVEL_DATA))

    # clears all of the blocks ingame
    def clear(self):
        self.global_blocks = []

    # recursively identifies what block is at pos, children have priority
    def identify_block(self, pos, blocks = None):
        if blocks == None: blocks = self.global_blocks
        for block in blocks:
            children = block.children[:]
            if isinstance(block, block_defs.SlotBlock):
                children.extend(list(block.slots.values())[:])
            ret = self.identify_block(pos, children)
            if ret: return ret
            if shared.check_collision(block.pos, block.size, pos): return block

    # handle placement input
    def begin_place(self, block_type):
        if not self.placing:
            self.ghost = getattr(block_defs, block_type)()
            self.ghost.opacity = 128
            self.placing = True

    def begin_move(self, target, pos):
        if self.placing or target == None: return

        self.ghost = target
        self.delete_block(pos)
        self.ghost.opacity = 128
        self.ghost.valid_parent = self.ghost.default_valid_parent # incase it's moving out of a slot
        self.placing = True

    def end_place(self, target, pos):
        if not self.placing: return

        self.placing = False
        self.ghost.opacity = 255
        if target:
            if isinstance(target, block_defs.SlotBlock):
                if not target.fill_slot(self.ghost, pos):
                    target.add_child(self.ghost)
                    del self.ghost
            else:
                target.add_child(self.ghost)
                del self.ghost
        else:
            self.global_blocks.append(self.ghost)
            del self.ghost
    
    # slotblock search has a slight variation, so a different helper function
    def delete_slotblock(self, pos, slots):
        for i, slot in slots.items():
            if isinstance(slot, block_defs.SlotBlock):
                if self.delete_slotblock(pos, slot.slots):
                    return True
            if shared.check_collision(slot.pos, slot.size, pos):
                del slots[i]
                return True
        return False

    # deletes whatever block is at pos, searches recursively
    def delete_block(self, pos, blocks = None):
        if blocks == None: blocks = self.global_blocks
        for i, block in enumerate(blocks):
            if isinstance(block, block_defs.SlotBlock):
                if self.delete_slotblock(pos, block.slots):
                    return True
            if self.delete_block(pos, block.children):
                return True
            if shared.check_collision(block.pos, block.size, pos):
                del blocks[i]
                return True
        return False

    # handle interacting with fieldblocks, pygame didn't support text input so i had to implement my own
    def begin_typing(self, target, pos):
        if self.typing: return
        if target and isinstance(target, block_defs.FieldBlock) and shared.check_collision(target.field_ps[0], target.field_ps[1], pos):
            self.typing = True
            self.field_block = target

    # processes whatever key input was made when typing on a fieldblock, only implements backspace and enter to unfocus
    def handle_typing(self, event):
        if event.key == pygame.K_RETURN:
            self.typing = False
            self.field_block.validate()
            self.field_block = None
        elif event.key == pygame.K_BACKSPACE:
            self.field_block.field = self.field_block.field[:-1]
        else:
            self.field_block.field += event.unicode

    # clones target block and begins placing
    def clone(self, target):
        if target != None and not placing:
            self.ghost = copy.deepcopy(target)
            self.ghost.opacity = 128
            self.placing = True

    # (re)starts the game, execute all start block_defs. at the end, check if the problem was completed
    def run(self):
        block_defs.global_vars = {}
        block_defs.global_fns = {}

        for root in self.global_blocks:
            if isinstance(root, block_defs.StartBlock):
                root.execute()

        # check if the level was completed
        if "goal" in block_defs.global_vars:
            if block_defs.global_vars["goal"] == shared.LEVEL_DATA[self.level][1]: # check if 'goal' variable is correct
                self.level = min(self.level + 1, len(shared.LEVEL_DATA)) # go to next level


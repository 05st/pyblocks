import pygame
import copy

import blocks as block_defs
import shared

class Game:
    def __init__(self):
        self.global_blocks = []
        self.level = 1

        self.ghost = None
        self.field_block = None

        self.typing = False
        self.placing = False

    def inc_level(self, n):
        self.level = shared.clamp(self.level + n, 1, len(shared.LEVEL_DATA))

    def clear(self):
        self.global_blocks = []

    def identify_block(self, pos, blocks = None):
        if blocks == None: blocks = self.global_blocks
        for block in blocks:
            children = block.children[:]
            if isinstance(block, block_defs.SlotBlock):
                children.extend(list(block.slots.values())[:])
            ret = self.identify_block(pos, children)
            if ret: return ret
            if shared.check_collision(block.pos, block.size, pos): return block

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

    def delete_slotblock(self, pos, slots):
        for i, slot in slots.items():
            if isinstance(slot, block_defs.SlotBlock):
                if self.delete_slotblock(pos, slot.slots):
                    return True
            if shared.check_collision(slot.pos, slot.size, pos):
                del slots[i]
                return True
        return False

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

    def begin_typing(self, target, pos):
        if self.typing: return
        if target and isinstance(target, block_defs.FieldBlock) and shared.check_collision(target.field_ps[0], target.field_ps[1], pos):
            self.typing = True
            self.field_block = target

    def handle_typing(self, event):
        if event.key == pygame.K_RETURN:
            self.typing = False
            self.field_block.validate()
            self.field_block = None
        elif event.key == pygame.K_BACKSPACE:
            self.field_block.field = self.field_block.field[:-1]
        else:
            self.field_block.field += event.unicode

    def clone(self, target):
        self.ghost = copy.deepcopy(target)
        self.ghost.opacity = 128
        self.placing = True

    # (re)starts the game, execute all start block_defs
    def run(self):
        block_defs.global_vars = {}
        block_defs.global_fns = {}

        for root in self.global_blocks:
            if isinstance(root, block_defs.StartBlock):
                root.execute()

        # check if the level was completed
        if "goal" in block_defs.global_vars:
            if block_defs.global_vars["goal"] == shared.LEVEL_DATA[self.level][1]:
                self.level = min(self.level + 1, len(shared.LEVEL_DATA))


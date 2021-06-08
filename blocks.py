import copy

import utility

DEF_SIZE = (200, 40)
DEF_POS = (0, 0)

class BaseBlock:
    default_valid_parent = True
    def __init__(self, label, color, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        self.label = label
        self.color = color
        self.opacity = opacity
        self.size = size
        self.pos = pos
        self.children = children[:]
        self.valid_parent = self.default_valid_parent

    def add_child(self, child):
        if self.valid_parent:
            self.children.append(child)

    def abs_height(self):
        height = self.size[1]
        for child in self.children:
            height += child.abs_height()
        return height

class SlotBlock(BaseBlock):
    def __init__(self, label, color, slots_count, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__(label, color, opacity, size, pos, children)
        self.slots_count = slots_count
        self.slots = copy.deepcopy(slots)
        self.slots_pos = {}

    def fill_slot(self, ghost, pos): # rewrite in future if possible
        for i, spos in self.slots_pos.items():
            if not i in self.slots:
                if utility.check_collision(spos, (self.size[1],) * 2, pos):
                    ghost.children = []
                    ghost.valid_parent = False
                    self.slots[i] = ghost
                    return True
        return False

class StartBlock(BaseBlock):
    def __init__(self, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Start", (46, 204, 113), opacity, size, pos, children)


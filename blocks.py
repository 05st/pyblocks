import copy

DEF_SIZE = (200, 40)
DEF_POS = (0, 0)

class BaseBlock:
    def __init__(self, label, color, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        self.label = label
        self.color = color
        self.opacity = opacity
        self.size = size
        self.pos = pos
        self.children = children[:]

    def add_child(self, child):
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

class StartBlock(BaseBlock):
    def __init__(self, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Start", (46, 204, 113), opacity, size, pos, children)


DEF_SIZE = (200, 40)
DEF_POS = (0, 0)

class BaseBlock:
    def __init__(self, label, color, opacity = 255, size = DEF_SIZE, pos = DEF_POS):
        self.label = label
        self.color = color
        self.opacity = opacity
        self.size = size
        self.pos = pos

class ParentBlock(BaseBlock):
    def __init__(self, label, color, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__(label, color, opacity, size, pos)
        self.children = children[:]



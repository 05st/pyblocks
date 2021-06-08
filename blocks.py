import copy

import utility

DEF_SIZE = (200, 40)
DEF_POS = (0, 0)

# BaseBlock is the root class, has children functionality
class BaseBlock:
    default_valid_parent = True
    default_valid_child = True
    def __init__(self, label, color, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        self.label = label
        self.color = color
        self.opacity = opacity
        self.size = size
        self.pos = pos
        self.children = children[:]
        self.valid_parent = self.default_valid_parent
        self.valid_child = self.default_valid_child

    def add_child(self, child):
        if self.valid_parent and child.valid_child:
            self.children.append(child)

    def abs_height(self):
        height = self.size[1]
        for child in self.children:
            height += child.abs_height()
        return height

    def execute(self):
        pass # to be overridden by inheriting classes

# SlotBlock class implements slot functionality into BaseBlcok
class SlotBlock(BaseBlock):
    def __init__(self, label, color, slots_count, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__(label, color, opacity, size, pos, children)
        self.slots_count = slots_count
        self.slots = copy.deepcopy(slots)
        self.slots_pos = {}

    def fill_slot(self, ghost, pos): # rewrite in future if possible
        if ghost.valid_child: # possibly use a different variable, like valid_item
            for i, spos in self.slots_pos.items():
                if not i in self.slots:
                    if utility.check_collision(spos, (self.size[1],) * 2, pos):
                        ghost.children = []
                        ghost.valid_parent = False
                        self.slots[i] = ghost
                        return True
        return False

# FieldBlocks contain a text field for input
class FieldBlock(BaseBlock):
    default_valid_parent = False
    def __init__(self, label, color, field = "", opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__(label, color, opacity, size, pos, children)
        self.field = field
        self.field_ps = None

    def validate(self):
        pass # to be filled in by inheriting classes

    def execute(self): # simply return the text
        return self.field

# FieldBlock which only accepts numbers
class NumBlock(FieldBlock):
    def __init__(self, field = "0.0", opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Num", (52, 152, 219), field, opacity, size, pos, children)

    def validate(self):
        filtered = ''.join(filter(lambda c: c.isdigit() or c == ".", self.field))
        if not filtered: filtered = "0.0"
        self.field = str(float(filtered))

# StartBlocks in global_blocks get executed, entry point block
class StartBlock(BaseBlock):
    default_valid_child = False
    def __init__(self, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Start", (46, 204, 113), opacity, size, pos, children)

    def execute(self): # execute all children
        for child in self.children:
            child.execute()

# AddBlocks add two numbers
class AddBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Add", (155, 89, 182), 2, slots, opacity, size, pos, children)

    def execute(self):
        val = float(self.slots[0].execute()) + float(self.slots[1].execute())
        print(val)
        return val


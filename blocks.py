import copy
import math

import utility

DEF_SIZE = (200, 40)
DEF_POS = (0, 0)

# dictionary for variables
global_vars = {}

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

# just a child class, no different functionality. 
# to make it easier for me
class TextBlock(FieldBlock):
    def __init__(self, field="text", opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Text", (52, 152, 219), field, opacity, size, pos, children)

# FieldBlock which only accepts numbers
class NumBlock(FieldBlock):
    def __init__(self, field = "0.0", opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Num", (52, 152, 219), field, opacity, size, pos, children)

    def validate(self):
        filtered = ''.join(filter(lambda c: c.isdigit() or c == ".", self.field))
        if not filtered: filtered = "0.0"
        self.field = str(float(filtered))

    def execute(self):
        return float(self.field)

# StartBlocks in global_blocks get executed, entry point block
class StartBlock(BaseBlock):
    default_valid_child = False
    def __init__(self, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Start", (46, 204, 113), opacity, size, pos, children)

    def execute(self): # execute all children
        for child in self.children:
            child.execute()

# PrintBlocks just print the result of the first slot
class PrintBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Print", (52, 73, 94), 1, slots, opacity, size, pos, children)

    def execute(self):
        if 0 in self.slots:
            print(self.slots[0].execute())

class IfBlock(SlotBlock):
    def __init__(self, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("If", (241, 196, 15), 1, slots, opacity, size, pos, children)

    def execute(self):
        if 0 in self.slots and self.slots[0].execute():
            for child in self.children:
                child.execute()

class WhileBlock(SlotBlock):
    def __init__(self, slots = {}, children = []):
        super().__init__("While", (241, 196, 15), 1, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        if 0 in self.slots:
            while self.slots[0].execute():
                for child in self.children:
                    child.execute()

class VarBlock(FieldBlock):
    default_valid_parent = False
    def __init__(self, field="a", opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Var", (192, 57, 43), field, opacity, size, pos, children)

    def validate(self):
        if not self.field:
            self.field = "a"

    def execute(self):
        if self.field in global_vars:
            return global_vars[self.field]

class SetBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}, opacity = 255, size = DEF_SIZE, pos = DEF_POS, children = []):
        super().__init__("Set", (231, 76, 60), 2, slots, opacity, size, pos, children)

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            if isinstance(self.slots[0], VarBlock):
                global_vars[self.slots[0].field] = self.slots[1].execute()

# operator blocks, i tried to automatically generate these classes but
# there was an issue with closures which i didn't have enough time to fix
class AddBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("+", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        try:
            return self.slots[0].execute() + self.slots[1].execute()
        except:
            pass

class SubBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("-", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        try:
            return self.slots[0].execute() - self.slots[1].execute()
        except:
            pass

class MulBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("x", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        try:
            return self.slots[0].execute() * self.slots[1].execute()
        except:
            pass

class DivBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("/", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        try:
            return self.slots[0].execute() / self.slots[1].execute()
        except:
            pass

class ModBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("%", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        try:
            # i had to do all these weird casts so types stayed consistent
            return float(int(self.slots[0].execute()) % int(self.slots[1].execute()))
        except:
            pass

class EqBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("=", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            a, b = self.slots[0].execute(), self.slots[1].execute()
            return math.isclose(a, b) if isinstance(a, float) and isinstance(b, float) else a == b

class GrBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__(">", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            a, b = self.slots[0].execute(), self.slots[1].execute()
            if isinstance(a, float) and isinstance(b, float):
                return a > b

class LsBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("<", (155, 89, 182), 2, slots, 255, DEF_SIZE, DEF_POS, [])

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            a, b = self.slots[0].execute(), self.slots[1].execute()
            if isinstance(a, float) and isinstance(b, float):
                return a < b


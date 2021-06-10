import copy
import math

import utility

# dictionary for variables
global_vars = {}
# functions
global_fns = {}

# BaseBlock is the root class, has children functionality
class BaseBlock:
    default_valid_parent = True
    default_valid_child = True
    def __init__(self, label, color, children = []):
        self.label = label
        self.color = color
        self.opacity = 255
        self.size = (200, 40) # will get filled in first iteration of rendering
        self.pos = (0, 0) # same here
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
    def __init__(self, label, color, slots_count, slots = {}, children = []):
        super().__init__(label, color, children)
        self.slots_count = slots_count
        self.slots = copy.deepcopy(slots)
        self.slots_pos = {}

    def fill_slot(self, ghost, pos): # rewrite in future if possible
        if not ghost.valid_child: return False
        for i, spos in self.slots_pos.items():
            if i not in self.slots and utility.check_collision(spos, (self.size[1],) * 2, pos):
                ghost.children = []
                ghost.valid_parent = False
                self.slots[i] = ghost
                return True
        return False

# FieldBlocks contain a text field for input
class FieldBlock(BaseBlock):
    default_valid_parent = False
    def __init__(self, label, color, field = "", children = []):
        super().__init__(label, color, children)
        self.field = field
        self.field_ps = None

    def validate(self):
        pass # to be filled in by inheriting classes

    def execute(self): # simply return the text
        return self.field

# just a child class, no different functionality. 
# to make it easier for me
class TextBlock(FieldBlock):
    def __init__(self, field="text"):
        super().__init__("Text", (52, 152, 219), field, [])

# FieldBlock which only accepts numbers
class NumBlock(FieldBlock):
    def __init__(self, field = "0.0"):
        super().__init__("Num", (52, 152, 219), field, [])

    def validate(self):
        filtered = ''.join(filter(lambda c: c.isdigit() or c == ".", self.field))
        if not filtered: filtered = "0.0"
        self.field = str(float(filtered))

    def execute(self):
        return float(self.field)

# blocks for boolean values
class TrueBlock(BaseBlock):
    default_valid_parent = False
    def __init__(self):
        super().__init__("True", (41, 128, 185), [])

    def execute(self):
        return True

class FalseBlock(BaseBlock):
    default_valid_parent = False
    def __init__(self):
        super().__init__("False", (41, 128, 185), [])

    def execute(self):
        return False

# StartBlocks in global_blocks get executed, entry point block
class StartBlock(BaseBlock):
    default_valid_child = False
    def __init__(self, children = []):
        super().__init__("Start", (46, 204, 113), children)

    def execute(self): # execute all children
        for child in self.children:
            child.execute()

# PrintBlocks just print the result of the first slot
class PrintBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("Print", (52, 73, 94), 1, slots, [])

    def execute(self):
        if 0 in self.slots:
            print(self.slots[0].execute())

class FuncBlock(FieldBlock):
    default_valid_parent = True
    default_valid_child = False
    def __init__(self, field = "func", children = []):
        super().__init__("Function", (230, 126, 34), field, children)
        global_fns[field] = self
        self.prev_field = field

    def __del__(self):
        if self.field in global_fns:
            global_fns.pop(self.field)

    def validate(self):
        if not self.field:
            self.field = "func"
        global_fns.pop(self.prev_field)
        global_fns[self.field] = self
        self.prev_field = self.field

    def execute(self):
        for child in self.children:
            r = child.execute()
            if isinstance(child, RetBlock): return r

class CallBlock(FieldBlock):
    def __init__(self, field = "func"):
        super().__init__("Call", (211, 84, 0), field, [])

    def validate(self):
        if not self.field:
            self.field = "func"

    def execute(self):
        if self.field in global_fns:
            return global_fns[self.field].execute()

class RetBlock(SlotBlock):
    def __init__(self, slots = {}):
        super().__init__("Return", (52, 73, 94), 1, slots, [])

    def execute(self):
        if 0 in self.slots:
            return self.slots[0].execute()

class IfBlock(SlotBlock):
    def __init__(self, slots = {}, children = []):
        super().__init__("If", (241, 196, 15), 1, slots, children)

    def execute(self):
        if 0 in self.slots and self.slots[0].execute():
            for child in self.children:
                child.execute()

class WhileBlock(SlotBlock):
    def __init__(self, slots = {}, children = []):
        super().__init__("While", (241, 196, 15), 1, slots, children)

    def execute(self):
        if 0 in self.slots:
            while self.slots[0].execute():
                for child in self.children:
                    child.execute()

class VarBlock(FieldBlock):
    def __init__(self, field="a"):
        super().__init__("Var", (192, 57, 43), field, [])

    def validate(self):
        if not self.field:
            self.field = "a"

    def execute(self):
        if self.field in global_vars:
            return global_vars[self.field]

class SetBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("Set", (231, 76, 60), 2, slots, [])

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            if isinstance(self.slots[0], VarBlock):
                global_vars[self.slots[0].field] = self.slots[1].execute()

# binary operator class for more code reusability
class OpBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, label, oper):
        super().__init__(label, (155, 89, 182), 2, {}, [])
        self.oper = oper

    def execute(self):
        try:
            return self.oper(self.slots[0].execute(), self.slots[1].execute())
        except: pass

AddBlock = lambda: OpBlock("+", lambda a, b: a + b)
SubBlock = lambda: OpBlock("-", lambda a, b: a - b)
MulBlock = lambda: OpBlock("*", lambda a, b: a * b)
DivBlock = lambda: OpBlock("/", lambda a, b: a / b)
ModBlock = lambda: OpBlock("%", lambda a, b: float(int(a) / int(b)))
EqBlock = lambda: OpBlock("=", lambda a, b: math.isclose(a, b) if isinstance(a, float) and isinstance(b, float) else a == b)
NEqBlock = lambda: OpBlock("!=", lambda a, b: (not math.isclose(a, b)) if isinstance(a, float) and isinstance(b, float) else a != b)
GrBlock = lambda: OpBlock(">", lambda a, b: a > b)
LsBlock = lambda: OpBlock("<", lambda a, b: a < b)

# had to implement this separately since it's unary
class NotBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("!", (155, 89, 182), 1, slots, [])

    def execute(self):
        if 0 in self.slots:
            val = self.slots[0].execute()
            if isinstance(val, bool): return not val


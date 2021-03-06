# blocks.py contains block class definitions
# since interpretation wasn't that complex, i put the interpreter code inside the classes themselves (execute() method)

# LIBRARY IMPORTS #
import copy
import math

# LOCAL MODULES #
import shared

# due to this class also being the interpreter, it was the best place to put these variables
# dictionary for variables
global_vars = {}
# functions
global_fns = {}

# BaseBlock is the root class, has children functionality
class BaseBlock:
    default_valid_parent = True # determines if block can contain children
    default_valid_child = True # determines if block can be added as child or into slot
    def __init__(self, label, color, children = []):
        self.label = label
        self.color = color
        self.opacity = 255
        self.size = (200, 30) # will get filled in first iteration of rendering
        self.pos = (0, 0) # same here
        self.children = children[:]
        self.valid_parent = self.default_valid_parent
        self.valid_child = self.default_valid_child

    def add_child(self, child):
        if self.valid_parent and child.valid_child:
            self.children.append(child)

    # accounts for the 2px border
    def abs_height(self):
        height = self.size[1] + 4
        for child in self.children:
            height += child.abs_height()
        return height

    def cleanup(self):
        pass # to be overridden (i didn't end up using this method for anything other than funcblocks)

    def execute(self):
        pass # to be overridden by inheriting classes


# SlotBlock class implements slot functionality into BaseBlcok
class SlotBlock(BaseBlock):
    def __init__(self, label, color, slots_count, slots = {}, children = []):
        super().__init__(label, color, children)
        self.slots_count = slots_count
        self.slots = copy.deepcopy(slots)
        self.slots_pos = {}

    def fill_slot(self, ghost, pos): # fill in the slot that was clicked on, if any. return true if success
        if not ghost.valid_child: return False
        for i, spos in self.slots_pos.items():
            if i not in self.slots and shared.check_collision(spos, (self.size[1],) * 2, pos):
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

# just a more specific class, no different functionality. 
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


# StartBlocks in global_blocks get executed first, entry point block
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

# used inside function blocks
class RetBlock(SlotBlock):
    def __init__(self, slots = {}):
        super().__init__("Return", (52, 73, 94), 1, slots, [])

    def execute(self):
        if 0 in self.slots:
            return self.slots[0].execute()


# really basic function implementation, no paramters support (although you can use variables to emulate)
class FuncBlock(FieldBlock):
    default_valid_parent = True
    default_valid_child = False
    def __init__(self, field = "func", children = []):
        super().__init__("Function", (230, 126, 34), field, children)
        self.prev_field = field
        global_fns[self.field] = self

    def validate(self):
        if not self.field:
            self.field = "func"
        global_fns[self.prev_field] = None
        global_fns[self.field] = self
        self.prev_field = self.field

    def cleanup(self):
        if global_fns[self.field] == self:
            global_fns[self.field] = None

    def execute(self):
        for child in self.children:
            val = child.execute()
            if isinstance(child, RetBlock):
                return val

# block that is used to call functions
class CallBlock(FieldBlock):
    def __init__(self, field = "func"):
        super().__init__("Call", (211, 84, 0), field, [])

    def validate(self):
        if not self.field:
            self.field = "func"

    def execute(self):
        if self.field in global_fns and global_fns[self.field] != None:
            return global_fns[self.field].execute()

# control flow blocks
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

class ForBlock(SlotBlock):
    def __init__(self, slots = {}, children = []):
        super().__init__("For", (241, 196, 15), 3, slots, children)

    def execute(self):
        try:
            self.slots[0].execute()
            while self.slots[1].execute():
                for child in self.children:
                    child.execute()
                self.slots[2].execute()
        except: pass

# variable block
class VarBlock(FieldBlock):
    def __init__(self, field="a"):
        super().__init__("Var", (192, 57, 43), field, [])

    def validate(self):
        if not self.field:
            self.field = "a"

    def execute(self):
        if self.field in global_vars:
            return global_vars[self.field]

# SetBlocks are used to assign and define variables
class SetBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("Set", (231, 76, 60), 2, slots, [])

    def execute(self):
        if 0 in self.slots and 1 in self.slots:
            if isinstance(self.slots[0], VarBlock):
                global_vars[self.slots[0].field] = self.slots[1].execute()


# binary operator class for more code reusability
class BOpBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, label, oper):
        super().__init__(label, (155, 89, 182), 2, {}, [])
        self.oper = oper

    def execute(self):
        try:
            return self.oper(self.slots[0].execute(), self.slots[1].execute())
        except: pass

AddBlock = lambda: BOpBlock("+", lambda a, b: a + b)
SubBlock = lambda: BOpBlock("-", lambda a, b: a - b)
MulBlock = lambda: BOpBlock("x", lambda a, b: a * b)
DivBlock = lambda: BOpBlock("/", lambda a, b: a / b)
ModBlock = lambda: BOpBlock("%", lambda a, b: float(int(a) % int(b)))
EqBlock = lambda: BOpBlock("=", lambda a, b: math.isclose(a, b) if isinstance(a, float) and isinstance(b, float) else a == b)
NEqBlock = lambda: BOpBlock("!=", lambda a, b: (not math.isclose(a, b)) if isinstance(a, float) and isinstance(b, float) else a != b)
GrBlock = lambda: BOpBlock(">", lambda a, b: a > b)
LsBlock = lambda: BOpBlock("<", lambda a, b: a < b)
AndBlock = lambda: BOpBlock("&&", lambda a, b: a and b)
OrBlock = lambda: BOpBlock("||", lambda a, b: a or b)

# unary operators
class UOpBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, label, oper):
        super().__init__(label, (155, 89, 182), 1, {}, [])
        self.oper = oper

    def execute(self):
        try:
            return self.oper(self.slots[0].execute())
        except: pass

NotBlock = lambda: UOpBlock("!", lambda a: not a)
RndBlock = lambda: UOpBlock("round", lambda a: float(int(a + 0.5)))
FlrBlock = lambda: UOpBlock("floor", lambda a: float(int(a)))
CelBlock = lambda: UOpBlock("ceil", lambda a: float(int(a + 1)))

# these operators also set the variable
class IncBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("++", (142, 68, 173), 1, slots, [])

    def execute(self):
        try:
            global_vars[self.slots[0].field] += 1
            return global_vars[self.slots[0].field]
        except: pass

class DecBlock(SlotBlock):
    default_valid_parent = False
    def __init__(self, slots = {}):
        super().__init__("--", (142, 68, 173), 1, slots, [])

    def execute(self):
        try:
            global_vars[self.slots[0].field] -= 1
            return global_vars[self.slots[0].field]
        except: pass


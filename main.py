import pygame

display = pygame.display.set_mode((1280, 720))
pygame.font.init()
font = pygame.font.SysFont("Arial", 25)

block_height = 40 # block height is universal
child_indent = 20 # pixels children get indented by
block_width_min = 200

# determine collision between a point and a rectangle
def pr_collision(r, s, p):
    x, y = p
    hx, hy = r
    return (x > hx and x < (hx + s[0])) and (y > hy and y < (hy + s[1])) # pygame collisionpoint() didn't work

# base Block class which all types of blocks inherit from
class Block:
    def __init__(self, text, color, pos = (0, 0), children = []):
        self.text = text
        self.color = color
        self.pos = pos
        self.children = children[:]
        self.num_child = len(children) # for more efficient count_children()
        self.width = block_width_min
        self.surface = pygame.Surface((self.width, block_height))
        self.surface.fill(self.color)
        self.surface.blit(font.render(self.text, True, (255, 255, 255)), (0, 0))
    def update_children(self):
        child_count = 0
        for child in self.children:
            child_count += 1
            child.pos = (self.pos[0] + child_indent, self.pos[1] + (block_height + 2) * child_count)
            child_count += child.count_all_children()
    def add_child(self, child):
        self.children.append(child)
        self.num_child += 1
    def count_all_children(self):
        count = self.num_child
        for child in self.children:
            count += child.count_all_children()
        return count
    def render(self):
        self.update_children()
        display.blit(self.surface, self.pos)
        for child in self.children:
            child.render()
    def execute(self):
        pass

# block type with slot functionality implemented
class SlotBlock(Block):
    def __init__(self, text, color, num_slots, pos = (0, 0), children = []):
        super().__init__(text, color, pos, children)
        self.num_slots = num_slots
        self.slots = {}
        self.slot_ps = {}
    def fill_slot(self, block, pos):
        for i, s in self.slot_ps.items():
            if pr_collision(s[0], s[1], pos):
                if not i in self.slots:
                    block.children = []
                    self.slots[i] = block
                    return True
        return False
    def get_slot(self, pos):
        for i, s in self.slot_ps.items():
            if pr_collision(s[0], s[1], pos):
                if i in self.slots:
                    return i
    def del_slot(self, i):
        self.slots.pop(i)
        self.slot_ps.pop(i)
    def update_slots(self):
        new_width = 100 + 50 * self.num_slots
        for i, slot in self.slots.items():
            new_width -= 50
            new_width += slot.width
        new_width += 5 * (self.num_slots - 1) # padding
        # must update surface due to width not being static
        if self.width != new_width:
            self.width = new_width
            self.surface = pygame.Surface((self.width, block_height))
            self.surface.fill(self.color)
            self.surface.blit(font.render(self.text, True, (255, 255, 255)), (0, 0))
        width_cur = 0
        for i in range(self.num_slots):
            self.slot_ps[i] = {}
            if i in self.slots:
                slot_surf = pygame.Surface((self.slots[i].width, block_height))
                self.slot_ps[i][0] = (self.pos[0] + 100 + width_cur + 5 * i, self.pos[1])
                self.slot_ps[i][1] = (self.slots[i].width, block_height)
                slot_surf.fill((255, 255, 255))
                slot_surf.blit(self.slots[i].surface, (0, 0))
                self.surface.blit(slot_surf, (100 + width_cur + 5 * i, 0))
                width_cur += self.slots[i].width
            else:
                slot_surf = pygame.Surface((50, block_height))
                self.slot_ps[i][0] = (self.pos[0] + 100 + width_cur + 5 * i, self.pos[1])
                self.slot_ps[i][1] = (50, block_height)
                slot_surf.fill((255, 255, 255))
                self.surface.blit(slot_surf, (100 + width_cur + 5 * i, 0))
                width_cur += 50
    def render(self):
        self.update_children()
        self.update_slots()
        display.blit(self.surface, self.pos)
        for child in self.children:
            child.render()

# StartBlocks get executed first; entry point to game
class StartBlock(Block):
    def __init__(self, pos = (0, 0), children = []):
        super().__init__("Start", (46, 204, 113), pos, children)
    def execute(self):
        for child in self.children:
            child.execute()

# list of all blocks. blocks are essentially trees of nodes
block_trees = [ 
    StartBlock((100, 100), [
        SlotBlock("test", (52, 152, 219), 2),
        SlotBlock("test", (52, 152, 219), 3),
        SlotBlock("test", (52, 152, 219), 4),
    ]),
]

def execute_starts():
    for root in block_trees:
        if isinstance(root, StartBlock):
            root.execute()

placing = False
ghost_block = None
def begin_placing():
    global placing, ghost_block
    if not placing:
        ghost_block = Block("testing", (231, 76, 60))
        ghost_block.surface.set_alpha(128)
        placing = True

# iterative search
def identify_block(pos):
    for root in block_trees:
        queue = [root]
        while queue:
            head = queue.pop(0)
            if pr_collision(head.pos, (head.width, block_height), pos):
                return head
            queue += head.children

def end_placing():
    global placing, ghost_block
    if placing:
        placing = False
        pos = pygame.mouse.get_pos()
        parent = identify_block(pos)
        ghost_block.surface.set_alpha(255)
        if parent:
            if isinstance(parent, SlotBlock):
                if not parent.fill_slot(ghost_block, pos):
                    parent.add_child(ghost_block)
            else:
                parent.add_child(ghost_block)
        else:
            block_trees.append(ghost_block)
        del ghost_block

def begin_move():
    global placing, ghost_block, block_trees
    if not placing:
        pos = pygame.mouse.get_pos()
        ghost_block = identify_block(pos)
        if ghost_block:
            if isinstance(ghost_block, SlotBlock):
                slot_id = ghost_block.get_slot(pos)
                if slot_id != None: 
                    slot = ghost_block.slots[slot_id]
                    ghost_block.del_slot(slot_id)
                    ghost_block = slot
                else:
                    delete_block(pos, block_trees)
            else:
                delete_block(pos, block_trees)
            ghost_block.surface.set_alpha(128)
            placing = True

# recursive search
def delete_block(pos, blocks):
    for i in range(len(blocks)): # since we want to modify the array we can't do "for x in blocks"
        if pr_collision(blocks[i].pos, (blocks[i].width, block_height), pos):
            if isinstance(blocks[i], SlotBlock):
                slot_id = blocks[i].get_slot(pos)
                if slot_id != None:
                    blocks[i].del_slot(slot_id)
                else:
                    del blocks[i]
            else:
                del blocks[i]
            break
        blocks[i].children = delete_block(pos, blocks[i].children[:])
        blocks[i].num_child = len(blocks[i].children)
    return blocks

input_map = {
    pygame.K_SPACE: execute_starts,
    pygame.K_1: begin_placing
}

running = True
while running:
    for event in pygame.event.get():
        running = event.type != pygame.QUIT
        if event.type == pygame.KEYDOWN:
            if event.key in input_map:
                input_map[event.key]()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if placing:
                    end_placing()
                else:
                    begin_move()
            elif event.button == 3:
                block_trees = delete_block(pygame.mouse.get_pos(), block_trees[:])

    display.fill((0, 0, 0))
    for root in block_trees:
        root.render()
    if placing:
        x, y = pygame.mouse.get_pos()
        ghost_block.pos = (x - ghost_block.width // 2, y - block_height // 2)
        ghost_block.render()
    pygame.display.update()


import blocks

# checks collision between rectangle and point
def check_collision(pos, size, point):
    rx, ry = pos
    px, py = point
    w, h = size
    return (px > rx and px < rx + w) and (py > ry and py < ry + h)

# recursive search, checks children first
def identify_block(pos, roots):
    for root in roots:
        children = root.children[:]
        if isinstance(root, blocks.SlotBlock):
            children += list(root.slots.values())[:]
        ret = identify_block(pos, children)
        if ret != None: return ret
        if check_collision(root.pos, root.size, pos): return root

# returns a list of strings that are all less than 70 characters
def wrap_text(text):
    words = text.split()
    ret = []

    curr = ""
    for word in words:
        if len(curr) + len(word) > 70 or word == "[BREAK]":
            ret.append(curr)
            curr = "" if word == "[BREAK]" else word
        else:
            curr += f" {word}"
    ret.append(curr)
    return ret

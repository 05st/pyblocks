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
        children = root.children
        ret = identify_block(pos, children)
        if ret != None: return ret
        if check_collision(root.pos, root.size, pos): return root


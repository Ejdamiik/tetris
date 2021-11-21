from typing import List, Tuple
from random import randint

Block = List[Tuple[int, int]]

BLOCK_I, BLOCK_J, BLOCK_L, BLOCK_S, BLOCK_Z, BLOCK_T, BLOCK_O = range(7)
LEFT, RIGHT, ROTATE_CW, ROTATE_CCW, DOWN, DROP, QUIT = range(7)

WALL = "##"
SQUARE = "[]"
EMPTY = "  "

Arena = List[List[bool]]
Anchor = Tuple[int, int]


def coords(block_type: int) -> Block:

    BLOCKS = [
        [(0, -1), (0, 0), (0, 1), (0, 2)],
        [(-1, 1), (0, 1), (0, 0), (0, - 1)],
        [(1, 1), (0, 1), (0, 0), (0, - 1)],
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(-1, 0), (0, 0), (0, 1), (1, 0)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
    ]

    return BLOCKS[block_type]


def rotate_cw(coords: Block) -> Block:

    return [(-y, x) for x, y in coords]


def rotate_ccw(coords: Block) -> Block:

    return [(y, -x) for x, y in coords]


def new_arena(cols: int, rows: int) -> Arena:

    return [[False] * cols for j in range(rows)]


def is_occupied(arena: Arena, x: int, y: int) -> bool:

    return (0 > y or y > len(arena) - 1) \
        or (0 > x or x > len(arena[0]) - 1) \
        or arena[y][x]


def set_occupied(arena: Arena, x: int, y: int, occupied: bool) -> None:

    arena[y][x] = occupied


def draw(arena: Arena, score: int) -> None:

    for row in arena:

        print(WALL, end="")

        for e in row:
            print(SQUARE, end="") if e else print(EMPTY,  end="")

        print(WALL)

    print((len(arena[0]) + 2) * WALL)

    spaces = 2 * len(arena[0]) - len("Score:") - len(str(score))
    print("  " + "Score:" + (spaces * " ") + str(score))


def next_block() -> Block:

    return coords(randint(0, 6))


def poll_event() -> int:

    # Not really implemented (no need to)
    return 2


def get_initial_anchor(arena: Arena, block: Block) -> Anchor:
    """
    Function to get real position of anchor at the beginning
    """

    columns = len(arena[0])

    y_min = min(block, key=lambda x: x[1])[1]

    x_min = min(block, key=lambda x: x[0])[0]
    x_max = max(block, key=lambda x: x[0])[0]
    block_width = x_max - x_min + 1

    width_diff = columns - block_width

    padding = width_diff // 2

    anchor_x = -x_min + padding
    anchor_y = -y_min

    return (anchor_x, anchor_y)


def shift_block(block: Block, anchor: Anchor) -> Block:

    anchor_x, anchor_y = anchor

    return [(x + anchor_x, y + anchor_y) for x, y in block]


def check_availibility(arena: Arena, real_block: Block) -> bool:

    for x, y in real_block:

        if is_occupied(arena, x, y):
            return False

    return True


def modify_arena(arena: Arena, real_block: Block, status: bool) -> None:

    for x, y in real_block:

        set_occupied(arena, x, y, status)


def move(arena: Arena,
         block: Block,
         anchor: Anchor,
         direction: Tuple[int, int],
         event: int) -> Tuple[Anchor, Block]:

    dx, dy = direction
    x, y = anchor
    old = shift_block(block, anchor)
    modify_arena(arena, old, False)

    old_block = block

    if event == 2:
        block = rotate_cw(block)

    elif event == 3:
        block = rotate_ccw(block)

    else:
        anchor = x + dx, y + dy

    new = shift_block(block, anchor)

    # If we cannot add new block, we add back the old one
    if not check_availibility(arena, new):
        modify_arena(arena, old, True)
        return (x, y), old_block

    modify_arena(arena, new, True)

    return anchor, block


def eval_score(arena: Arena) -> int:

    score = 0
    filled = 0

    for row_i in range(len(arena)):

        if False not in arena[row_i]:

            move_rows(arena, row_i - 1)
            filled += 1

    score += filled ** 2

    return score


def move_rows(
        arena: Arena, last_row_to_move: int,
) -> None:

    width = len(arena[0])
    for y in range(last_row_to_move, -1, -1):

        row = arena[y].copy()

        # Clearing row
        arena[y] = [False] * width
        arena[y + 1] = row


def play(arena: Arena) -> int:

    active = False
    score = 0

    while True:

        current_block = next_block()
        anchor = get_initial_anchor(arena, current_block)
        real = shift_block(current_block, anchor)

        if not check_availibility(arena, real):
            draw(arena, score)
            return score

        modify_arena(arena, real, True)

        active = True

        while active:

            draw(arena, score)
            event = poll_event()

            old_anchor = anchor
            # From every 'move' event we gen new position of anchor and
            # current block type
            if event == DOWN:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (0, 1), 4)

                if old_anchor == anchor:

                    active = False

            elif event == DROP:

                first = True

                while anchor != old_anchor or first:

                    old_anchor = anchor
                    anchor, current_block = move(
                        arena, current_block, old_anchor, (0, 1), 5)
                    first = False

                active = False

            elif event == LEFT:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (-1, 0), 0)

            elif event == RIGHT:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (1, 0), 1)

            elif event == ROTATE_CW:

                anchor, current_block = move(
                    arena, current_block, anchor, (0, 0), 2)

            elif event == ROTATE_CCW:

                anchor, current_block = move(
                    arena, current_block, anchor, (0, 0), 3)

            elif event == QUIT:
                draw(arena, score)
                return score
        # Evaluating score when block gets inactive
        score += eval_score(arena)

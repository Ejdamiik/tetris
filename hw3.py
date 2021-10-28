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

    new = []

    for x, y in coords:
        new.append((-y, x))

    return new


def rotate_ccw(coords: Block) -> Block:

    new = []

    for x, y in coords:
        new.append((y, -x))

    return new


def new_arena(cols: int, rows: int) -> Arena:

    arena = [[False for i in range(cols)] for j in range(rows)]
    return arena


def is_occupied(arena: Arena, x: int, y: int) -> bool:

    if 0 > y or y > len(arena) - 1:
        return True

    if 0 > x or x > len(arena[0]) - 1:
        return True

    # coords in reversed order bcs of matrix coords work reversed
    return arena[y][x]


def set_occupied(arena: Arena, x: int, y: int, occupied: bool) -> None:

    arena[y][x] = occupied


def draw(arena: Arena, score: int) -> None:

    for row in arena:

        print(WALL, end="")

        for e in row:
            if e:
                print(SQUARE, end="")
            else:
                print(EMPTY,  end="")

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


def get_real_pos(block: Block, anchor: Anchor) -> Block:

    real = []

    anchor_x, anchor_y = anchor

    for x, y in block:

        real_x = x + anchor_x
        real_y = y + anchor_y

        real.append((real_x, real_y))

    return real


def add_to_arena(arena: Arena, real_block: Block) -> None:

    for x, y in real_block:

        set_occupied(arena, x, y, True)


def check_availibility(arena: Arena, real_block: Block) -> bool:

    for x, y in real_block:

        if is_occupied(arena, x, y):
            return False

    return True


def delete_from_arena(arena: Arena, real_block: Block) -> None:

    for x, y in real_block:
        set_occupied(arena, x, y, False)


def move(arena: Arena,
         block: Block,
         anchor: Anchor,
         direction: Tuple[int, int],
         rotate_type: int = 0) -> Tuple[Anchor, Block]:

    dx, dy = direction
    x, y = anchor
    old = get_real_pos(block, anchor)
    delete_from_arena(arena, old)

    old_block = block

    if rotate_type == 1:
        block = rotate_cw(block)

    elif rotate_type == 2:
        block = rotate_ccw(block)

    else:
        anchor = x + dx, y + dy

    new = get_real_pos(block, anchor)

    status = check_availibility(arena, new)

    # If we cannot add new block, we add back the old one
    if status is False:
        add_to_arena(arena, old)
        return (x, y), old_block

    add_to_arena(arena, new)

    return anchor, block


def eval_score(arena: Arena, score: int) -> int:

    filled = 0
    first_filled = None

    for row_i in range(len(arena)):

        if False not in arena[row_i]:

            if filled == 0:
                first_filled = row_i

            filled += 1
            last_filled = row_i
            clear_row(arena, row_i)

    score += filled ** 2

    if first_filled:
        move_rows(arena, first_filled - 1, last_filled)
    return score


def move_rows(
        arena: Arena, last_row_to_move: int, last_able_row: int
        ) -> None:

    for row_i in range(last_row_to_move, -1, -1):

        for column_i in range(len(arena[0])):

            x = column_i
            y = row_i

            occupation_status = is_occupied(arena, x, y)
            set_occupied(arena, x, y, False)

            while not is_occupied(arena, x, y) and y <= last_able_row:
                y += 1

            set_occupied(arena, x, y - 1, occupation_status)


def clear_row(arena: Arena, row_i: int) -> None:

    for col in range(len(arena[0])):

        set_occupied(arena, col, row_i, False)


def play(arena: Arena) -> int:

    active = False
    score = 0

    while True:

        current_block = next_block()
        anchor = get_initial_anchor(arena, current_block)
        real = get_real_pos(current_block, anchor)

        status = check_availibility(arena, real)
        if status is False:
            draw(arena, score)
            return score

        add_to_arena(arena, real)

        active = True

        while active:

            draw(arena, score)
            event = poll_event()

            old_anchor = anchor
            # From every 'move' event we gen new position of anchor and
            # current block type
            if event == DOWN:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (0, 1))

                if old_anchor == anchor:

                    active = False

            elif event == DROP:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (0, 1))

                while anchor != old_anchor:

                    old_anchor = anchor
                    anchor, current_block = move(
                        arena, current_block, old_anchor, (0, 1))

                active = False

            elif event == LEFT:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (-1, 0))

            elif event == RIGHT:

                anchor, current_block = move(
                    arena, current_block, old_anchor, (1, 0))

            elif event == ROTATE_CW:

                anchor, current_block = move(
                    arena, current_block, anchor, (0, 0), 1)

            elif event == ROTATE_CCW:

                anchor, current_block = move(
                    arena, current_block, anchor, (0, 0), 2)

            elif event == QUIT:
                draw(arena, score)
                return score

        # Evaluating score when block gets inactive
        score = eval_score(arena, score)

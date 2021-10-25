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

    # occupied -- True
    if 0 > y or y > len(arena) - 1:
        return True

    if 0 > x or x > len(arena[0]) - 1:
        return True

    return arena[y][x]


def set_occupied(arena: Arena, x: int, y: int, occupied: bool) -> None:

    arena[y][x] = occupied


def draw(arena: Arena, score: int) -> None:

    # Desk
    for row in arena:

        print(WALL, end="")

        for e in row:
            if e:
                print(SQUARE, end="")
            else:
                print(EMPTY,  end="")

        print(WALL)

    # Lower border
    print((len(arena[0]) + 2) * WALL)

    # Score
    spaces = 2 * len(arena[0]) - len("Score:") - len(str(score))
    print("  " + "Score:" + (spaces * " ") + str(score))


def next_block() -> Block:

    return coords(randint(0, 6))


def poll_event() -> int:

    return None


def get_initial_head(arena: Arena, block: Block) -> Anchor:

    columns = len(arena[0])

    y_min = min(block, key=lambda x: x[1])[1]

    middle = columns // 2

    head_x = middle - 1
    head_y = -y_min

    head = (head_x, head_y)
    return head


def get_real_pos(block: Block, head: Anchor) -> Block:

    real = []

    head_x, head_y = head

    for x, y in block:

        real_x = x + head_x
        real_y = y + head_y

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
         head: Anchor,
         direction: Tuple[int, int],
         rotate_type: int = 0) -> Tuple[Anchor, Block]:

    dx, dy = direction
    x, y = head
    old = get_real_pos(block, head)
    delete_from_arena(arena, old)

    old_block = block

    if rotate_type == 1:
        block = rotate_cw(block)

    elif rotate_type == 2:
        block = rotate_ccw(block)

    else:
        head = x + dx, y + dy

    new = get_real_pos(block, head)

    status = check_availibility(arena, new)

    if status is False:
        add_to_arena(arena, old)
        return (x, y), old_block

    add_to_arena(arena, new)

    return head, block


def eval_score(arena: Arena, score: int) -> int:

    filled = 0

    for row_i in range(len(arena)):

        if False not in arena[row_i]:
            filled += 1
            clear_row(arena, row_i)

    score += filled ** 2

    return score


def clear_row(arena: Arena, row_i: int) -> None:

    for col in range(len(arena[0])):

        set_occupied(arena, col, row_i, False)


def play(arena: Arena) -> int:

    active = False
    score = 0

    while True:

        current_block = next_block()
        head = get_initial_head(arena, current_block)
        real = get_real_pos(current_block, head)

        status = check_availibility(arena, real)
        if status is False:
            draw(arena, score)
            return score

        add_to_arena(arena, real)

        active = True

        while active:

            draw(arena, score)
            event = poll_event()

            old_head = head
            if event == DOWN:

                head, current_block = move(
                    arena, current_block, old_head, (0, 1))

                if old_head == head:

                    active = False

            elif event == DROP:

                head, current_block = move(
                    arena, current_block, old_head, (0, 1))

                while head != old_head:

                    old_head = head
                    head, current_block = move(
                        arena, current_block, old_head, (0, 1))

                active = False

            elif event == LEFT:

                head, current_block = move(
                    arena, current_block, old_head, (-1, 0))

            elif event == RIGHT:

                head, current_block = move(
                    arena, current_block, old_head, (1, 0))

            elif event == ROTATE_CW:

                head, current_block = move(
                    arena, current_block, head, (0, 0), 1)

            elif event == ROTATE_CCW:

                head, current_block = move(
                    arena, current_block, head, (0, 0), 2)

            elif event == QUIT:
                draw(arena, score)
                return score

            score = eval_score(arena, score)

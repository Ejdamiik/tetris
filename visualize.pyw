from collections import deque
from typing import Deque
import tkinter as tk
import time

import engine


# game parameters; feel free to change them
ROWS = 22
COLS = 10
DELAY = 1000  # how often shall DOWN happen automatically; in milliseconds

BORDER = 32
CELL_SIZE = 20
FONT = ('system', '16')
TILE_COLOUR = 'blue'

EVENTS = {
    'a': engine.LEFT,
    'Left': engine.LEFT,
    'd': engine.RIGHT,
    'Right': engine.RIGHT,
    's': engine.DOWN,
    'Down': engine.DOWN,
    'space': engine.DROP,
    'q': engine.ROTATE_CCW,
    'Prior': engine.ROTATE_CCW,
    'e': engine.ROTATE_CW,
    'Next': engine.ROTATE_CW,
    'x': engine.QUIT,
}

GO_MSG = 'Game over. Final score: {}.\nPress r to restart or x to quit.'


class Tetris:
    def __init__(self) -> None:
        self.running = False
        self.events: Deque[int] = deque()

        self.root = tk.Tk()
        self.canvas = tk.Canvas(
            width=2 * BORDER + (COLS + 2) * CELL_SIZE,
            height=4 * BORDER + (ROWS + 1) * CELL_SIZE,
        )
        self.draw_border()
        self.canvas.pack()

        self.root.bind_all('<Key>', self.key_event)

    def draw_border(self) -> None:
        for x in BORDER, BORDER + (COLS + 1) * CELL_SIZE:
            self.canvas.create_rectangle(
                x, BORDER,
                x + CELL_SIZE, BORDER + (ROWS + 1) * CELL_SIZE,
                fill='black'
            )

        self.canvas.create_rectangle(
            BORDER, BORDER + ROWS * CELL_SIZE,
            BORDER + (COLS + 2) * CELL_SIZE, BORDER + (ROWS + 1) * CELL_SIZE,
            fill='black'
        )

    def start(self) -> None:
        self.root.update()
        self.root.event_generate('<Key>', keysym='r')
        self.root.mainloop()

    def run(self) -> None:
        self.running = True
        self.root.after(DELAY, self.fall)
        score = engine.play(engine.new_arena(COLS, ROWS))
        self.canvas.delete('score')
        self.canvas.create_text(
            BORDER + (COLS + 2) * CELL_SIZE // 2,
            5 * BORDER // 2 + (ROWS + 1) * CELL_SIZE,
            text=GO_MSG.format(score), font=FONT,
            justify=tk.CENTER, tags=('content', 'score')
        )
        self.running = False

    def fall(self) -> None:
        if self.running:
            self.events.append(engine.DOWN)
            self.root.after(DELAY, self.fall)

    def key_event(self, ev: tk.Event) -> None:
        if self.running:
            event = EVENTS.get(ev.keysym)
            if event is not None:
                self.events.append(event)
        elif ev.keysym == 'r':
            self.run()
        elif ev.keysym == 'x':
            self.root.destroy()

    def draw(self, arena: engine.Arena, score: int) -> None:
        self.canvas.delete('content')

        for y in range(ROWS):
            for x in range(COLS):
                if engine.is_occupied(arena, x, y):
                    cx, cy = (BORDER + c * CELL_SIZE for c in (x + 1, y))
                    self.canvas.create_rectangle(
                        cx, cy, cx + CELL_SIZE, cy + CELL_SIZE,
                        fill=TILE_COLOUR, tags='content'
                    )

        self.canvas.create_text(
            BORDER + (COLS + 2) * CELL_SIZE // 2,
            5 * BORDER // 2 + (ROWS + 1) * CELL_SIZE,
            text=f"Score: {score}", font=FONT, tags=('content', 'score')
        )

    def poll_event(self) -> int:
        while not self.events:
            time.sleep(0.01)
            self.root.update()
        return self.events.popleft()


def main() -> None:
    tetris = Tetris()

    engine.draw = tetris.draw
    engine.poll_event = tetris.poll_event

    tetris.start()


if __name__ == '__main__':
    main()
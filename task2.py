from queue import Queue
import tkinter as tk
from dataclasses import dataclass
from random import randint
import numpy as np

# import pyjion
# pyjion.enable()


@dataclass
class Point:
    x: int
    y: int

    def draw(self, canvas: tk.Canvas, color: str = "black", radius: int = 5):
        canvas.create_oval(self.x - radius, self.y - radius, self.x + radius,
                           self.y + radius, fill=color, outline=color)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Point):
            return self.x == __o.x and self.y == __o.y
        return False

    def __iter__(self):
        yield self.x
        yield self.y

    def in_rect(self, p1: 'Point', p2: 'Point') -> bool:
        maxx = max(p1.x, p2.x)
        minx = min(p1.x, p2.x)
        maxy = max(p1.y, p2.y)
        miny = min(p1.y, p2.y)
        return minx <= self.x <= maxx and miny <= self.y <= maxy

    def transform(self, transform: np.ndarray):
        p = np.array([self.x, self.y, 1])
        p = np.matmul(transform, p)
        self.x = int(p[0])
        self.y = int(p[1])

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5):
        highlight = canvas.create_oval(self.x - r, self.y - r, self.x + r,
                                       self.y + r, fill="red", outline="red")
        canvas.after(timeout, canvas.delete, highlight)

    @property
    def center(self) -> 'Point':
        return Point(self.x, self.y)


@dataclass
class Line:
    p1: Point
    p2: Point

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=color)

    def in_rect(self, p1: Point, p2: Point) -> bool:
        """Проверка, что линия пересекает прямоугольник"""
        return all((self.p1.in_rect(p1, p2), self.p2.in_rect(p1, p2)))

    def transform(self, transform: np.ndarray):
        self.p1.transform(transform)
        self.p2.transform(transform)

    def highlight(self, canvas: tk.Canvas, timeout: int = 200):
        highlight = canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill="red")
        canvas.after(timeout, canvas.delete, highlight)

    @property
    def center(self) -> Point:
        return Point((self.p1.x + self.p2.x) // 2, (self.p1.y + self.p2.y) // 2)

    def get_x(self, y: int) -> int:
        """Получить x для точки с заданным y"""
        if self.p1.x == self.p2.x:
            return self.p1.x
        return int((y - self.p1.y) * (self.p2.x - self.p1.x) / (self.p2.y - self.p1.y) + self.p1.x)

    def copy(self):
        return Line(Point(self.p1.x, self.p1.y), Point(self.p2.x, self.p2.y))


class App(tk.Tk):
    W: int = 1000
    H: int = 600
    R: int = 5
    lines: list[Line]
    start: Line
    n: int = 0
    noise: float = 1
    tear: int = 25

    def __init__(self):
        super().__init__()
        self.title("Nvidia Midpoint™ Displacement®")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(0, 0)
        self.start = Line(Point(50, self.H / 2), Point(self.W - 50, self.H / 2))
        self.create_widgets()
        self.start.draw(self.canvas)
        self.mainloop()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H-70, bg="white")
        self.scales = tk.Frame()
        self.scale_1 = tk.Scale(self.scales, from_=0, to_=10, orient=tk.HORIZONTAL, label='Iterations', command=self._n)
        self.scale_2 = tk.Scale(self.scales, from_=0, to_=2, resolution=0.1,
                                orient=tk.HORIZONTAL, label='Noise', command=self._noise)
        self.scale_3 = tk.Scale(self.scales, from_=0, to_=100, orient=tk.HORIZONTAL, label='Tear', command=self._tear)
        self.canvas.pack()
        self.scales.pack()
        self.scale_1.pack(side=tk.LEFT)
        self.scale_2.pack(side=tk.LEFT)
        self.scale_3.pack(side=tk.LEFT)
        self.scale_1.set(self.n)
        self.scale_2.set(self.noise)
        self.scale_3.set(self.tear)

    def reset(self, *_):
        self.canvas.delete('all')
        self.lines = [self.start.copy()]

    def draw(self):
        for l in self.lines:
            l.draw(self.canvas)

    def _n(self, n: str):
        self.n = int(n)
        self.reset()
        self.displace()
        self.draw()

    def _noise(self, r: str):
        self.noise = float(r)
        self.reset()
        self.displace()
        self.draw()

    def _tear(self, t: str):
        self.tear = int(t)
        self.reset()
        self.displace()
        self.draw()

    def displace(self):
        if self.n == 0:
            return
        gens = 0
        sentinel = object()
        lines = []
        q: Queue[Line | object] = Queue()
        q.put(self.start.copy())
        q.put(sentinel)
        while q:
            i = q.get()
            if i is sentinel:
                gens += 1
                self.lines = lines
                lines = []
                q.put(sentinel)
                if gens == self.n:
                    return
            else:
                c = i.center
                c1 = Point(c.x, c.y + self.noise * randint(-self.tear, self.tear))
                a = Line(i.p1, c1)
                b = Line(c1, i.p2)
                q.put(a)
                q.put(b)
                lines.append(a)
                lines.append(b)


if __name__ == "__main__":
    App()

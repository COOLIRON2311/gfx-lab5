from random import randint
import turtle as t
import tkinter as tk
from functools import lru_cache

# import pyjion
# pyjion.enable()

Color = tuple[int, int, int]
Angle = float | tuple


class LSystem:
    atoms: set  # алфавит
    axiom: str  # направление
    rules: list  # правила вида A -> B
    angle: Angle  # угол поворота в градусах

    def __init__(self, atoms: set, axiom: str, rules: list, angle: Angle):
        self.atoms = atoms
        self.axiom = axiom
        self.rules = rules
        self.angle = angle

    @staticmethod
    def parse(s: str) -> 'LSystem':
        lines = [i.strip() for i in s.splitlines() if i]
        header = lines[0].split(' ')
        axiom = header.pop()
        angle = header.pop()
        if '..' in angle:
            angle = tuple(map(float, angle.split('..')))
        else:
            angle = float(angle)
        atoms = set(header)
        rules = []
        for line in lines[1:]:
            rule = line.split(' -> ')
            if len(rule) != 2:
                raise ValueError('Invalid rule')
            rules.append(rule)
        return LSystem(atoms, axiom, rules, angle)

    def __str__(self) -> str:
        s = f'{self.atoms} {self.angle} {self.axiom}\n'
        for key, value in self.rules:
            s += f'{key} -> {value}\n'
        return s

    @lru_cache(maxsize=16)
    def apply(self, n: int = 1) -> str:
        # print(self, n)
        state = self.axiom
        for _ in range(n):
            new = []
            for letter in state:
                rule_applied = False
                for atom, sub in self.rules:
                    if letter == atom:
                        new.append(sub)
                        rule_applied = True
                        break
                if not rule_applied:
                    new.append(letter)

            state = ''.join(new)
        return state


class Plotter(t.Turtle):
    ANGLE: int
    sc: t._Screen
    lsystem: LSystem
    win: tk.Toplevel | tk.Tk
    canvas: t.TurtleScreen
    stack: list[tuple]
    ln: int = 10
    x: int = 0
    y: int = 0
    n: int = 1
    col: Color = (0, 0, 0)
    pensz: int = 4

    def __init__(self, lsystem: LSystem, angle: int = 0):
        self.lsystem = lsystem
        super().__init__()
        self.stack = []
        self.sc = t.Screen()
        self.sc.colormode(255)
        self.sc.bgcolor(255, 250, 205)
        self.speed(0)
        self.ANGLE = angle
        self.rtr = tk.BooleanVar(value=True)
        self.win = self.sc.getcanvas().winfo_toplevel()
        self.bbox = tk.Frame(self.win)
        self.button1 = tk.Button(self.bbox, text='Draw', command=self.fast_draw, width=30)
        self.button2 = tk.Button(self.bbox, text='Clear', command=self.clear, width=30)
        self.button3 = tk.Button(self.bbox, text='Color Draw', command=self.col_draw, width=30)
        self.check = tk.Checkbutton(self.bbox, text='Real-time rendering',
                                    variable=self.rtr, onvalue=True, offvalue=False)
        self.button4 = tk.Button(self.bbox, text='+90°', command=self.rotate, height=6)
        self.scale1 = tk.Scale(self.win, from_=-1000, to=1000, orient=tk.HORIZONTAL, command=self.set_x, label='X')
        self.scale2 = tk.Scale(self.win, from_=-1000, to=1000, orient=tk.VERTICAL, command=self.set_y, label='Y')
        self.scale3 = tk.Scale(self.win, from_=0, to=13, orient=tk.HORIZONTAL, command=self.set_n, label='N')
        self.scale4 = tk.Scale(self.win, from_=1, to=100, orient=tk.HORIZONTAL, command=self.set_ln, label='Zoom')
        self.bbox.pack(side=tk.LEFT, padx=5, pady=5)
        self.button4.pack(side=tk.LEFT, padx=5)
        self.button1.pack(padx=5)
        self.button2.pack(padx=5)
        self.button3.pack(padx=5)
        self.check.pack(padx=5)
        self.scale2.pack(side=tk.RIGHT)
        self.scale1.pack(side=tk.RIGHT)
        self.scale4.pack(side=tk.RIGHT)
        self.scale3.pack(side=tk.RIGHT)
        self.scale1.set(self.x)
        self.scale2.set(self.y)
        self.scale3.set(self.n)
        self.scale4.set(self.ln)
        t.done()

    def draw(self):
        self.position()
        state = self.lsystem.apply(self.n)

        for atom in state:
            if atom in self.lsystem.atoms:
                self.forward(self.ln)
            elif atom == '+':
                if isinstance(self.lsystem.angle, tuple):
                    angle = randint(*self.lsystem.angle)
                else:
                    angle = self.lsystem.angle
                self.left(angle)
            elif atom == '-':
                if isinstance(self.lsystem.angle, tuple):
                    angle = randint(*self.lsystem.angle)
                else:
                    angle = self.lsystem.angle
                self.right(angle)
            elif atom == '[':
                self.stack.append((self.xcor(), self.ycor(), self.heading()))
            elif atom == ']':
                x, y, h = self.stack.pop()
                self.penup()
                self.goto(x, y)
                self.setheading(h)
                self.pendown()

    def tint(self, c: Color, _t: float) -> Color:
        """Tint a color by a factor of t, where 0 <= t <= 1"""
        r = int(c[0] + (255 - c[0]) * _t)
        g = int(c[1] + (255 - c[1]) * _t)
        b = int(c[2] + (255 - c[2]) * _t)
        return (r, g, b)

    def _col_draw(self):
        self.position()
        state = self.lsystem.apply(self.n)
        col = self.col
        pw = self.pensz
        ln = self.ln

        self.pensize(pw)
        self.pencolor(col)
        for atom in state:
            if atom in self.lsystem.atoms:
                self.forward(ln)
            elif atom == '+':
                if isinstance(self.lsystem.angle, tuple):
                    angle = randint(*self.lsystem.angle)
                else:
                    angle = self.lsystem.angle
                self.left(angle)
            elif atom == '-':
                if isinstance(self.lsystem.angle, tuple):
                    angle = randint(*self.lsystem.angle)
                else:
                    angle = self.lsystem.angle
                self.right(angle)
            elif atom == '[':
                self.stack.append((self.xcor(), self.ycor(), self.heading(), col, pw, ln))
            elif atom == ']':
                x, y, h, col, pw, ln = self.stack.pop()
                self.penup()
                self.goto(x, y)
                self.setheading(h)
                self.pensize(pw)
                self.pencolor(col)
                self.pendown()
            elif atom == '@':
                pw *= 0.8
                ln *= 0.8
                col = self.tint(col, 0.1)
                self.pensize(pw)
                self.pencolor(col)

    def rotate(self):
        self.sc.tracer(False)
        self.ANGLE += 90
        self.clear()
        if self.rtr.get():
            self.draw()
        self.sc.tracer(True)

    def position(self):
        self.penup()
        self.goto(self.x, self.y)
        self.setheading(self.ANGLE)
        self.pendown()

    def fast_draw(self):
        self.sc.tracer(False)
        self.clear()
        self.draw()
        self.sc.tracer(True)

    def col_draw(self):
        self.sc.tracer(False)
        self.clear()
        self._col_draw()
        self.sc.tracer(True)

    def clear(self):
        self.reset()

    def set_ln(self, value):
        self.sc.tracer(False)
        self.ln = int(value)
        self.clear()
        if self.rtr.get():
            self.draw()
        self.sc.tracer(True)

    def set_x(self, value):
        self.sc.tracer(False)
        self.x = int(value)
        self.clear()
        if self.rtr.get():
            self.draw()
        self.sc.tracer(True)

    def set_y(self, value):
        self.sc.tracer(False)
        self.y = int(value)
        self.clear()
        if self.rtr.get():
            self.draw()
        self.sc.tracer(True)

    def set_n(self, value):
        self.sc.tracer(False)
        self.n = int(value)
        if self.n > 9:
            self.rtr.set(False)
        self.clear()
        if self.rtr.get():
            self.draw()
        self.sc.tracer(True)


def main():
    with open('task1a.txt', 'r', encoding='utf8') as f:
        lsystem = LSystem.parse(f.read())
    Plotter(lsystem)


if __name__ == '__main__':
    main()

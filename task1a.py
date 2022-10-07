import turtle as t
import tkinter as tk
from functools import cache


class LSystem:
    atoms: set  # алфавит
    axiom: str  # направление
    rules: list  # правила вида A -> B
    angle: float  # угол поворота в градусах

    def __init__(self, atoms: set, axiom: str, rules: list, angle: float):
        self.atoms = atoms
        self.axiom = axiom
        self.rules = rules
        self.angle = angle

    @staticmethod
    def parse(s: str) -> 'LSystem':
        lines = [i.strip() for i in s.splitlines() if i]
        header = lines[0].split(' ')
        axiom = header.pop()
        angle = float(header.pop())
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

    @cache
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
    sc: t._Screen
    lsystem: LSystem
    win: tk.Toplevel
    canvas: t.TurtleScreen
    ln: int = 10
    x: int = 0
    y: int = 0
    n: int = 1

    def __init__(self, lsystem: LSystem):
        self.lsystem = lsystem
        super().__init__()
        self.sc = t.Screen()
        self.speed(0)
        self.win = self.sc.getcanvas().winfo_toplevel()
        self.bbox = tk.Frame(self.win)
        self.button1 = tk.Button(self.bbox, text='Draw', command=self.draw, width=30)
        self.button2 = tk.Button(self.bbox, text='Clear', command=self.clear, width=30)
        self.scale1 = tk.Scale(self.win, from_=-2000, to=2000, orient=tk.HORIZONTAL, command=self.set_x, label='X')
        self.scale2 = tk.Scale(self.win, from_=-2000, to=2000, orient=tk.VERTICAL, command=self.set_y, label='Y')
        self.scale3 = tk.Scale(self.win, from_=0, to=7, orient=tk.HORIZONTAL, command=self.set_n, label='N')
        self.scale4 = tk.Scale(self.win, from_=1, to=100, orient=tk.HORIZONTAL, command=self.set_ln, label='Zoom')
        self.bbox.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X)
        self.button1.pack(padx=50, pady=5)
        self.button2.pack(padx=50, pady=5)
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
                self.left(self.lsystem.angle)
            elif atom == '-':
                self.right(self.lsystem.angle)

    def position(self):
        self.penup()
        self.goto(self.x, self.y)
        self.pendown()

    def clear(self, *_):
        self.reset()

    def set_ln(self, value):
        self.sc.tracer(False)
        self.ln = int(value)
        self.clear()
        self.draw()
        self.sc.tracer(True)

    def set_x(self, value):
        self.sc.tracer(False)
        self.x = int(value)
        self.clear()
        self.draw()
        self.sc.tracer(True)

    def set_y(self, value):
        self.sc.tracer(False)
        self.y = int(value)
        self.clear()
        self.draw()
        self.sc.tracer(True)

    def set_n(self, value):
        self.sc.tracer(False)
        self.n = int(value)
        self.clear()
        self.draw()
        self.sc.tracer(True)


def main():
    with open('task1a.txt', 'r', encoding='utf8') as f:
        lsystem = LSystem.parse(f.read())
    Plotter(lsystem)


if __name__ == '__main__':
    main()

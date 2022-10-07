from turtle import Turtle, Screen, done


class LSystem:
    atom: str # алфавит
    direction: str # направление
    rules: dict # правило
    angle: float # угол
    n: int

    def __init__(self, atom: str, direction: str, rules: dict, angle: float, n: int = 1):
        self.atom = atom
        self.direction = direction
        self.rules = rules
        self.angle = angle
        self.n = n


    @staticmethod
    def parse(s: str) -> 'LSystem':
        lines = [i for i in s.splitlines() if i]
        header = lines[0].split(' ')
        atom = header[0]
        angle = float(header[1])
        direction = header[2]
        rules = {}
        for line in lines[1:]:
            rule = line.split(' -> ')
            if len(rule) != 2:
                raise ValueError('Invalid rule')
            rules[rule[0]] = rule[1]
        return LSystem(atom, direction, rules, angle)

    def __str__(self) -> str:
        s = f'{self.atom} {self.angle} {self.direction}\n'
        for key, value in self.rules.items():
            s += f'{key} -> {value}\n'
        return s

    def apply(self) -> str:
        state = self.direction
        for _ in range(self.n):
            for atom, sub in self.rules.items():
                state = state.replace(atom, sub)
        return state

    def draw(self):
        t = Turtle()
        sc = Screen()
        t.penup()
        t.setx(-sc.window_width() / 2 + 50)
        t.pendown()
        t.speed(0)
        state = self.apply()
        ln = 10

        for atom in state:
            if atom == self.atom:
                t.forward(ln)
            elif atom == '+':
                t.right(self.angle)
            elif atom == '-':
                t.left(self.angle)
        done()


a = LSystem.parse('''
F 60 F
F -> F-F++F-F''')
# a = LSystem.parse('''
# F 90 X
# F -> F
# X -> X+YF+
# Y -> -FX-Y''')
print(a)
a.n = 2
a.draw()

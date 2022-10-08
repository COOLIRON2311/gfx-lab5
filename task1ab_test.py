import unittest
from task1ab import LSystem, Plotter


class TestTask1a(unittest.TestCase):
    VISUAL = True
    def test_koch_curve(self):
        lsystem = LSystem.parse('''
            F -60 F
            F -> F-F++F-F''')
        self.assertEqual(lsystem.apply(), 'F-F++F-F')
        if self.VISUAL:
            Plotter(lsystem)

    def test_koch_curve90(self):
        lsystem = LSystem.parse('''
            F 90 F
            F -> F+F-F-F+F''')
        self.assertEqual(lsystem.apply(), 'F+F-F-F+F')
        if self.VISUAL:
            Plotter(lsystem)

    def test_koch_snowflake(self):
        lsystem = LSystem.parse('''
            F 60 F++F++F
            F -> F-F++F-F''')
        self.assertEqual(lsystem.apply(), 'F-F++F-F++F-F++F-F++F-F++F-F')
        if self.VISUAL:
            Plotter(lsystem)

    def test_koch_island(self):
        lsystem = LSystem.parse('''
            F 90 F+F+F+F
            F -> F+F-F-FF+F+F-F''')
        self.assertEqual(lsystem.apply(), 'F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F')
        if self.VISUAL:
            Plotter(lsystem)

    def test_sierpinski_triangle(self):
        lsystem = LSystem.parse('''
            F G 120 F-G-G
            F -> F-G+F+G-F
            G -> GG''')
        self.assertEqual(lsystem.apply(), 'F-G+F+G-F-GG-GG')
        if self.VISUAL:
            Plotter(lsystem)

    def test_sierpinksi_arrowhead(self):
        lsystem = LSystem.parse('''
            X Y F 60 YF
            X -> YF+XF+Y
            Y -> XF-YF-X''')
        self.assertEqual(lsystem.apply(), 'XF-YF-XF')
        if self.VISUAL:
            Plotter(lsystem)

    def test_hilbert_curve(self):
        lsystem = LSystem.parse('''
            X Y F 90 X
            F -> F
            X -> -YF+XFX+FY-
            Y -> +XF-YFY-FX+''')
        self.assertEqual(lsystem.apply(), '-YF+XFX+FY-')
        if self.VISUAL:
            Plotter(lsystem)

    def test_dragon_curve(self):
        lsystem = LSystem.parse('''
            X Y F 90 X
            F -> F
            X -> X+YF+
            Y -> -FX-Y''')
        self.assertEqual(lsystem.apply(), 'X+YF+')
        if self.VISUAL:
            Plotter(lsystem)

    def test_gosper_curve(self):
        lsystem = LSystem.parse('''
            X Y F 60 XF
            F -> F
            X -> X+YF++YF-FX--FXFX-YF+
            Y -> -FX+YFYF++YF+FX--FX-Y''')
        self.assertEqual(lsystem.apply(), 'X+YF++YF-FX--FXFX-YF+F')
        if self.VISUAL:
            Plotter(lsystem)

    def test_pushdown_tree(self):
        lsystem = LSystem.parse('''
            F 20 F
            F -> F[+F]F[-F]F''')
        self.assertEqual(lsystem.apply(), 'F[+F]F[-F]F')
        if self.VISUAL:
            Plotter(lsystem, 90)

    def test_pushdown_tree0(self):
        lsystem = LSystem.parse('''
            F 20 X
            F ->  FF
            X -> F[+X]F[-X]+X''')
        self.assertEqual(lsystem.apply(), 'F[+X]F[-X]+X')
        if self.VISUAL:
            Plotter(lsystem, 90)

    def test_pushdown_tree1(self):
        lsystem = LSystem.parse('''
            F 22 F
            F -> FF-[-F+F+F]+[+F-F-F]''')
        self.assertEqual(lsystem.apply(), 'FF-[-F+F+F]+[+F-F-F]')
        if self.VISUAL:
            Plotter(lsystem, 90)

    def test_pushdown_tree2(self):
        lsystem = LSystem.parse('''
            F 20 X
            F -> FF
            X -> F[+X]F[-X]+X''')
        self.assertEqual(lsystem.apply(), 'F[+X]F[-X]+X')
        if self.VISUAL:
            Plotter(lsystem, 90)

    def test_pushdown_tree3(self):
        lsystem = LSystem.parse('''
            F 22.5 X
            F -> FF
            X -> F-[[X]+X]+F[+FX]-X''')
        self.assertEqual(lsystem.apply(), 'F-[[X]+X]+F[+FX]-X')
        if self.VISUAL:
            Plotter(lsystem, 90)

    def test_mosaic(self):
        lsystem = LSystem.parse('''
            F 60 X
            F -> F
            X -> [-F+F[Y]+F][+F-F[X]-F]
            Y -> [-F+F[Y]+F][+F-F-F]''')
        self.assertEqual(lsystem.apply(), '[-F+F[Y]+F][+F-F[X]-F]')
        if self.VISUAL:
            Plotter(lsystem)

    def test_pushdown_color_tree(self):
        lsystem = LSystem.parse('''
            F 0..45 X
            X -> F[@[-X]+X]''')
        self.assertEqual(lsystem.apply(), 'F[@[-X]+X]')
        if self.VISUAL:
            Plotter(lsystem, 90)

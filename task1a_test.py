import unittest
from task1a import LSystem, Plotter


class TestTask1a(unittest.TestCase):
    def test_koch_curve(self):
        lsystem = LSystem.parse('''
            F -60 F
            F -> F-F++F-F''')
        self.assertEqual(lsystem.apply(), 'F-F++F-F')
        Plotter(lsystem)

    def test_koch_curve90(self):
        lsystem = LSystem.parse('''
            F 90 F
            F -> F+F-F-F+F''')
        self.assertEqual(lsystem.apply(), 'F+F-F-F+F')
        Plotter(lsystem)

    def test_koch_snowflake(self):
        lsystem = LSystem.parse('''
            F 60 F++F++F
            F -> F-F++F-F''')
        self.assertEqual(lsystem.apply(), 'F-F++F-F++F-F++F-F++F-F++F-F')
        Plotter(lsystem)

    def test_koch_island(self):
        lsystem = LSystem.parse('''
            F 90 F+F+F+F
            F -> F+F-F-FF+F+F-F''')
        self.assertEqual(lsystem.apply(), 'F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F+F+F-F-FF+F+F-F')
        Plotter(lsystem)

    def test_sierpinski_triangle(self):
        lsystem = LSystem.parse('''
            F G 120 F-G-G
            F -> F-G+F+G-F
            G -> GG''')
        self.assertEqual(lsystem.apply(), 'F-G+F+G-F-GG-GG')
        Plotter(lsystem)

    def test_sierpinksi_arrowhead(self):
        lsystem = LSystem.parse('''
            X Y F 60 YF
            X -> YF+XF+Y
            Y -> XF-YF-X''')
        self.assertEqual(lsystem.apply(), 'XF-YF-XF')
        Plotter(lsystem)

    def test_hilbert_curve(self):
        lsystem = LSystem.parse('''
            X Y F 90 X
            F -> F
            X -> -YF+XFX+FY-
            Y -> +XF-YFY-FX+''')
        self.assertEqual(lsystem.apply(), '-YF+XFX+FY-')
        Plotter(lsystem)

    def test_dragon_curve(self):
        lsystem = LSystem.parse('''
            X Y F 90 X
            F -> F
            X -> X+YF+
            Y -> -FX-Y''')
        self.assertEqual(lsystem.apply(), 'X+YF+')
        Plotter(lsystem)

    def test_gosper_curve(self):
        lsystem = LSystem.parse('''
            X Y F 60 XF
            F -> F
            X -> X+YF++YF-FX--FXFX-YF+
            Y -> -FX+YFYF++YF+FX--FX-Y''')
        self.assertEqual(lsystem.apply(), 'X+YF++YF-FX--FXFX-YF+F')
        Plotter(lsystem)

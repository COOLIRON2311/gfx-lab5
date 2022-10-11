from asyncio.windows_events import NULL
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from math import cos, radians, sin, tan
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

import numpy as np


class Mode(Enum):
    Rotate = 1  # вращение
    Translate = 2  # перемещение
    Scale = 3  # масштабирование
    Shear = 4  # сдвиг
    PointDraw = 5  # рисование точки
    LineDraw = 6  # рисование линии
    PolygonDraw = 7  # рисование полигона
    SelectShape = 8  # выбор примитива
    ApplySpecFunc = 9  # применение специальной функции

    def __str__(self) -> str:
        return super().__str__().split(".")[-1]


class ShapeType(Enum):
    Point = 0  # точка
    Line = 1  # линия
    Polygon = 2  # полигон

    def __str__(self) -> str:
        return super().__str__().split(".")[-1]


class SpecialFunctions(Enum):
    None_ = 0
    PointInConvexPoly = 1
    PointInNonConvexPoly = 2
    ClassifyPointPosition = 3
    RotateEdge90 = 4
    EdgeIntersect = 5
    BezierCurve = 6

    def __str__(self) -> str:
        match self:
            case SpecialFunctions.None_:
                return "No special function"
            case SpecialFunctions.PointInConvexPoly:
                return "Point in convex polygon"
            case SpecialFunctions.PointInNonConvexPoly:
                return "Point in non-convex polygon"
            case SpecialFunctions.ClassifyPointPosition:
                return "Classify point position"
            case SpecialFunctions.RotateEdge90:
                return "Rotate edge 90 degrees"
            case SpecialFunctions.EdgeIntersect:
                return "Edge intersection"
            case SpecialFunctions.BezierCurve:
                return "Bezier curve"
        return super().__str__()


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

    def intersection(self, line: 'Line') -> Point | None:
        y1 = min(self.p1.y, self.p2.y)
        y2 = max(self.p1.y, self.p2.y)
        for y in range(y1, y2 + 1):
            x1 = self.get_x(y)
            x2 = line.get_x(y)
            if abs(x1 - x2) <= 1:
                return Point(x1, y)
        return None


@dataclass
class Polygon:
    lines: list[Line]
    points: list[Point]

    def __init__(self, points) -> None:
        self.points = points
        ln = len(points)
        self.lines = [Line(points[i], points[(i + 1) % ln]) for i in range(ln)]

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        for line in self.lines:
            line.draw(canvas, color)

    def points_list(self):
        return [(p.x, p.y) for p in self.points]

    def in_rect(self, p1: Point, p2: Point) -> bool:
        """Проверка, что полигон пересекает прямоугольник"""
        return all(line.in_rect(p1, p2) for line in self.lines)

    def transform(self, transform: np.ndarray):
        for point in self.points:
            point.transform(transform)
        for line in self.lines:
            line.transform(transform)

    def highlight(self, canvas: tk.Canvas, timeout: int = 200):
        highlight = canvas.create_polygon(self.points_list(), fill='', outline="red")
        canvas.after(timeout, canvas.delete, highlight)

    @property
    def center(self) -> Point:
        return Point(sum(p.x for p in self.points) // len(self.points),
                     sum(p.y for p in self.points) // len(self.points))


class App(tk.Tk):
    W: int = 1000
    H: int = 600
    R: int = 5
    mode: str
    points: list[Point]
    line_buffer: list[Point]
    lines: list[Line]
    polygon_buffer: list[Point]
    polygons: list[Polygon]
    shape_type: ShapeType
    selected_shape = None
    _spec_func_idx: int = 6
    _shape_type_idx: int = 1
    rect_sel_p1: Point
    rect_sel_p2: Point
    tp: Point  # temporary point

    def __init__(self):
        super().__init__()
        self.title("Affine Transformation")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(0, 0)
        self.mode = Mode.PointDraw
        self.shape_type = ShapeType.Line
        self.points = []
        self.lines = []
        self.polygons = []
        self.line_buffer = []
        self.polygon_buffer = []
        self.rect_sel_p1 = None
        self.rect_sel_p2 = None
        self.tp = None

        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H-30, bg="white")
        self.buttons = tk.Frame(self)
        self.button1 = tk.Button(self.buttons, text="Rotate", command=self.rotate)
        self.button2 = tk.Button(self.buttons, text="Scale", command=self.scale)
        self.button3 = tk.Button(self.buttons, text="Shear", command=self.shear)
        self.button4 = tk.Button(self.buttons, text="Translate", command=self.translate)
        self.button5 = tk.Button(self.buttons, text="Point Draw", command=self.point_draw)
        self.button6 = tk.Button(self.buttons, text="Line Draw", command=self.line_draw)
        self.button7 = tk.Button(self.buttons, text="Polygon Draw", command=self.polygon_draw)
        self.button8 = tk.Button(self.buttons, text="Reset", command=self.reset)
        self.label1 = tk.Label(self.buttons, text=f"Shape: {self.shape_type}", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.button9 = tk.Button(self.buttons, text="Select Shape", command=self.select_shape)
        self.button10 = tk.Button(self.buttons, text="Apply", command=self.apply_spec_func)
        self.listbox = tk.Listbox(self.buttons, selectmode=tk.SINGLE, height=1, width=28)
        self.scrollbar = tk.Scrollbar(self.buttons, orient=tk.VERTICAL)
        self.label2 = tk.Label(self.buttons, text=f"Mode: {self.mode}", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.canvas.pack()
        self.canvas.config(cursor="cross")
        self.buttons.pack(side="bottom", fill="x")
        self.button1.pack(side="left", fill="x")
        self.button2.pack(side="left", fill="x")
        self.button3.pack(side="left", fill="x")
        self.button4.pack(side="left", fill="x")
        self.button5.pack(side="left", fill="x")
        self.button6.pack(side="left", fill="x")
        self.button7.pack(side="left", fill="x")
        self.button8.pack(side="left", fill="x")
        self.label2.pack(side="right", fill="x", padx=5)
        self.label1.pack(side="right", fill="x", padx=5)
        self.button10.pack(side="right", fill="x", padx=5)
        self.listbox.pack(side="right", fill="x")
        self.scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.scroll)
        self.listbox.delete(0, tk.END)
        self.listbox.insert(0, *SpecialFunctions)

        self.button9.pack(side="right", fill="x", padx=5)
        self.canvas.bind("<Button-1>", self.click)
        self.bind("<Escape>", self.del_temp_point)
        self.bind("<Button-3>", self.set_temp_point)
        self.bind("<Return>", self.redraw)
        self.bind("<Delete>", self.clear_buffs)
        self.bind("<Button-2>", self.swap_shape_type)
        self.bind("<BackSpace>", self.delete_shape)
        self.bind("<F1>", self.debug)
        self.bind("<B1-Motion>", self.mouse_move)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.scroll('scroll', f'{self._spec_func_idx}', 'units')
        # self.mainloop()

    def debug(self, *args):
        print(*args)
        print(f"Points: {self.points}")
        print(f"Lines: {self.lines}")
        print(f"Polygons: {self.polygons}")
        print(f"Line buffer: {self.line_buffer}")
        print(f"Polygon buffer: {self.polygon_buffer}")
        print(f"Selected shape: {self.selected_shape}")
        print(f"Mode: {self.mode}")
        print(f"Shape type: {self.shape_type}")
        print(f"Spec func idx: {self._spec_func_idx}")
        print(f"Shape type idx: {self._shape_type_idx}")
        print(f"Rect sel p1: {self.rect_sel_p1}")
        print(f"Rect sel p2: {self.rect_sel_p2}")
        print(f"Temp point: {self.tp}")
        print()

    def scroll(self, *args):
        # print(args)
        d = int(args[1])
        if 0 < self._spec_func_idx + d < len(SpecialFunctions):
            self._spec_func_idx += d
        self.listbox.yview(*args)

    def reset(self, *_):
        self.canvas.delete("all")
        self.mode = Mode.PointDraw
        self.label2.config(text=f"Mode: {self.mode}")
        self.points = []
        self.polygons = []
        self.lines = []
        self.line_buffer = []
        self.polygon_buffer = []
        self.tp = None

    def redraw(self, *_, delete_points=True):
        self.canvas.delete("all")
        if delete_points:
            self.points = []
        for point in self.points:
            point.draw(self.canvas)
        for line in self.lines:
            line.draw(self.canvas)
        for polygon in self.polygons:
            polygon.draw(self.canvas)

    def clear_buffs(self, *_):
        self.line_buffer = []
        self.polygon_buffer = []

    def rotate(self):
        self.mode = Mode.Rotate
        self.label2.config(text=f"Mode: {self.mode}")
        if self.selected_shape is not None:
            inp = sd.askfloat('Rotate', 'Angle (degrees): ')
            if inp is None:
                return
            phi = radians(inp)
            if self.tp is not None:
                m, n = self.tp
            else:
                m, n = self.selected_shape.center
            # https://scask.ru/a_book_mm3d.php?id=45
            mat = np.array([
                [cos(phi), -sin(phi), -m * cos(phi) + n * sin(phi) + m],
                [sin(phi), cos(phi), -m * sin(phi) - n * cos(phi) + n],
                [0, 0, 1]])
            self.selected_shape.transform(mat)
            self.redraw(delete_points=False)
            self.after(1, self.focus_force)

    def scale(self):
        self.mode = Mode.Scale
        self.label2.config(text=f"Mode: {self.mode}")
        if self.selected_shape is not None:
            inp = sd.askstring('Scale', 'Scale x, y:')
            if inp is None:
                return
            sx, sy = map(float, inp.split(','))
            if self.tp is not None:
                m, n = self.tp
            else:
                m, n = self.selected_shape.center
            mat = np.array([
                [sx, 0, -m * sx + m],
                [0, sy, -n * sy + n],
                [0, 0, 1]])
            self.selected_shape.transform(mat)
            self.redraw(delete_points=False)
            self.after(1, self.focus_force)

    def shear(self):
        self.mode = Mode.Shear
        self.label2.config(text=f"Mode: {self.mode}")
        if self.selected_shape is not None:
            # print(self.selected_shape)
            inp = sd.askstring('Shear', 'Shear x, y:')
            if inp is None:
                return
            shx, shy = map(radians, map(float, inp.split(',')))
            if self.tp is not None:
                m, n = self.tp
            else:
                m, n = self.selected_shape.center
            # used sympy to get this matrix
            mat = np.array([
                [1, tan(shx), -n * tan(shx)],
                [tan(shy), 1, -m * tan(shy)],
                [0, 0, 1]])
            self.selected_shape.transform(mat)
            self.redraw(delete_points=False)
            self.after(1, self.focus_force)
            # print(self.selected_shape)

    def translate(self):
        self.mode = Mode.Translate
        self.label2.config(text=f"Mode: {self.mode}")
        if self.selected_shape is not None:
            inp = sd.askstring('Translate', 'Translate x, y:')
            if inp is None:
                return
            tx, ty = map(float, inp.split(','))
            mat = np.array([
                [1, 0, tx],
                [0, 1, ty],
                [0, 0, 1]])
            self.selected_shape.transform(mat)
            self.redraw(delete_points=False)
            self.after(1, self.focus_force)

    def point_draw(self):
        self.mode = Mode.PointDraw
        self.label2.config(text=f"Mode: {self.mode}")

    def line_draw(self):
        self.mode = Mode.LineDraw
        self.label2.config(text=f"Mode: {self.mode}")

    def polygon_draw(self):
        self.mode = Mode.PolygonDraw
        self.label2.config(text=f"Mode: {self.mode}")

    def select_shape(self):
        self.mode = Mode.SelectShape
        self.label2.config(text=f"Mode: {self.mode}")

    def delete_shape(self, _):
        if self.selected_shape:
            if isinstance(self.selected_shape, Point):
                self.points.remove(self.selected_shape)
            if isinstance(self.selected_shape, Line):
                self.lines.remove(self.selected_shape)
            elif isinstance(self.selected_shape, Polygon):
                self.polygons.remove(self.selected_shape)
            self.selected_shape = None
            self.redraw(delete_points=False)

    def apply_spec_func(self):
        func = SpecialFunctions(self._spec_func_idx)

        match func:
            case SpecialFunctions.None_:
                pass

            case SpecialFunctions.PointInConvexPoly:
                point = self.tp
                if point is None:
                    mb.showwarning("Error", "No point selected")
                    return

                res = True

                shape = self.selected_shape
                if shape is None or not isinstance(shape, Polygon):
                    mb.showwarning("Error", "No polygon selected")
                    return

                for line in shape.lines:
                    if self.on_left(line, point):
                        res = False
                        break
                if res:
                    mb.showinfo("Result", "Point is inside polygon")
                else:
                    mb.showinfo("Result", "Point is NOT inside polygon")

            case SpecialFunctions.PointInNonConvexPoly:
                point = self.tp
                if point is None:
                    mb.showwarning("Error", "No point selected")
                    return

                ray = Line(point, Point(self.W, point.y))
                counter = 0

                shape = self.selected_shape
                if shape is None or not isinstance(shape, Polygon):
                    mb.showwarning("Error", "No polygon selected")
                    return

                for line in shape.lines:
                    if self.are_intersected(line, ray):
                        # print(line)
                        line.highlight(self.canvas, 1000)
                        counter += 1

                if counter % 2 != 0:
                    mb.showinfo("Result", "Point is inside polygon")
                else:
                    mb.showinfo("Result", "Point is NOT inside polygon")

            case SpecialFunctions.ClassifyPointPosition:
                point = self.tp
                if point is None:
                    mb.showwarning("Error", "No point selected")
                    return

                shape = self.selected_shape
                if shape is None or not isinstance(shape, Line):
                    mb.showwarning("Error", "No line selected")
                    return

                if self.on_left(shape, point):
                    mb.showinfo("Result", "Point is on the left side of the line")
                else:
                    mb.showinfo("Result", "Point is on the right side of the line")

            case SpecialFunctions.RotateEdge90:
                center = self.lines[-1].center
                phi = radians(90)
                mat = np.array([
                    [cos(phi), -sin(phi), -center.x * cos(phi) + center.y * sin(phi) + center.x],
                    [sin(phi), cos(phi), -center.x * sin(phi) - center.y * cos(phi) + center.y],
                    [0, 0, 1]])

                p1 = self.lines[-1].p1
                p2 = self.lines[-1].p2

                l1 = Line(p1, center)
                l2 = Line(center, p2)
                l1.transform(mat)
                l2.transform(mat)

                self.redraw(delete_points=False)
                self.after(1, self.focus_force)

            case SpecialFunctions.EdgeIntersect:
                if len(self.lines) < 2:
                    mb.showwarning("Error", "Not enough lines")
                    return
                self.lines[-1].highlight(self.canvas, 500)
                self.lines[-2].highlight(self.canvas, 500)
                r = self.lines[-1].intersection(self.lines[-2])
                if r:
                    mb.showinfo("Result", f"Lines intersect at {r}")
                else:
                    mb.showinfo("Result", "Lines are NOT intersected")

            case SpecialFunctions.BezierCurve:
                if len(self.points) < 4:
                    mb.showwarning("Error", "Not enough points")
                    return

                self.redraw(delete_points=False)

                for i in range(0, len(self.points), 2):
                    if i+3 < len(self.points):
                        p0 = self.points[i]
                        p1 = self.points[i+1]
                        p2 = self.points[i+2]
                        p3 = self.points[i+3]
                        l1 = Line(p0, p1)
                        l2 = Line(p2, p3)
                        last = l2.center
                        if i == 0:
                            self.cubeBezierCurve(p0, p1, p2, last)
                        else:
                            if p3 == self.points[-1]:
                                self.cubeBezierCurve(l1.center, p1, p2, p3)
                            else:
                                self.cubeBezierCurve(l1.center, p1, p2, last)
                if len(self.points) % 2 != 0:
                    p0 = last
                    p1 = self.points[-2]
                    p3 = self.points[-1]
                    l = Line(p1, p3)
                    self.cubeBezierCurve(last, p1, l.center, p3)

        self.mode = Mode.PointDraw
        self.label2.config(text=f"Mode: {self.mode}")

    def cubeBezierCurve(self, p0: Point, p1: Point, p2: Point, p3: Point):
        matB = np.array([
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0]
        ])

        matX = np.array([p0.x, p1.x, p2.x, p3.x])
        matY = np.array([p0.y, p1.y, p2.y, p3.y])

        appmatX = np.matmul(matB, matX)
        appmatY = np.matmul(matB, matY)

        prevPoint = p0

        for t in np.arange(0, 1, 0.001):
            tempmat = np.array([np.power(t, 3), np.power(t, 2), t, 1])
            X = np.matmul(tempmat, appmatX)
            Y = np.matmul(tempmat, appmatY)
            cPoint = Point(X, Y)
            nl = Line(prevPoint, cPoint)
            nl.draw(self.canvas)
            prevPoint = cPoint

    def on_left(self, line: Line, p: Point):
        o = line.p1
        a = line.p2
        b = p

        s_d = (o.y-b.y)*(a.x-o.x) - (b.x-o.x)*(o.y-a.y)

        return s_d > 0

    def are_intersected(self, l1: Line, l2: Line):
        denum = (l1.p1.x - l1.p2.x)*(l2.p1.y-l2.p2.y) - (l1.p1.y-l1.p2.y)*(l2.p1.x-l2.p2.x)
        if denum == 0:
            return None

        t = ((l1.p1.x - l2.p1.x)*(l2.p1.y-l2.p2.y) - (l1.p1.y-l2.p1.y)*(l2.p1.x-l2.p2.x)) / denum

        point = Point(l1.p1.x+t*(l1.p2.x-l1.p1.x), l1.p1.y+t*(l1.p2.y-l1.p1.y))

        lowx1, highx1 = sorted([l1.p1.x, l1.p2.x])
        lowy1, highy1 = sorted([l1.p1.y, l1.p2.y])
        lowx2, highx2 = sorted([l2.p1.x, l2.p2.x])
        lowy2, highy2 = sorted([l2.p1.y, l2.p2.y])

        if lowx1 <= point.x <= highx1 and lowy1 <= point.y <= highy1 and lowx2 <= point.x <= highx2 and lowy2 <= point.y <= highy2:
            return point
        return None

    def _in_point(self, p: Point, x: int, y: int) -> bool:
        return (x - p.x) ** 2 + (y - p.y) ** 2 <= self.R ** 2

    def swap_shape_type(self, _):
        if self.mode == Mode.SelectShape:
            self._shape_type_idx = (self._shape_type_idx + 1) % len(ShapeType)
            self.shape_type = ShapeType(self._shape_type_idx)
            self.label1.config(text=f"Shape: {self.shape_type}")

    def mouse_move(self, event: tk.Event):
        if self.mode == Mode.SelectShape:
            if self.rect_sel_p1:
                self.rect_sel_p2 = Point(event.x, event.y)
                self.redraw(delete_points=False)
                self.canvas.create_rectangle(self.rect_sel_p1.x, self.rect_sel_p1.y,
                                             self.rect_sel_p2.x, self.rect_sel_p2.y,
                                             outline="red", dash=(4, 4))
            else:
                self.rect_sel_p1 = Point(event.x, event.y)
                self.rect_sel_p2 = None

    def mouse_release(self, _: tk.Event):
        if self.mode == Mode.SelectShape:
            if self.rect_sel_p1 and self.rect_sel_p2:
                self.redraw(delete_points=False)
                match self.shape_type:
                    case ShapeType.Point:
                        for p in self.points:
                            if p.in_rect(self.rect_sel_p1, self.rect_sel_p2):
                                p.highlight(self.canvas)
                                self.selected_shape = p
                                break
                    case ShapeType.Line:
                        for line in self.lines:
                            if line.in_rect(self.rect_sel_p1, self.rect_sel_p2):
                                line.highlight(self.canvas)
                                self.selected_shape = line
                                break
                    case ShapeType.Polygon:
                        for polygon in self.polygons:
                            if polygon.in_rect(self.rect_sel_p1, self.rect_sel_p2):
                                polygon.highlight(self.canvas)
                                self.selected_shape = polygon
                                break
                # if self.selected_shape is not None:
                    # self.selected_shape.center.highlight(self.canvas, timeout=1000)
                self.rect_sel_p1 = None
                self.rect_sel_p2 = None

    def set_temp_point(self, event: tk.Event):
        self.tp = Point(event.x, event.y)
        self.tp.highlight(self.canvas, timeout=500)

    def del_temp_point(self, _: tk.Event):
        self.tp = None

    def click(self, event: tk.Event):
        match self.mode:
            case Mode.PointDraw:
                point = Point(event.x, event.y)
                self.points.append(point)
                point.draw(self.canvas)

            case Mode.LineDraw:
                for p in self.points:
                    if self._in_point(p, event.x, event.y):
                        self.line_buffer.append(p)
                        p.highlight(self.canvas)

                if len(self.line_buffer) == 2:
                    line = Line(self.line_buffer[0], self.line_buffer[1])
                    self.line_buffer = []
                    line.draw(self.canvas)
                    self.lines.append(line)

            case Mode.PolygonDraw:
                point = Point(event.x, event.y)
                for p in self.points:
                    if self._in_point(point, p.x, p.y):
                        if len(self.polygon_buffer) > 0 and p == self.polygon_buffer[0]:
                            polygon = Polygon(self.polygon_buffer)
                            self.polygon_buffer = []
                            polygon.draw(self.canvas)
                            self.polygons.append(polygon)
                        else:
                            self.polygon_buffer.append(p)
                            p.highlight(self.canvas)
                        break


if __name__ == "__main__":
    App()

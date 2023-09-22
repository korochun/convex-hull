import math

from deq import Deq
from r2point import R2Point

ORIGIN = R2Point(0, 0)


# вычисление угла, под которым виден отрезок
def segment_angle(p, q):
    l1 = ORIGIN.dist(p)
    l2 = ORIGIN.dist(q)
    if l1 == 0 or l2 == 0:
        return 0
    return math.degrees(math.acos((p.x * q.x + p.y * q.y) / l1 / l2))


# условное вычисление угла
def poly_segment_angle(p, q):
    if R2Point.area(p, q, ORIGIN) < 0.0:
        return segment_angle(p, q)
    else:
        return 0


class Figure:
    """ Абстрактная фигура """

    def perimeter(self):
        return 0.0

    def area(self):
        return 0.0

    def angle(self):
        return 0.0


class Void(Figure):
    """ "Hульугольник" """

    def add(self, p):
        return Point(p)


class Point(Figure):
    """ "Одноугольник" """

    def __init__(self, p):
        self.p = p

    def add(self, q):
        return self if self.p == q else Segment(self.p, q)


class Segment(Figure):
    """ "Двуугольник" """

    def __init__(self, p, q):
        self.p, self.q = p, q

    def perimeter(self):
        return 2.0 * self.p.dist(self.q)

    def add(self, r):
        if R2Point.is_triangle(self.p, self.q, r):
            return Polygon(self.p, self.q, r)
        elif self.q.is_inside(self.p, r):
            return Segment(self.p, r)
        elif self.p.is_inside(r, self.q):
            return Segment(r, self.q)
        else:
            return self

    def angle(self):
        return segment_angle(self.p, self.q)


class Polygon(Figure):
    """ Многоугольник """

    def __init__(self, a, b, c):
        self.points = Deq()
        self.points.push_first(b)
        if not b.is_light(a, c):
            a, c = c, a
        self.points.push_first(a)
        self.points.push_last(c)
        self._perimeter = a.dist(b) + b.dist(c) + c.dist(a)
        self._area = abs(R2Point.area(a, b, c))

        self._angle = (poly_segment_angle(a, b)
                       + poly_segment_angle(b, c)
                       + poly_segment_angle(c, a))

    def perimeter(self):
        return self._perimeter

    def area(self):
        return self._area

    def angle(self):
        return self._angle

    # добавление новой точки
    def add(self, t):

        # поиск освещённого ребра
        for n in range(self.points.size()):
            if t.is_light(self.points.last(), self.points.first()):
                break
            self.points.push_last(self.points.pop_first())

        # хотя бы одно освещённое ребро есть
        if t.is_light(self.points.last(), self.points.first()):

            # учёт удаления ребра, соединяющего конец и начало дека
            self._perimeter -= self.points.first().dist(self.points.last())
            self._area += abs(R2Point.area(t,
                                           self.points.last(),
                                           self.points.first()))
            self._angle -= poly_segment_angle(
                self.points.last(), self.points.first())

            # удаление освещённых рёбер из начала дека
            p = self.points.pop_first()
            while t.is_light(p, self.points.first()):
                self._perimeter -= p.dist(self.points.first())
                self._area += abs(R2Point.area(t, p, self.points.first()))
                self._angle -= poly_segment_angle(p, self.points.first())
                p = self.points.pop_first()
            self.points.push_first(p)

            # удаление освещённых рёбер из конца дека
            p = self.points.pop_last()
            while t.is_light(self.points.last(), p):
                self._perimeter -= p.dist(self.points.last())
                self._area += abs(R2Point.area(t, p, self.points.last()))
                self._angle -= poly_segment_angle(self.points.last(), p)
                p = self.points.pop_last()
            self.points.push_last(p)

            # добавление двух новых рёбер
            self._perimeter += t.dist(self.points.first()) + \
                t.dist(self.points.last())
            self._angle += (poly_segment_angle(t, self.points.first())
                            + poly_segment_angle(self.points.last(), t))
            self.points.push_first(t)

        return self


if __name__ == "__main__":
    f = Void()
    print(type(f), f.__dict__)
    f = f.add(R2Point(0.0, 0.0))
    print(type(f), f.__dict__)
    f = f.add(R2Point(1.0, 0.0))
    print(type(f), f.__dict__)
    f = f.add(R2Point(0.0, 1.0))
    print(type(f), f.__dict__)

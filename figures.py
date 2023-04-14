from PyQt5.QtGui import QColor, QPolygonF, QPainter, QPen
from PyQt5.QtCore import QPoint, QPointF, QRect
# from PyQt5.QtWidgets import QPainter


class Figure:

    def __init__(self, start_point=QPoint()):
        self.p_point_array = QPolygonF()
        self.line_width = 1
        self.line_color = QColor(0, 0, 0)
        self.start_x = start_point.x()
        self.start_y = start_point.y()
        self.end_x = 0
        self.end_y = 0

    def set_color(self, color: QColor):
        self.line_color = color

    def set_width(self, width: int):
        self.line_width = width

    def get_color(self) -> QColor:
        return self.line_color

    def get_width(self) -> int:
        return self.line_width

    def add_point(self, new_point: QPoint):
        self.p_point_array.append(QPointF(new_point))

    def draw_dynamic(self, painter: QPainter, current_point: QPoint):
        painter.drawPolyline(self.p_point_array)

    def draw(self, painter: QPainter):
        painter.drawPolyline(self.p_point_array)

    def get_line_vector(self) -> QPointF:
        if len(self.p_point_array) == 2:
            return self.p_point_array[1] - self.p_point_array[0]


class Line(Figure):

    def __init__(self, start_point=QPoint()):
        super().__init__(start_point)

    def draw_dynamic(self, painter: QPainter, current_point: QPoint):
        pen = QPen(self.line_color, self.line_width)
        painter.setPen(pen)
        painter.drawLine(self.p_point_array[0], current_point)

    def draw(self, painter: QPainter):
        pen = QPen(self.line_color, self.line_width)
        painter.setPen(pen)
        if len(self.p_point_array) > 1:
            painter.drawPolyline(self.p_point_array)
        else:
            painter.drawPoint(self.p_point_array[0])


class Polygon(Figure):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)
        self.p_point_array = QPolygonF()

    def draw(self, paint: QPainter):
        if self.p_point_array.size() > 1:
            paint.drawPolygon(self.p_point_array)
        else:
            paint.drawPoints(self.p_point_array)

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        p_temp_point_array = QPolygonF(self.p_point_array)
        p_temp_point_array << current_point
        if p_temp_point_array.size() > 1:
            paint.drawPolyline(p_temp_point_array)
        if p_temp_point_array.size() == 1:
            paint.drawPoint(p_temp_point_array[0])


class Rect(Polygon):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        # convert qreal to int
        end_x = int(current_point.rx())
        end_y = int(current_point.ry())
        paint.drawRect(self.start_x, self.start_y, end_x - self.start_x,
                       end_y - self.start_y)

    def draw(self, paint: QPainter):
        end_x = int(self.p_point_array[1].rx())
        end_y = int(self.p_point_array[1].ry())

        paint.drawRect(self.start_x, self.start_y, end_x - self.start_x,
                       end_y - self.start_y)


class Triangle(Polygon):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        # convert qreal to int
        end_x = int(current_point.rx())
        end_y = int(current_point.ry())

        points = [
            QPointF(self.start_x, self.start_y),  # left_botton_point
            QPointF((self.start_x + end_x) / 2, end_y),  # top_point
            QPointF(end_x, self.start_y),  # right_bottom_point
        ]
        paint.drawPolygon(points)

    def draw(self, paint: QPainter):
        points = [
            QPointF(self.start_x, self.start_y),  # left_botton_point
            QPointF((self.start_x + self.end_x) / 2, self.end_y),  # top_point
            QPointF(self.end_x, self.start_y),  # right_bottom_point
        ]
        # update p_point_array
        self.p_point_array = QPolygonF([points[0], points[1], points[2]])
        paint.drawPolygon(points)


class Curve(Figure):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)
        self.p_point_array = []

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        self.p_point_array.append(current_point)
        if len(self.p_point_array) > 1:
            paint.drawPolyline(self.p_point_array)
        # only one point: without moving cursor, just click
        else:
            paint.drawPoints(self.p_point_array)

    def draw(self, paint: QPainter):
        if len(self.p_point_array) > 1:
            paint.drawPolyline(self.p_point_array)
        # only one point: without moving cursor, just click
        else:
            paint.drawPoints(self.p_point_array)


class Ellipse(Figure):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        # convert qreal to int
        end_x = int(current_point.rx())
        end_y = int(current_point.ry())
        rectangle = QRect(self.start_x, self.start_y, end_x - self.start_x,
                          end_y - self.start_y)
        paint.drawEllipse(rectangle)

    def draw(self, paint: QPainter):
        end_x = int(self.p_point_array[1].rx())
        end_y = int(self.p_point_array[1].ry())

        rectangle = QRect(self.start_x, self.start_y, end_x - self.start_x,
                          end_y - self.start_y)
        paint.drawEllipse(rectangle)


class Circle(Ellipse):

    def __init__(self, start_point: QPoint):
        super().__init__(start_point)

    def draw_dynamic(self, paint: QPainter, current_point: QPoint):
        # convert qreal to int
        end_x = int(current_point.rx())

        rectangle = QRect(self.start_x, self.start_y, end_x - self.start_x,
                          end_x - self.start_x)
        paint.drawEllipse(rectangle)

    def draw(self, paint: QPainter):
        end_x = int(self.p_point_array[1].rx())

        rectangle = QRect(self.start_x, self.start_y, end_x - self.start_x,
                          end_x - self.start_x)
        paint.drawEllipse(rectangle)

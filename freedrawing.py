from PyQt5 import QPainter, QColor, QtWidgets, Qt, QRectF\
    , QGraphicsView, QGraphicsItem, QGraphicsPathItem, QPainterPath, QPen\
    ,QGraphicsScene,QLabel


class MyScene(QGraphicsScene):  #自定场景
    pen_color = Qt.red  #预设笔的颜色
    pen_width = 5  #预设笔的宽度
    Eraser_pen_width = 20  #预设橡皮擦的宽度

    def __init__(self):  #初始函数
        super(MyScene, self).__init__(parent=None)  #实例化QGraphicsScene
        self.setSceneRect(0, 0, 600, 500)  #设置场景起始及大小，默认场景是中心为起始，不方便后面的代码

        # self.setForegroundBrush(Qt.white)
        self.EraseMode = False

        self.shape = "Free pen"

        # rect=QGraphicsRectItem(0,0,50,50)
        # rect.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        # rect.setPos(60,100)
        # self.addItem(rect)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.drawRect(0, 0, 600, 500)

    def Eraser(self, b=False):
        self.EraseMode = b
        return self.EraseMode

    def Shape(self, s):
        self.shape = s
        return self.Shape

    def ChangePenColor(self, color):
        self.pen_color = QColor(color)

    def ChangePenThickness(self, thickness):
        self.pen_width = thickness

    def ChangeEraserThickness(self, EraserThickness):
        self.Eraser_pen_width = EraserThickness


class GraphicView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.scene = MyScene()  # 设置管理QgraphicsItems的场景
            self.shape = "Free pen"  # 预设画笔为自由风格画笔
            self.pen_color = Qt.red  # 预设笔的颜色
            self.pen_width = 5  # 预设笔的宽度

            # 预设以下参数的值，以防画板打开第一时间操作导入图片后self.wx-self.x=None-None而出错
            self.x = 0
            self.y = 0
            self.wx = 0
            self.wy = 0

            self.setScene(self.scene)  # Qgraphicsview设置场景MyScene()

        except Exception as e:
            print(e)

    def Shape(self, s):
        """返回画笔属性状态"""
        self.shape = s
        if self.shape == "move":
            self.setDragMode(QGraphicsView.RubberBandDrag)  # 设置为支持橡皮筋框选模式
        else:
            self.setDragMode(QGraphicsView.NoDrag)  # 其他情况设置为不可拖拽模式
        return self.shape

    def ChangePenColor(self, color):
        """返回变更的画笔颜色"""
        self.pen_color = QColor(color)  # 当画笔颜色变化时，设置画笔颜色
        return self.pen_color

    def ChangePenThickness(self, thickness):
        """返回变更的画笔粗细"""
        self.pen_width = thickness  # 当画笔颜色变化时，设置画笔粗细

    def get_item_at_click(self, event):  # 返回鼠标点击的QgraphicsItem
        """ 返回你所点击的item """
        pos = event.pos()  # 注意此时是Qgraphicsview的鼠标点击位置
        # x=self.graphicsView.mapFromParent(pos)
        # y=self.graphicsView.mapFromScene(pos)
        # z=self.graphicsView.mapFromGlobal(pos)
        # print(pos,x,y,z)
        # print(pos)
        item = self.itemAt(pos)
        return item

    def mousePressEvent(self, event):
        """重载鼠标按下事件"""
        super(GraphicView,
              self).mousePressEvent(event)  # 此重置句必须要有，目的是为了画完Item后Item可被选择

        try:
            self.lastPoint = event.pos()  # 记录鼠标在Qgraphicsview按下的位置点
            self.x = self.lastPoint.x()
            self.y = self.lastPoint.y()

            pos = event.pos()  # 记录鼠标按下的位置
            self.t = self.mapToScene(pos)

            item = self.get_item_at_click(
                event)  # 记录鼠标点击Item的信息，若无Item，此函数返回None
            """"鼠标右键按下Item时，将其删除事件"""
            if event.button() == Qt.RightButton:
                if isinstance(item, QGraphicsItem):
                    self.scene.removeItem(item)
            """"触发鼠标左件事件"""
            if event.button() == Qt.LeftButton:

                self.tempPath = QGraphicsPathItem(
                )  # 设置一个内存上的QGraphicsPathItem，方便MouseMoveEvent画图时有双缓冲绘图效果
                self.tempPath.setFlags(
                    QtWidgets.QGraphicsItem.ItemIsSelectable
                    | QtWidgets.QGraphicsItem.ItemIsMovable
                    | QtWidgets.QGraphicsItem.ItemIsFocusable
                    | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
                    | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)

                self.path1 = QPainterPath()  # 实例路径函数，用于自由画笔风格
                self.path1.moveTo(pos)  # 设置路径开始点

                if self.shape == "line":
                    self.a = Arrow(self.scene, self.pen_color,
                                   self.pen_width)  # 设置实例化自定义的箭头类，但不传入起始点位置参数
                    self.a.set_src(self.x, self.y)  # 设置自定义箭头类的箭头线起始点

                # 千万不要再初始化__init__那里设置画笔Qpen，不然笔颜色，大小无法修改
                pp = QPen()  # 实例QPen
                pp.setColor(self.pen_color)  #设置颜色
                pp.setWidth(self.pen_width)  #设置宽度

                self.tempPath.setPen(pp)  # self.tempPath应用笔
                if item != None:
                    self.wl = item.boundingRect().width()
                    PaintBoard1().wc(self.wl)

        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event):
        """重载鼠标移动事件"""
        super(GraphicView, self).mouseMoveEvent(
            event)  # 此重置句必须要有，目的是为了画完Item后Item可被移动，可放在MouseMoveEvent最后

        self.endPoint = event.pos()  # 返回鼠标移动时的点位置
        self.wx = self.endPoint.x()
        self.wy = self.endPoint.y()

        self.w = self.wx - self.x  # 用于绘画矩形Rect和Ellipse图形时的宽（长）
        self.h = self.wy - self.y  # 用于绘画矩形Rect和Ellipse图形时的高（宽）

        self.m = self.mapFromScene(event.pos())
        item = self.get_item_at_click(event)

        if event.buttons(
        ) & Qt.LeftButton:  #仅左键时触发，event.button返回notbutton，需event.buttons()判断，这应是对象列表，用&判断

            try:
                # if item != None and isinstance(item,QGraphicsRectItem)==False:
                if item != None and item.type(
                ) != 4:  # 判断自定义的图片类（自己设置了图片的type()=4）时，画笔可以在图片上画图，而不会使图片在绘图时移动
                    super(GraphicView, self).mouseMoveEvent(event)

                elif self.shape == "circle":  # 圆形的item.type()=3
                    self.setCursor(Qt.ArrowCursor)  # 设置鼠标形状
                    if item == None:  # 若无点击Item时，画笔可以画圆形
                        pass
                    else:  # 若鼠标有点击图片类Item，设置该图片图元不可被选择和不可移动
                        item.setFlag(QGraphicsItem.ItemIsMovable,
                                     enabled=False)
                        item.setFlag(QGraphicsItem.ItemIsSelectable,
                                     enabled=False)
                    self.path2 = QPainterPath()  # 为了实现双缓冲的效果，另设一个QPainterPath
                    self.path2.addEllipse(self.t.x(), self.t.y(), self.w,
                                          self.h)  # 添加绘图路径
                    self.tempPath.setPath(
                        self.path2
                    )  # 由于self.path2是在内存上一直刷新，并销毁之前的绘图路径，此时tempath设置路径就能在绘图时有双缓冲效果
                    self.scene.addItem(self.tempPath)  # Myscene()场景中添加图元

                elif self.shape == "rect":  # 矩形的item.type()=3
                    self.setCursor(Qt.ArrowCursor)
                    if item == None:
                        pass
                    else:
                        item.setFlag(QGraphicsItem.ItemIsSelectable,
                                     enabled=False)
                        item.setFlag(QGraphicsItem.ItemIsMovable,
                                     enabled=False)
                    self.path3 = QPainterPath()
                    self.path3.addRect(self.x, self.y, self.w, self.h)
                    self.tempPath.setPath(self.path3)
                    self.scene.addItem(self.tempPath)

                elif self.shape == "Free pen":  # 自由风格画笔绘图的图元item.type()==2
                    self.setCursor(Qt.ArrowCursor)
                    if item == None:
                        pass
                    elif item != None:
                        item.setFlag(QGraphicsItem.ItemIsSelectable,
                                     enabled=False)
                        item.setFlag(QGraphicsItem.ItemIsMovable,
                                     enabled=False)
                    if self.path1:  # 即self.path1==True
                        self.path1.lineTo(event.pos())  # 移动并连接点
                        self.tempPath.setPath(
                            self.path1
                        )  # self.QGraphicsPath添加路径，如果写在上面的函数，是没线显示的，写在下面则在松键才出现线
                        self.scene.addItem(self.tempPath)

                elif self.shape == "line":  # 箭头类图元item.type()==2
                    self.setCursor(Qt.ArrowCursor)
                    if item == None:
                        pass
                    else:
                        item.setFlag(QGraphicsItem.ItemIsSelectable,
                                     enabled=False)
                        item.setFlag(QGraphicsItem.ItemIsMovable,
                                     enabled=False)
                    self.a.set_dst(self.wx, self.wy)  # 更新箭头类线条的末端点位置
                    self.a.update()  # 自定义箭头类图元刷新，不然没有双缓冲绘图效果
                    self.scene.addItem(self.a)

                elif self.shape == "move":  # 设置当self.shape=="Move"时，不做其他附加操作
                    self.setCursor(Qt.SizeAllCursor)
                    if item == None:
                        pass
                    else:
                        item.setFlag(QGraphicsItem.ItemIsSelectable,
                                     enabled=True)
                        item.setFlag(QGraphicsItem.ItemIsMovable, enabled=True)

            except Exception as e:
                print(e)
        # super().mouseMoveEvent(event)  # 该重置鼠标移动事件语句也可以写在这里

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(
            event)  # 此重置句必须要有，目的是为了画完Item后Item，Item不会出现移动bug
        item = self.get_item_at_click(event)
        try:
            if self.shape == "rect":
                if item.isSelected():
                    pass
                else:
                    self.scene.removeItem(self.tempPath)
                    self.r = RectItem(self.pen_color, self.pen_width,
                                      self.tempPath.boundingRect())
                    self.scene.addItem(self.r)

            elif self.shape == "circle":
                self.scene.removeItem(self.tempPath)
                self.e = EllipseItem(self.pen_color, self.pen_width,
                                     self.tempPath.boundingRect())
                self.scene.addItem(self.e)

        except Exception as e:
            print(e)

        # super().mouseReleaseEvent(event)  # 该重置鼠标移动事件语句也可以写在这里

    def get_items_at_rubber(self):
        """ 返回选择区域内的Items"""
        area = self.graphicsView.rubberBandRect()
        return self.graphicsView.items(area)

    # def wheelEvent(self, event):   # 可以利用鼠标滚轮进行Item的缩放或旋转
    #     """ 重载鼠标滚轮事件"""
    #     try:
    #         #factor = 1.41 ** (-event.delta() / 240.0)
    #         item=self.get_item_at_click(event)
    #         t=[]
    #         f = event.angleDelta().y()/120.0
    #         t.append(f)
    #         print(len(t))
    #         if event.angleDelta().y()/120.0 > 0:
    #             factor=1.2
    #         else:
    #             factor=0.8
    #         # item.setScale(factor)
    #         item.setRotation(30)
    #         # item.boundingRect().adjust()
    #
    #     except Exception as e:
    #         print(e)


class PItem(QGraphicsRectItem):
    """ 导入图片可缩放的自定义图片类，实际是重写QGraphicsRectItem类"""
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +10.0
    handleSpace = -4.0

    # 设置鼠标形状
    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, filename, *args):
        """初始化图形类基础信息"""
        super().__init__(*args)
        self.filename = filename  # 记录导入的图片存储路径
        self.setZValue(-1)  # 使插入的图片在Myscene()的-1层
        self.pix = QPixmap(filename)  # 设置Pixmap为导入的图片
        self.g = PaintBoard1()

        self.handles = {}

        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()

    def type(self):
        type = 4  # 重写本次自定义图片类的Item.type()的值为4
        return type

    def handleAt(self, point):  # point为鼠标的点位置信息
        """返回自设定的小handle是否包含鼠标所在的点位置，若是，则返回鼠标在第几个handle上"""
        for k, v, in self.handles.items(
        ):  # k为数值1~8，辨别是handleTopLeft=1还是其他；v则是返回小handle的QRectF
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """执行鼠标在图片上移动的事件（非鼠标点击事件）"""
        if self.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[
                handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """执行鼠标移动到图片外边的事件（非鼠标点击事件）"""
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """执行鼠标在图片上点击事件"""
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect(
            )  # 返回点击的Rect的boundingRect虚函数
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """执行鼠标在图片上点击后按住鼠标移动的事件"""
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())  # 此句鼠标点击图片并移动时返回None值
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """执行鼠标在图片上释放事件"""
        super().mouseReleaseEvent(mouseEvent)
        # 重设以下参数
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """返回图形的boundingRect，其中包含resize handles的boundingRect"""
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """基于图形的形状尺寸和位置，更新现有的resize handles位置"""
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2,
                                                    b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s,
                                                   s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(),
                                                     b.center().y() - s / 2, s,
                                                     s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s,
                                                      b.center().y() - s / 2,
                                                      s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(),
                                                     b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2,
                                                       b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s,
                                                      b.bottom() - s, s, s)

    def interactiveResize(self, mousePos):
        """用于交互式的矩形变换，如重设点位置"""
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:

            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.updateHandlesPos()

    def shape(self):
        """返回Item的shape形状，并在local coordinates添加到QPainterPath上"""
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():  # 当该自定义图形类被选中时
            for shape in self.handles.values():  # 在每个handles点上加上小圆圈
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """在Qgraphicview上绘制边框的选择小圆圈"""
        point = QPointF(0, 0)  # 插入的图片的左上角位置
        self.w = self.rect().width()
        self.h = self.rect().height()
        self.pixfixed = self.pix.scaled(self.w, self.h)
        painter.drawPixmap(point, self.pixfixed, self.rect())

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(
            QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap,
                 Qt.RoundJoin))
        for shape in self.handles.values():
            if self.isSelected():
                painter.drawEllipse(shape)

    def w_and_h_show(self):
        pass


class RectHandle(QGraphicsRectItem):  #QGraphicsRectItem
    """ 自定义小handles的名称、序号、控制点位置"""
    # handles 按照顺时针排列
    handle_names = ('left_top', 'middle_top', 'right_top', 'right_middle',
                    'right_bottom', 'middle_bottom', 'left_bottom',
                    'left_middle')
    # 设定在控制点上的光标形状
    handle_cursors = {
        0: Qt.SizeFDiagCursor,
        1: Qt.SizeVerCursor,
        2: Qt.SizeBDiagCursor,
        3: Qt.SizeHorCursor,
        4: Qt.SizeFDiagCursor,
        5: Qt.SizeVerCursor,
        6: Qt.SizeBDiagCursor,
        7: Qt.SizeHorCursor
    }
    offset = 6.0  # 外边界框相对于内边界框的偏移量，也是控制点的大小

    #min_size = 8 * offset  # 矩形框的最小尺寸

    def update_handles_pos(self):
        """
        更新控制点的位置
        """
        o = self.offset  # 偏置量
        s = o * 2  # handle 的大小
        b = self.rect()  # 获取内边框
        x1, y1 = b.left(), b.top()  # 左上角坐标
        offset_x = b.width() / 2
        offset_y = b.height() / 2
        # 设置 handles 的位置
        self.handles[0] = QRectF(x1 - o, y1 - o, s, s)
        self.handles[1] = self.handles[0].adjusted(offset_x, 0, offset_x, 0)
        self.handles[2] = self.handles[1].adjusted(offset_x, 0, offset_x, 0)
        self.handles[3] = self.handles[2].adjusted(0, offset_y, 0, offset_y)
        self.handles[4] = self.handles[3].adjusted(0, offset_y, 0, offset_y)
        self.handles[5] = self.handles[4].adjusted(-offset_x, 0, -offset_x, 0)
        self.handles[6] = self.handles[5].adjusted(-offset_x, 0, -offset_x, 0)
        self.handles[7] = self.handles[6].adjusted(0, -offset_y, 0, -offset_y)


class RectItem(RectHandle):
    """ 自定义可变矩形类"""

    def __init__(self, color, width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handles = {}  # 控制点的字典
        self.setAcceptHoverEvents(True)  # 设定为接受 hover 事件
        self.setFlags(QGraphicsItem.ItemIsSelectable |  # 设定矩形框为可选择的
                      QGraphicsItem.ItemSendsGeometryChanges |  # 追踪图元改变的信息
                      QGraphicsItem.ItemIsFocusable |  # 可聚焦
                      QGraphicsItem.ItemIsMovable)  # 可移动
        self.update_handles_pos()  # 初始化控制点
        self.reset_Ui()  # 初始化 UI 变量
        self.pen_color = color
        self.pen_width = width

    def reset_Ui(self):
        '''初始化 UI 变量'''
        self.handleSelected = None  # 被选中的控制点
        self.mousePressPos = None  # 鼠标按下的位置
        #self.mousePressRect = None  # 鼠标按下的位置所在的图元的外边界框

    def boundingRect(self):
        """
        限制图元的可视化区域，且防止出现图元移动留下残影的情况
        """
        o = self.offset
        # 添加一个间隔为 o 的外边框
        return self.rect().adjusted(-o, -o, o, o)

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        # painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        painter.drawRect(self.rect())
        # painter.drawEllipse(self.rect())

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 0, 200)))
        painter.setPen(
            QPen(QColor(0, 0, 0, 255), 0, Qt.SolidLine, Qt.RoundCap,
                 Qt.RoundJoin))

        for shape in self.handles.values():
            if self.isSelected():
                painter.drawEllipse(shape)

    def handle_at(self, point):
        """
        返回给定 point 下的控制点 handle
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return

    def hoverMoveEvent(self, event):
        """
        当鼠标移到该 item（未按下）上时执行。
        """
        super().hoverMoveEvent(event)
        handle = self.handle_at(event.pos())
        cursor = self.handle_cursors[
            handle] if handle in self.handles else Qt.ArrowCursor
        self.setCursor(cursor)

    def hoverLeaveEvent(self, event):
        """
        当鼠标离开该形状（未按下）上时执行。
        """
        super().hoverLeaveEvent(event)
        self.setCursor(Qt.ArrowCursor)  # 设定鼠标光标形状

    def mousePressEvent(self, event):
        """
        当在 item 上按下鼠标时执行。
        """
        super().mousePressEvent(event)
        self.handleSelected = self.handle_at(event.pos())
        if self.handleSelected in self.handles:
            self.mousePressPos = event.pos()

    def mouseReleaseEvent(self, event):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(event)
        self.update()
        self.reset_Ui()

    def mouseMoveEvent(self, event):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected in self.handles:
            self.interactiveResize(event.pos())
        else:
            super().mouseMoveEvent(event)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        rect = self.rect()
        self.prepareGeometryChange()
        # movePos = mousePos - self.mousePressPos
        # move_x, move_y = movePos.x(), movePos.y()
        if self.handleSelected == 0:
            rect.setTopLeft(mousePos)
        elif self.handleSelected == 1:
            rect.setTop(mousePos.y())
        elif self.handleSelected == 2:
            rect.setTopRight(mousePos)
        elif self.handleSelected == 3:
            rect.setRight(mousePos.x())
        elif self.handleSelected == 4:
            rect.setBottomRight(mousePos)
        elif self.handleSelected == 5:
            rect.setBottom(mousePos.y())
        elif self.handleSelected == 6:
            rect.setBottomLeft(mousePos)
        elif self.handleSelected == 7:
            rect.setLeft(mousePos.x())
        self.setRect(rect)
        self.update_handles_pos()


class EllipseItem(RectHandle):
    """ 自定义可变椭圆类"""

    def __init__(self, color, width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handles = {}  # 控制点的字典
        self.setAcceptHoverEvents(True)  # 设定为接受 hover 事件
        self.setFlags(QGraphicsItem.ItemIsSelectable |  # 设定矩形框为可选择的
                      QGraphicsItem.ItemSendsGeometryChanges |  # 追踪图元改变的信息
                      QGraphicsItem.ItemIsFocusable |  # 可聚焦
                      QGraphicsItem.ItemIsMovable)  # 可移动
        self.update_handles_pos()  # 初始化控制点
        self.reset_Ui()  # 初始化 UI 变量
        self.pen_color = color
        self.pen_width = width

    def reset_Ui(self):
        '''初始化 UI 变量'''
        self.handleSelected = None  # 被选中的控制点
        self.mousePressPos = None  # 鼠标按下的位置
        #self.mousePressRect = None  # 鼠标按下的位置所在的图元的外边界框

    def boundingRect(self):
        """
        限制图元的可视化区域，且防止出现图元移动留下残影的情况
        """
        o = self.offset
        # 添加一个间隔为 o 的外边框
        return self.rect().adjusted(-o, -o, o, o)

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        # painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        # painter.drawRect(self.rect())
        painter.drawEllipse(self.rect())

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 0, 200)))
        painter.setPen(
            QPen(QColor(0, 0, 0, 255), 0, Qt.SolidLine, Qt.RoundCap,
                 Qt.RoundJoin))

        for shape in self.handles.values():
            if self.isSelected():
                painter.drawEllipse(shape)

    def handle_at(self, point):
        """
        返回给定 point 下的控制点 handle
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return

    def hoverMoveEvent(self, event):
        """
        当鼠标移到该 item（未按下）上时执行。
        """
        super().hoverMoveEvent(event)
        handle = self.handle_at(event.pos())
        cursor = self.handle_cursors[
            handle] if handle in self.handles else Qt.ArrowCursor
        self.setCursor(cursor)

    def hoverLeaveEvent(self, event):
        """
        当鼠标离开该形状（未按下）上时执行。
        """
        super().hoverLeaveEvent(event)
        self.setCursor(Qt.ArrowCursor)  # 设定鼠标光标形状

    def mousePressEvent(self, event):
        """
        当在 item 上按下鼠标时执行。
        """
        super().mousePressEvent(event)
        self.handleSelected = self.handle_at(event.pos())
        if self.handleSelected in self.handles:
            self.mousePressPos = event.pos()

    def mouseReleaseEvent(self, event):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(event)
        self.update()
        self.reset_Ui()

    def mouseMoveEvent(self, event):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected in self.handles:
            self.interactiveResize(event.pos())
        else:
            super().mouseMoveEvent(event)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        rect = self.rect()
        self.prepareGeometryChange()
        # movePos = mousePos - self.mousePressPos
        # move_x, move_y = movePos.x(), movePos.y()
        if self.handleSelected == 0:
            rect.setTopLeft(mousePos)
        elif self.handleSelected == 1:
            rect.setTop(mousePos.y())
        elif self.handleSelected == 2:
            rect.setTopRight(mousePos)
        elif self.handleSelected == 3:
            rect.setRight(mousePos.x())
        elif self.handleSelected == 4:
            rect.setBottomRight(mousePos)
        elif self.handleSelected == 5:
            rect.setBottom(mousePos.y())
        elif self.handleSelected == 6:
            rect.setBottomLeft(mousePos)
        elif self.handleSelected == 7:
            rect.setLeft(mousePos.x())
        self.setRect(rect)
        self.update_handles_pos()


class Arrow(QGraphicsPathItem):
    """ 自定义箭头类，类重写的是QGraphicsPathItem"""

    def __init__(self, scene, color, penwidth, parent=None):
        super().__init__(parent)
        self.pen_color = color  # 从Qgraphicsview导入笔的颜色
        self.pen_width = penwidth  # 从Qgraphicsview导入笔的宽度

        self.scene = scene  #从Qgraphicsview导入Myscene()这个场景，并设置为它

        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self.setFlags(QGraphicsItem.ItemIsSelectable |  # 设定矩形框为可选择的
                      QGraphicsItem.ItemSendsGeometryChanges |  # 追踪图元改变的信息
                      QGraphicsItem.ItemIsFocusable |  # 可聚焦
                      QGraphicsItem.ItemIsMovable)  # 可移动

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        path = QPainterPath(QPointF(self.pos_src[0], self.pos_src[1]))
        path.lineTo(self.pos_dst[0], self.pos_dst[1])
        return path

    def boundingRect(self):
        o = self.offset = self.pen_width * 10
        x1, y1 = self.pos_src
        x2 = self.shape().boundingRect().width()
        y2 = self.shape().boundingRect().height()
        self.QF = QRectF(x1, y1, x2, y2)
        return self.shape().boundingRect().adjusted(-o, -o, o, o)
        # return self.QF.adjusted(-o,-o,o,o)

    def shape(self):
        return self.calc_path()

    def paint(self, painter, option, widget=None):
        self.setPath(self.calc_path())
        path = self.path()
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        painter.drawPath(path)

        x1, y1 = self.pos_src
        x2, y2 = self.pos_dst

        self.source = QPointF(x1, y1)
        self.dest = QPointF(x2, y2)
        self.line = QLineF(self.source, self.dest)
        # 设置垂直向量
        v = self.line.unitVector()
        v.setLength(self.pen_width * 4)
        v.translate(QPointF(self.line.dx(), self.line.dy()))
        # 设置水平向量
        n = v.normalVector()
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()
        # 设置箭头三角形的三个点
        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()
        # 以下用于绘制箭头，外边框粗为1.0
        painter.setPen(QPen(self.pen_color, 1.0, Qt.SolidLine))
        painter.setBrush(self.pen_color)
        painter.drawPolygon(p1, p2, p3)


class TextItemDlg(QDialog):
    """ 自定义文本类所用到的窗口，用的是类似Qwidget"""

    def __init__(self, item=None, position=None, scene=None, parent=None):
        super(QDialog, self).__init__(parent)
        try:
            self.item = item

            self.position = position

            self.scene = scene
            self.font = None

            self.background_color_str = "white"
            self.booltext = False

            self.editor = QTextEdit()
            self.editor.setAcceptRichText(False)
            self.editor.setTabChangesFocus(True)
            editorLabel = QLabel("文字输入框:")
            editorLabel.setBuddy(self.editor)
            self.fontComboBox = QFontComboBox()
            self.fontComboBox.setCurrentFont(QFont("Times", PointSize))
            fontLabel = QLabel("&字体：")
            fontLabel.setBuddy(self.fontComboBox)
            self.fontSpinBox = QSpinBox()
            self.fontSpinBox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.fontSpinBox.setRange(5, 300)
            self.fontSpinBox.setValue(PointSize)
            fontSizeLabel = QLabel("&字体大小：")
            fontSizeLabel.setBuddy(self.fontSpinBox)
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                              | QDialogButtonBox.Cancel)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.textcolorlabel = QLabel("字体颜色：")
            self.textcolor = QComboBox()
            self.backgroundcolorlabel = QLabel("文本框颜色:")
            self.backgroundcolorlabel.setAlignment(Qt.AlignRight
                                                   | Qt.AlignVCenter)
            self.backgroundcolor = QComboBox()
            # 获取颜色列表(字符串类型)
            self.__colorList = QColor.colorNames()
            # 用各种颜色填充下拉列表
            self.__fillColorList(self.textcolor)
            self.__fillColorList1(self.backgroundcolor)

            self.bold_btn = QPushButton("B/加粗")
            self.bold_btn.setCheckable(True)
            self.Italic_btn = QPushButton("I/斜体")
            self.Italic_btn.setCheckable(True)
            self.underline_btn = QPushButton("U/下划线")
            self.underline_btn.setCheckable(True)

            if self.item is not None:
                self.editor.setPlainText(self.item.toPlainText())
                self.fontComboBox.setCurrentFont(self.item.font())
                self.fontSpinBox.setValue(self.item.font().pointSize())

            layout = QGridLayout()
            layout.addWidget(editorLabel, 0, 0)
            layout.addWidget(self.bold_btn, 0, 1)
            layout.addWidget(self.Italic_btn, 0, 2)
            layout.addWidget(self.underline_btn, 0, 3)
            layout.addWidget(self.editor, 1, 0, 1, 6)
            layout.addWidget(fontLabel, 2, 0)
            layout.addWidget(self.fontComboBox, 2, 1, 1, 2)
            layout.addWidget(fontSizeLabel, 2, 3)
            layout.addWidget(self.fontSpinBox, 2, 4, 1, 2)
            layout.addWidget(self.buttonBox, 4, 0, 1, 6)
            layout.addWidget(self.textcolor, 3, 1, 1, 1)
            layout.addWidget(self.textcolorlabel, 3, 0)
            layout.addWidget(self.backgroundcolorlabel, 3, 2)
            layout.addWidget(self.backgroundcolor, 3, 3, 1, 1)
            self.setLayout(layout)

            self.fontComboBox.currentFontChanged.connect(self.updateUi)
            self.fontSpinBox.valueChanged.connect(self.updateUi)
            self.editor.textChanged.connect(self.updateUi)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)
            # self.textcolor.currentIndexChanged.connect(self.on_textcolorChange)
            self.textcolor.currentIndexChanged.connect(self.updateUi)
            self.backgroundcolor.currentIndexChanged.connect(
                self.on_backgroundcolorChange)
            self.setWindowTitle("添加文本")
            self.setWindowIcon(QIcon("q.ico"))
            self.updateUi()
            self.bold_btn.clicked.connect(self.on_bold_btn_clicked)

        except Exception as e:
            print(e)

    def on_bold_btn_clicked(self):
        self.booltext = self.bold_btn.isChecked()

    def on_textcolorChange(self):
        self.color_index = self.textcolor.currentIndex()
        self.color_str = self.__colorList[self.color_index]

    def on_backgroundcolorChange(self):
        self.background_color_index = self.backgroundcolor.currentIndex()
        self.background_color_str = self.__colorList[
            self.background_color_index]

    def __fillColorList(self, comboBox):
        index_red = 0
        index = 0
        for color in self.__colorList:
            if color == "red":
                index_red = index
            index += 1
            pix = QPixmap(120, 30)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix), None)
            comboBox.setIconSize(QSize(100, 20))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        comboBox.setCurrentIndex(index_red)

    def __fillColorList1(self, comboBox):
        index_white = 0
        index = 0
        for color in self.__colorList:
            if color == "white":
                index_white = index
            index += 1
            pix = QPixmap(120, 30)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix), None)
            comboBox.setIconSize(QSize(100, 20))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        comboBox.setCurrentIndex(index_white)

    def updateUi(self):
        try:
            self.font = self.fontComboBox.currentFont()
            self.font.setPointSize(self.fontSpinBox.value())
            self.editor.document().setDefaultFont(self.font)
            self.color_index = self.textcolor.currentIndex()
            self.color_str = self.__colorList[self.color_index]
            pl = QPalette()
            pl.setColor(QPalette.Text, QColor(self.color_str))
            self.editor.setPalette(pl)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.editor.toPlainText()))
            self.font.setBold(self.booltext)
        except Exception as e:
            print(e)

    def accept(self):
        try:
            if self.item is None:
                self.item = TextItem("", self.position, self.scene)
            self.font = self.fontComboBox.currentFont()
            self.font.setPointSize(self.fontSpinBox.value())

            self.item.setFont(self.font)
            text = '<span style="background:' + self.background_color_str + ';"><font color="' + self.color_str + '">' + self.editor.toPlainText(
            ) + '</font></span>'

            # 测试是否有换行符
            # for i,t in enumerate(text):
            #     if t=="\n":
            #         print("y")
            #         t="<br/>"

            text_fixed = text.replace("\n", "<br/>")
            print(text_fixed)
            self.item.setHtml(text_fixed)
            QDialog.accept(self)
        except Exception as e:
            print(e)


PointSize = 15


class TextItem(QGraphicsTextItem):
    """ 自定义文本类"""

    def __init__(self, text, position, scene, font=QFont("宋体", PointSize)):
        super(TextItem, self).__init__(text)
        try:
            self.setFlags(
                QtWidgets.QGraphicsItem.ItemIsSelectable
                | QtWidgets.QGraphicsItem.ItemIsMovable
                | QtWidgets.QGraphicsItem.ItemIsFocusable
                | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
                | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
            self.setFont(font)
            self.setDefaultTextColor(Qt.red)
            self.setPos(position)
            scene.clearSelection()
            scene.addItem(self)
            self.setSelected(True)
        except Exception as e:
            print(e)

    def parentWidget(self):
        try:
            return self.scene().views()[0]
        except Exception as e:
            print(e)

    def mouseDoubleClickEvent(self, event):
        dialog = TextItemDlg(self, self.parentWidget())
        dialog.exec_()


# 画板弹窗界面
class PaintBoard1(QWidget, painter):

    def __init__(self):
        super(QWidget, self).__init__()

        self.setupUi(self)
        self.graphics = GraphicView()

        self.scene = self.graphics.scene
        self.graphics.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # 千万记得用addWidget(self.graphics)，而不是addWidget(addWidget)，不然传参数会有问题
        self.gridLayout_paintbox.addWidget(self.graphics)

        self.pix = None
        self.pixfixed = None
        self.pw = None
        self.ph = None

        # 获取颜色列表(字符串类型)
        self.__colorList = QColor.colorNames()
        # 用各种颜色填充下拉列表
        self.__fillColorList(self.comboBox_penColor)
        # 下拉菜单改变画笔颜色
        # 关联下拉列表的当前索引变更信号与函数on_PenColorChange
        self.comboBox_penColor.currentIndexChanged.connect(
            self.on_PenColorChange)

        # 设置画笔粗细大小
        self.Pen_Thickness.setMaximum(50)
        self.Pen_Thickness.setMinimum(0)
        self.Pen_Thickness.setValue(5)
        self.Pen_Thickness.setSingleStep(1)
        # 关联spinBox值变化信号和函数on_PenThicknessChange
        self.Pen_Thickness.valueChanged.connect(self.on_PenThicknessChange)

        # 信号与槽
        self.Openfile_btn.clicked.connect(self.on_btn_Open_Clicked)
        self.Quit_btn.clicked.connect(self.on_btn_Quit_Clicked)
        self.Clear_btn.clicked.connect(self.clean_all)
        # self.Eraser_cbtn.clicked.connect(self.on_cbtn_Eraser_clicked)
        self.Save_btn.clicked.connect(self.on_btn_Save_Clicked)
        self.circle_btn.clicked.connect(self.on_circle_btn_clicked)
        self.Free_pen_btn.clicked.connect(self.on_Free_pen_btn_clicked)
        self.line_btn.clicked.connect(self.line_btn_clicked)
        self.rect_btn.clicked.connect(self.on_rect_btn_clicked)
        self.text_btn.clicked.connect(self.addText)
        self.pic_move_btn.clicked.connect(self.on_pic_move_btn_clicked)
        self.drawback_btn.clicked.connect(self.drawback)
        self.set_upper_btn.clicked.connect(self.item_up)
        self.set_lower_btn.clicked.connect(self.item_down)
        self.test.clicked.connect(self.item_rect_change)

    def line_btn_clicked(self, *type):
        type = "line"
        self.graphics.Shape(type)

    def wc(self, w):

        self.w = w
        print(self.w)
        self.strw = str(int(self.w))
        self.wid = QLabel()
        self.wid.setText(self.strw)
        self.gridLayout_paintbox.addWidget(self.wid)

    def wh_change(self, w, h):
        try:
            self.w = w
            self.h = h
            print(self.w, self.h)

        except Exception as e:
            print(e)

    # 记录鼠标选择的items
    def selectedItem(self):
        items = self.scene.selectedItems()
        if len(items) == 1:
            return items[0]
        return None

    def item_rect_change(self):
        item = self.selectedItem()
        if item == None:
            pass
        else:
            width = item.boundingRect().width()
            height = item.boundingRect().height()
            self.width_value.setText(str(int(width)))
            self.height_value.setText(str(int(height)))
        self.scene.addItem(Rectangle(200, 150, 100, 100))

    # 上移一层
    def item_up(self):
        try:
            if self.selectedItem() == None:
                print("no item selected")
            # item=self.scene.itemAt(self.point)
            else:
                z = self.selectedItem().zValue()
                self.selectedItem().setZValue(z + 1)
        except Exception as e:
            print(e)

    # 下移一层
    def item_down(self):
        try:
            if self.selectedItem() == None:
                print("no item selected")
            else:
                z = self.selectedItem().zValue()
                self.selectedItem().setZValue(z - 1)
        except Exception as e:
            print(e)

    # 撤销上一个绘图的图元
    def drawback(self, *item):
        try:
            items = self.scene.items()
            item = items[0]
            print(item)
            self.scene.removeItem(item)
        except Exception as e:
            print(e)

    # 设置图片移动
    def on_pic_move_btn_clicked(self, *type):
        type = "move"
        self.graphics.Shape(type)
        self.scene.clearSelection()

    # 添加文本
    def addText(self):
        try:
            dialog = TextItemDlg(position=QPoint(200, 200),
                                 scene=self.scene,
                                 parent=None)
            dialog.exec_()
        except Exception as e:
            print(e)

    def on_Scene_size_clicked(self):
        w = self.scene.width()
        h = self.scene.height()
        p = self.width()
        q = self.height()
        s = self.size()

    def on_Free_pen_btn_clicked(self, *shape):
        shape = "Free pen"
        self.graphics.Shape(shape)

    # 设置画圆圈
    def on_circle_btn_clicked(self, *shape):  # 注意传入参数为文字时，为*加上变量，即“*变量”
        try:
            shape = "circle"
            self.graphics.Shape(shape)
        except Exception as e:
            print(e)

    def on_rect_btn_clicked(self, *shape):
        shape = "rect"
        self.graphics.Shape(shape)

    # 打开图片功能
    def on_btn_Open_Clicked(self):
        try:
            openPath = QFileDialog.getOpenFileName(self, '打开图片', '.\\',
                                                   '*.png;*.jpg')
            # print(openPath)
            if openPath[0] == "":
                print("已取消")
                return
            filename = openPath[0]
            # print(filename)
            self.pix = QPixmap()
            self.pix.load(filename)
            # print(self.pix.width(),self.pix.height())
            # 对于图片长宽超过800,600的，缩放后完全显示
            self.pixfixed = self.pix.scaled(600, 600, Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
            # self.scene.addPixmap(self.pixfixed)
            # print(self.pixfixed.width(),self.pixfixed.height())
            item1 = PItem(filename, 0, 0, 600, 500)
            self.scene.addItem(item1)

            item = QGraphicsPixmapItem(self.pixfixed)
            # item.setFlag(QGraphicsItem.ItemIsSelectable)
            item.setFlag(QGraphicsItem.ItemIsMovable)
            item.setZValue(-1)
            # self.pixrect=item.boundingRect()
            # self.scene.addItem(item)
            self.pw = self.pixfixed.width()
            self.ph = self.pixfixed.height()
        except Exception as e:
            print(e)

    # 退出画板主窗口
    def on_btn_Quit_Clicked(self):
        self.close()

    # 图片保存功能
    def on_btn_Save_Clicked(self):
        try:
            savePath = QFileDialog.getSaveFileName(self, '保存图片', '.\\',
                                                   '*.jpg;*.png')

            if savePath[0] == "":
                print("取消保存")
                return
            # pm=QPixmap(self.pixfixed.width(), self.pixfixed.height())
            pm = QPixmap(600, 500)  # 注意，设置画布的大小为Myscene的大小，下边保存时才不会产生黑边

            pm.fill(Qt.white)  # 当区域没有Item时，保存图片不产生黑色区域

            # 设置绘图工具
            painter1 = QPainter(pm)
            painter1.setRenderHint(QPainter.Antialiasing)
            painter1.setRenderHint(QPainter.SmoothPixmapTransform)

            # 使打印长和宽与导入的Pixmap图片长宽匹配，不会产生黑边
            # self.graphics.render(painter1,QRectF(0,0,self.pixfixed.width(),self.pixfixed.height()),QRect(0,0,self.pixfixed.width(),self.pixfixed.height()))

            # 注意，大小设置与Myscene的大小一致，画布大小一致时，才真的不会产生黑边
            self.graphics.render(painter1, QRectF(0, 0, 600, 500),
                                 QRect(0, 0, 600, 500))
            # QRect(0, 0, 600, 500))
            painter1.end()
            pm.save(savePath[0])

        except Exception as e:
            print(e)

    # combobox填充颜色序列
    def __fillColorList(self, comboBox):
        index_red = 0
        index = 0
        for color in self.__colorList:
            if color == "red":
                index_red = index
            index += 1
            pix = QPixmap(120, 30)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix), None)
            comboBox.setIconSize(QSize(100, 20))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        comboBox.setCurrentIndex(index_red)

    # 画笔颜色更改
    def on_PenColorChange(self):
        color_index = self.comboBox_penColor.currentIndex()
        color_str = self.__colorList[color_index]
        self.graphics.ChangePenColor(color_str)

    # 画笔粗细调整
    def on_PenThicknessChange(self):
        penThickness = self.Pen_Thickness.value()
        self.graphics.ChangePenThickness(penThickness)
        # 设置鼠标Qcursor指标为画笔图片
        # pm = QPixmap('pen.ico')
        # l= self.Pen_Thickness.value()
        # if l<=10:
        #     l=10
        # pm = pm.scaled(l, l, Qt.KeepAspectRatio)
        # cursor = QCursor(pm)
        # self.setCursor(cursor)

    # 橡皮擦粗细调整
    def on_EraserThicknessChange(self):
        EraserThickness = self.Eraser_thickness.value()
        self.scene.ChangeEraserThickness(EraserThickness)
        pm = QPixmap('circle.ico')
        r = self.Eraser_thickness.value()
        pm = pm.scaled(r, r, Qt.KeepAspectRatio)
        cursor = QCursor(pm)
        self.setCursor(cursor)

    # 清除图元
    def clean_all(self):
        try:
            self.scene.clear()
        except Exception as e:
            print(e)


class Rectangle(QtWidgets.QGraphicsRectItem):
    """ 自定义可变矩形类，采用鼠标中键动态设置矩形大小"""

    def __init__(self, x, y, w, h):
        super(Rectangle, self).__init__(0, 0, w, h)
        self.setPen(QPen(Qt.red, 5))
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable
                      | QtWidgets.QGraphicsItem.ItemIsMovable
                      | QtWidgets.QGraphicsItem.ItemIsFocusable
                      | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
                      | QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setPos(QPointF(x, y))
        self.setZValue(1)

    def mouseMoveEvent(self, e):
        # print(self.x,self.y)
        if e.buttons() & Qt.LeftButton:
            super(Rectangle, self).mouseMoveEvent(e)
        if e.buttons() & Qt.MidButton:
            self.setRect(QRectF(QPoint(), e.pos()).normalized())

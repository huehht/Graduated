import math
from figures import Figure


class CEdge:  # 边

    def __init__(self):
        self.x = 0  # 当前横坐标
        self.ymax = 0  # 边的上端y坐标，取整数值
        self.dx = 0  # 斜率倒数

    def __lt__(self, other):
        if self.x == other.x:
            return self.dx < other.dx
        return self.x < other.x


class CScanLine:

    def __init__(self, p_polygon: Figure):
        self.p_polygon = p_polygon  # 多边形figure对象
        self.active_edge_table = []
        self.InitInfo()
        self.FillPolygon()  # 读取内部及边界信息

    def InitInfo(self):  # 多边形的初始化信息
        self.top = -math.inf  # 上端y坐标
        self.bottom = math.inf  # 下端y坐标
        self.left = math.inf  # 左端x坐标
        self.right = -math.inf  # 右端x坐标

        for iter in self.p_polygon.p_point_array:
            if iter.x() < self.left:
                self.left = iter.x()
            if iter.x() > self.right:
                self.right = iter.x()
            if iter.y() > self.top:
                self.top = iter.y()
            if iter.y() < self.bottom:
                self.bottom = iter.y()

        self.width = self.right - self.left + 1
        self.height = self.top - self.bottom + 1

    def BuildET(self):  # 建立边表

        count = len(self.p_polygon.p_point_array)  # 应等于多边形的顶点数
        self.edge_table = [[]] * (self.top - self.bottom + 1
                                  )  # 针对每个y值存储多个边（edge）的list

        for i in range(count):
            e = CEdge()

            p = self.p_polygon.p_point_array[i]
            q = self.p_polygon.p_point_array[(i + 1) % count]

            if p.y() == q.y():  # 水平边
                e.x = p.x()
                e.ymax = p.y()
                e.dx = 999999999
                self.edge_table[int(p.y() - self.bottom)].append(e)
                e.x = q.x()
                e.ymax = q.y()
                e.dx = 999999999
                self.edge_table[int(q.y() - self.bottom)].append(e)
            else:
                if q.y() < p.y():
                    p, q = q, p
                e.x = p.x()
                e.ymax = q.y()
                if q.y() == p.y():
                    e.dx = 0
                else:
                    e.dx = (q.x() - p.x()) / (q.y() - p.y())
                self.edge_table[int(p.y() - self.bottom)].append(e)

    def UpdateAET(self, aheight):  # 更新活性边表AET
        for iter in self.active_edge_table[::-1]:  # 删除不在当前扫描线之内的边
            if iter.ymax <= aheight:

                self.active_edge_table.remove(iter)

        for iter in self.active_edge_table:
            iter.x += iter.dx

        for iter in self.edge_table[aheight - self.bottom]:
            self.active_edge_table.append(iter)  # 插入新增边

        # for iter in self.active_edge_table:
        #     print(iter.x, iter.dx, iter.ymax)
        # print()

        self.active_edge_table = sorted(self.active_edge_table)  # 按照横坐标从小到大排序

    def CalcIntersects(self, aheight):  # 按照横坐标获取扫描线与多边形的交点
        intersects = []
        if not self.active_edge_table:  # 活性边表为空
            return
        step = 2
        iters = [
            self.active_edge_table[i:i + step]
            for i in range(0, len(self.active_edge_table), step)
        ]
        for iter in iters[1:len(iters) - 1]:
            if abs(iter[0].x - iter[1].x) > 1e-3:
                intersects.append(iter[0].x)
                intersects.append(iter[1].x)

        intersects.sort()
        self.intersects = intersects

    def FillPolygon(self):  # 填充多边形
        self.BuildET()
        self.mat_inside = {}  # 存储像素点是否在多边形内的字典

        for i in range(self.bottom, self.top + 1):
            self.UpdateAET(i)
            self.CalcIntersects(i)

            status = False  # 初始状态为外部
            intPts = []  # 存放内部线的两端

            for j in range(len(self.intersects)):
                if not intPts:
                    intPts.append(int(self.intersects[j]))  # 将x坐标加入列表
                elif int(self.intersects[j]) == intPts[-1]:
                    intPts.pop()  # 相邻两个重合点相抵消
                else:
                    intPts.append(int(self.intersects[j]))
            intPts.append(math.inf)
            # print(intPts)

            index = 0
            for j in range(self.left - 1, self.right + 1):  # 处理每一个像素点
                if j == intPts[index]:
                    status = not status
                    index += 1
                self.mat_inside[(j, i)] = status

    def GetRectArea(self):  # 获取多边形矩形面积
        return self.width * self.height

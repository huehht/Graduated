class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class LineSegment:

    def __init__(self, p1, p2):
        if p1.y < p2.y:
            self.p1 = p1
            self.p2 = p2
        else:
            self.p1 = p2
            self.p2 = p1


def scanline(points):
    ymin = min(points, key=lambda p: p.y).y
    ymax = max(points, key=lambda p: p.y).y

    eps = 1e-6

    edge_table = [[] for _ in range(ymax - ymin + 1)]

    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]

        if abs(p1.x - p2.x) < eps and abs(p1.y - p2.y) < eps:
            continue

        if p1.y == p2.y:
            continue

        if p1.y < p2.y:
            edge = LineSegment(p1, p2)
        else:
            edge = LineSegment(p2, p1)

        edge_table[edge.p1.y - ymin].append(edge)

    active_edges = []
    xintersections = []

    for y in range(ymin, ymax + 1):
        for edge in edge_table[y - ymin]:
            active_edges.append(edge)

        active_edges = [e for e in active_edges if e.p2.y > y]

        active_edges.sort(key=lambda e: e.p1.x)

        for i in range(0, len(active_edges), 2):
            if i + 1 >= len(active_edges):
                break

            x1 = active_edges[i].p1.x
            x2 = active_edges[i + 1].p1.x
            xintersections.append((x1, x2))

        for edge in active_edges:
            edge.p1.x += edge.p1.y / ymax
            edge.p2.x += edge.p2.y / ymax

    total_area = 0
    total_x = 0
    total_y = 0

    for x1, x2 in xintersections:
        total_area += ymax
        centroid_x = (x2**2 - x1**2) / (2 * (x2 - x1))
        centroid_y = ymax / 2
        total_x += centroid_x
        total_y += centroid_y

    total_x /= total_area
    total_y /= total_area

    return total_area, (total_x, total_y)

import sympy
import pygame


colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0)
}


def getPointsFromExpression(exp, ps):
    points = []
    x = sympy.Symbol("x")
    for num in ps:
        out = exp.subs(x, num)
        points.append([num, out])

    return points


class generateAxis(object):
    def __init__(self, limit, precision=100):
        self.limit = abs(limit)
        self.inc = -limit
        self.precision = precision

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.inc <= self.limit:
            ret, self.inc = self.inc, self.inc + (self.limit/self.precision)
            return ret

        raise StopIteration()


class Graph(object):
    def __init__(self, canvas, axis=[10, 10]):
        self.canvas = canvas
        self.points = []
        self.axis = [abs(x) for x in axis]
        self.font = pygame.font.SysFont(None, 14)

    def drawPoints(self):
        ps = [self.toPyGame(x) for x in self.points]
        pygame.draw.aalines(self.canvas, colors["black"], False, ps, 1)

    def setEq(self, eq):
        self.points = self.getPointsFromEquation(eq)

    def getPointsFromEquation(self, eq):
        ex = sympy.parse_expr(eq, evaluate=False)
        return self.getPointsFromExpression(ex)

    def getPointsFromExpression(self, ex):
        points = []
        sym = sympy.Symbol("x")

        for x in generateAxis(self.axis[0]):
            points.append([x, ex.subs(sym, x)])

        return points

    def getAxisRatios(self):
        return self.canvas.get_width()/(self.axis[0] * 2), self.canvas.get_height()/(self.axis[1] * 2)

    def toPyGame(self, point):
        x, y = point
        xr, yr = self.getAxisRatios()
        return [(x + self.axis[0]) * xr, (self.axis[1] - y) * yr]

    def drawAxis(self):
        h, w = self.canvas.get_height(), self.canvas.get_width()

        for x in range(21):
            bottom, top = [x/20 * w, h/2 + 5], [x/20 * w, h/2 - 5]
            pygame.draw.line(self.canvas, colors["black"], top, bottom, 1)
            text = self.font.render(str(int(-self.axis[0] + (x/10 * self.axis[0]))), True, colors["black"])
            rect = text.get_rect()
            rect.center = [bottom[0], bottom[1] + 10]

            self.canvas.blit(text, rect)

        for y in range(21):
            left, right = [w/2 - 5, y/20 * h], [w/2 + 5, y/20 * h]

            pygame.draw.line(self.canvas, colors["black"], left, right, 1)

            text = self.font.render(str(int(self.axis[1] - (y/10 * self.axis[1]))), True, colors["black"])
            rect = text.get_rect()
            rect.center = [right[0] + 10, right[1]]

            self.canvas.blit(text, rect)

        pygame.draw.line(self.canvas, colors["red"], [0, h / 2], [w, h / 2], 1)
        pygame.draw.line(self.canvas, colors["red"], [w / 2, 0], [w / 2, h], 1)


def main():
    pygame.init()

    canvas = pygame.display.set_mode((500, 500))

    pygame.display.set_caption("Graphing Util")

    graph = Graph(canvas)
    graph.setEq("-(x**2) + 7")

    while 1:
        # white
        canvas.fill(colors["white"])

        graph.drawAxis()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        graph.drawPoints()

        pygame.display.update()


main()

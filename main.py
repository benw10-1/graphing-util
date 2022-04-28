import sympy
import pygame
import math


colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "activated": pygame.Color("lightskyblue3"),
    "deactivated": pygame.Color("chartreuse4"),
    "green": (0, 255, 0)
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
        self.points = None
        self.axis = [abs(x) for x in axis]
        self.font = pygame.font.SysFont(None, 14)
        self.eq = None
        self.orb = None

    def drawPoints(self):
        if not self.points:
            errortext = pygame.font.SysFont(None, 32).render("?", True, colors["red"])
            rect = errortext.get_rect()
            rect.center = self.toPyGame([0, 0])

            self.canvas.blit(errortext, rect)

            return

        pygame.draw.aalines(self.canvas, colors["black"], False, self.points, 1)

        if self.orb:
            # set bounds for our orb so it cant go off screen
            # self.orb[0] = max(0, min(self.canvas.get_width(), self.orb[0]))
            # self.orb[1] = max(0, min(self.canvas.get_height(), self.orb[1]))

            sym1 = sympy.Symbol("x")

            result = [self.orb[0], self.eq.subs(sym1, self.orb[0])]

            center = self.toPyGame(result)
            center[0] = max(0, min(self.canvas.get_width(), center[0]))
            center[1] = max(0, min(self.canvas.get_height(), center[1]))
            center = [round(center[0]), round(center[1])]

            pygame.draw.circle(self.canvas, colors["green"], center, 10)

            if int(result[0]) != result[0]:
                xformat = f"{result[0]:10.2f}"
            else:
                xformat = str(int(result[0]))
            if int(result[1]) != result[1]:
                yformat = f"{result[1]:10.2f}"
            else:
                yformat = str(int(result[1]))

            text = pygame.font.SysFont(None, 24).render(xformat + ", " + yformat, True, colors["black"])
            rect = text.get_rect()
            rect.center = [3 * self.canvas.get_width()/4, 50]

            self.canvas.blit(text, rect)

    def setEq(self, eq):
        self.points = []
        for x in self.getPointsFromEquation(eq):
            try:
                for item in x:
                    int(item)
                self.points.append(self.toPyGame(x))
            except Exception as e:
                self.points = False
                break

    def getPointsFromEquation(self, eq):
        ex = sympy.sympify(eq, evaluate=False)
        self.eq = ex
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

    def fromPyGame(self, point):
        x, y = point
        xr, yr = self.getAxisRatios()

        return [x/xr - self.axis[0], -y/yr + self.axis[0]]

    def drawAxis(self):
        h, w = self.canvas.get_height(), self.canvas.get_width()

        for x in range(21):
            bottom, top = [x/20 * w, h/2 + 5], [x/20 * w, h/2 - 5]

            pygame.draw.line(self.canvas, colors["black"], top, bottom, 1)

            floating = -self.axis[0] + (x/10 * self.axis[0])
            text = self.font.render(f"{floating:10.1f}", True, colors["black"])
            rect = text.get_rect()
            rect.center = [bottom[0] - 10, bottom[1] + 10]

            self.canvas.blit(text, rect)

        for y in range(21):
            left, right = [w/2 - 5, y/20 * h], [w/2 + 5, y/20 * h]

            pygame.draw.line(self.canvas, colors["black"], left, right, 1)

            floating = self.axis[1] - (y/10 * self.axis[1])

            text = self.font.render(f"{floating:10.1f}", True, colors["black"])
            rect = text.get_rect()
            rect.center = [right[0] + 5, right[1]]

            self.canvas.blit(text, rect)

        pygame.draw.line(self.canvas, colors["red"], [0, h / 2], [w, h / 2], 1)
        pygame.draw.line(self.canvas, colors["red"], [w / 2, 0], [w / 2, h], 1)

    def setOrb(self, pos):
        self.orb = pos

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                self.axis[0] += 1
                self.axis[1] += 1
            if event.button == 4:
                self.axis[0] = max(1, self.axis[0] - 1)
                self.axis[1] = max(1, self.axis[1] - 1)
            if self.eq:
                self.setEq(self.eq)
        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            self.setOrb(self.fromPyGame([x, y]))


class InputBox(object):
    def __init__(self, surface, pos=[100, 50]):
        self.pos = pos
        self.canvas = surface
        self.active = False
        self.text = ""
        self.rect = pygame.Rect(0, 0, 140, 32)
        self.rect.center = pos
        self.font = pygame.font.SysFont(None, 24)

    def drawBox(self):
        if self.active:
            color = colors["activated"]
        else:
            color = colors["deactivated"]

        pygame.draw.rect(self.canvas, color, self.rect)
        text = self.font.render(self.text, True, colors["white"])
        self.canvas.blit(text, (self.rect.x + 5, self.rect.y + 8))

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN:
            if not self.active:
                return
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == 13:
                if self.text:
                    self.active = False
                    return True
                self.active = False
                return False
            else:
                self.text += event.unicode


def main():
    pygame.init()

    canvas = pygame.display.set_mode((500, 500))

    pygame.display.set_caption("Graphing Util")

    initial = "-(x^2) + 1"

    graph = Graph(canvas)
    graph.setEq(initial)

    inputBox = InputBox(canvas)
    inputBox.text = initial

    while 1:
        # white
        canvas.fill(colors["white"])

        graph.drawAxis()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            if inputBox.handleEvent(event):
                graph.setEq(inputBox.text)
            graph.handleEvent(event)

        graph.drawPoints()
        inputBox.drawBox()

        pygame.display.update()


main()

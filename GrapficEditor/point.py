from config import WIDTH, HEIGHT, CELL_HEIGHT
class Point:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def coordinates(self):
        return f"({(self.x - WIDTH // 2) } ; {(HEIGHT // 2 - self.y) })"
		


    def get_d(pos, line):
        A = line.y2 - line.y1
        B = line.x1 - line.x2
        C = line.x2 * line.y1 - line.x1 * line.y2
        b = abs(A*pos[0]+B*pos[1]+C)
        d = (A**2+B**2)**0.5
        if d!= 0:
            return b/d
        else:
            return 0

from config import WIDTH, HEIGHT, CELL_HEIGHT
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def line_length(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def equation(x1,y1,x2,y2,mod):
        A = y2 - y1
        B = x1 - x2
        C = (x2  ) * (y1) - (x1) * (y1)
        
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        
        return f"{round(A,1)}{mod[0]} + {(round(B,1))}{mod[1]} + {round(C,1)} = 0"

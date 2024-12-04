from config import WIDTH, HEIGHT, CELL_HEIGHT
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def line_length(x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def equation(self):
        A = self.y2 - self.y1
        B = self.x1 - self.x2
        C = (self.x2  ) * (self.y1) - (self.x1  ) * (self.y1)
        
        A = self.y2 - self.y1
        B = self.x1 - self.x2
        C = self.x2 * self.y1 - self.x1 * self.y2
        
        return f"{(A- 2*(WIDTH ))}x + {(2*(HEIGHT )-B)}y + {C} = 0"

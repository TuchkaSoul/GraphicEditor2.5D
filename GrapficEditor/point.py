from config import WIDTH, HEIGHT, CELL_HEIGHT
class Point:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def coordinates(self):
        return f"({(self.x - WIDTH // 2) } ; {(HEIGHT // 2 - self.y) })"
		
    def get_distance(point0, point1):
        return ((point0[0]-point1[0])**2+(point0[1]-point1[1]))**0.5
    def get_distance3d(point0, point1):
        return ((point0[0]-point1[0])**2+(point0[1]-point1[1])**2+(point0[2]-point1[2])**2)**0.5

    def get_distance_line_2d(pos, point0, point1):
        A = point1[1] - point0[1]
        B = point0[0] - point1[0]
        C = point1[0] * point0[1] - point0[0] * point1[1]        
        b = abs(A*pos[0]+B*pos[1]+C)
        d = (A**2+B**2)**0.5
        if d!= 0:
            return b/d
        else:
            return 0
    
    def get_distance_line_2d(pos, point0, point1):
        A = point1[1] - point0[1]
        B = point0[0] - point1[0]
        C = point1[0] * point0[1] - point0[0] * point1[1]        
        b = abs(A*pos[0]+B*pos[1]+C)
        d = (A**2+B**2)**0.5
        if d!= 0:
            return b/d
        else:
            return 0
        
    
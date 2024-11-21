import pygame
import math

# Константы
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

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
        C = self.x2 * self.y1 - self.x1 * self.y2
        return f"{A}x + {B}y + {C} = 0"

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def coordinates(self):
        return f"({self.x}, {self.y})"
    
    def get_d(pos,line):
        A = line.y2 - line.y1
        B = line.x1 - line.x2
        C = line.x2 * line.y1 - line.x1 * line.y2
        b= abs(A*pos[0]+B*pos[1]+C)
        d=(A**2+B**2)**0.5
        if d!=0:
            return b/d
        else:
            return 0 

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Приложения для работы с сиплексами")
        self.lines = []
        self.points = []
        self.status=""
        self.mode = "create"
        self.selected_line = None
        self.selected_point = None
        self.font = pygame.font.Font(None, 24)
        self.curspos=""
        
        self.edit_line = None
        self.edit_point = None
        

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mode == "create":
                        self.create_line(event.pos)
                    elif self.mode == "edit1":
                        self.edit1_line(event.pos)
                    elif self.mode == "edit2":
                        self.edit2_line(event.pos)    
                    elif self.mode == "delete":
                        self.delete_line(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.update_status(event.pos)
                elif event.type == pygame.KEYUP:
                    if event.key==pygame.K_q:
                        self.toggle_mode()

            self.draw()
            pygame.display.flip()
            self.clock.tick(144)


    def create_line(self, pos):
        if len(self.points) < 2 :            
            self.points.append(Point(pos[0], pos[1]))
            
        if len(self.points) == 2:
            if (self.points[0].x!=pos[0] and self.points[0].y!=pos[1]):
                self.lines.append(Line(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
            self.points = []

    def edit1_line(self, pos):
        line = self.selected_line
        if line==None:
            return
        if Line.line_length(line.x1,line.y1,pos[0],pos[1])<Line.line_length(line.x2,line.y2,pos[0],pos[1]):
            self.points.append(Point(line.x1,line.y1))
            self.lines.remove(line)
            self.mode="edit2"
            return
        else:
            self.points.append(Point(line.x2,line.y2))
            self.lines.remove(line)
            self.mode="edit2"
            return
                
                    
    def edit2_line(self, pos):
        if len(self.points) < 2:
            self.points.append(Point(pos[0], pos[1]))
        if len(self.points) == 2:
            self.lines.append(Line(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
            self.points = []
          
        self.mode="edit1"       
                    
                    

    def delete_line(self, pos):
        for line in self.lines:
            if Point.get_d(pos, line)<5:
                self.lines.remove(line)
                break

    def update_status(self, pos):
        self.selected_line=None
        self.status = ""
        for line in self.lines:
            if Point.get_d(pos, line)<5:
                if self.selected_line==None:#line.x1 < pos[0] < line.x2 and line.y1 < pos[1] < line.y2:
                    self.selected_line = line                    
                elif Point.get_d(pos, line)<Point.get_d(pos, self.selected_line):
                    self.selected_line = line                
                self.status = self.selected_line.equation()+"   "
            elif self.selected_line!=None: 
                self.selected_line=self.selected_line
                self.status = self.selected_line.equation()+"   "
            
        else:
            for point in self.points:
                if math.hypot(point.x - pos[0], point.y - pos[1]) < 5:
                    self.selected_point = point
                    self.status = point.coordinates()+"   "
                    break
                else:  
                    self.selected_point = None
                    self.status = ""
                
        
        if len(self.points)==1:
            self.edit_point=Point(pos[0], pos[1])
        elif self.edit_point!=None:
            self.edit_point=None
                  
        self.curspos =f"({pos[0]};{pos[1]})"
        

    def draw(self):
        self.screen.fill(WHITE)
        for line in self.lines:
            pygame.draw.line(self.screen, BLACK, (line.x1, line.y1), (line.x2, line.y2), 2)
        for point in self.points:
            pygame.draw.circle(self.screen, RED, (point.x, point.y), 5)
        if self.edit_point!=None and len(self.points)==1:
            pygame.draw.line(self.screen, RED, (self.points[0].x, self.points[0].y), (self.edit_point.x, self.edit_point.y), 1)
        if self.selected_line:
            pygame.draw.line(self.screen, RED, (self.selected_line.x1, self.selected_line.y1), (self.selected_line.x2, self.selected_line.y2), 2)
        elif self.selected_point:
            pygame.draw.circle(self.screen, RED, (self.selected_point.x, self.selected_point.y), 5)
        self.screen.blit(self.font.render(self.status, True, BLACK), (10, 10))
        self.screen.blit(self.font.render(self.curspos, True, BLACK), (0, HEIGHT-20))
        if self.mode == "create":
            self.screen.blit(self.font.render("Режим: Создать", True, BLACK), (10, 40))
        elif self.mode == "edit1":
            self.screen.blit(self.font.render("Режим: Редактировать", True, BLACK), (10, 40))
        elif self.mode == "edit2":
            self.screen.blit(self.font.render("Режим: Редактирование точки", True, BLACK), (10, 40))    
        elif self.mode == "delete":
            self.screen.blit(self.font.render("Режим: Удалить", True, BLACK), (10, 40))

    def toggle_mode(self):
        if self.mode == "create":
            self.mode = "edit1"
        elif self.mode == "edit1":
            self.mode = "delete"
        elif self.mode == "delete":
            self.mode = "create"

    def show_coordinates(self):
        self.screen.fill(WHITE)
        for i in range(10):
            pygame.draw.line(self.screen, RED, (0, i * 50), (WIDTH, i * 50), 1)
            pygame.draw.line(self.screen, BLACK, (i * 50, 0), (i * 50, HEIGHT), 1)
        pygame.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
import numpy as np
import pygame
import math
from config import WIDTH, HEIGHT, WHITE, BLACK, RED, CREY, CELL_HEIGHT, FPS
from point import Point
from line import Line
from grafic_object import ObjectInfo

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Приложения для работы с сиплексами cg2.5")
        self.scale=20
        self.coord_modes={"xy":[0,1],
                             "xz":[0,2],
                             "zy":[2,1]
                             }
                            
        self.coord_mode=[0,1]
        self.projected_mode={
            "xyz":np.array([
            [ 1,  0,  0,  0],
            [ 0,  1,  0,  0], 
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  1]]),
            
            "izo":
            np.array([
            [math.sqrt(1/2),-math.sqrt(1/6),0,0],
            [0,math.sqrt(2/3),0,0],
            [-math.sqrt(1/2),-math.sqrt(1/6),0,0],
            [0,0,0,1],
            ]),
            "free":
            np.array([
            [ 1,  0,  0,  0],
            [ 0,  0,  0,  0], 
            [ math.sqrt(2)/2,  math.sqrt(2)/2,  0,  0],
            [ 0,  0,  0,  1],
            ])}
        self.zero_coords=[WIDTH/2/(CELL_HEIGHT/self.scale),HEIGHT/(CELL_HEIGHT/self.scale)/2,0,1]
        # self.coord_line=np.array([self.zero_coords,[],])
        self.curent_ObjectInfo=ObjectInfo()
        self.show_coords =True
        self.point_sys_coord =None
        self.line_sys_coord=[]
        self.canvas_coords =np.array([[0,0,0,1]])        
        self.show_coords =True
        
        self.matrix_sys_coord = np.array([
            [1, 0, 0, 0],
            [0, -1, 0, 0], 
            [0, 0, 1, 0],
            [self.zero_coords[0], self.zero_coords[1], self.zero_coords[1], 1/(CELL_HEIGHT/self.scale)]])
        self.is_show_main=True
        self.lines = []
        self.points = np.array([[0,0,5,1]])
        self.canvas_points = np.array([[0,0,0,1]])
        
        self.splain_points = None
        self.splain_lines = []
        self.is_draw_splain=False
        
        
        
        self.selected_line = None
        self.selected_lines = None
        self.selected_point = None
        
        self.edit_line = None
        self.edit_point = None
        self.selection_rect = None
        
        self.status = ""
        self.curspos = ""
        self.mode = "create"
        self.font = pygame.font.Font(None, 24)                       
        
        self.dragging = False
        self.free_coord_xyz =0
        self.drag_offset = (0, 0 , 0)
        
        
        self.points_surface = pygame.Surface((WIDTH, HEIGHT))
        self.points_surface.set_colorkey(WHITE)
        
    def save_lines_to_file(self,lst, filename):
        """
        Записывает список кортежей в файл в формате TXT.
        
        Parameters:
        lst (list): список кортежей для записи
        filename (str): имя файла для записи
        """
        with open(filename, 'w') as f:
            for item in lst:
                f.write(str(item) + '\n')    
        
    def save_matrix_to_file(self, matrix, filename, format='csv'):
        """
        Записывает numpy матрицу в файл в формате CSV или TXT.
        
        Parameters:
        matrix (numpy.array): матрица для записи
        filename (str): имя файла для записи
        format (str): формат файла (csv или txt, по умолчанию csv)
        """
        if format.lower() == 'csv':
            np.savetxt(filename, matrix, delimiter=',', fmt='%.3f')
        elif format.lower() == 'txt':
            np.savetxt(filename, matrix, delimiter=' ', fmt='%s')
        else:
            raise ValueError("Неправильный формат файла. Доступные форматы: csv, txt")
     
    def mode_izometric(self):
        matrix_izometric=self.projected_mode["izo"]
        self.coord_mode=self.coord_modes["xy"]       
        
        self.canvas_points=np.matmul(np.matmul(self.points,matrix_izometric),self.matrix_sys_coord)
        self.canvas_points=self.canvas_points/self.canvas_points[:,-1][:,None]
        
        self.canvas_coords=np.matmul(np.matmul(self.point_sys_coord,matrix_izometric),self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        if self.is_draw_splain:
           self.splain_points=np.matmul(np.matmul(np.matmul(self.splain_points,np.linalg.inv(self.matrix_sys_coord)),matrix_izometric),self.matrix_sys_coord)
           self.splain_points=self.splain_points/self.splain_points[:,-1][:,None]
           
        self.draw_sys_coord()
        
        
        
        
    def update_canvas_coord(self):        
        self.canvas_points= np.matmul(self.points,self.matrix_sys_coord)
        self.canvas_points=self.canvas_points/self.canvas_points[:,-1][:,None]
        
        self.canvas_coords=np.matmul(self.point_sys_coord,self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        self.draw_sys_coord()
        
        

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit(0)
                                
                if event.type==pygame.MOUSEMOTION:
                    self.print_cursor(event)
                    if event.buttons[0] and self.mode!="create":
                        if self.selection_rect is None and not self.dragging:
                            self.selection_rect = [event.pos, event.pos]
                        else: 
                            
                            if self.dragging:
                                pos = np.matmul(np.array([[event.pos[0],event.pos[1],0,1]]),np.linalg.inv(self.matrix_sys_coord))
                                
                                for point in self.selected_lines:
                                    self.canvas_points[point[1],self.coord_mode[0]] += (pos[0,0] - self.drag_offset[0,0])
                                    self.canvas_points[point[1],self.coord_mode[1]] -= (pos[0,1] - self.drag_offset[0,1])
                                    self.points[point[1],self.coord_mode[0]] += (pos[0,0] - self.drag_offset[0,0])/(CELL_HEIGHT/self.scale)
                                    self.points[point[1],self.coord_mode[1]] += (pos[0,1] - self.drag_offset[0,1])/(CELL_HEIGHT/self.scale)
                                    
                                self.drag_offset = pos.copy()
                                self.draw_sys_coord()
                            else:
                                self.selection_rect[1] = event.pos
                            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mode == "edit1" and self.selected_lines:
                        if event.button == 1:
                            self.dragging = True
                            self.drag_offset = np.matmul(np.array([[event.pos[0],event.pos[1],0,1]]),np.linalg.inv(self.matrix_sys_coord))
                if event.type==pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.mode=="create":
                        self.create_poligon(event.pos)
                    if self.mode=="edit1" and self.selection_rect:
                        self.select_lines_in_rect(self.selection_rect)
                        self.selection_rect = None
                    elif self.dragging:
                        self.dragging=False
                        self.selected_lines=None
                        self.selection_rect = None
                if event.type==pygame.KEYUP :
                    if event.key == pygame.K_ESCAPE and self.mode=="create" and self.edit_line is not None:
                        self.lines.append((self.points.shape[0]-1,self.edit_point))
                        self.edit_line=None
                        self.edit_point=None
                    if  event.key == pygame.K_0 and self.mode=="create":
                        self.mode_izometric()                     
                            
                    if event.key == pygame.K_9 and self.mode=="create":
                        self.update_canvas_coord()   
                    
                    if event.key == pygame.K_1 and self.mode=="create":
                        self.is_draw_splain= not self.is_draw_splain
                        self.splain()
                    if event.key == pygame.K_x or event.key == pygame.K_y or event.key == pygame.K_z:   
                        self.matrix_sys_coord[3]=[0,0,0,1/(CELL_HEIGHT/self.scale)]  
                        if event.key == pygame.K_x:
                            self.coord_mode=self.coord_modes["zy"]
                        if event.key == pygame.K_y:
                            self.coord_mode=self.coord_modes["xz"]
                        if event.key == pygame.K_z:
                            self.coord_mode=self.coord_modes["xy"]
                        self.matrix_sys_coord[3]=[0,0,0,1/(CELL_HEIGHT/self.scale)]   
                        self.matrix_sys_coord[3,self.coord_mode[0]]=self.zero_coords[0]
                        self.matrix_sys_coord[3,self.coord_mode[1]]=self.zero_coords[1]
                        self.draw_sys_coord()
                    if event.key == pygame.K_q:
                        self.toggle_mode()
                    
                    if event.key == pygame.K_o: #отображение поставленных точек
                        if self.is_show_main:
                            self.is_show_main=False
                        else:
                            self.is_show_main=True    
                if event.type == pygame.MOUSEWHEEL:
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        if event.y > 0:
                            self.scale += 0.1*self.scale
                        elif self.scale -1> 0:
                            self.scale -= 0.1*self.scale
                        self.zero_coords=[WIDTH/2/(CELL_HEIGHT/self.scale),HEIGHT/(CELL_HEIGHT/self.scale)/2,0,1]
                        self.matrix_sys_coord[3] = np.array([self.zero_coords[0], self.zero_coords[1], self.zero_coords[0], 1/(CELL_HEIGHT/self.scale)])
                        self.update_canvas_coord()
                        self.draw_sys_coord()                        
                    if event.y > 0:
                        self.free_coord_xyz += 0.5
                    else:
                        self.free_coord_xyz -= 0.5                          
                    
                        
                if event.type==pygame.KEYDOWN :
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LCTRL]and keys[pygame.K_LSHIFT] and keys[pygame.K_DELETE]:
                        print("del")
                        self.is_show_main=True
                        self.lines = []
                        self.points = np.array([[0,0,0,1]])
                        self.canvas_points = np.array([[0,0,0,1]])
                        self.edit_line=None
                        self.splain_points = None
                        self.splain_lines = []
                        self.is_draw_splain=False
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_s]:
                        print("Save")
                        self.save_matrix_to_file(self.points,'Истинные точки.csv')
                        self.save_matrix_to_file(self.canvas_points,'Экранные точки.txt')        
                        self.save_lines_to_file(self.lines,'Линии.txt')    

            #вся информация
            #self.update_status(pos)           
            
                
            if pygame.mouse.get_focused():                     
                self.draw()
                pygame.display.flip()
                self.clock.tick(FPS)

    def print_cursor(self, event):
        pos=self.free_coord_xyz*(CELL_HEIGHT/self.scale)
        pos=np.array([[pos,pos,pos,1]])
        pos[0,self.coord_mode[0]]=event.pos[0]
        pos[0,self.coord_mode[1]]=event.pos[1]
        matrix_sys_coord = np.array([
            [1, 0, 0, 0],
            [0, -1, 0, 0], 
            [0, 0, 1, 0],
            [0, 0, 0, 1/(CELL_HEIGHT/self.scale)]])
        
        pos=np.matmul(pos,np.linalg.inv(matrix_sys_coord))
        pos=pos/pos[:,-1][:,None]
        self.curspos = f"({round(pos[0,0],2)} ; {round(pos[0,1],2)} ; {round(pos[0,2],2)})"
                
    def create1_point(self, pos):
        #преврали в матричную форму
        free=self.free_coord_xyz*(CELL_HEIGHT/self.scale)
        new_point =np.array([[free,free,free,1]])
        new_point[0,self.coord_mode[0]]=pos[0]
        new_point[0,self.coord_mode[1]]=pos[1]
        
        #преобразовали в классическую систему координат
        a= np.matmul(new_point,np.linalg.inv(self.matrix_sys_coord))
        a=a/a[:,-1][:,None]        
        
        if a[0].tolist() in self.points.tolist():            
            print("такая точка уже есть")
            
        else:
            self.points=np.append(self.points,a, axis=0)
            self.canvas_points=np.append(self.canvas_points,new_point, axis=0)     
        
        
    def create_line(self, pos):
        if self.edit_line ==None:
            self.create1_point(pos)     
            self.edit_line=[self.points.shape[0]-1,-1]            
        elif self.edit_line[1] == -1:
            self.create1_point(pos)
            if (self.edit_line[0]!=self.points.shape[0]-1):
                self.edit_line[1]=self.points.shape[0]-1
                self.lines.append(self.edit_line)
                self.edit_line=None            
        
           
        
        
        
    def create_poligon(self, pos):
        if self.edit_line ==None:
            self.create1_point(pos)     
            self.edit_line=[self.points.shape[0]-1,-1]
            self.edit_point=self.points.shape[0]-1
        elif self.edit_line[1] == -1:
            self.create1_point(pos)
            if (self.edit_line[0]!=self.points.shape[0]-1):
                self.edit_line=(self.edit_line[0],self.points.shape[0]-1)
                # self.edit_line[1]=self.points.shape[0]-1
                self.lines.append(self.edit_line)
                self.edit_line=[self.edit_line[1],-1 ]
            else:
                self.edit_line=[self.points.shape[0]-1,self.edit_point]
                self.lines.append(self.edit_line)
                
                self.edit_line=None
                self.edit_point=None
        # print(self.lines)
        

    def edit1_line(self, pos):
        line = self.selected_line
        if line == None:
            return
        if Line.line_length(line.x1, line.y1, pos[0], pos[1]) > Line.line_length(line.x2, line.y2, pos[0], pos[1]):
            self.points.append(Point(line.x1,line.y1))
            self.lines.remove(line)
            self.mode="edit2"
            return
        else:
            self.points.append(Point(line.x2,line.y2))
            self.lines.remove(line)
            self.mode="edit2"
            return
            #can help us better understand the implications of our actions and the potential consequences of our decisions.

    def edit2_line(self, pos):
        if len(self.points) < 2:
            self.points.append(Point(pos[0], pos[1]))
        if len(self.points) == 2:
            self.lines.append(Line(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
            self.points = []

        self.mode = "edit1"

    

    def select_lines_in_rect(self, rect):
        selected_lines = []
        x, y, w, h = rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        i=0
        for point in self.canvas_points:
            if x<=point[self.coord_mode[0]]<=w  and y<=point[self.coord_mode[1]]<=h:
                selected_lines.append([self.points[i],i])
            i+=1
        if len(selected_lines)==1:
            self.edit_point=None
            self.edit_point=selected_lines[0][1]
            self.edit_line=(self.edit_point,-1)
        self.selected_lines = selected_lines
       
        print(selected_lines)    

    def update_status(self, pos):
        self.selected_line = None
        self.selected_point= None
        self.status = ""
        for line in self.lines:
            if Point.get_d(pos, line) < 5 and (((line.x1<=pos[0]<=line.x2) or (line.x1>=pos[0]>=line.x2)) and ((line.y1<=pos[1]<=line.y2)or (line.y1>=pos[1]>=line.y2))):
                self.selected_line = line
                self.status = self.selected_line.equation() + "   "
            elif self.selected_line!= None:
                self.selected_line = self.selected_line
                self.status = self.selected_line.equation() + "   "

        else:
            if self.points!=None:
                for point in self.points:
                    if math.hypot(point[0] - pos[0], point[1] - pos[1]) < 5:
                        self.selected_point = point                    
                        break
            if self.show_coords:
                if (pos[0]%(CELL_HEIGHT/self.scale)<=(CELL_HEIGHT/self.scale)/20 or (CELL_HEIGHT/self.scale)-pos[0]%(CELL_HEIGHT/self.scale)<=(CELL_HEIGHT/self.scale)/20) and (pos[0]%(CELL_HEIGHT/self.scale)<=(CELL_HEIGHT/self.scale)/20 or (CELL_HEIGHT/self.scale)-pos[0]%(CELL_HEIGHT/self.scale)<=(CELL_HEIGHT/self.scale)/20): 
                    self.selected_point = Point((round((pos[0])))*(CELL_HEIGHT/self.scale),(round(pos[1]))*(CELL_HEIGHT/self.scale))
        
        if self.selected_point!=None:
            self.status += self.selected_point.coordinates() + "   "
                    

        if self.points.shape[0] > 0:
            for point in self.points:
                pygame.draw.circle(self.screen, BLACK, (point[0], point[1]), 5)
                
            self.edit_point = Point(pos[0], pos[1])
        elif self.edit_point!= None:
            self.edit_point = self.edit_point

        self.curspos = f"({(pos[0] - WIDTH // 2) } ; {(HEIGHT // 2 - pos[1]) })  "+f"({(pos[0]) } ; {(pos[1]) })"

    def get_coord_point(self):
        line_sys_coord=[(0,1),(2,3),(4,5)]
        point_sys_coord=np.array([
                                    [-1000,0,0,1],
                                    [1000,0,0,1],
                                    [0,-1000,0,1],
                                    [0,1000,0,1],
                                    [0,0,-1000,1],
                                    [0,0,1000,1]])
        for x in range(-50,51,5):
            for y in range(-50,51,5):
                point_sys_coord=np.append(point_sys_coord,np.asarray([[x,y,-50,1],[x,y,50,1]]),axis=0)
                line_sys_coord.append((point_sys_coord.shape[0]-2,point_sys_coord.shape[0]-1))
        for x in range(-50,51,5):
            for z in range(-50,51,5):
                point_sys_coord=np.append(point_sys_coord,np.asarray([[x,-50,z,1],[x,50,z,1]]),axis=0)
                line_sys_coord.append((point_sys_coord.shape[0]-2,point_sys_coord.shape[0]-1))
        for y in range(-50,51,5):
            for z in range(-50,51,5):
                point_sys_coord=np.append(point_sys_coord,np.asarray([[-50,y,z,1],[50,y,z,1]]),axis=0)
                line_sys_coord.append((point_sys_coord.shape[0]-2,point_sys_coord.shape[0]-1))
        self.point_sys_coord=point_sys_coord
        self.line_sys_coord=line_sys_coord
    def draw_sys_coord(self):
        self.points_surface.fill(WHITE)  # Clear the surface
        if self.point_sys_coord is None:
            self.get_coord_point()
            # print(self.point_sys_coord)
            self.canvas_coords=np.matmul(self.point_sys_coord,self.matrix_sys_coord)
            self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
            
        i =self.coord_mode[0]
        j=self.coord_mode[1]
        print(F"i={i}\tj={j}")
        if self.show_coords:
                        
            pygame.draw.line(self.points_surface, (255,0,0), (self.canvas_coords[0,i], self.canvas_coords[0,j]), (self.canvas_coords[1,i], self.canvas_coords[1,j]),4)
            pygame.draw.line(self.points_surface, (0,0,255), (self.canvas_coords[2,i], self.canvas_coords[2,j]), (self.canvas_coords[3,i], self.canvas_coords[3,j]),4)
            pygame.draw.line(self.points_surface, (0,255,0), (self.canvas_coords[4,i], self.canvas_coords[4,j]), (self.canvas_coords[5,i], self.canvas_coords[5,j]),5)
                                    
            for line in self.line_sys_coord:            
                pygame.draw.line(self.points_surface, BLACK, (self.canvas_coords[line[0],i], self.canvas_coords[line[0],j]), (self.canvas_coords[line[1],i], self.canvas_coords[line[1],j]))
            for point in self.canvas_coords:
                pygame.draw.circle(self.points_surface, CREY, (point[i], point[j]), 3)

         
    def splain(self):        
        self.point_splain=None
        self.splain_points=None
        self.splain_lines.clear()
        if not self.is_draw_splain:
            return
        c=np.delete(self.points,0,axis=0)
        a=np.array([
                  [-1/6, 1/2, -1/2,1/6],
                  [ 1/2, -1,   1/2, 0],
                  [-1/2,  0,   1/2, 0],
                  [ 1/6,  4/6, 1/6, 0]])
        self.edit_line=[0,-1] 
        c=np.append(c,c[:-1],axis=0)
        for i in range(3,c.shape[0],1):            
            b=c[i-3:i+1,0:3]   
            AB=np.matmul(a,b)
            for t in range(0,25,1):
                t=t/25                
                point_splain=np.matmul(np.array([[math.pow(t,3),math.pow(t,2),math.pow(t,1),1]]),AB)                
                point_splain=np.append(point_splain,[[1]],axis=1)
                if self.splain_points is not None:
                    if point_splain.tolist() not in self.splain_points.tolist():
                        self.splain_points=np.append(self.splain_points,point_splain,axis=0)
                else:
                    self.splain_points=point_splain.copy()
                if (self.edit_line[0]!=self.splain_points.shape[0]-1):
                    self.edit_line[1]=self.splain_points.shape[0]-1                    
                    self.splain_lines.append(self.edit_line.copy())
                    self.edit_line[0]=self.edit_line[1]
                    
                    
        self.edit_line=None
        
        self.splain_points= np.matmul(self.splain_points,self.matrix_sys_coord)
        self.splain_points=self.splain_points/self.splain_points[:,-1][:,None]
        print(f"В сплаине сейчас {self.splain_points.shape[0]} точек")
          
    def draw(self):
        
        if self.point_sys_coord is None:
            self.draw_sys_coord()           
            
        
        self.screen.fill(WHITE)
        self.screen.blit(self.points_surface, (0, 0)) 
        
            
        
        
        
        if self.selection_rect:
            pygame.draw.rect(self.screen, (0, 255, 0, 128), pygame.Rect(self.selection_rect[0][0], self.selection_rect[0][1], self.selection_rect[1][0] - self.selection_rect[0][0], self.selection_rect[1][1] - self.selection_rect[0][1]), 2)
            
        if self.selected_lines:
            for line in self.selected_lines:
                pygame.draw.circle(self.screen, (0, 255, 0), (self.canvas_points[line[1],self.coord_mode[0]], self.canvas_points[line[1],self.coord_mode[1]]), 5)
        if self.is_show_main:
            for line in self.lines:            
                pygame.draw.line(self.screen, BLACK, (self.canvas_points[line[0],self.coord_mode[0]], self.canvas_points[line[0],self.coord_mode[1]]), (self.canvas_points[line[1],self.coord_mode[0]], self.canvas_points[line[1],self.coord_mode[1]]),3)
            for point in self.canvas_points:
                pygame.draw.circle(self.screen, RED, (point[self.coord_mode[0]], point[self.coord_mode[1]]), 3)
            
        if self.is_draw_splain:
            for line in self.splain_lines:            
                pygame.draw.line(self.screen, CREY, (self.splain_points[line[0],self.coord_mode[0]], self.splain_points[line[0],self.coord_mode[1]]), (self.splain_points[line[1],self.coord_mode[0]], self.splain_points[line[1],self.coord_mode[1]]),2 )
            # for point in self.splain_points:
            #     pygame.draw.circle(self.screen, BLACK, (point[self.coord_mode[0]], point[self.coord_mode[1]]), 1)
            
        if self.edit_line!=None:
            pygame.draw.line(self.screen, BLACK, (self.canvas_points[self.edit_line[0],self.coord_mode[0]], self.canvas_points[self.edit_line[0],self.coord_mode[1]]), (pygame.mouse.get_pos()),3)
        
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
            
    def delete_line1(self):
        if self.selected_lines:            
            for line in self.selected_lines:
                self.lines.remove(line)                
            self.selected_lines=None
            return
        if self.selected_line:
            self.lines.remove(self.selected_line)
            
    def delete_line(self, pos):        
        for line in self.lines:
            if Point.get_d(pos, line) < 3:
                self.lines.remove(line)
                break
            
            
if __name__ == "__main__":
    app = App()
    app.run()

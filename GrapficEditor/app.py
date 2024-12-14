import numpy as np
import pygame
import math
from config import WIDTH, HEIGHT, WHITE, BLACK, RED, CREY, CELL_HEIGHT, FPS
from point import Point
from line import Line
from grafic_object import ObjectInfo
import tkinter as tk
from point import Point



class App:
    def __init__(self):
        pygame.init()
        self.edit1_matrix=None
        self.root = None
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Приложения для работы с сиплексами cg2.5")
        self.scale=20
        self.coord_modes={"xy":[0,1],
                             "xz":[0,2],
                             "zy":[2,1]
                             }
        self.R_G_Active=False
        self.print_info=True                    
        self.coord_mode=[0,1]
        
        self.projected_mode={
            "xyz":np.array([
            [ 1,  0,  0,  0],
            [ 0,  1,  0,  0], 
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  1]]),
            
            "izo":
            np.array([
            [math.sqrt(1/2),-math.sqrt(1/6),math.sqrt(1/3),0],
            [0,math.sqrt(2/3),math.sqrt(1/3),0],
            [-math.sqrt(1/2),-math.sqrt(1/6),math.sqrt(1/3),0],
            [0,0,0,1],
            ]),
            "free":
            np.array([
            [ 1,  0,  0,  0],
            [ 0,  1,  0,  0], 
            [ math.sqrt(2)/2,  math.sqrt(2)/2,  0,  0],
            [ 0,  0,  0,  1],
            ]),
            "room":
            np.array([
            [ 1,  0,  0,  0],
            [ 0,  1,  0,  0], 
            [ math.sqrt(2)/4,  math.sqrt(2)/4,  0,  0],
            [ 0,  0,  0,  1],
            ])}
        
        self.projected_matrix=self.projected_mode["izo"]
        self.zero_coords=[WIDTH/2/(CELL_HEIGHT/self.scale),HEIGHT/(CELL_HEIGHT/self.scale)/2,0,1]
        # self.coord_line=np.array([self.zero_coords,[],])
        self.curent_ObjectInfo=ObjectInfo()
        self.show_coords =True
        self.point_sys_coord =None
        self.line_sys_coord=[]
        self.canvas_coords =np.array([[0,0,0,1]])        
        self.show_coords =True
        self.f=0
        self.q=0
        self.z=100
        self.matrix_sys_coord = np.array([
            [1, 0, 0, 0],
            [0, -1, 0, 0], 
            [0, 0, 1, 0],
            [self.zero_coords[0], self.zero_coords[1], 0, 1/(CELL_HEIGHT/self.scale)]])
        self.is_show_main=True
        self.lines = []
        self.points = np.array([[0,0,5,1]])
        self.canvas_points = np.array([[0,0,0,1]])
        
        self.splain_points = None
        self.splain_lines = []
        self.is_draw_splain=False
        
        self.selection_rect = None
        
        self.selected_point = None 
        self.selected_line = None
        
        self.selected_points = None
        self.selected_lines = None
        
        
        self.edit_line = None
        self.edit_point = None
        
        self.status = ""
        self.curspos = ""
        self.mode = "create"
        self.font = pygame.font.Font(None, 24)                       
        
        self.dragging = False
        self.free_coord_xyz =0
        self.drag_offset = (0, 0 , 0)
        
        
        self.points_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
        self.points_surface.set_colorkey(WHITE)
        self.points_surface = self.points_surface.convert_alpha()
    # def root_init_(self):
    #     root =tk.Tk()
    #     root.title("Пульт Управления")     # устанавливаем заголовок окна
    #     root.geometry(f"300x{HEIGHT}+1200+0")
        
    #     root.frame = tk.Frame(root)
    #     root.frame.pack()
    #     root.button_frame = tk.Frame(root.frame)
    #     root.button_frame.pack()

    #     root.create_button = tk.Button(root.button_frame, text="Создать", command=self.toggle_mode)
    #     root.create_button.pack(side=tk.LEFT)

    #     root.edit_button = tk.Button(root.button_frame, text="Редактировать", command=self.edit1_line)
    #     root.edit_button.pack(side=tk.LEFT)

    #     root.delete_button = tk.Button(root.button_frame, text="Удалить", command=self.delete_line)
    #     root.delete_button.pack(side=tk.LEFT)

    #     root.splain_button = tk.Button(root.button_frame, text="Сплайн", command=self.splain)
    #     root.splain_button.pack(side=tk.LEFT)

    #     root.coord_frame = tk.Frame(root.frame)
    #     root.coord_frame.pack()
        
                            
    #     root.x_button = tk.Button(root.coord_frame, text="X", command=lambda: self.coord_mode=self.coord_modes["zy"])
    #     root.x_button.pack(side=tk.LEFT)

    #     root.y_button = tk.Button(root.coord_frame, text="Y", command=lambda: self.coord_mode=self.coord_modes["xz"])
    #     root.y_button.pack(side=tk.LEFT)

    #     root.z_button = tk.Button(root.coord_frame, text="Z", command=lambda: self.coord_mode=self.coord_modes["xy"])
    #     root.z_button.pack(side=tk.LEFT)

    #     root.show_main_button = tk.Button(self.frame, text="Показать основные точки", command=self.show_main_points)
    #     root.show_main_button.pack()
        
        
    #     return root
   
    def move_zero_coords(self, dx, dy):
        self.zero_coords[0] += dx
        self.zero_coords[1] += dy
        self.matrix_sys_coord[3, self.coord_mode[0]] = self.zero_coords[0]
        self.matrix_sys_coord[3, self.coord_mode[1]] = self.zero_coords[1]        
        self.update_canvas_coord()
        
    def find_ave_point(self,points):
        if points is None and self.points.shape[0]>0:
            points=range(self.points.shape[0])
        ave_point=np.array([0,0,0,1])
        for point in points:
            ave_point[0]+=self.points[point,0]
            ave_point[1]+=self.points[point,1]
            ave_point[2]+=self.points[point,2]
        ave_point[0]/=self.points.shape[0]
        ave_point[1]/=self.points.shape[0]
        ave_point[2]/=self.points.shape[0]
        return ave_point 
    
    def S_edit(self,points,m,n,k):
        if points is None:
            if self.points.shape[0]>0:
                points=range(self.points.shape[0])
            else:
                raise ValueError("Неправильный формат" )            
        A_matrix =np.empty([0,4])
        for point in points:
            A_matrix=np.append(A_matrix,self.points[point],axis=0)               
        matrix=np.array([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [m,n,k,1]])
        if A_matrix.shape[0]>0:
            A_matrix=np.matmul(np.matmul(A_matrix,matrix),self.matrix_sys_coord)
            A_matrix=A_matrix/A_matrix[:,-1][:,None]
        for point in points:
            self.points[point]=A_matrix[point]
    
    def get_matrix_tk1(self,default_values): 
        
        def save_values():
            values = []
            for row in entries:
                row_values = []
                for entry in row:
                    row_values.append(float(entry.get()))
                values.append(row_values)
            self.projected_matrix=np.array(values)
            self.M_edit(self.selected_points,self.projected_matrix)
            root.destroy()
            self.root=None
            

        def reset_values():
            
            for i in range(4):
                for j in range(4):
                    entries[i][j].delete(0, tk.END)
                    entries[i][j].insert(0, self.projected_matrix[i,j])
        
        
        
        def validate_input(P):
            return P.replace('.', '', 1).replace('-', '', 1).isdigit() or P == "" or P == "-" or P == "."       
        root=tk.Tk()
        root.title("Измените матрицу для преобразования")# устанавливаем заголовок окна
        root.geometry(f"300x{300}+{int(WIDTH/2)}+{int(HEIGHT/2)}")
        entries = []
        if default_values is None:
            default_values = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        vcmd = (root.register(validate_input), '%P')
        for i in range(4):
            row = []
            for j in range(4):
                entry = tk.Entry(root, width=5,validate="key",vcmd=vcmd)
                entry.grid(row=i, column=j)
                entry.insert(0, default_values[i][j])
                row.append(entry)
            entries.append(row)
            
        button_frame = tk.Frame(root)
        button_frame.grid(row=4, column=0, columnspan=4)
        button_frame1 = tk.Frame(root)
        button_frame1.grid(row=5, column=0, columnspan=4)
        save_button = tk.Button(button_frame, text="Сохранить", command=save_values)
        save_button.pack(side=tk.LEFT)

        reset_button = tk.Button(button_frame, text="Сбросить", command=reset_values)
        reset_button.pack(side=tk.LEFT) 
        
        mode_var = tk.StringVar()
        mode_var.set(list(self.projected_mode.keys())[0])  # default value

        mode_menu = tk.OptionMenu(button_frame, mode_var, *self.projected_mode.keys())
        mode_menu.pack(side=tk.LEFT)
        
        def switch_mode():
            if self.mode == "create":
                self.mode = "edit1"
                mode_button.config(text="Редактировать")
                # код для режима редактирования
                print("Режим редактирования")
            else:
                self.mode = "create"
                mode_button.config(text="Создать")
                # код для режима создания
                print("Режим создания") 
        mode_button = tk.Button(button_frame1, text="Создать", command=switch_mode)
        mode_button.pack(side=tk.LEFT)

        def apply_mode():
            mode = mode_var.get()
            print(f"Выбран режим: {mode}")
            print(self.projected_mode[mode])
            self.projected_matrix=self.projected_mode[mode]            
            reset_values()
            
        self.button = tk.Button(button_frame, text="Применить", command=apply_mode)
        self.button.pack()  
        root.grab_set()
        self.root=root
        
    def get_matrix_tk(self, default_values):
        def save_values():
            values = []
            for row in entries:
                row_values = []
                for entry in row:
                    row_values.append(float(entry.get()))
                values.append(row_values)
            self.projected_matrix = np.array(values)
            self.M_edit(self.selected_points, self.projected_matrix)
            root.destroy()
            self.root = None

        def reset_values():
            for i in range(4):
                for j in range(4):
                    entries[i][j].delete(0, tk.END)
                    entries[i][j].insert(0, self.projected_matrix[i, j])

        def validate_input(P):
            return P.replace('.', '', 1).replace('-', '', 1).isdigit() or P == "" or P == "-" or P == "."

        root = tk.Tk()
        root.title("Измените матрицу для преобразования")
        root.geometry(f"500x300+{int(WIDTH / 2)}+{int(HEIGHT / 2)}")
        root.configure(bg="#f0f0f0")

        entries = []
        if default_values is None:
            default_values = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
        vcmd = (root.register(validate_input), '%P')

        matrix_frame = tk.Frame(root, bg="#f0f0f0")
        matrix_frame.pack(pady=20)

        for i in range(4):
            row = []
            for j in range(4):
                entry = tk.Entry(matrix_frame, width=5, validate="key", vcmd=vcmd, font=("Arial", 12))
                entry.grid(row=i, column=j, padx=5, pady=5)
                entry.insert(0, default_values[i, j])
                row.append(entry)
            entries.append(row)

        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        button_frame1 = tk.Frame(root, bg="#f0f0f0")
        button_frame1.pack(pady=10)
        save_button = tk.Button(button_frame, text="Сохранить", command=save_values, font=("Arial", 12), bg="#4CAF50", fg="#ffffff")
        save_button.pack(side=tk.LEFT, padx=10)

        reset_button = tk.Button(button_frame, text="Сбросить", command=reset_values, font=("Arial", 12), bg="#4CAF50", fg="#ffffff")
        reset_button.pack(side=tk.LEFT, padx=10)

        mode_var = tk.StringVar()
        mode_var.set(list(self.projected_mode.keys())[0])

        mode_menu = tk.OptionMenu(button_frame1, mode_var, *self.projected_mode.keys())
        mode_menu.pack(side=tk.LEFT, padx=10)

        def switch_mode():
            if self.mode == "create":
                self.mode = "edit1"
                mode_button.config(text="Редактировать")
                print("Режим редактирования")
            else:
                self.mode = "create"
                mode_button.config(text="Создать")
                print("Режим создания")

        mode_button = tk.Button(button_frame, text="Создать", command=switch_mode, font=("Arial", 12), bg="#4CAF50", fg="#ffffff")
        mode_button.pack(pady=5)

        def apply_mode():
            mode = mode_var.get()
            print(f"Выбран режим: {mode}")
            print(self.projected_mode[mode])
            self.projected_matrix = self.projected_mode[mode]
            reset_values()

        apply_button = tk.Button(button_frame1, text="Применить", command=apply_mode, font=("Arial", 12), bg="#4CAF50", fg="#ffffff")
        apply_button.pack()

        root.grab_set()
        self.root = root
    
    
       
    def M_edit(self,points,matrix):
        if points is None:
            if self.points.shape[0]>0:
                points=range(self.points.shape[0])
            else:
                raise ValueError("Неправильный формат файла. Доступные форматы: csv, txt")            
        A_matrix =np.empty([0,4])
        for point in points:
            if self.mode=="edit1":
                A_matrix=np.append(A_matrix,[self.points[point]],axis=0)
            else:
                A_matrix=np.append(A_matrix,[self.canvas_points[point]],axis=0)                

        
        if A_matrix.shape[0]>0:
            A_matrix=np.matmul(A_matrix,matrix)
            A_matrix=A_matrix/A_matrix[:,-1][:,None]
            if not self.mode=="edit1": 
                self.canvas_coords=np.matmul(np.matmul(self.point_sys_coord,matrix),self.matrix_sys_coord)
                self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        i=0
        for point in points:
            if self.mode=="edit1":                
                self.points[point]=A_matrix[i]                
            else:
                self.canvas_points[point]=A_matrix[i]
            i+=1
        if self.mode=="edit1":                
            self.update_canvas_coord()
               
        
    def del_point(self,id_point):
        if isinstance(id_point, int):
            id_point=[id_point]
        print(id_point)
        id_point.sort(reverse=True)
        print(id_point)
        for id in id_point:
            self.points = np.delete(self.points, (id), axis=0)
            self.canvas_points = np.delete(self.canvas_points, (id), axis=0)
            self.selected_line=None
            self.selected_point =None            
            lines_n=[]
            for line in self.lines:                
                if id not in line:
                    lines_n.append([line[0] if line[0]<id else line[0]-1,line[1] if line[1]<id else line[1]-1])
            self.lines=lines_n
        self.selected_points=None
        
    def find_point(self,pos,distan=5.0)->int:
        """Функция для магнитного соединения точек
        Также может найти точку.
         возникает ошибка в листе при выборе нескольких точек. надо препроверить
        Args:
            pos (list): содержит положение курсора [x,y] в экранных координатах
            distan (float): на каком растоянии в пикселях будет искать ближайшую точку
"
        Возвращает:
            int: индекс точки которая ближе всего к курсору на растоянии distan
            
            -1: если такой точки нет в этом радиусе
        """
        near_points=[]
        for point in range(self.points.shape[0]):
            if Point.get_distance([self.canvas_points[point,self.coord_mode[0]],self.canvas_points[point,self.coord_mode[1]]],pos)<distan:
                near_points.append(point)                
        if len(near_points)>1:
            near_point=-1
            min_distan=10000000
            for point in near_points:                
                cur_distan=Point.get_distance3d(self.canvas_points[point],[pos[0],pos[1],self.free_coord_xyz])
                if min_distan>cur_distan:
                    min_distan=cur_distan
                    near_point=point
            return near_point    
        elif len(near_points)==1:
            return near_points[0]
        else:
            return -1
    
    def find_line(self,pos,distan=5.0)->int:
        """Функция может найти индекс линии.
        
        Args:
            pos (list): содержит положение курсора [x,y] в экранных координатах
            distan (float): на каком растоянии в пикселях будет искать ближайшую линию
"
        Возвращает:
            int: индекс точки которая ближе всего к курсору на растоянии distan
            
            -1: если такой точки нет в этом радиусе
        """
        def is_point_inside_rect(pos, p1, p2,distance=5):
            x1, y1 = p1[self.coord_mode[0]],p1[self.coord_mode[1]]
            x2, y2 = p2[self.coord_mode[0]],p2[self.coord_mode[1]]
            x, y = pos

            return (min(x1, x2)-distance <= x <= max(x1, x2)+distance and
                    min(y1, y2)-distance <= y <= max(y1, y2)+distance)
            
        near_line=[]
        
        for line in range(len(self.lines)):
            p1=self.canvas_points[self.lines[line][0]]
            p2=self.canvas_points[self.lines[line][1]]            
            if Point.get_distance_line_2d(pos,p1,p2)<distan and is_point_inside_rect(pos,p1,p2):
                near_line.append(line)
        if len(near_line)>1:
            near_point=-1
            min_distan=10000000
            for line in near_line:
                p1=self.canvas_points[self.lines[line][0]]
                p2=self.canvas_points[self.lines[line][1]]                
                cur_distan=Point.get_distance_line_2d(pos,p1,p2)
                if min_distan>cur_distan:
                    min_distan=cur_distan
                    near_point=line
            return self.lines[near_point]    
        elif len(near_line)==1:
            return self.lines[near_line[0]]
        else:
            return -1
           
    def save_lines_to_file(self,lst, filename):
        """Записывает список кортежей в файл в формате TXT. 
        Args:
            lst (list): список кортежей для записи
            filename (str): имя файла для записи
        """
        with open(filename, 'w') as f:
            for item in lst:
                f.write(str(item) + '\n')    
        
    def save_matrix_to_file(self, matrix, filename, format='csv'):
        """
        Записывает numpy матрицу в файл в формате CSV или TXT.
        
        Параметры:
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
     
    def save_to_xml(self, data, filename):
        """
        Сохраняет данные в файл в формате XML.
        
        Параметры:
            data (dict или list): данные для сохранения
            filename (str): имя файла для сохранения
        """
        import xml.etree.ElementTree as ET
        root = ET.Element("data")
        
        if isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(root, key)
                elem.text = str(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                elem = ET.SubElement(root, f"item_{i}")
                if isinstance(item, tuple):
                    for j, value in enumerate(item):
                        subelem = ET.SubElement(elem, f"value_{j}")
                        subelem.text = str(value)
                else:
                    elem.text = str(item)
        
        tree = ET.ElementTree(root)
        tree.write(filename)

    def load_from_xml(self, filename):
        """
        Загружает данные из файла в формате XML.
        
        Параметры:
            filename (str): имя файла для загрузки
        
        Возвращает:
            dict или list: данные, загруженные из файла
        """
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            root = tree.getroot()
            
            data = {}
            for child in root:
                if child.tag.startswith("item_"):
                    values = []
                    for subchild in child:
                        values.append(subchild.text)
                    data[child.tag] = tuple(values)
                else:
                    data[child.tag] = child.text
            
            return data
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
            return None
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return None
        
    def load_lines_from_file(self, filename):
        """
        Загружает список кортежей из файла в формате TXT.
        
        Параметры:
            filename (str): имя файла для загрузки
        
        Возвращает:
            list: список cgbcrjd , загруженный из файла
        """
        try:
            with open(filename, 'r') as f:
                lines = [list(map(int, line.strip().replace('[', '').replace(']', '').split(', '))) for line in f]
            return lines
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
            return []
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return []

    def load_matrix_from_file(self, filename, format='csv'):
        """
        Загружает numpy матрицу из файла в формате CSV или TXT.
        
        Параметры:
            filename (str): имя файла для загрузки
            format (str): формат файла (csv или txt, по умолчанию csv)
        
        Возвращает:
            numpy.array: матрица, загруженная из файла
        """
        try:
            if format.lower() == 'csv':
                matrix = np.loadtxt(filename, delimiter=',')
            elif format.lower() == 'txt':
                matrix = np.loadtxt(filename, delimiter=' ')
            else:
                raise ValueError("Неправильный формат файла. Доступные форматы: csv, txt")
            return matrix
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
            return None
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return None 
     
    def mode_izometric(self):
        matrix_izometric=self.projected_mode["room"]
        self.coord_mode=self.coord_modes["xy"]       
        self.R_G_Active=True       
        self.canvas_points=np.matmul(np.matmul(self.points,matrix_izometric),self.matrix_sys_coord)
        self.canvas_points=self.canvas_points/self.canvas_points[:,-1][:,None]
        
        self.canvas_coords=np.matmul(np.matmul(self.point_sys_coord,matrix_izometric),self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        if self.is_draw_splain:
           self.splain_points=np.matmul(np.matmul(np.matmul(self.splain_points,np.linalg.inv(self.matrix_sys_coord)),matrix_izometric),self.matrix_sys_coord)
           self.splain_points=self.splain_points/self.splain_points[:,-1][:,None]
           
        self.draw_sys_coord()
        
    def R_canvas_coord(self,f,q,z=10):
        z=10
        self.coord_mode=self.coord_modes["xy"]
        self.R_G_Active=True 
        matrix_izometric=np.array(
            [[math.cos(math.radians(f)),math.cos(math.radians(q))*math.sin(math.radians(f)), 0,  0*math.cos(math.radians(q))*math.sin(math.radians(f))/z],
            [0, math.cos(math.radians(q)),  0,  0*-1*math.sin(math.radians(q))/z],
            [math.cos(math.radians(q)), -1*(math.cos(math.radians(f))*math.sin(math.radians(q))),   0,  0*-1*math.cos(math.radians(f))*math.cos(math.radians(q))/z],
            [0,0,0,1]])       
        self.projected_matrix=matrix_izometric      
        self.canvas_points=np.matmul(np.matmul(self.points,matrix_izometric),self.matrix_sys_coord)
        self.canvas_points=self.canvas_points/self.canvas_points[:,-1][:,None]
        
        
        self.canvas_coords=np.matmul(np.matmul(self.point_sys_coord,matrix_izometric),self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        
        if self.is_draw_splain:
           self.splain_points=np.matmul(np.matmul(np.matmul(self.splain_points,np.linalg.inv(self.matrix_sys_coord)),matrix_izometric),self.matrix_sys_coord)
           self.splain_points=self.splain_points/self.splain_points[:,-1][:,None]
           
        self.draw_sys_coord()
        
        
    def update_canvas_coord(self):
        self.R_G_Active=False        
        self.canvas_points= np.matmul(self.points,self.matrix_sys_coord)
        self.canvas_points=self.canvas_points/self.canvas_points[:,-1][:,None]
        
        self.canvas_coords=np.matmul(self.point_sys_coord,self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
        self.draw_sys_coord()
        
    def run(self):
        running = True
        dbclock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit(0)
                                
                if event.type==pygame.MOUSEMOTION: #события возникающие при движении мыши
                    if event.buttons[1]:
                        self.free_coord_xyz=0
                        self.print_cursor(event)
                    if pygame.key.get_pressed()[pygame.K_LCTRL]  and event.buttons[2]:
                        self.f+=event.rel[0]/10
                        self.q+=event.rel[1]/10
                        self.R_canvas_coord(self.f,self.q,self.free_coord_xyz)                    
                    elif event.buttons[2]:
                        dx = event.rel[0]/(CELL_HEIGHT/self.scale)
                        dy = event.rel[1]/(CELL_HEIGHT/self.scale)
                        # Левая кнопка мыши
                        
                        self.move_zero_coords(dx, dy)
                        self.draw_update_sys_coord()
                    self.selected_point=self.find_point(event.pos)
                    if self.selected_point==-1:
                        self.selected_point=None
                    self.selected_line=self.find_line(event.pos)
                    if self.selected_line==-1:
                        self.selected_line=None
                    # else:
                    #     print(self.selected_line)
                    self.print_cursor(event)
                    if event.buttons[0] and self.mode!="create":
                        if self.selection_rect is None and not self.dragging:
                            self.selection_rect = [event.pos, event.pos]
                        else:                             
                            if self.dragging:
                                if self.R_G_Active:
                                    self.R_G_Active=False 
                                    self.coord_mode=self.coord_modes["xy"] 
                                    self.update_canvas_coord()     
                                          
                                
                                for point in self.selected_points:
                                    self.canvas_points[point,self.coord_mode[0]] += (event.rel[0])
                                    self.canvas_points[point,self.coord_mode[1]] += (event.rel[1])
                                    self.points[point,self.coord_mode[0]] += (event.rel[0])/(CELL_HEIGHT/self.scale)
                                    if self.coord_mode[1]!=2:
                                        self.points[point,self.coord_mode[1]] -= (event.rel[1])/(CELL_HEIGHT/self.scale)
                                    else:
                                        self.points[point,self.coord_mode[1]] += (event.rel[1])/(CELL_HEIGHT/self.scale)
                                    
                                # self.update_canvas_coord()
                                # self.draw_sys_coord()
                            else:
                                self.selection_rect[1] = event.pos
                            
                if event.type == pygame.MOUSEBUTTONDOWN: #события возникающие при отпускании какой то кнопки мыши
                    if self.mode == "edit1":
                        if self.selected_points:
                            if event.button == 1:
                                self.dragging = True
                                self.drag_offset = np.matmul(np.array([[event.pos[0],event.pos[1],0,1]]),np.linalg.inv(self.matrix_sys_coord))
                
                if event.type==pygame.MOUSEBUTTONUP:#события возникающие при нажатии какой то кнопки мыши
                    # if dbclock.tick() < 200:
                    #     print("doubleclick")
                    #     self.select_lines_in_rect([[event.pos[0]+5,event.pos[1]-50], [event.pos[0]-5,event.pos[1]+50]])
                    #     self.dragging = True
                    #     self.drag_offset = np.matmul(np.array([[event.pos[0],event.pos[1],0,1]]),np.linalg.inv(self.matrix_sys_coord))
                    #     self.mode ="edit1"

                    if event.button == 1:
                        if self.mode=="create":
                            self.create_poligon(event.pos)
                        if self.mode=="edit1" :
                            if self.selected_line is not None:
                                self.edit1_line(event.pos) 
                            if self.selection_rect:
                                self.select_lines_in_rect(self.selection_rect)
                                self.selection_rect = None 
                            elif self.dragging:
                                self.dragging=False
                                self.selected_points=None
                                self.selected_lines=None
                                self.selection_rect = None       
                                       
                if event.type == pygame.MOUSEWHEEL: #события возникающие при движения колесика 
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        if event.y > 0:
                            self.scale += 0.1*self.scale
                        elif self.scale -1> 0:
                            self.scale -= 0.1*self.scale
                        self.zero_coords=[WIDTH/2/(CELL_HEIGHT/self.scale),HEIGHT/(CELL_HEIGHT/self.scale)/2,0,1]
                        self.matrix_sys_coord[3] = np.array([self.zero_coords[0], self.zero_coords[1], self.zero_coords[0], 1/(CELL_HEIGHT/self.scale)])
                        # self.matrix_sys_coord[3]=[0,0,0,1/(CELL_HEIGHT/self.scale)]
                        # self.matrix_sys_coord[3,self.coord_mode[0]]=self.zero_coords[0]
                        # self.matrix_sys_coord[3,self.coord_mode[1]]=self.zero_coords[1]
                        self.update_canvas_coord()
                        self.draw_sys_coord()
                        self.R_G_Active=False                         
                    elif not pygame.key.get_pressed()[pygame.K_LCTRL]:
                        if event.y > 0:
                            self.free_coord_xyz += 0.5
                        else:
                            self.free_coord_xyz -= 0.5
                                                 
                    
                if event.type==pygame.KEYUP :#события возникающие при нажатии какой то клавиши
                    if event.key == pygame.K_ESCAPE and self.edit_line is not None:
                        # self.lines.append((self.points.shape[0]-1,self.edit_point)) закрывать ли полигон
                        self.edit_line=None
                        self.edit_point=None
                    
                    if event.key == pygame.K_m:                            
                        self.get_matrix_tk(self.projected_matrix)
                            
                                
                        
                         
                    if  event.key == pygame.K_0:
                        self.mode_izometric()
                    if event.key == pygame.K_KP_0:                        
                        self.R_canvas_coord(self.f,self.q,self.free_coord_xyz) 
                    if  event.key == pygame.K_DELETE :
                        if self.selected_points is not None:
                            self.del_point(self.selected_points)
                        if self.selected_point is not None:
                            self.del_point(self.selected_point)
                        elif self.selected_line is not None:
                            self.lines.remove(self.selected_line)
                            self.selected_line=None
                    if event.key == pygame.K_9:
                        self.update_canvas_coord()   
                    
                    if event.key == pygame.K_1 and self.mode=="create":
                        self.is_draw_splain= not self.is_draw_splain
                        self.splain()
                    if event.key == pygame.K_x or event.key == pygame.K_y or event.key == pygame.K_z:   
                          
                        if event.key == pygame.K_x:
                            self.coord_mode=self.coord_modes["zy"]                            
                        if event.key == pygame.K_y:
                            self.coord_mode=self.coord_modes["xz"]
                        if event.key == pygame.K_z:
                            self.coord_mode=self.coord_modes["xy"]
                        
                        self.matrix_sys_coord[3]=[self.zero_coords[0],self.zero_coords[0],self.zero_coords[0],1/(CELL_HEIGHT/self.scale)]
                        self.matrix_sys_coord[3,self.coord_mode[0]]=self.zero_coords[0]
                        self.matrix_sys_coord[3,self.coord_mode[1]]=self.zero_coords[1]
                        self.update_canvas_coord()                        
                        self.draw_sys_coord()
                    if event.key == pygame.K_q:
                        self.toggle_mode()
                    
                    if event.key == pygame.K_o: #отображение поставленных точек
                        if self.is_show_main:
                            self.is_show_main=False
                            self.self.print_info=False
                        else:
                            self.is_show_main=True
                            self.self.print_info=True 
                    if event.key == pygame.K_i: #отображение поставленных точек
                        if self.self.print_info:
                            self.self.print_info=False
                        else:
                            self.self.print_info=True   
                               
                if event.type==pygame.KEYDOWN :
                     #события возникающие при отпускании какой то клавиши
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LCTRL]and keys[pygame.K_LSHIFT] and keys[pygame.K_DELETE]:
                        print("Очищено")
                        self.is_show_main=True
                        self.lines = []
                        self.selected_line=None
                        self.splain_points=None
                        self.points = np.array([[0,0,0,1]])
                        self.canvas_points = np.array([[0,0,0,1]])
                        self.edit_line=None
                        self.splain_points = None
                        self.splain_lines = []
                        self.is_draw_splain=False
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_s]:
                        print("Сохранено")
                        self.save_matrix_to_file(self.points,'Истинные точки.csv')
                        self.save_matrix_to_file(self.canvas_points,'Экранные точки.txt')        
                        self.save_lines_to_file(self.lines,'Линии.txt') 
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_l]:
                        print("Открываю")
                        self.points=self.load_matrix_from_file('Истинные точки.csv')
                        self.lines=self.load_lines_from_file('Линии.txt')
                        self.update_canvas_coord()
                        

            #вся информация
            #self.update_status(pos)           
            
                
            if pygame.mouse.get_focused():
                pygame.event.poll()                   
                self.draw()                              
                pygame.display.flip()                
                self.clock.tick(FPS)
                pygame.event.pump()
            if self.root is not None:
                    self.root.update()  

    def print_cursor(self, event):
        pos=self.free_coord_xyz*(CELL_HEIGHT/self.scale)
        pos=np.array([[pos,pos,pos,1]])
        pos[0,self.coord_mode[0]]=event.pos[0]
        pos[0,self.coord_mode[1]]=event.pos[1]
        
        
        pos=np.matmul(pos,np.linalg.inv(self.matrix_sys_coord))
        pos=pos/pos[:,-1][:,None]
        def mod_print():
            for mode in self.coord_modes.items():
                if mode[1]==self.coord_mode:
                    return mode[0]
            return None
        self.curspos = f"({round(pos[0,0],2)} ; {round(pos[0,1],2)} ; {round(self.free_coord_xyz,2)})   (f= {round(self.f%360,2)} q={round(self.q%360,2)}) отображаются {mod_print()}"
                
    def create1_point(self, pos):
        # self.matrix_sys_coord[3] = np.array([self.zero_coords[0], self.zero_coords[1], self.zero_coords[0], 1/(CELL_HEIGHT/self.scale)])
        self.matrix_sys_coord[3]=[0,0,0,1/(CELL_HEIGHT/self.scale)]
        self.matrix_sys_coord[3,self.coord_mode[0]]=self.zero_coords[0]
        self.matrix_sys_coord[3,self.coord_mode[1]]=self.zero_coords[1]
        self.update_canvas_coord()
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
            print(new_point,",  ",a)
            
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
        
        # Если линия редактирования не инициализирована
        if self.edit_line is None:
            # Если есть выделенная точка, использовать ее как стартовую
            if self.selected_point is not None:
                self.edit_line = [self.selected_point, -1]
                self.edit_point = self.selected_point
            # Если нет выделенной точки, создать новую точку
            else:
                self.create1_point(pos)
                self.edit_line = [self.points.shape[0] - 1, -1]
                self.edit_point = self.points.shape[0] - 1

        # Если вторая точка линии редактирования не определена (==-1)
        elif self.edit_line[1] == -1:
            # Если есть выделенная точка, связать ее с текущей edit_point
            if self.selected_point is not None:
                # Обновить edit_line, чтобы связать предыдущую точку с выделенной
                self.edit_line[1]= self.selected_point
                self.lines.append(self.edit_line)  # Добавить линию в список
                self.edit_point = self.selected_point  # Обновить edit_point
                self.edit_line = [self.edit_point, -1]                # Сбросить edit_line для новой точки
            # Если нет выделенной точки, создать новую точку
            else:
                self.create1_point(pos)
                # Если новая точка не является продолжением предыдущей, создать линию
                if self.edit_line[0]!= self.points.shape[0] - 1:
                    self.edit_line = [self.edit_line[0], self.points.shape[0] - 1]
                    self.lines.append(self.edit_line)
                    self.edit_line = [self.edit_line[1], -1]  # Обновить edit_line для новой точки
                # Если новая точка продолжает предыдущую, завершить полигон
                else:
                    
                    self.edit_line = [self.points.shape[0] - 1, self.edit_point]
                    self.lines.append(self.edit_line)
                    self.edit_line = None  # Сбросить edit_line и edit_point после завершения полигона
                    self.edit_point = None  
            
    def create1_poligon(self, pos):#рудимент
        if self.edit_line ==None:            
            if self.selected_point is not None:
                self.edit_line=[self.selected_point,-1]
                self.edit_point=self.selected_point
            else:
                self.create1_point(pos)                    
                self.edit_line=[self.points.shape[0]-1,-1]
            self.edit_point=self.points.shape[0]-1
        elif self.edit_line[1] == -1:
            if self.selected_point is not None:
                self.edit_line=[self.edit_point,-1 ]                
                
                self.edit_point=self.selected_point
                self.edit_line[1]=self.edit_point
                self.lines.append(self.edit_line)
                print(self.edit_line)
                
                
            else:
                self.create1_point(pos)                    
                
                
            if (self.edit_line[0]!=self.points.shape[0]-1):
                self.edit_line=(self.edit_line[0],self.points.shape[0]-1)
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
        
        self.edit_point=line[1] if Line.line_length(self.canvas_coords[line[0],self.coord_mode[0]],self.canvas_coords[line[0],self.coord_mode[1]], pos[0], pos[1]) > Line.line_length(self.canvas_coords[line[1],self.coord_mode[0]],self.canvas_coords[line[1],self.coord_mode[1]], pos[0], pos[1]) else line[0]
        self.mode="create"
        self.edit_line=[self.edit_point,-1]            
        self.lines.remove(line)
        
        self.selected_line=None
        return
        
            #can help us better understand the implications of our actions and the potential consequences of our decisions.

    def edit2_line(self):
        print("cltkfnm")
        

    
    def select_lines_in_rect(self, rect):
        selected_points = []
        x, y, w, h = rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        i=0
        for point in self.canvas_points:
            if x<=point[self.coord_mode[0]]<=w  and y<=point[self.coord_mode[1]]<=h:
                selected_points.append(i)
            i+=1
        if len(selected_points)==1:
            self.edit_point=None
            # self.edit_point=selected_lines[0][1]
            # self.edit_line=(self.edit_point,-1)
        selected_lines=[]
        for line in self.lines:
            if line[0] in selected_points and line[1] in selected_points:
                selected_lines.append(line)
        
        self.selected_points = selected_points
        self.selected_lines=selected_lines
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
    def draw_update_sys_coord(self):
        self.canvas_coords=np.matmul(self.point_sys_coord,self.matrix_sys_coord)
        self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
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
        self.points_surface.fill(WHITE)
        self.points_surface.set_alpha(50)
        if self.point_sys_coord is None:
            self.get_coord_point()
            # print(self.point_sys_coord)
            self.canvas_coords=np.matmul(self.point_sys_coord,self.matrix_sys_coord)
            self.canvas_coords=self.canvas_coords/self.canvas_coords[:,-1][:,None]
            
        i =self.coord_mode[0]
        j=self.coord_mode[1]        
        if self.show_coords:
                        
            
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
        
        def eq(line=None,x=0,y=0):
            
            if not self.print_info:
                return
            def mod_print():
                for mode in self.coord_modes.items():
                    if mode[1]==self.coord_mode:
                        return mode[0]
                return None
            if line is None:
                line=self.selected_line
            t=[]
            if self.R_G_Active:                
                t.append(f"x(t)={round((self.points[line[0],0]),2)}+({round((self.points[line[0],0]-self.points[line[1],0]),2)})t")
                t.append(f"y(t)={round((self.points[line[0],1]),2)}+({round((self.points[line[0],1]-self.points[line[1],1]),2)})t")
                t.append(f"z(t)={round((self.points[line[0],2]),2)}+({round((self.points[line[0],2]-self.points[line[1],2]),2)})t")
                point1=[WIDTH-185+x,25-y*3]
            else:
                t.append(f"{Line.equation(self.points[line[0],self.coord_mode[0]],self.points[line[0],self.coord_mode[1]],self.points[line[1],self.coord_mode[0]],self.points[line[1],self.coord_mode[1]],mod_print())}")
                point1=[WIDTH-185+x,25-y]
            point =[(self.canvas_points[line[0],self.coord_mode[0]]+self.canvas_points[line[1],self.coord_mode[0]])/2,(self.canvas_points[line[0],self.coord_mode[1]]+self.canvas_points[line[1],self.coord_mode[1]])/2]
            
            pygame.draw.line(self.screen, BLACK, point, point1,1)

            pygame.draw.circle(self.screen, BLACK, point, 2)
            
            if self.R_G_Active:
                point1=[WIDTH-180+x,20-y*3]
            for text in t:
                self.screen.blit(self.font.render(text, True, BLACK), point1)
                point1[1]+=15
        
        
        if self.point_sys_coord is None:
            self.draw_sys_coord()
        
            
        
        self.screen.fill(WHITE)
        i =self.coord_mode[0]
        j=self.coord_mode[1] 
        pygame.draw.line(self.screen, (255,0,0), (self.canvas_coords[0,i], self.canvas_coords[0,j]), (self.canvas_coords[1,i], self.canvas_coords[1,j]),4)
        pygame.draw.line(self.screen, (0,0,255), (self.canvas_coords[2,i], self.canvas_coords[2,j]), (self.canvas_coords[3,i], self.canvas_coords[3,j]),4)
        pygame.draw.line(self.screen, (0,255,0), (self.canvas_coords[4,i], self.canvas_coords[4,j]), (self.canvas_coords[5,i], self.canvas_coords[5,j]),5)           
           
        self.screen.blit(self.points_surface, (0, 0)) 
        
        
        
        
        if self.selection_rect:
            pygame.draw.rect(self.screen, (0, 255, 0, 128), pygame.Rect(self.selection_rect[0][0], self.selection_rect[0][1], self.selection_rect[1][0] - self.selection_rect[0][0], self.selection_rect[1][1] - self.selection_rect[0][1]), 2)
            
        if self.selected_points:
            for line in self.selected_points:
                self.screen.blit(self.font.render(f"({round(self.points[line,0],2)} {round(self.points[line,1],2)} {round(self.points[line,2],2)})", True, BLACK), (self.canvas_points[line,self.coord_mode[0]], self.canvas_points[line,self.coord_mode[1]]))
                pygame.draw.circle(self.screen, (0, 255, 0), (self.canvas_points[line,self.coord_mode[0]], self.canvas_points[line,self.coord_mode[1]]), 5)
        if self.selected_lines:
            x=0
            for line in self.selected_lines:
                eq(line,0,x)
                x-=20
                pygame.draw.line(self.screen, (0, 255, 0), (self.canvas_points[line[0],self.coord_mode[0]], self.canvas_points[line[0],self.coord_mode[1]]), (self.canvas_points[line[1],self.coord_mode[0]], self.canvas_points[line[1],self.coord_mode[1]]),5)
        if self.selected_point is not None:
            if self.selected_points is None:  
                self.screen.blit(self.font.render(f"{(self.points[self.selected_point,self.coord_mode[0]], self.points[self.selected_point,self.coord_mode[1]])}", True, BLACK), (self.canvas_points[self.selected_point,self.coord_mode[0]], self.canvas_points[self.selected_point,self.coord_mode[1]]))
            elif not self.selected_point in self.selected_points:
                self.screen.blit(self.font.render(f"{(self.points[self.selected_point,self.coord_mode[0]], self.points[self.selected_point,self.coord_mode[1]])}", True, BLACK), (self.canvas_points[self.selected_point,self.coord_mode[0]], self.canvas_points[self.selected_point,self.coord_mode[1]]))
            pygame.draw.circle(self.screen, RED, (self.canvas_points[self.selected_point,self.coord_mode[0]], self.canvas_points[self.selected_point,self.coord_mode[1]]), 5)
        if self.selected_line is not None:
            if self.selected_lines is None:                
                eq()
            elif not self.selected_line in self.selected_lines:
                eq()
            line =self.selected_line
            pygame.draw.line(self.screen, BLACK, (self.canvas_points[line[0],self.coord_mode[0]], self.canvas_points[line[0],self.coord_mode[1]]), (self.canvas_points[line[1],self.coord_mode[0]], self.canvas_points[line[1],self.coord_mode[1]]),5)    
        
        if self.is_show_main:
            for line in self.lines:            
                pygame.draw.line(self.screen, BLACK, (self.canvas_points[line[0],self.coord_mode[0]], self.canvas_points[line[0],self.coord_mode[1]]), (self.canvas_points[line[1],self.coord_mode[0]], self.canvas_points[line[1],self.coord_mode[1]]),3)
            for line in self.canvas_points:
                pygame.draw.circle(self.screen, RED, (line[self.coord_mode[0]], line[self.coord_mode[1]]), 3)
            
        if self.is_draw_splain:
            for line in self.splain_lines:            
                pygame.draw.line(self.screen, CREY, (self.splain_points[line[0],self.coord_mode[0]], self.splain_points[line[0],self.coord_mode[1]]), (self.splain_points[line[1],self.coord_mode[0]], self.splain_points[line[1],self.coord_mode[1]]),2 )
            # for point in self.splain_points:
            #     pygame.draw.circle(self.screen, BLACK, (point[self.coord_mode[0]], point[self.coord_mode[1]]), 1)
            
        if self.edit_line!=None:
            pygame.draw.line(self.screen, BLACK, (self.canvas_points[self.edit_line[0],self.coord_mode[0]], self.canvas_points[self.edit_line[0],self.coord_mode[1]]), (pygame.mouse.get_pos()),3)
        
        
        
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
            self.mode = "create"
        
            
    def delete_line1(self):
        if self.selected_points:            
            for line in self.selected_points:
                self.lines.remove(line)                
            self.selected_points=None
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

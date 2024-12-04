import numpy as np
from config import WIDTH, HEIGHT, WHITE, BLACK, RED, CREY, CELL_HEIGHT, FPS

class ObjectInfo:
    def __init__(self, true_points=None, lines=None, color_line=BLACK, color_point=CREY, other_settings=None):
        self.true_points = true_points
        self.projected_points = None
        self.lines=lines
        self.color_line = color_line
        self.color_point = color_point
        self.other_settings = other_settings

    def set_true_points(self,points):
        self.true_points=points
    
    def get_true_points(self):
        return self.true_points

    def set_projected_points(self,project_matrix):
        self.projected_points=np.matmul(self.true_points,project_matrix)
        self.projected_points=self.projected_points/self.projected_points[:,-1][:,None]
        
    def get_projected_points(self):       
        return self.projected_points

    def get_color(self):
        return self.color

    def get_thickness(self):
        return self.thickness

    def get_other_settings(self):
        return self.other_settings
    
    def add_point(self,point,index=-1):
        if index==-1:
            self.true_points=np.insert(self.true_points, self.true_points.shape[0], point, axis=0)
import numpy as np

def midpoint(p1, p2, displacement):
    """
    Вычисляет среднюю точку между двумя точками с добавлением случайного смещения по z.
    
    Parameters:
    p1 (numpy.array): первая точка
    p2 (numpy.array): вторая точка
    displacement (float): случайное смещение по z
    
    Returns:
    numpy.array: средняя точка с добавленным смещением
    """
    mid = (p1 + p2) / 2
    mid[2] +=0.5
    # mid[2] += np.random.uniform(-displacement, displacement)
    return mid

def fractal_landscape(points, displacement, iterations=1):
    """
    Генерирует фрактальный ландшафт на основе заданных точек и смещения.
    
    Parameters:
    points (numpy.array): матрица 3x4 с координатами точек (x, y, z, 1)
    displacement (float): случайное смещение по z
    iterations (int): количество итераций (по умолчанию 1)
    
    Returns:
    numpy.array: матрица с координатами точек фрактального ландшафта
    """
    landscape = points.copy()
    new_points = []
     
    for i in range(3):
        p1 = landscape[i]
        p2 = landscape[(i + 1) % len(landscape)]
        mid = midpoint(p1, p2, displacement)
        new_points.extend([p1,mid,p2])
        
    if iterations==0:
        points=np.append(points, np.array(new_points),axis=0)        
    else:
        a=fractal_landscape(np.array([points[0],new_points[0],points[1]]),displacement,iterations-1)
        points=np.append(points,a,axis=0)
        a=fractal_landscape(np.array([points[1],new_points[1],points[2]]),displacement,iterations-1)
        points=np.append(points,a,axis=0)
        a=fractal_landscape(np.array([points[2],new_points[2],points[0]]),displacement,iterations-1)
        points=np.append(points,a,axis=0)
        a=fractal_landscape(np.array(new_points),displacement,iterations-1)
        points=np.append(points,a,axis=0)        
    return points

import numpy as np

def save_matrix_to_file(matrix, filename, format='csv'):
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

# Пример использования
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])
# save_matrix_to_file(matrix,'matrix.csv', format='csv')
# save_matrix_to_file(matrix,'matrix.txt', format='txt')



points = np.array([
    [2/7, 0, 1/7],
    [-3/7, 1, -5/7],
    [-3/7, 0, 4/7]    
])
a=np.array([
    [0.6],
    [2.55],
    [0.8]    
])
displacement = 0.1
# landscape = fractal_landscape(points, displacement, iterations=7)
print(np.matmul(points,a)[0]*2)
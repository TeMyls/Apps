from MatrixMath import *
import numpy as np

class VTX3D():
    def __init__(self, x , y, z):
        self.vertex = np.array(
            set_matrix3D(x, y, z),  dtype=np.float64
        )
        self.x_angle = 180
        self.y_angle = 180
        self.z_angle = 180

    def get_X(self):
        return self.vertex[0, 0]

    def get_Y(self):
        return self.vertex[1, 0]
    
    def get_Z(self):
        return self.vertex[2, 0]


    def __str__(self):
        return "X {} Y {} Z {}".format(self.get_X(), self.get_Y(), self.get_Z())
    
    def set_coords(self, x, y, z):
        self.vertex[0, 0] = x
        self.vertex[1, 0] = y
        self.vertex[2, 0] = z
        self.vertex[3, 0] = 1

    def transform(self, translation_matrix, transform_matrix, matrix_translation):
        #multiple ways to transform points
        '''
        XnY = np.linalg.multi_dot(
                            [
                            self.vertex,
                            translation_matrix, #moves to origin
                            transform_matrix, #applies transform
                            matrix_translation, #moves back to original position
                            
                            ] 
        )
        
        '''
        '''
        XnY = translation_matrix @ self.vertex #moves to origin
        #print(XnY, '\n')
        XnY = transform_matrix @ XnY #applies transform
        #print(XnY, '\n')
        XnY = matrix_translation @ XnY #moves back to original position
        '''
        '''
        XnY = np.dot(translation_matrix, self.vertex) #moves to origin
        #print(XnY, '\n')
        XnY = np.dot(transform_matrix, XnY) #applies transform
        #print(XnY, '\n')
        XnY = np.dot(matrix_translation, XnY) #moves back to original position
        '''
        '''
        XnY = np.dot(matrix_translation, np.dot(transform_matrix, np.dot(translation_matrix, self.vertex)))
        '''
        full_transform = matrix_translation @ transform_matrix @ translation_matrix
        XnY = full_transform @ self.vertex
        self.set_coords(XnY[0 ,0], XnY[1, 0], XnY[2, 0])
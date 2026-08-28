from MatrixMath import *
import numpy as np

class VTX2D():
    def __init__(self, x , y):
        self.vertex = np.array(
            set_matrix2D(x, y),  dtype=np.float64
        )

    def get_X(self):
        return self.vertex[0, 0]

    def get_Y(self):
        return self.vertex[1, 0]

    def __str__(self):
        return "X {} Y {}".format(self.get_X(), self.get_Y())
    
    def set_coords(self, x, y):
        self.vertex[0, 0] = x
        self.vertex[1, 0] = y
        self.vertex[2, 0] = 1

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
        self.set_coords(XnY[0 ,0], XnY[1, 0])
        self.been_transformed = True

import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
#from numpy import eye, dot, linalg, array, uint8
from numpy import array, uint8,  dot, float64, eye
from numpy import radians as to_radians
import math
import time

def path_correction(file_path):
    foward_slash = "/"
    back_slash = "\\"
    file_path = file_path.replace(foward_slash, back_slash)

    return file_path

def hide_widget(widget):
    widget.grid_remove()
        
def show_widget(widget):
    widget.grid()

def disable_widget(widget):
    widget.config(state="disabled")

def enable_widget(widget):
    widget.config(state="normal")

def arrange_widgets(arrangement):
    for ind_y in range(len(arrangement)):
        for ind_x in range(len(arrangement[ind_y])):

            if arrangement[ind_y][ind_x] == None:
                pass
            else:
                arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NEWS")


#https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip():

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


        
class ImageSplitter(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        pass

    

class Vertex():
    def __init__(self, x , y):
        self.v = array(
            set_matrix2D(x, y),  dtype=float64
        )


    def get_X(self):
        return self.v[0, 0]

    def get_Y(self):
        return self.v[1, 0]

    def __str__(self):
        return "X {} Y {}".format(self.get_X(), self.get_Y())
    
    def set_coords(self, x, y):
        self.v[0, 0] = x
        self.v[1, 0] = y
        self.v[2, 0] = 1

    def transform(self, translation_matrix, transform_matrix, matrix_translation):
        
        '''
        XnY = np.linalg.multi_dot(
                            [
                            self.v,
                            translation_matrix, #moves to origin
                            transform_matrix, #applies transform
                            matrix_translation, #moves back to original position
                            
                            ] 
        )
        
        '''
        '''
        XnY = translation_matrix @ self.v #moves to origin
        #print(XnY, '\n')
        XnY = transform_matrix @ XnY #applies transform
        #print(XnY, '\n')
        XnY = matrix_translation @ XnY #moves back to original position
        '''
        '''
        XnY = dot(translation_matrix, self.v) #moves to origin
        #print(XnY, '\n')
        XnY = dot(transform_matrix, XnY) #applies transform
        #print(XnY, '\n')
        XnY = dot(matrix_translation, XnY) #moves back to original position
        '''
        XnY = dot(matrix_translation, dot(transform_matrix, dot(translation_matrix, self.v)))
        #print('nump')
        #print(XnY)
        self.set_coords(XnY[0 ,0], XnY[1, 0])


    
    

    
class Sheet():
    def __init__(self, vertices, x_divisions, y_divisions) :
        '''
        0 - Sheet is a class that represents a collection of vertices from the very edges of the shape to the edges of individual pixel polygons made of XY vertices
        1 - pixel grid is a 2D array/list of Hex Codes, that represent the pixels in an image, and empty cell/pixel is denoted by None instead of a hexcode
        2 - pixel coords is a dictionary of vertex coordinates 
            say for instance a 4x4 grid
            "X-Y-Z" as a string that is a key to a dictionary/hashmap
            Each of these keys would have an array linking to their vertex coordinates 
                [V1, V2, V3, V4] of their polygon 
            'V' is an x, y vertex
            "Z" refers to the layer in the stack, it is 0 for this example
            'N' and 'M' are it's respective dimensions 
            For a 4x4 cell grid both M and N would be 4

                        M
    
            V-------V-------V-------V-------V
            | 0-0-0 | 0-1-0 | 0-2-0 | 0-3-Z | 
            V-------V-------V-------V-------V
            | 1-0-0 | 1-1-0 | 1-2-0 | 1-3-0 |
       N    V-------V-------V-------V-------V  
            | 2-0-0 | 2-1-0 | 2-2-0 | 2-3-0 | 
            V-------V-------V-------V-------V
            | 3-0-0 | 3-1-0 | 3-2-0 | 3-3-0 |
            V-------V-------V-------V-------V

            
            

        3 - pixel vertices is a list of the vertices in an area, the vertices that are values in pixel coords are the same objects  in this list
            The amount of unique vertices are as follows
            4 outside vertices with 2 neighbors
            2(M - 1) + 2(N - 1) vertices with 3 neighbors
            (M - 1 ) * (N - 1) vettices with 4 neighbors

            For a 4x4 grid it's 4 + (2(4 - 1) + 2(4 - 1)) +  ((4 - 1) * (4 - 1)) which equals 25 vertices
            Why? Computationally more efficient. 16 rectangle polygons with 4 vertices each totaling 48 vertices with many sharing the same coordinates doesn't scale well.
            With each vertex being an object, updating them once will change all of them in whatever data structure their in
        '''
        #vertices is to have 8 x-y points making a rectangle
        #these vertices are 
        self.top_left = Vertex(
            vertices[0],
            vertices[1],
        )

        self.bottom_left = Vertex(
            
            vertices[2],
            vertices[3],
        )

        self.bottom_right = Vertex(
            vertices[4],
            vertices[5],
        )

        

        self.top_right = Vertex(
            vertices[6],
            vertices[7],
        )


        self.borders = [
            self.top_left, 
            self.bottom_right, 
            self.bottom_left, 
            self.top_right
        ]



        self.pixel_grid = []
        self.pixel_coords = {}
        self.pixel_vertices = []

        self.z_layer = 0

        self.pixel_canvas_width = x_divisions
        self.pixel_canvas_height = y_divisions

        self.sprite_column = 0

        self.t_mat = eye(3)
        self.mat_t = eye(3)
        self.mt = eye(3)
        self.grid_x = -1
        self.grid_y = -1

    def test(self, e):
        return str(e)

    def transform_vertex(self, vertex):
        vertex.transform(self.t_mat, self.mt, self.mat_t)
        return vertex
    
    def coord_transform(self, vertices):
        if vertices:
            top_left_vertex = vertices[0]
            bottom_right_vertex = vertices[1]
            top_right_vertex = vertices[2]
            bottom_left_vertex = vertices[3]

            top_left_vertex.transform(self.t_mat, self.mt, self.mat_t)
            bottom_right_vertex.transform(self.t_mat, self.mt, self.mat_t)
            top_right_vertex.transform(self.t_mat, self.mt, self.mat_t)
            bottom_left_vertex.transform(self.t_mat, self.mt, self.mat_t)
        return vertices

    def transform_coords(self, key, value):
        if value:
            top_left_vertex = value[0]
            bottom_right_vertex = value[1]
            top_right_vertex = value[2]
            bottom_left_vertex = value[3]

            top_left_vertex.transform(self.t_mat, self.mt, self.mat_t)
            bottom_right_vertex.transform(self.t_mat, self.mt, self.mat_t)
            top_right_vertex.transform(self.t_mat, self.mt, self.mat_t)
            bottom_left_vertex.transform(self.t_mat, self.mt, self.mat_t)
        return key, value

   
    def apply_transform(self, translation_matrix, transform_matrix, matrix_translation):
        #each of the matrices/arrays should be numpy arrays
        #map(self.multi_transform, transform_matrix, translation_matrix, matrix_translation)
        #
        
        self.t_mat = translation_matrix
        self.mt = transform_matrix
        self.mat_t = matrix_translation
        '''
        #experiments, slower
        self.borders = list(map(self.vertex_transform, self.borders))
        
        self.pixel_coords = dict(map(self.transform_coords, self.pixel_coords.keys(), self.pixel_coords.values()))
        
        
        self.pixel_coords = dict(
                                zip(
                                    self.pixel_coords.keys(), map(self.coord_transform, self.pixel_coords.values()) 
                                    )
                                )
        '''
        '''
        for vertex in self.pixel_vertices:
            vertex.transform(translation_matrix, transform_matrix, matrix_translation)
        '''
        
        for vertex in self.borders:
            vertex.transform(translation_matrix, transform_matrix, matrix_translation)

        
        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            if vertices:
                top_left_vertex = vertices[0]
                bottom_right_vertex = vertices[1]
                top_right_vertex = vertices[2]
                bottom_left_vertex = vertices[3]

                top_left_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                bottom_right_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                top_right_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                bottom_left_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
        





    def __str__(self):
        return "V0-X:{} Y:{}|V1-X:{} Y:{}|V2-X:{} Y:{}|V3-X:{} Y:{}".format(
            self.top_left.get_X(), self.top_left.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(), self.bottom_left.get_Y(),
            self.top_right.get_X(), self.top_right.get_Y()
            )

    def coord_str(self, c, x, y, z):
        return str(c) + '-' +  str(x) + '-' + str(y) + '-' + str(z)
    
    def str_coord(self, string):
        if '-' in string:
            c, x, y, z = map(int, string.split('-'))
            return c, x, y, z
        return 0, 0, 0

    def in_bounds(self, grid_x, grid_y, grid_w, grid_h):
        return 0 <= grid_x < grid_w and 0 <= grid_y < grid_h 

    def degrees_to_radians(self, deg):
        return to_radians(deg) #(deg * math.pi)/180



    def get_borders(self):
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]
   
    def display_1d(self, arr):
        s = ""
        for i in range(len(arr)):
            #for j in range(len(arr2d[i])):
            s = s + str(arr[i]) + " "
            #s = s + '\n'
        print(s)    
    
    def display_2d(self, arr2d):
        s = ""
        for y in range(len(arr2d)):
            for x in range(len(arr2d[y])):
                s = s + str(arr2d[y][x]) + " "
            s = s + '\n'
        print(s)
    
    def print_data(self):
        '''
        print("Level {}".format(self.z_layer))
        print("Vertex Count {}".format(len(self.pixel_vertices)))

        for vertex in self.borders:

            print("Border X: {} Y: {}".format(vertex.get_X(), vertex.get_Y()))


        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            
            if vertices:
                print(key)
                top_left_vertex = vertices[0]
                bottom_right_vertex = vertices[1]
                top_right_vertex = vertices[2]
                bottom_left_vertex = vertices[3]

                print("Key:{}".format(key))
                print("Top Left X: {} Y: {}".format(top_left_vertex.get_X(), top_left_vertex.get_Y()))
                print("Bottom Right X: {} Y: {}".format(bottom_right_vertex.get_X(), bottom_right_vertex.get_Y()))
                print("Top Right X: {} Y: {}".format(top_right_vertex.get_X(), top_right_vertex.get_Y()))
                print("Bottom Left X: {} Y: {}".format(bottom_left_vertex.get_X(), bottom_left_vertex.get_Y()))
            #else:
            #    print("No Vertices")
        print()
        '''
        print(f"Layer {self.z_layer} Column {self.sprite_column}")
        self.display_2d(self.pixel_grid)


    
    def DDA_raycast(self, x0, y0, radians, limit):
        x_inc = math.cos(radians)
        y_inc = math.sin(radians)

        _x = x0
        _y = y0

        d = get_distance(x0, y0, _x, _y)
        while d < limit:
            _x += x_inc
            _y += y_inc
            d = get_distance(x0, y0, _x, _y)

        return _x, _y
    
    def DDA(self, x0, y0, x1, y1):
        #Digital Differential Analyzer
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx),abs(dy))
            
        x_inc = dx/steps
        y_inc = dy/steps
        
        x = x0
        y = y0
        
        coordinates = []
        
        for i in range(int(steps)):
            x += x_inc
            y += y_inc
            floored_coords = [math.floor(x), math.floor(y)]
            if floored_coords not in coordinates:
                coordinates.append(floored_coords)
                
        return coordinates

    def delete_loner_vertcies(self, grid_x, grid_y):
        pass

    def recycle_vertices(self, grid_x, grid_y, left_top, right_top, right_bottom, left_bottom, is_erasing):
        #The purpose of this to reuse existing vertices

        #[N,NE,E,SE,S,SW,W,NW]
        #possible directions
        #8 direction
        '''
                        x  y 
                        0,-1
            -1,-1                   1, -1
                V-----V-----V-----V
                |  NW |  N  |  NE | 
                V-----V-----V-----V     
        -1,0    |  W  |  CC |  E  |     1, 0
                V-----V-----V-----V
                |  SW |  S  |  SE | 
                V-----V-----V-----V
            -1,1                    1, 1
                        0, 1
        '''
        temp = Vertex(-1, -1)
        #The vertices of CC
        top_left  = Vertex(left_top[0], left_top[1])
        top_right  = Vertex(right_top[0], right_top[1])
        bottom_right = Vertex(right_bottom[0], right_bottom[1])
        bottom_left = Vertex(left_bottom[0], left_bottom[1])

        reuse_top_left = False
        reuse_top_right = False
        reuse_bottom_right = False
        reuse_bottom_left = False

        delete_top_left = True
        reuse_top_right = True
        reuse_bottom_right = True
        reuse_bottom_left = True

        bottom_right_vectors = [
            #x y
            (1, 0), #East
            (1, 1), #South East
            (0,  1) #South
        ]

        bottom_left_vectors = [
            #x y
            (-1, 0), #West
            (-1, 1), #South West
            (0,  1) #South
        ]

        top_left_vectors = [
            #x y
            (0, -1), #North
            (-1,-1), #North West
            (-1, 0) #West
        ]

        top_right_vectors = [
            #x y
            (0, -1), #North
            (1,-1),  #North East
            (1, 0)   #East
        ]

        
        
        """
            top_left     = vertices[0]
            top_right    = vertices[1]
            bottom_right = vertices[2]
            bottom_left  = vertices[3]
       """
        
        
        for i in range(len(bottom_right_vectors)):
            if self.in_bounds(grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_str(self.sprite_column, grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1], self.z_layer)
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    
                    if i == 0: #East
                        n_bottom_left  = vertices[3]
                        bottom_right = n_bottom_left
                    elif i == 1: #South East
                        n_top_left = vertices[0]
                        bottom_right = n_top_left
                    elif i == 2: #South
                        n_top_right    = vertices[1]
                        bottom_right = n_top_right

                    print("resusing bottom right")
                    reuse_bottom_right = True
                    break

                    

        #for i in range(len(bottom_left_vectors)):
            if self.in_bounds(grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_str(self.sprite_column, grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1], self.z_layer)
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    if i == 0: #West
                        n_bottom_right = vertices[2]
                        bottom_left = n_bottom_right
                    elif i == 1: #South West
                        n_top_right    = vertices[1]
                        bottom_left = n_top_right
                    elif i == 2: #South
                        n_top_left     = vertices[0]
                        bottom_left = n_top_left

                    print("resuing bottom left")
                    reuse_bottom_left = True
                    

                    
        
        #for i in range(len(top_left_vectors)):
            if self.in_bounds(grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_str(self.sprite_column, grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1], self.z_layer)
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    if i == 0: #North
                        n_bottom_left  = vertices[3]
                        top_left = n_bottom_left
                    elif i == 1: #North West
                        n_bottom_right = vertices[2]
                        top_left = n_bottom_right
                    elif i == 2: #West
                        n_top_right    = vertices[1]
                        top_left = n_top_right

                    print("resuing top left")
                    reuse_top_left = True
                    
                    
                    
        #for i in range(len(top_right_vectors)):
            if self.in_bounds(grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_str(self.sprite_column, grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1], self.z_layer)
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]

                    if i == 0: #North
                        n_bottom_right  = vertices[2]
                        top_right = n_bottom_right
                    elif i == 1: #North East
                        n_bottom_left = vertices[3]
                        top_right = n_bottom_left
                    elif i == 2: #East
                        n_top_left     = vertices[0]
                        top_right = n_top_left
                    print("reusing top right")
                    reuse_top_right = True
                    

        
        if is_erasing == False:
            print("nah")
            if not reuse_top_right:
                top_right.set_coords(right_top[0], right_top[1])

            if not reuse_bottom_right:  
                bottom_right.set_coords(right_bottom[0], right_bottom[1])

            if not reuse_bottom_left:
                bottom_left.set_coords(left_bottom[0], left_bottom[1])

            if not reuse_top_left:
                top_left.set_coords(left_top[0], left_top[1])



            if bottom_left not in  self.pixel_vertices:
                self.pixel_vertices.append(bottom_left)

            if bottom_right not in self.pixel_vertices:
                self.pixel_vertices.append(bottom_right)

            if top_left not in self.pixel_vertices:
                self.pixel_vertices.append(top_left)

            if top_right not in  self.pixel_vertices:
                self.pixel_vertices.append(top_right)
        else:
            #The Vertices of CC that should be deleted if "is_erasing" is selected
            #lone vertices that aren't connected to others should be deleted
            key_coord = self.coord_str(self.sprite_column, self.sprite_column, grid_x, grid_y, self.z_layer)
            cc_vertices = self.pixel_coords[key_coord]
            if cc_vertices:
                print('yep')
                top_left_vertex = cc_vertices[0]
                top_right_vertex = cc_vertices[1]
                bottom_right_vertex = cc_vertices[2]
                bottom_left_vertex = cc_vertices[3]
                #remove a vertex if it has no neighbors
                if str(top_right_vertex) == str(top_right):
                    #if top_right in self.pixel_vertices:
                        self.pixel_vertices.remove(top_right_vertex)

                if str(bottom_right_vertex) == str(bottom_right):
                    #if bottom_right in self.pixel_vertices:
                        self.pixel_vertices.remove(bottom_right_vertex)

                if str(bottom_left_vertex) == str(bottom_left):
                    #if bottom_left in self.pixel_vertices:
                        self.pixel_vertices.remove(bottom_left_vertex)

                if str(top_right_vertex) == str(top_left):
                    #if top_left in self.pixel_vertices:
                        self.pixel_vertices.remove(top_left_vertex)

        
            

        

       
        
        return top_left, top_right, bottom_right, bottom_left  

    def paint_pixel(self, mouse_x, mouse_y, canvas_width, canvas_height, angle, scaling, canvas, color, is_erasing):
    
        canvas.delete("lines")
        
        #Mouse Color start ##############################
        if False:
            #top line
            canvas.create_line(
                mouse_x, mouse_y,
                mouse_x + math.cos(-self.degrees_to_radians(90 - angle)) * canvas_width, mouse_y + math.sin(self.degrees_to_radians(90 - angle)) * canvas_height, 
                fill = "red",
                tags="lines"
            )
            
            #left line
            canvas.create_line(
                mouse_x, mouse_y,
                mouse_x + math.cos(self.degrees_to_radians(-angle)) * canvas_width, mouse_y + math.sin(self.degrees_to_radians(-angle)) * canvas_height, 
                fill = "green",
                tags="lines"
            )
        #Mouse Color end ##############################

        intersect_x = line_line_intersection(
            #current point
            mouse_x, mouse_y,
            #directly above the point at starting degrees
            mouse_x + math.cos(-self.degrees_to_radians(90 - angle)) * canvas_width, mouse_y + math.sin(self.degrees_to_radians(90 - angle)) * canvas_height, 
            #top left of drawable area at starting degrees

            self.top_left.get_X(), self.top_left.get_Y(),
            #top right
         
            self.top_right.get_X(), self.top_right.get_Y()
        )

        intersect_y = line_line_intersection(
            #current point
            mouse_x, mouse_y,
            #directly to the left of point at starting degrees
            mouse_x + math.cos(self.degrees_to_radians(-angle)) * canvas_width, mouse_y + math.sin(self.degrees_to_radians(-angle)) * canvas_height, 
            #top left of drawable area at starting degrees
            self.top_left.get_X(), self.top_left.get_Y(),
            #bottom left
            self.bottom_left.get_X(), self.bottom_left.get_Y(),
        )

        #print(intersect_x, intersect_y)
        #the current x, y mouse position is the bottom right, 
        #intersection_x  the top right
        #intersection_y the bottom left, 
        #the first and second index of the pixel sheet being the top left
        #together these make a rectangle that takes of different fractions of the area of the current size of the pixel sheet
        #this fraction is used to calculate the grid area

        distance_x = math.sqrt((intersect_x[0] - self.top_left.get_X()) ** 2 + (intersect_x[1] - self.top_left.get_Y()) ** 2)
        distance_y = math.sqrt((intersect_y[0] - self.top_left.get_X()) ** 2 + (intersect_y[1] - self.top_left.get_Y()) ** 2)
        max_distance_x = (self.pixel_canvas_width * scaling)
        max_distance_y = (self.pixel_canvas_height * scaling) 

        #pixel grid coords
        grid_x = math.floor((distance_x/max_distance_x) * self.pixel_canvas_width)
        grid_y = math.floor((distance_y/max_distance_y) * self.pixel_canvas_height)

        self.grid_x = grid_x
        self.grid_y = grid_y

        col_X2, col_Y2 = self.DDA_raycast(self.top_left.get_X(), self.top_left.get_Y(), self.degrees_to_radians(180 - angle), (grid_x + 1) * scaling)
        col_X1, col_Y1 = self.DDA_raycast(self.top_left.get_X(), self.top_left.get_Y(), self.degrees_to_radians(180 - angle), grid_x * scaling)
        row_X2, row_Y2 = self.DDA_raycast(self.top_left.get_X(), self.top_left.get_Y(), self.degrees_to_radians(270 -  angle), (grid_y + 1) * scaling)
        row_X1, row_Y1 = self.DDA_raycast(self.top_left.get_X(), self.top_left.get_Y(), self.degrees_to_radians(270 -  angle), grid_y * scaling)

        #polygon vertices 
        top_left_x, top_left_y = self.DDA_raycast(col_X1, col_Y1, self.degrees_to_radians(270 - angle), (grid_y) * scaling)
        bottom_right_x, bottom_right_y = self.DDA_raycast(col_X2, col_Y2, self.degrees_to_radians(270 - angle), (grid_y + 1) * scaling)
        top_right_x, top_right_y  = self.DDA_raycast(row_X1, row_Y1, self.degrees_to_radians(180 - angle), (grid_x + 1) * scaling)
        bottom_left_x, bottom_left_y = self.DDA_raycast(row_X2, row_Y2, self.degrees_to_radians(180 - angle), (grid_x) * scaling)

        #
        if True:
            #Row and Column Tracker
            canvas.create_line(
                #top left
                self.top_left.get_X(), self.top_left.get_Y(),
                col_X2, col_Y2, 
                fill = "yellow",
                tags="lines"
            )

        
        
            canvas.create_line(
                    #top left
                    self.top_left.get_X(), self.top_left.get_Y(),
                    col_X1, col_Y1, 
                    fill = "cyan",
                    tags="lines"
                )
            
            
            
            
            canvas.create_line(
                    #top left
                    self.top_left.get_X(), self.top_left.get_Y(),
                    row_X2, row_Y2, 
                    fill = "cyan",
                    tags="lines"
                )
            
            
            
            canvas.create_line(
                    #top left
                    self.top_left.get_X(), self.top_left.get_Y(),
                    row_X1, row_Y1, 
                    fill = "yellow",
                    tags="lines"
                )

        
            #Polygon Vertex maker

            
           
            
            #top left 
            canvas.create_line(
                    col_X1, col_Y1,
                    top_left_x, top_left_y, 
                    fill = "cyan",
                    tags="lines"
                )
            
            #bottom right
            canvas.create_line(
                    col_X2, col_Y2,
                    bottom_right_x, bottom_right_y, 
                    fill = "magenta",
                    tags="lines"
                )


            
            #top right
            canvas.create_line(
                    row_X1, row_Y1,
                    top_right_x, top_right_y, 
                    fill = "white",
                    tags="lines"
                )

            #bottom left
            canvas.create_line(
                    row_X2, row_Y2,
                    bottom_left_x, bottom_left_y, 
                    fill = "yellow",
                    tags="lines"
                )
       
        self.pixel_grid[grid_y][grid_x] = color
        key_coord = self.coord_str(self.sprite_column, grid_x, grid_y, self.z_layer)


            
        if not is_erasing:
            self.pixel_coords[key_coord] = [
                                            Vertex(top_left_x, top_left_y),
                                            Vertex(top_right_x, top_right_y),
                                            Vertex(bottom_right_x, bottom_right_y),
                                            Vertex(bottom_left_x, bottom_left_y)
                                        ]
        else:
            self.pixel_coords[key_coord] = []

        '''
        if not is_erasing:
            top_left, top_right, bottom_right, bottom_left  = self.recycle_vertices(
                                grid_x, grid_y, 
                                (top_left_x, top_left_y),
                                (top_right_x, top_right_y),
                                (bottom_right_x, bottom_right_y),
                                (bottom_left_x, bottom_left_y),
                                is_erasing
                                )
            

            self.pixel_coords[key_coord] = [
                                            top_left, top_right, bottom_right, bottom_left
                                        ]
            

        else:


            
            top_left, top_right, bottom_right, bottom_left  = self.recycle_vertices(
                                grid_x, grid_y, 
                                (top_left_x, top_left_y),
                                (top_right_x, top_right_y),
                                (bottom_right_x, bottom_right_y),
                                (bottom_left_x, bottom_left_y),
                                is_erasing
                                )
            self.pixel_coords[key_coord] = []
        '''        
        
        '''
        self.canvas.create_polygon(polygon,
                                    #fill = self.selected_color,
                                    outline="silver",
                                    tags=("lines")
                                    )
        '''




class MainCanvas(ttk.Frame):
    def __init__(self, parent, c_dimension, p_width, p_height, p_layers, *args, **kwargs):
        super().__init__(parent)

        
 
        self.sprite_sheet = []
        


        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        self.pixel_canvas_layers = p_layers

        self.pixel_scale = 0
        self.max_pixel_scale = 0
        self.min_pixel_scale = 1
        

        self.focus_grid_color = "purple"
        self.canvas_bg_color = 'gray'
        self.canvas = tk.Canvas(self, width=c_dimension, height=c_dimension, bg=self.canvas_bg_color) 

        self.sub_wn = None
        
        self.pivot_matrix = array(
            translation_matrix2D(0, 0), dtype=float64
        )

        self.matrix_pivot = array(
            translation_matrix2D(0, 0), dtype=float64
        )


        #the rest of the area iis space for rotations

        # x, y of last pixel
        self.last_pixel = []

        
        



        
        #for key in self.pixel_coords:
        #    print(key, list(map(str, self.pixel_coords[key])))
       
             

        #print(len(self.pixel_grid))
        #self.display_2d(self.pixel_grid)

        self.color_button = ttk.Button(self, text="Change Color", command=self.choose_color)
        self.clear_button = ttk.Button(self, text="Clear Sheet", command=self.clear)
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.data_buttom = ttk.Button(self, text="Console Data", command=self.display_data)
        self.import_button = ttk.Button(self, text="Import", command=self.image_import)
        self.cadd_button = ttk.Button(self, text="C+", command=self.create_sprite_stack)
        self.csub_button = ttk.Button(self, text="C-", command=None)
        self.radd_button = ttk.Button(self, text="R+", command=self.create_sprite_layer)
        self.rsub_button = ttk.Button(self, text="R-", command=None)

        self.angle = 180
        self.rotation_label = tk.Label(self, text="Rotation")
        self.rotation_angle = tk.IntVar()
        self.rotation_slider = tk.Scale(
            self,
            variable=self.rotation_angle,
            from_ = 0,
            to = 360,
            orient = "horizontal",
            length=c_dimension,
            command = self.rotate_sprite_stack
        )
        self.rotation_angle.set(self.angle)
        
        self.sheet_row = 0
        self.row_lbl = tk.Label(self, text="Row")
        self.row_iv = tk.IntVar(value=self.sheet_row)
        self.row_scl = tk.Scale(
            self,
            variable=self.row_iv,
            from_ = 0,
            to = self.pixel_canvas_layers - 1,
            orient = "vertical",
            length=c_dimension,
            command = self.cell_select
        )

        self.sheet_col = 0
        self.col_lbl = tk.Label(self, text="Column")
        self.col_iv = tk.IntVar(value=self.sheet_col)
        self.col_scl = tk.Scale(
            self,
            variable=self.col_iv,
            from_ = 0,
            to = 0,
            orient = "vertical",
            length=c_dimension,
            command = self.cell_select
        )

        self.sheet_spacing = 0
        self.spacing_label = tk.Label(self, text="Spacing")
        self.spacing = tk.IntVar(value=self.sheet_spacing)
        self.spacing_slider = tk.Scale(
            self,
            variable=self.spacing,
            from_ = 0,
            to = self.pixel_canvas_height,
            orient = "vertical",
            length=c_dimension,
            command = self.space_sprite_stack
        )


        self.translation_lbl = tk.Label(self, text="Move")
        self.translation = 0
        self.movement = tk.IntVar(value=self.translation)
        self.translate_scl = tk.Scale(
            self,
            variable = self.movement,
            from_ = -1000,
            to = 1000,
            #increment= 1,
            #width=10,
            #state="readonly",
            orient = "vertical",
            length=c_dimension,
            command = self.translate_y_stack
        )

        self.translate_scl.set(self.translation)

        self.translate0_btn = ttk.Button(
            self,
            text = "Reset Move",
            command= self.translate_reset
        )

       
     

        self.settings_cbv = tk.IntVar()
        self.settings_cbv.set(0)
        self.settings_cb = tk.Checkbutton(self, text = "Settings",
                                                    variable=self.settings_cbv,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=self.display_settings)


        #Visibility Radiobuttons
        self.visible_grid_cbv = tk.IntVar()
        self.visible_grid_cbv.set(0)
        self.visible_grid_cb = tk.Checkbutton(self, text = "Grid Visibility",
                                                    variable=self.visible_grid_cbv,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=None)
        
            
        self.visible_layer_cbv = tk.IntVar()
        self.visible_layer_cbv.set(0)
        self.visible_layer_cb = tk.Checkbutton(self, text = "Layer Visibility",
                                                    variable=self.visible_layer_cbv,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=None)
        
        self.visible_borders_cbv = tk.IntVar()
        self.visible_borders_cbv.set(0)
        self.visible_borders_cb = tk.Checkbutton(self, text = "Border Visibility",
                                                    variable=self.visible_borders_cbv,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=None)
        
        self.visible_cell_cbv = tk.IntVar()
        self.visible_cell_cbv.set(0)
        self.visible_cell_cb = tk.Checkbutton(self, text = "Cell Visibility",
                                                    variable=self.visible_cell_cbv,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=None)
        
        self.setting_rb_widgets = []
        
        self.brush_size = 0
        self.selected_color = "#000000" #"black" 
        #print(self.hex_to_rbg(self.selected_color))
        
        arrangement = [
                #[None                , None                , None                , None               ]
                [None                , self.row_lbl        , self.col_lbl        , self.spacing_label      , self.translation_lbl    ],
                [self.canvas         , self.row_scl        , self.col_scl        , self.spacing_slider     , self.translate_scl      ],
                [self.rotation_label , None                , None                , self.translate0_btn     , None                    ],
                [self.rotation_slider, self.color_button   , self.clear_button   , self.settings_cb        , None                    ],
                [None                , self.save_button    , self.data_buttom    , self.visible_borders_cb , None                    ], 
                [None                , self.import_button  , None                , self.visible_layer_cb   , None                    ],
                [None                , self.cadd_button     , self.csub_button   , None                    , None                    ],
                [None                , self.radd_button     , self.rsub_button   , None                    , None                    ]
        ]

        arrange_widgets(arrangement)
        



        self.canvas.bind("<B1-Motion>", self.draw) 
        self.canvas.bind("<B3-Motion>", self.erase) 
        
        self.canvas.bind("<ButtonPress-1>", self.draw)
        self.canvas.bind("<ButtonPress-3>", self.erase) 

        self.canvas.bind("<MouseWheel>", self.scale_sprite_stack)
        
        

        self.init_sprite_stack(c_dimension)

    def prepare_transforms(self):
        self.rotation_slider.set(180)
        prev_angle = self.angle
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)
        transform_matrix = array(rotation_matrix2D(angle_change))
        self.apply_stack_transformations(transform_matrix, False, True, False, False, False)

        
        prev_spacing = self.sheet_spacing
        max_spacing = int(self.spacing_slider["to"])
        
        self.spacing_slider.set(max_spacing)
        self.sheet_spacing = self.spacing_slider.get()
        
        sign = prev_spacing - max_spacing
        spacing_change = sign * self.pixel_scale #* (self.pixel_canvas_height/self.pixel_canvas_layers)
        #0, (self.sheet_row - i)  * spacing_change, x, y
        transform_matrix = array(translation_matrix2D(0, spacing_change))
        self.apply_stack_transformations(transform_matrix, False, False, True, False, False)

        

    def init_sprite_stack(self,c_dimension):
        
        #rectangle diagonal
        #these exists so pixels are always square
        diagonal = math.sqrt(self.pixel_canvas_width ** 2 + self.pixel_canvas_height ** 2)
        ratio_x = (self.pixel_canvas_width/diagonal) 
        ratio_y = (self.pixel_canvas_height/diagonal)
        column = []

        for z in range(self.pixel_canvas_layers):
            
            
            #(c_dimension - current_sheet)/2
            
            #top left
            x0 = (c_dimension * (1 - ratio_x)/2) 
            y0 = (c_dimension * (1 - ratio_x)/2)  #self.pixel_scale * z
            #bottom left
            x1 = x0 
            y1 = y0 + c_dimension * ratio_y
            #bottom right
            x2 = x0 + c_dimension * ratio_x
            y2 = y0 + c_dimension * ratio_y
            #top right
            x3 = x0 + c_dimension * ratio_x
            y3 = y0 

        
            sheet = [
                #x, y, x, y, x etc
                x0, y0,
                x1, y1,
                x2, y2,
                x3, y3,

            ]

            sheet = Sheet(sheet, self.pixel_canvas_width, self.pixel_canvas_height)
            sheet.z_layer = z
            sheet.sprite_column = 0
            drawable_x = x2 - x0
            drawable_y = y2 - y0
            
            x_start = x0 
            y_start = y0
            x_space = (drawable_x/self.pixel_canvas_width) 
            y_space = (drawable_y/self.pixel_canvas_height) 

            if z < 1:
                #print("spacing", x_space, y_space)
                self.pixel_scale = x_space
                self.max_pixel_scale = x_space
                self.min_pixel_scale = 1
                
            
            for y in range(self.pixel_canvas_height + 1):
            
                vy = y_start + y * y_space
                if y < self.pixel_canvas_height:
                    sheet.pixel_grid.append([])

                for x in range(self.pixel_canvas_width + 1):
                    
                    vx = x_start + x * x_space
                    
                    #v = Vertex(round(vx), round(vy))
                    #vertices.append(v)
                    
                    if x < self.pixel_canvas_width:
                        if y < self.pixel_canvas_height:
                            sheet.pixel_grid[y].append(None)
                            sheet.pixel_coords.update({sheet.coord_str(sheet.sprite_column, x, y, z) : []})
                    
            column.append(sheet)
            #self.sheet_columns.append(sheet)

        self.sprite_sheet.append(column)
        #self.current_sheet = self.sheet_columns[self.sheet_row]
        self.current_sheet = self.sprite_sheet[self.sheet_col][self.sheet_row]
        self.render_stack_levels()

    def create_sprite_stack(self):
        
        
        self.prepare_transforms()

        c_dimension = 0
        ratio_x = 0
        ratio_y = 0
        #for x in range(len(self.sprite_sheet)):
        column = []
        #the row in the last sprite column
        for row in range(len(self.sprite_sheet[-1])):
            sheet = self.sprite_sheet[-1][row]
        #for z in range(self.pixel_canvas_layers):
            #last_stack = self.sprite_sheet[-1][self.sheet_row]
            '''
            self.top_left.get_X(), self.top_left.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(), self.bottom_left.get_Y(),
            self.top_right.get_X(), self.top_right.get_Y()
            '''
            #(c_dimension - current_sheet)/2
            
            #top left
            x0 = sheet.top_right.get_X()
            y0 = sheet.top_right.get_Y()
            #bottom left
            x1 = sheet.bottom_right.get_X()
            y1 = sheet.bottom_right.get_Y()
            #bottom right
            x2 = x0 + (sheet.top_right.get_X() - sheet.top_left.get_X())
            y2 = y0 + (sheet.bottom_right.get_Y() - sheet.top_right.get_Y())
            #top right
            x3 = x0 + (sheet.top_right.get_X() - sheet.top_left.get_X())
            y3 = y0 

        
            sheet = [
                #x, y, x, y, x etc
                x0, y0,
                x1, y1,
                x2, y2,
                x3, y3,

            ]

            sheet = Sheet(sheet, self.pixel_canvas_width, self.pixel_canvas_height)
            sheet.z_layer = row
            sheet.sprite_column = len(self.sprite_sheet)
            drawable_x = x2 - x0
            drawable_y = y2 - y0
            
            x_start = x0 
            y_start = y0
            x_space = (drawable_x/self.pixel_canvas_width) 
            y_space = (drawable_y/self.pixel_canvas_height) 

            if row < 1:
                #print("spacing", x_space, y_space)
                self.pixel_scale = x_space
                self.max_pixel_scale = x_space
                self.min_pixel_scale = 1
                
            
            for y in range(self.pixel_canvas_height + 1):
            
                vy = y_start + y * y_space
                if y < self.pixel_canvas_height:
                    sheet.pixel_grid.append([])

                for x in range(self.pixel_canvas_width + 1):
                    
                    vx = x_start + x * x_space
                    
                    #v = Vertex(round(vx), round(vy))
                    #vertices.append(v)
                    
                    if x < self.pixel_canvas_width:
                        if y < self.pixel_canvas_height:
                            sheet.pixel_grid[y].append(None)
                            sheet.pixel_coords.update({sheet.coord_str(sheet.sprite_column, x, y, row) : []})
                    
            column.append(sheet)
            #self.sheet_columns.append(sheet)

        self.sprite_sheet.append(column)
        
        #self.sheet_col += 1
        #self.col_iv.set(self.sheet_col)
        self.col_scl.config(to=len(self.sprite_sheet) - 1)
        self.render_stack_levels()

    def create_sprite_layer(self):
        
        self.prepare_transforms()


        c_dimension = 0
        ratio_x = 0
        ratio_y = 0
        #for x in range(len(self.sprite_sheet)):
        #column = []
        #the last rows in each sprite column 
        for col in range(len(self.sprite_sheet)):
            sheet = self.sprite_sheet[col][len(self.sprite_sheet[col]) - 1]
        
            '''
            self.top_left.get_X(), self.top_left.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(), self.bottom_left.get_Y(),
            self.top_right.get_X(), self.top_right.get_Y()
            '''
            #(c_dimension - current_sheet)/2
            
            #top left
            x0 = sheet.bottom_left.get_X()
            y0 = sheet.bottom_left.get_Y()
            #top right
            x3 = sheet.bottom_right.get_X()
            y3 = sheet.bottom_right.get_Y()
            #bottom left
            x1 = x0 + (sheet.bottom_left.get_X() - sheet.top_left.get_X())
            y1 = y0 + (sheet.bottom_right.get_Y() - sheet.top_right.get_Y())
            #bottom right
            x2 = x3 + (sheet.bottom_left.get_X() - sheet.top_left.get_X())
            y2 = y3 + (sheet.bottom_right.get_Y() - sheet.top_right.get_Y())
            

        
            sheet = [
                #x, y, x, y, x etc
                x0, y0,
                x1, y1,
                x2, y2,
                x3, y3,

            ]

            sheet = Sheet(sheet, self.pixel_canvas_width, self.pixel_canvas_height)
            sheet.z_layer = len(self.sprite_sheet[col])
            sheet.sprite_column = col
            drawable_x = x2 - x0
            drawable_y = y2 - y0
            
            x_start = x0 
            y_start = y0
            x_space = (drawable_x/self.pixel_canvas_width) 
            y_space = (drawable_y/self.pixel_canvas_height) 

            if len(self.sprite_sheet[col]) - 1 < 1:
                #print("spacing", x_space, y_space)
                self.pixel_scale = x_space
                self.max_pixel_scale = x_space
                self.min_pixel_scale = 1
                
            
            for y in range(self.pixel_canvas_height + 1):
            
                vy = y_start + y * y_space
                if y < self.pixel_canvas_height:
                    sheet.pixel_grid.append([])

                for x in range(self.pixel_canvas_width + 1):
                    
                    vx = x_start + x * x_space
                    
                    #v = Vertex(round(vx), round(vy))
                    #vertices.append(v)
                    
                    if x < self.pixel_canvas_width:
                        if y < self.pixel_canvas_height:
                            sheet.pixel_grid[y].append(None)
                            sheet.pixel_coords.update({sheet.coord_str(sheet.sprite_column, x, y, len(self.sprite_sheet[col]) - 1) : []})
                    
            self.sprite_sheet[col].append(sheet)
            #self.sheet_columns.append(sheet)

        #self.sprite_sheet.append(column)
        
        #self.sheet_col += 1
        #self.col_iv.set(self.sheet_col)
        #self.col_scl.config(to=len(self.sprite_sheet) - 1)
        self.row_scl.config(to=len(self.sprite_sheet[0]) - 1)
        self.render_stack_levels()

    def delete_sprite_layer(self):
        pass

    def delete_sprite_stack(self):
        pass

    
    def render_stack_layer(self):
        pass

    def render_stack_levels(self):
        self.canvas.delete("all")
        cur_level = self.row_iv.get()
        #self.sprite_sheet[self.sheet_col][self.sheet_row]
        for col in range(len(self.sprite_sheet)):
            for row in range(len(self.sprite_sheet[col])):
                sheet = self.sprite_sheet[col][row]
                
                for key in sheet.pixel_coords:
                        
                    vertices = sheet.pixel_coords[key]
                    
                    if vertices:
                        self.canvas.delete(key)
                        column, x_pixel, y_pixel, z_level = sheet.str_coord(key)
                        color = sheet.pixel_grid[y_pixel][x_pixel]

                        #pixel polygon vertices not sheet
                        top_left_x, top_left_y = vertices[0].get_X(), vertices[0].get_Y()
                        top_right_x, top_right_y = vertices[1].get_X(), vertices[1].get_Y()
                        bottom_right_x, bottom_right_y = vertices[2].get_X(), vertices[2].get_Y()
                        bottom_left_x, bottom_left_y = vertices[3].get_X(), vertices[3].get_Y()
                        
                        polygon = [
                                    top_left_x, top_left_y, 
                                    top_right_x, top_right_y, 
                                    bottom_right_x, bottom_right_y, 
                                    bottom_left_x, bottom_left_y
                                ]
                        #print(top_left)
                        fill = ''
                        if color != None:
                            fill = color
                        

                        '''
                        self.canvas.create_polygon(polygon,
                                                fill = fill,
                                                outline="black",
                                                tags=(key)
                                                )
                        '''

                        if row == cur_level:

                            self.canvas.create_polygon(polygon,
                                                fill = fill,
                                                outline= fill,
                                                tags=(key)
                                                )
                            
                        
                        else:
                            
                            self.canvas.create_polygon(polygon,
                                                        fill = '',
                                                        outline=fill,
                                                        tags=(key)
                                                        )
                self.canvas.create_polygon(sheet.get_borders(),
                                            fill = '',
                                            outline= "black",
                                            tags=(key)
                                            )
                        
    def apply_stack_transformations(self, transform_matrix, is_scaling, is_rotating, is_spacing, is_focusing, is_moving):
        start = time.time()

        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2


        self.pivot_matrix[0, 2] = cx
        self.pivot_matrix[1, 2] = cy

        self.matrix_pivot[0, 2] = -cx
        self.matrix_pivot[1, 2] = -cy

        if is_spacing:
            spacing_change = transform_matrix[1, 2]
        
        for col in range(len(self.sprite_sheet)):
            for row in range(len(self.sprite_sheet[col])):
                sheet = self.sprite_sheet[col][row]
                prev_sheet = sheet
                
                
                if is_scaling or is_moving:
                    pass
                elif is_spacing:
                    
                    if row != self.sheet_row:
                        transform_matrix[1, 2] = (self.sheet_row - row)  * spacing_change
                    else:
                        #tx
                        transform_matrix[0, 2] = 0
                        #ty
                        transform_matrix[1, 2] = 0

                elif is_rotating:
                    """
                    self.top_left.get_X(), self.top_left.get_Y(),
                    self.bottom_right.get_X(), self.bottom_right.get_Y(),
                    self.bottom_left.get_X(), self.bottom_left.get_Y(),
                    self.top_right.get_X(), self.top_right.get_Y()
                    """

                    #print(sheet.borders)
                    cx, cy = line_line_intersection(
                        sheet.top_left.get_X(), sheet.top_left.get_Y(),
                        sheet.bottom_right.get_X(), sheet.bottom_right.get_Y(),
                        sheet.bottom_left.get_X(), sheet.bottom_left.get_Y(),
                        sheet.top_right.get_X(), sheet.top_right.get_Y()
                        
                        
                    )

                    #print('yep')
                    '''
                    self.v[0, 0] = x
                    self.v[1, 0] = y
                    '''
                    self.pivot_matrix[0, 2] = cx
                    self.pivot_matrix[1, 2] = cy

                    self.matrix_pivot[0, 2] = -cx
                    self.matrix_pivot[1, 2] = -cy
                    
                
                elif is_focusing:
                    #if i != 0:
                    #if i != 0:
                        prev_sheet = self.sprite_sheet[col][row - 1]
                    #print("spaced")

                        cx, cy = line_line_intersection(
                            prev_sheet.top_left.get_X(), prev_sheet.top_left.get_Y(),
                            prev_sheet.bottom_right.get_X(), prev_sheet.bottom_right.get_Y(),
                            prev_sheet.bottom_left.get_X(), prev_sheet.bottom_left.get_Y(),
                            prev_sheet.top_right.get_X(), prev_sheet.top_right.get_Y()
                        ) 

                        self.pivot_matrix[0, 2] = cx
                        self.pivot_matrix[1, 2] = cy

                        self.matrix_pivot[0, 2] = -cx
                        self.matrix_pivot[1, 2] = -cy

                #if i == 0:
                    #print("Pivot Matrix", self.pivot_matrix, "\n")
                    #print(transform_matrix, "\n")
                
                
                sheet.apply_transform(self.matrix_pivot, transform_matrix,  self.pivot_matrix)

        print("Transfrom Time {}".format(time.time() - start))
            
            

        
        #self.render_other_levels()
        #self.render_selected_level()
        self.render_stack_levels()
        
    def scale_sprite_stack(self, event):


        scaling_change = 1 + (abs(event.delta)//event.delta)/10
        prev_scale = self.pixel_scale

        self.pixel_scale = self.pixel_scale * scaling_change
        if self.pixel_scale < self.min_pixel_scale:
            self.pixel_scale = prev_scale
        if self.pixel_scale >= self.max_pixel_scale:
            self.pixel_scale = prev_scale

        if prev_scale != self.pixel_scale:
            
            transform_matrix = array(scale_matrix2D(scaling_change, scaling_change))
            self.apply_stack_transformations(transform_matrix, True, False, False, False, False)
            
    def rotate_sprite_stack(self, *args):

        prev_angle = self.angle
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)

        transform_matrix = array(rotation_matrix2D(angle_change))
        self.apply_stack_transformations(transform_matrix, False, True, False, False, False)

    def space_sprite_stack(self, *args):
        prev_spacing = self.sheet_spacing
        self.sheet_spacing = self.spacing_slider.get()
        
        sign = prev_spacing - self.sheet_spacing 
        spacing_change = sign * self.pixel_scale #* (self.pixel_canvas_height/self.pixel_canvas_layers)
        #0, (self.sheet_row - i)  * spacing_change, x, y
        transform_matrix = array(translation_matrix2D(0, spacing_change))
        self.apply_stack_transformations(transform_matrix, False, False, True, False, False)

    def cell_select(self, *args):
        #prev_level = self.sheet_row
        self.sheet_row = self.row_scl.get()
        self.sheet_col = self.col_scl.get()
        #if self.sheet_spacing != 0:
        self.current_sheet = self.sprite_sheet[self.sheet_col][self.sheet_row]
        #sign = prev_level - self.sheet_row 
        #focus_change = sign * self.pixel_scale * (self.pixel_canvas_height/self.pixel_canvas_layers)

        

        #transform_matrix = array(translation_matrix2D(0, focus_change))
        #self.apply_stack_transformations(transform_matrix, False, False, True, False, False)

    def translate_y_stack(self, *args):
        prev_translation = self.translation
        self.translation = self.translate_scl.get()

        #sign = last_translation 
        movement_change = (prev_translation - self.translation) #* (self.pixel_scale * self.pixel_canvas_height)
        transform_matrix = array(translation_matrix2D(0, movement_change))
        self.apply_stack_transformations(transform_matrix, False, False, False, False, True)

    def translate_reset(self, *args):
        #self.translate_scl.set(0)
        self.movement.set(0)
        self.translation = 0
        
    def display_1d(self, arr):
        s = ""
        for i in range(len(arr)):
            #for j in range(len(arr2d[i])):
            s = s + str(arr[i]) + " "
            #s = s + '\n'
        print(s)    
    
    def display_2d(self, arr2d):
        s = ""
        for y in range(len(arr2d)):
            for x in range(len(arr2d[y])):
                s = s + str(arr2d[y][x]) + " "
            s = s + '\n'
        print(s)

    def hex_to_rbg(self, hex_color):
        hex_color = hex_color.lstrip('#')
        arr = []
        for i in (0, 2, 4):
            arr.append(int(hex_color[i:i+2], 16))
        #alpha value
        arr.append(255)
        return arr

    def wn_open(self, window):
        #https://stackoverflow.com/questions/76940339/is-there-a-way-to-check-if-a-window-is-open-in-tkinter
        # window has been created an exists, so don't create again.
        return window is not None and window.winfo_exists()

    def draw_canvas_divisions(self, canvas, canvas_size:int, h_divisions:int, v_divisions:int, ratio_h, ratio_v):
        
        if h_divisions > 0:
            canvas.delete("h_lines")
            size = round(canvas_size * ratio_v)
            step = math.floor(size/h_divisions)
            
            for i in range(0, size, step + 1):
                canvas.create_line(
                    0, i,
                    canvas_size * ratio_h, i,
                    tags=("h_lines")
                )

        if v_divisions > 0:
            canvas.delete("v_lines")
            size = round(canvas_size * ratio_h)
            step = math.floor(size/v_divisions)
            for i in range(0, size, step + 1):
                canvas.create_line(
                    i, 0,
                    i, canvas_size * ratio_v,
                    tags=("v_lines")
                )
        

    def image_import(self):
        if self.wn_open(self.sub_wn):
            return

        filetypes = [
                    #("All files", "*.*"),
                    ("png files", "*.png"),
                    ("jpg files", ".jpg .jpeg"),
                    
                    ]
        

        file_path = filedialog.askopenfilename(
                                    initialdir = os.getcwd(),
                                    defaultextension = ".png",
                                    title="Import Image",
                                    filetypes= filetypes                   
                                    ) 
        
        if file_path:
            
            file_path = path_correction(file_path)
            
            # Open the image
            img = Image.open(file_path)
            img = img.convert("RGBA")
            # Get image dimensions
            im_width, im_height = img.size
            # Access pixel data
            #pixels = image.load()
            
            
            

            #Pop up Window
            self.sub_wn = Toplevel()
            self.sub_wn.resizable(False, False)
            #above tkinter windows
            self.sub_wn.lift()
            self.sub_wn.title("Image Splitter") 

            canvas_size = 500
            mx_dim = max(im_width, im_height)
            scale_dim = canvas_size/mx_dim

            ratio_x = im_width/mx_dim
            ratio_y = im_height/mx_dim
            
            scaled_img = img.resize((round(scale_dim * im_width), round(scale_dim * im_height)),  Image.Resampling.NEAREST)
            display_img = ImageTk.PhotoImage(scaled_img)
            og_img = ImageTk.PhotoImage(img)
            

            display_canvas = tk.Canvas(self.sub_wn, width=canvas_size, height=canvas_size, bg=self.canvas_bg_color) 
            display_canvas.create_image(
                0, 0,                    # Image display position (top-left coordinate)
                anchor='nw',             # Anchor, top-left is the origin
                image=display_img        # Display image data
            )

            horizontal_label =  ttk.Label(self.sub_wn, text="Horizontal Splits", anchor="center")
            horizontal_iv = tk.IntVar(value=0)
            horizontal_slider = tk.Scale(
                self.sub_wn,
                variable= horizontal_iv,
                from_ = 1,
                to = im_height,
                orient = "horizontal",
                #length=50,
                command = lambda _ :self.draw_canvas_divisions(
                    display_canvas,
                    canvas_size,
                    horizontal_iv.get(),
                    0,
                    ratio_x,
                    ratio_y
                )
            )

            vertical_label =  ttk.Label(self.sub_wn, text="Vertical Splits", anchor="center")
            vertical_iv = tk.IntVar(value=0)
            vertical_slider = tk.Scale(
                self.sub_wn,
                variable= vertical_iv,
                from_ = 1,
                to = im_width,
                orient = "horizontal",
                #length=50,
                command = lambda _ :self.draw_canvas_divisions(
                    display_canvas,
                    canvas_size,
                    0,
                    vertical_iv.get(),
                    ratio_x,
                    ratio_y
                )
            )


            arrangement = [
                [display_canvas, None           ],
                [horizontal_label, None ],
                [horizontal_slider, None],
                [vertical_label, None ],
                [vertical_slider, None]
            ]

            arrange_widgets(arrangement)

            self.sub_wn.mainloop()

            '''
            # Iterate through pixels
            for x in range(width):
                for y in range(height):
                    # Access pixel value
                    r, g, b, a = pixels[x, y]

                    # Modify pixel value (example: invert colors)
                    pixels[x, y] = (255 - r, 255 - g, 255 - b,  a)
            #finish this
            # Save the modified image
            #image.save("modified_image.png")
            '''


    def save(self):

        
        filetypes = [
                    #("All files", "*.*"),
                    ("png files", "*.png"),
                    
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        
        if save_path:
            full_grid = []
            pixel_rows = []
            tot_rows = int(self.row_scl["to"] + 1)
            tot_cols = int(self.col_scl["to"] + 1)
            vertical_cells = self.current_sheet.pixel_canvas_height * tot_rows
            grid_pixel =  [[] for i in range(vertical_cells)]
           
            
            for col in range(len(self.sprite_sheet)):
                i = 0
                for row in range(len(self.sprite_sheet[col])):
                    sheet = self.sprite_sheet[col][row]
                    coords = sheet.pixel_grid

                    
                    for x in range(len(coords)):
                        
                        
                        for y in range(len(coords[col])):
                            
                                

                            #rgba
                            #each in rgb alpha
                            #grid_pixel[i].append(coords[r][c])
                            
                            if coords[x][y] != None:
                                
                                grid_pixel[i].append(self.hex_to_rbg(coords[x][y]))
                            else:
                                grid_pixel[i].append([255, 255, 255, 0])
                            
                        i +=  1
            
            
            
            #self.current_sheet.display_2d(grid_pixel)
            #self.display_2d(grid_pixel)
            #print(grid_pixel)
            
            im = array(grid_pixel, dtype= uint8)
            im = Image.fromarray(im , 'RGBA')
            im.save(save_path)
            
                           
    def choose_color(self):
        print("pixel grid")
        self.display_2d(self.current_sheet.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        print(color_code)
        if color_code[1]:
            self.selected_color = color_code[1]
    
    def display_data(self):
        print("Data")
        
        #self.current_sheet.print_data()
        
        print(self.selected_color)
        for col in range(len(self.sprite_sheet)):
            for row in range(len(self.sprite_sheet[col])):
                sheet = self.sprite_sheet[col][row]
                sheet.print_data()

    def checkbutton_on(self, cb, cbv):
        return cbv.get() == cb.cget("onvalue")

    def display_settings(self):
        if self.checkbutton_on(self.settings_cb, self.settings_cbv):
        #self.settings_cbv.get() == self.settings_cb.cget("onvalue"):
            print("yea")

        else:
            print("no")


    def clear(self):
        #only clears selected sheet
        self.current_sheet.pixel_vertices = []
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_width):
                key_coord = self.current_sheet.coord_str(self.current_sheet.sprite_column, x, y, self.row_iv.get())
                self.canvas.delete(key_coord)
                
                self.current_sheet.pixel_coords[key_coord] = []
                self.current_sheet.pixel_grid[y][x] = None
               
        #self.canvas.delete('all')
        self.last_pixel = None
    
    
    def erase(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.current_sheet.get_borders(), x, y):
            #print('yep')
            self.current_sheet.paint_pixel(x, y, canvas_width, canvas_height, -self.angle, self.pixel_scale, self.canvas, self.canvas_bg_color, True)
            self.render_stack_levels()

    '''
    def erase_drag(self, event):

        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        


        #if self.last_pixel:
            
        between = self.DDA(x, y, self.last_pixel[0], self.last_pixel[1])
        #print(between)
        self.last_pixel.clear()
        self.last_pixel = [x, y]

            
        if len(between) >= 2:
            while between:
                point = between.pop()
                px = point[0]
                py = point[1]
                for key in self.pixel_coords:
                    column, x_pixel, y_pixel, z_level = self.str_coord(key)

                    #if self.pixel_grid[y_pixel][x_pixel] == None:
                    #    break

                    vertices = self.pixel_coords[key]
                
                    top_left  = vertices[0]
                    top_right  = vertices[1]
                    bottom_right = vertices[2]
                    bottom_left = vertices[3]
                    polygon = [
                                top_left.x, top_left.y, 
                                top_right.x, top_right.y,
                                bottom_right.x, bottom_right.y,
                                bottom_left.x, bottom_left.y
                            ]
                    if polygon_point(polygon, px, py):
                        self.pixel_grid[y_pixel][x_pixel] = None
                        #self.pixel_coords[current_coord] = True
                        #self.display_2d(self.pixel_grid)

                        self.canvas.create_polygon(polygon,
                                                    fill = '',
                                                    outline='',
                                                    tags=(key)
                                                    )
                        #self.canvas.update_idletasks()
                        break
    '''
                     
    def draw_drag(self, event): 
        

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if polygon_point(self.current_sheet.get_borders(), x, y):
            #print('yep')
            cur_level = self.row_iv.get()
            self.current_sheet.paint_pixel(x, y, canvas_width, canvas_height, -self.angle, self.pixel_scale, self.canvas, self.selected_color, False)
            key_coord = self.coord_str(self.current_sheet.sprite_column, self.current_sheet.grid_x, self.current_sheet.grid_y, cur_level)
                    
                
            #print("drag", self.last_pixel[0], self.last_pixel[1], grid_x, grid_y)
            
            if self.current_sheet.grid_x != self.last_pixel[0] and self.current_sheet.grid_y != self.last_pixel[1]:
                     
                between = self.current_sheet.DDA(self.last_pixel[0], self.last_pixel[1], self.current_sheet.grid_x, self.current_sheet.grid_y)
                #coord_keys = [self.coord_str(coord[0], coord[1], cur_level) for coord in between]
                #print(between)
                for i in range(len(between)):
                    
                    x_pixel, y_pixel = between[i]
                    key_coord = self.current_sheet.coord_str(self.current_sheet.sprite_column, between[i][0], between[i][1], cur_level)
                    vertices = self.current_sheet.pixel_coords[key_coord]
                    top_left  = vertices[0]
                    top_right  = vertices[1]
                    bottom_right = vertices[2]
                    bottom_left = vertices[3]
                    polygon = [
                                top_left.x, top_left.y, 
                                top_right.x, top_right.y,
                                bottom_right.x, bottom_right.y,
                                bottom_left.x, bottom_left.y
                            ]
                    
                    self.current_sheet.pixel_grid[y_pixel][x_pixel] = self.selected_color
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = self.selected_color,
                                                outline=self.selected_color,
                                                tags=(key_coord)
                                                )

                #print(between)
                self.render_stack_levels()
                self.last_pixel = [self.current_sheet.grid_x, self.current_sheet.grid_y]
           
    def _draw(self, event): 
        #individual sheet drawing
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.current_sheet.get_borders(), x, y):
            #print('yep')
            self.current_sheet.paint_pixel(x, y, canvas_width, canvas_height, -self.angle, self.pixel_scale, self.canvas, self.selected_color, False)
            self.render_stack_levels()
            if not self.last_pixel:
                self.last_pixel = [self.current_sheet.grid_x, self.current_sheet.grid_y]

    def draw(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        for col in range(len(self.sprite_sheet)):
            for row in range(len(self.sprite_sheet[col])):
                sheet = self.sprite_sheet[col][row]
                if polygon_point(sheet.get_borders(), x, y):
                    #print('yep')
                    sheet.paint_pixel(x, y, canvas_width, canvas_height, -self.angle, self.pixel_scale, self.canvas, self.selected_color, False)
                    self.render_stack_levels()
                    if not self.last_pixel:
                        self.last_pixel = [sheet.grid_x, sheet.grid_y]
            
    
    
        
class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Stack-A-Sprite") 

        #pixel width, height, and sheet layers
        self.mn_canvas = MainCanvas(self, 512, 4, 4, 1)
        self.mn_canvas.grid()
        
if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    app.resizable()
    app.mainloop()
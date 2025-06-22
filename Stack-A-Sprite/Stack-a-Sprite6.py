import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
#from numpy import eye, dot, linalg, array, uint8
from numpy import array, uint8,  dot, float64
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


        
class PaletteFrame(Toplevel):
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
        #self.v[2, 0] = 1

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
        XnY =dot(matrix_translation, dot(transform_matrix, dot(translation_matrix, self.v)))
        #print('nump')
        #print(XnY)
        self.set_coords(XnY[0 ,0], XnY[1, 0])


    
    

    
class Sheet():
    def __init__(self, vertices, x_divisions, y_divisions, c_width, c_height) :
        '''
        0 - Sheet is an array containing a layer's the drawable area
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
        self.vertices = []
        self.z_layer = 0

        self.pixel_canvas_width = x_divisions
        self.pixel_canvas_height = y_divisions

   
    def apply_transform(self, translation_matrix, transform_matrix, matrix_translation):
        #each of the matrices/arrays should be numpy arrays
        #map(self.multi_transform, transform_matrix, translation_matrix, matrix_translation)
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

    def coord_str(self, x, y, z):
        return str(x) + '-' + str(y) + '-' + str(z)
    
    def str_coord(self, string):
        if '-' in string:
            x, y, z = map(int, string.split('-'))
            return x, y, z
        return 0, 0, 0

    def in_bounds(self, grid_x, grid_y, grid_w, grid_h):
        return 0 <= grid_x < grid_w and 0 <= grid_y < grid_h 

    def degrees_to_radians(self, deg):
        return to_radians(deg) #(deg * math.pi)/180

    def get_vertices(self, np_arr):
        pass

    def get_borders(self):
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]
   
    def _get_vertices(self, grid_x, grid_y, itr, ibr, ibl, itl):
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

        top_left  = Vertex(-1, -1)  #Vertex(itl[0], itl[1])
        top_right  = Vertex(-1, -1) #Vertex(itr[0], itr[1])
        bottom_right = Vertex(-1, -1) #Vertex(ibr[0], ibr[1])
        bottom_left = Vertex(-1, -1) #Vertex(ibl[0], ibl[1])


        has_top_left = False
        has_top_right = False
        has_bottom_right = False
        has_bottom_left = False

        #[N,NE,E,SE,S,SW,W,NW]
        #possible directions
        #8 direction
        x_vectors = [0,1,1,1,0,-1,-1,-1]
        y_vectors = [-1,-1,0,1,1,1,0,-1]


        #
        n_pos  = Vertex(grid_x + x_vectors[0], grid_y + y_vectors[0])
        ne_pos = Vertex(grid_x + x_vectors[1], grid_y + y_vectors[1])
        e_pos  = Vertex(grid_x + x_vectors[2], grid_y + y_vectors[2])
        se_pos = Vertex(grid_x + x_vectors[3], grid_y + y_vectors[3])
        s_pos  = Vertex(grid_x + x_vectors[4], grid_y + y_vectors[4])
        sw_pos = Vertex(grid_x + x_vectors[5], grid_y + y_vectors[5])
        w_pos  = Vertex(grid_x + x_vectors[6], grid_y + y_vectors[6])
        nw_pos = Vertex(grid_x + x_vectors[7], grid_y + y_vectors[7])
        
        #N and NE 
        #N's bottom left and bottom right is current cell's top left and top right
        #NE's bottom left is current cell's top right
        if self.in_bounds(n_pos.x, n_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(n_pos.x, n_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                top_left = n_bottom_left
                top_right = n_bottom_right
                has_top_left = True
                has_top_right = True
                #print("yep north")


        if self.in_bounds(ne_pos.x, ne_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(ne_pos.x, ne_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                top_right = n_bottom_left
                has_top_right = True
                #print("yep north east")

        
        if not has_top_right:
            if itr:

                top_right.x = itr[0]
                top_right.y = itr[1]

            else:
                top_right.x = self.pixel_top[grid_x][0]
                top_right.y = self.pixel_top[grid_x][1]

            
                
            #top_right  = Vertex(itr[0], itr[1])
            #print("yeah top right")
        if top_right not in  self.pixel_mesh[self.level.get()]:
            self.pixel_mesh[self.level.get()].append(top_right)

        #E and SE 
        #E's bottom top left and bottom left is current cell's top right and bottom right
        #SE's top left is current cell's bottom right
        
        if self.in_bounds(e_pos.x, e_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(e_pos.x, e_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                top_right = n_top_left
                bottom_right = n_bottom_left
                has_top_right = True
                has_bottom_right = True
                #print("yep east")

        if self.in_bounds(se_pos.x, se_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(se_pos.x, se_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                bottom_right = n_top_left
                has_bottom_right = True
                #print("yep south east")

        if not has_bottom_right:
            if ibr:

                bottom_right.x = ibr[0]
                bottom_right.y = ibr[1]

            else:
                
                bottom_right.x = self.pixel_top[grid_x + 1][0]
                bottom_right.y = self.pixel_top[grid_x + 1][1]
            
            
            #bottom_right = Vertex(ibr[0], ibr[1])
            #print("yeah bottom right")
        if bottom_right not in self.pixel_mesh[self.level.get()]:
            self.pixel_mesh[self.level.get()].append(bottom_right)

        #S and SW 
        #S's bottom top_right and top_left is current cell's bottom right and bottom left
        #SW's top left is current cell's bottom left
        
        if self.in_bounds(s_pos.x, s_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(s_pos.x, s_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                bottom_right = n_top_right
                bottom_left = n_top_left
                has_bottom_left = True
                has_bottom_right = True
                #print("yep south")
                

        if self.in_bounds(sw_pos.x, sw_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(sw_pos.x, sw_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                bottom_left = n_top_right
                has_bottom_left = True
                #print("yep south west")



        if not has_bottom_left:
            if ibl:

                bottom_left.x = ibl[0]
                bottom_left.y = ibl[1]
                

            else:

                bottom_left.x = self.pixel_left[grid_y + 1][0]
                bottom_left.y = self.pixel_left[grid_y + 1][1]

            
            #print("yeah bottom left")
        if bottom_left not in self.pixel_mesh[self.level.get()]:
            self.pixel_mesh[self.level.get()].append(bottom_left)

        #W and NW
        #W's top_right and bottom_right is current cell's top left and bottom left
        #NW's bottom right is current cell's top left
        #actually bottom left and or top left of current cell
        if self.in_bounds(w_pos.x, w_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(w_pos.x, w_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                top_left = n_top_right
                bottom_left = n_bottom_right
                has_top_left = True
                has_bottom_left = True
                #print("yep west")


        if self.in_bounds(nw_pos.x, nw_pos.y, self.pixel_canvas_width, self.pixel_canvas_height):
            coord_key = self.coord_str(nw_pos.x, nw_pos.y, self.level.get())
            if self.pixel_coords.get(coord_key):
                vertices = self.pixel_coords[coord_key]
                n_top_left     = vertices[0]
                n_top_right    = vertices[1]
                n_bottom_right = vertices[2]
                n_bottom_left  = vertices[3]

                top_left = n_bottom_right
                has_top_left = True
                #print("yep north west")

        if not has_top_left:

            if itl:

                top_left.x = itl[0]
                top_left.y = itl[1]

            else:
                
                top_left.x = self.pixel_left[grid_y][0]
                top_left.y = self.pixel_left[grid_y][1]

            
            #print("yeah top left")

        if top_left not in self.pixel_mesh[self.level.get()]:
            self.pixel_mesh[self.level.get()].append(top_left)

        return top_left, top_right, bottom_right, bottom_left  
    
    def print_data(self):
        print("Level {}".format(self.z_layer))
        for vertex in self.borders:

            print("Border X: {} Y: {}".format(vertex.get_X(), vertex.get_Y()))


        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            if vertices:
                top_left_vertex = vertices[0]
                bottom_right_vertex = vertices[1]
                top_right_vertex = vertices[2]
                bottom_left_vertex = vertices[3]

                print("Key:{}".format(key))
                print("Top Left X: {} Y: {}".format(top_left_vertex.get_X(), top_left_vertex.get_Y()))
                print("Bottom Right X: {} Y: {}".format(bottom_right_vertex.get_X(), bottom_right_vertex.get_Y()))
                print("Top Right X: {} Y: {}".format(top_right_vertex.get_X(), top_right_vertex.get_Y()))
                print("Bottom Left X: {} Y: {}".format(bottom_left_vertex.get_X(), bottom_left_vertex.get_Y()))
        print()

    
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

    def paint_pixel(self, mouse_x, mouse_y, canvas_width, canvas_height, angle, scaling, canvas, color):
    
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
        key_coord = self.coord_str(grid_x, grid_y, self.z_layer)
        self.pixel_coords[key_coord] = [
                                        Vertex(top_left_x, top_left_y),
                                        Vertex(top_right_x, top_right_y),
                                        Vertex(bottom_right_x, bottom_right_y), 
                                        Vertex(bottom_left_x, bottom_left_y)
                                    ]
                
        
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

        
 
        
        self.sprite_stack = []


        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        self.pixel_canvas_layers = p_layers

        self.pixel_scale = 0
        self.max_pixel_scale = 0
        self.min_pixel_scale = 1
        

        self.focus_grid_color = "purple"
        self.canvas_bg_color = 'gray'
        self.canvas = tk.Canvas(self, width=c_dimension, height=c_dimension, bg=self.canvas_bg_color) 


        
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
        self.clear_button = ttk.Button(self, text="Clear Level", command=self.clear)
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.data_buttom = ttk.Button(self, text="Console Data", command=self.display_data)

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
        
        self.pixel_level = 0
        self.level_label = tk.Label(self, text="Level")
        self.level = tk.IntVar(value=self.pixel_level)
        self.level_slider = tk.Scale(
            self,
            variable=self.level,
            from_ = 0,
            to = self.pixel_canvas_layers - 1,
            orient = "vertical",
            length=c_dimension,
            command = self.focus_sprite_stack
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
                [None                , self.level_label    , self.spacing_label  , self.translation_lbl    ],
                [self.canvas         , self.level_slider   , self.spacing_slider , self.translate_scl      ],
                [self.rotation_label , None                , None                , self.translate0_btn     ],
                [self.rotation_slider, self.color_button   , self.clear_button   , self.settings_cb        ],
                [None                , self.save_button    , self.data_buttom    , self.visible_borders_cb ],
                [None                , None                , None                , self.visible_layer_cb   ],
                [None                , None                , None                , self.visible_grid_cb    ]
        ]

        arrange_widgets(arrangement)
        



        self.canvas.bind("<B1-Motion>", self.draw) 
        #self.canvas.bind("<B3-Motion>", self.erase) 
        
        self.canvas.bind("<ButtonPress-1>", self.draw)
        #self.canvas.bind("<ButtonPress-3>", self.erase) 
        self.canvas.bind("<MouseWheel>", self.scale_sprite_stack)
        
        

        self.create_sprite_stack(c_dimension)



    def create_sprite_stack(self,c_dimension):
        
        #rectangle diagonal
        #these exists so pixels are always square
        diagonal = math.sqrt(self.pixel_canvas_width ** 2 + self.pixel_canvas_height ** 2)
        ratio_x = (self.pixel_canvas_width/diagonal) 
        ratio_y = (self.pixel_canvas_height/diagonal)

        for z in range(self.pixel_canvas_layers):
            
            
            #(c_dimension - sprite_sheet)/2
            
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

            sheet = Sheet(sheet, self.pixel_canvas_width, self.pixel_canvas_height, c_dimension, c_dimension)
            sheet.z_layer = z
            drawable_x = x2 - x0
            drawable_y = y2 - y0
            
            x_start = x0 
            y_start = y0
            x_space = (drawable_x/self.pixel_canvas_width) 
            y_space = (drawable_y/self.pixel_canvas_height) 

            if z < 1:
                print("spacing", x_space, y_space)
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
                            sheet.pixel_coords.update({sheet.coord_str(x, y, z) : []})
                    

            self.sprite_stack.append(sheet)

        self.sprite_sheet = self.sprite_stack[self.pixel_level]
        self.render_stack_levels()


        
        

    def degrees_to_radians(self, deg):
        return to_radians(deg) #(deg * math.pi)/180
    
    def render_stack_layer(self):
        pass

    def render_stack_levels(self):
        self.canvas.delete("all")
        cur_level = self.level.get()
        for i in range(len(self.sprite_stack)):
            sheet = self.sprite_stack[i]
            
            for key in sheet.pixel_coords:
                    
                vertices = sheet.pixel_coords[key]
                
                if vertices:
                    self.canvas.delete(key)
                    x_pixel, y_pixel, z_level = sheet.str_coord(key)
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

                    if i == cur_level:

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
        
        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2


        self.pivot_matrix[0, 2] = cx
        self.pivot_matrix[1, 2] = cy

        self.matrix_pivot[0, 2] = -cx
        self.matrix_pivot[1, 2] = -cy

        if is_spacing:
            spacing_change = transform_matrix[1, 2]
        
        for i in range(len(self.sprite_stack)):
            sheet = self.sprite_stack[i]
            prev_sheet = sheet
            
            
            if is_scaling or is_moving:
                pass
            elif is_spacing:
                
                if i != self.pixel_level:
                    transform_matrix[1, 2] = (self.pixel_level - i)  * spacing_change
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
                    prev_sheet = self.sprite_stack[i - 1]
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
        #0, (self.pixel_level - i)  * spacing_change, x, y
        transform_matrix = array(translation_matrix2D(0, spacing_change))
        self.apply_stack_transformations(transform_matrix, False, False, True, False, False)

    def focus_sprite_stack(self, *args):
        prev_level = self.pixel_level
        self.pixel_level = self.level_slider.get()
        #if self.sheet_spacing != 0:
        self.sprite_sheet = self.sprite_stack[self.pixel_level]
        sign = prev_level - self.pixel_level 
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
        for row in range(len(arr2d)):
            for col in range(len(arr2d[row])):
                s = s + str(arr2d[row][col]) + " "
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
        
        
        grid_pixel = []
        row = 0
        for i in range(len(self.sprite_stack)):
            sheet = self.sprite_stack[i]
            
            coords = sheet.pixel_grid
            for y in range(len(coords)):
                grid_pixel.append([])
                for x in range(len(coords[y])):
                    #each in rgb alpha
                    if coords[y][x] != None:
                        grid_pixel[row].append(self.hex_to_rbg(coords[y][x]))
                    else:
                        grid_pixel[row].append([255, 255, 255, 0])
                row += 1
                    
        #self.display_2d(grid_pixel)

        im = array(grid_pixel, dtype= uint8)
        im = Image.fromarray(im , 'RGBA')
        im.save(save_path)
                           
    def choose_color(self):
        print("pixel grid")
        self.display_2d(self.sprite_sheet.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        print(color_code)
        if color_code[1]:
            self.selected_color = color_code[1]
    
    def display_data(self):
        print("Data")
        
        self.sprite_sheet.print_data()
        
        print(self.selected_color)
        #for vert in self.pixel_vertices:
        #    print(vert)

    def checkbutton_on(self, cb, cbv):
        return cbv.get() == cb.cget("onvalue")

    def display_settings(self):
        if self.checkbutton_on(self.settings_cb, self.settings_cbv):
        #self.settings_cbv.get() == self.settings_cb.cget("onvalue"):
            print("yea")

        else:
            print("no")


    def clear(self):
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_width):
                self.canvas.delete(self.coord_str(x, y, self.level.get()))
                self.sprite_sheet.pixel_grid[y][x] = None
               
        #self.canvas.delete('all')
        self.last_pixel = None
    
    '''
    def erase(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.sprite_sheet, x, y):
            #print('yep')
            grid_x, grid_y = self.get_pixel_grid_coords(x, y, canvas_width, canvas_height)
            key_coord = self.coord_str(grid_x, grid_y, self.level.get())
            if self.pixel_coords.get(key_coord):
                vertices = self.pixel_coords[key_coord]
                        
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

                
                #if not self.pixel_grid[y_pixel][x_pixel]:
                if polygon_point(polygon, x, y):
                    self.pixel_grid[grid_y][grid_x] = None
                    self.canvas.create_polygon(polygon,
                                                fill = self.canvas_bg_color,
                                                #outline='',
                                                tags=(key_coord)
                                                )
                    
                    
            
    
                if not self.last_pixel:
                    self.last_pixel = [x, y]
    
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
                    x_pixel, y_pixel, z_level = self.str_coord(key)

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
                            
    def draw_drag(self, event): 
        

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if polygon_point(self.sprite_sheet, x, y):
            #print('yep')
            cur_level = self.level.get()
            grid_x, grid_y = self.get_pixel_grid_coords(x, y, canvas_width, canvas_height)
            key_coord = self.coord_str(grid_x, grid_y, cur_level)
                    
                
            #print("drag", self.last_pixel[0], self.last_pixel[1], grid_x, grid_y)
            
            if grid_x != self.last_pixel[0] and grid_y != self.last_pixel[1]:
                     
                between = self.DDA(self.last_pixel[0], self.last_pixel[1], grid_x, grid_y)
                #coord_keys = [self.coord_str(coord[0], coord[1], cur_level) for coord in between]
                #print(between)
                for i in range(len(between)):
                    
                    x_pixel, y_pixel = between[i]
                    key_coord = self.coord_str(between[i][0], between[i][1], cur_level)
                    vertices = self.pixel_coords[key_coord]
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
                    
                    self.pixel_grid[y_pixel][x_pixel] = self.selected_color
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = self.selected_color,
                                                outline=self.selected_color,
                                                tags=(key_coord)
                                                )

                #print(between)
                
                self.last_pixel = [grid_x, grid_y]
    '''           
    def draw(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.sprite_sheet.get_borders(), x, y):
            #print('yep')
            self.sprite_sheet.paint_pixel(x, y, canvas_width, canvas_height, -self.angle, self.pixel_scale, self.canvas, self.selected_color)
            #key_coord = self.coord_str(grid_x, grid_y, self.level.get())
            #print("GX:{} GY:{}".format(grid_x, grid_y))
            #polygon = shape
            '''
            #print(self.get_existing_vertices(grid_x, grid_y, self.pixel_canvas_width, self.pixel_canvas_height))
            if self.sprite_sheet.pixel_coords.get(key_coord):

                vertices = self.sprite_sheet.pixel_coords[key_coord]
                
                
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
                
                
                
                
            else:
                

                


                
                
                #top_left  = Vertex(-1, -1)  #Vertex(itl[0], itl[1])
                #top_right  = Vertex(-1, -1) #Vertex(itr[0], itr[1])
                #bottom_right = Vertex(-1, -1) #Vertex(ibr[0], ibr[1])
                #bottom_left = Vertex(-1, -1) #Vertex(ibl[0], ibl[1])

            

                top_left, top_right, bottom_right, bottom_left = self.get_vertices(grid_x, grid_y, itr, ibr, ibl, itl)


                    
                
                self.pixel_coords[key_coord] = [top_left, top_right, bottom_right, bottom_left]
                polygon = [
                            top_left.x, top_left.y, 
                            top_right.x, top_right.y,
                            bottom_right.x, bottom_right.y,
                            bottom_left.x, bottom_left.y
                        ]


                #print(list(map(str, self.pixel_coords[key_coord])))
            '''
            
            '''
            #if not self.pixel_grid[y_pixel][x_pixel]:
            #if polygon:
                #if polygon_point(polygon, x, y):
                    
                    self.sprite_sheet.pixel_grid[grid_y][grid_x] = self.selected_color
                    self.sprite_sheet.pixel_coords[key_coord] = polygon
                    self.canvas.create_polygon(polygon,
                                                fill = self.selected_color,
                                                outline=self.selected_color,
                                                tags=(key_coord)
                                                )
            '''
            self.render_stack_levels()
            #if not self.last_pixel:
            #    self.last_pixel = [grid_x, grid_y]
            
    
    
        
class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Stack-A-Sprite") 

        
        self.mn_canvas = MainCanvas(self, 512, 32, 32, 3)
        self.mn_canvas.grid()
        
if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    app.resizable()
    app.mainloop()
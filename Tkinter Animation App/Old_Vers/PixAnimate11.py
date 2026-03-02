import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk, ImageSequence
from MatrixMath import *
from collisions import *
import numpy as np
from numpy import radians as to_radians
import math
import time

def angle_to(x1, y1, x2, y2):
    #in radians
    return math.atan2(y2 - y1, x2 - x1)

def distance_to(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    s = dx * dx + dy * dy
    return math.sqrt(s)

def in_bounds(x, y, w, h):
    return 0 <= x < w and 0 <= y < h

def degrees_to_radians(deg):
    return to_radians(deg) #(deg * math.pi)/180

def ellipse(cx, cy, rx, ry):
    # Python3 program for implementing 
    # Mid-Point Ellipse Drawing Algorithm 
    
    x = 0
    y = ry

    # Initial decision parameter of region 1 
    d1 = ((ry * ry) - (rx * rx * ry) + (0.25 * rx * rx))
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y

    points = []

    # For region 1 
    while (dx < dy): 

        # Print points based on 4-way symmetry 
        points.append((x + cx, y + cy))
        points.append((-x + cx, y + cy)) 
        points.append((x + cx, -y + cy ))
        points.append((-x + cx, -y + cy))

        # Checking and updating value of 
        # decision parameter based on algorithm 
        if (d1 < 0): 
            x += 1
            dx = dx + (2 * ry * ry)
            d1 = d1 + dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx = dx + (2 * ry * ry) 
            dy = dy - (2 * rx * rx)
            d1 = d1 + dx - dy + (ry * ry)

    # Decision parameter of region 2 
    d2 = (((ry * ry) * ((x + 0.5) * (x + 0.5))) + ((rx * rx) * ((y - 1) * (y - 1))) - (rx * rx * ry * ry))

    # Plotting points of region 2 
    while (y >= 0):

        # printing points based on 4-way symmetry 
        points.append((x + cx, y + cy))
        points.append((-x + cx, y + cy))
        points.append((x + cx, -y + cy))
        points.append((-x + cx, -y + cy))

        # Checking and updating parameter 
        # value based on algorithm 
        if (d2 > 0):
            y -= 1; 
            dy = dy - (2 * rx * rx); 
            d2 = d2 + (rx * rx) - dy; 
        else:
            y -= 1; 
            x += 1; 
            dx = dx + (2 * ry * ry); 
            dy = dy - (2 * rx * rx); 
            d2 = d2 + dx - dy + (rx * rx); 
    return points

def DDA(x0, y0, x1, y1):
        #Digital Differential Analyzer
        
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx),abs(dy))
        
        coordinates = []
        if steps != 0:
            x_inc = dx/steps
            y_inc = dy/steps
            
            x = x0
            y = y0
            
            
            
            for i in range(int(steps)):
                x += x_inc
                y += y_inc
                floored_coords = [math.floor(x), math.floor(y)]
                if floored_coords not in coordinates:
                    coordinates.append(floored_coords)
                    
            
        return coordinates

def DDA_raycast(x0, y0, radians, limit):
        x_inc = math.cos(radians)
        y_inc = math.sin(radians)

        _x = x0
        _y = y0

        d = distance_to(x0, y0, _x, _y)
        while d < limit:
            _x += x_inc
            _y += y_inc
            d = distance_to(x0, y0, _x, _y)

        return _x, _y

def path_correction(file_path):
    foward_slash = "/"
    back_slash = "\\"
    file_path = file_path.replace(foward_slash, back_slash)

    return file_path

def hide_widget(widget):
    widget.grid_remove()
        
def show_widget(widget):
    widget.grid()

def hide_pack_widget(widget):
    widget.pack_forget()

def show_pack_widget(widget):
    widget.pack()

def disable_widget(widget):
    widget.config(state="disabled")

def enable_widget(widget):
    widget.config(state="normal")

def delete_widget(widget):
    widget.destroy()

def arrange_widgets(arrangement, branch = "NEWS"):
    for ind_y in range(len(arrangement)):
        for ind_x in range(len(arrangement[ind_y])):

            if arrangement[ind_y][ind_x] == None:
                pass
            else:
                arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = branch)

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


class Vertex():
    def __init__(self, x , y):
        self.v = np.array(
            set_matrix2D(x, y),  dtype=np.float64
        )
        self.been_transformed = False

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
        XnY = np.dot(translation_matrix, self.v) #moves to origin
        #print(XnY, '\n')
        XnY = np.dot(transform_matrix, XnY) #applies transform
        #print(XnY, '\n')
        XnY = np.dot(matrix_translation, XnY) #moves back to original position
        '''
        '''
        XnY = np.dot(matrix_translation, np.dot(transform_matrix, np.dot(translation_matrix, self.v)))
        '''
        full_transform = matrix_translation @ transform_matrix @ translation_matrix
        XnY = full_transform @ self.v

        #print('nump')
        #print(XnY)
        self.set_coords(XnY[0 ,0], XnY[1, 0])
        self.been_transformed = True


class KeyFrame():
    def __init__(self, pixel_width, pixel_height, canvas_width, canvas_height):
        '''
        0 - KeyFrame is a class that represents a collection of vertices from the very edges of the shape to the edges of individual pixel polygons made of XY vertices
        1 - pixel grid is a 2D array/list of Hex Codes, that represent the pixels in an image, and empty cell/pixel is denoted by None instead of a hexcode
        2 - pixel coords is a dictionary of vertex coordinates 
            say for instance a 4x4 grid
            "X-Y" as a string that is a key to a dictionary/hashmap
            Each of these keys would have an array linking to their vertex coordinates 
                [V1, V2, V3, V4] of their polygon 
            'V' is an x, y vertex
            'N' and 'M' are it's respective dimensions 
            For a 4x4 cell grid both M and N would be 4

                        M
    
            V-------V-------V-------V-------V
            | 0-0   | 0-1   | 0-2   | 0-3   | 
            V-------V-------V-------V-------V
            | 1-0   | 1-1   | 1-2   | 1-3   |
       N    V-------V-------V-------V-------V  
            | 2-0   | 2-1   | 2-2   | 2-3   | 
            V-------V-------V-------V-------V
            | 3-0   | 3-1   | 3-2   | 3-3   |
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
        


        #very painful bug
        #it's possible to initialize a 2D array like this but all the rows change at once when updating the contents of one
        #print([[None] * pixel_width] * pixel_height)

        '''
        for y in range(self.pixel_canvas_height):
            self.pixel_grid.append([])
            for x in range(self.pixel_canvas_width):
                self.pixel_grid[y].append(None)
        '''

        #self.pixel_grid = [[None for _ in range(pixel_width)] for _ in range(pixel_height)]
        

        
        self.pixel_grid =[[None] * pixel_width for _ in range(pixel_height)]
        #print(self.pixel_grid)
        self.pixel_coords = {}
        self.pixel_vertices = []


        self.pixel_canvas_width = pixel_width
        self.pixel_canvas_height = pixel_height
        
        

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        

        
        self.pixel_scale = -1
        

        self.brush_size = 1
        #The hexadecimal color black initially
        #self.color = "#000000" 
        #print(self.hex_to_rbg(self.color))

        #line stroke drawing vars
        self.is_drawing_line = False

        
        self.stroke_pixels = []
        self.temp_pixels = []
        self.temp_colors = []
        self.first_pixel = []
        self.last_pixel = []
        self.anchor_pixel = []

        #print(f"{self.canvas_width} {self.canvas_height}")
    
        
        #rectangle vars
        self.rect = None
        self.rect_x = None
        self.rect_y = None
        self.rect_w = None
        self.rect_h = None

    def transform_pixels(self, translation_matrix, transform_matrix, matrix_translation, canvas, borders):
        #grid_pixel = [[  None ] * len(self.pixel_grid[0]) for _ in range(len(self.pixel_grid))]
        #canvas.delete("all")
        keys = []
        colors = []
        full_transform = matrix_translation @ transform_matrix @ translation_matrix
        '''
        if self.temp_pixels:
            print("yep")
            
            colors = [self.pixel_grid[ pxl[1] ][ pxl[0] ] for pxl in self.temp_pixels]
            

            self.temp_pixels = list(map(self.str_to_coord, self.pixel_coords.keys()))

        else:

        '''
        
        #returns a tuple of (x, y)
        keys = list(map(self.str_to_coord, self.pixel_coords.keys()))
        colors = [self.pixel_grid[ pxl[1] ][ pxl[0] ] for pxl in keys]


        while keys:
            key = keys.pop()
            color = colors.pop()
            old_x, old_y = key[0], key[1]
            XnY = np.array(
                set_matrix2D(old_x, old_y),  dtype=np.float64
            )
            #if self.pixel_grid[old_y][old_x] != None:
            
            
            current_coord = self.coord_to_str(old_x, old_y)
            XnY = full_transform @ XnY
            
            new_x, new_y = round(XnY[0 ,0]), round(XnY[1, 0])
            
            
            if in_bounds(new_x, new_y, len(self.pixel_grid[0]), len(self.pixel_grid)):
                
                if self.pixel_coords.get(current_coord):
                    del self.pixel_coords[current_coord]
                current_coord = self.coord_to_str(new_x, new_y)

                self.pixel_grid[old_y][old_x] = None
                self.pixel_grid[new_y][new_x] = color
                #if not self.pixel_grid[old_y][old_x] and not self.pixel_grid[new_y][new_x]:
                    
                

                self.draw_pixel(canvas, current_coord,  color,  color, current_coord, borders) 
                

            
            else:
                current_coord = self.coord_to_str(old_x, old_y)
                self.pixel_grid[old_y][old_x] = None
                if self.pixel_coords.get(current_coord):
                    del self.pixel_coords[current_coord]
            
        
        #self.render_grid(canvas, borders)
        #self.pixel_grid = grid_pixel


    def transform_vertices(self, translation_matrix, transform_matrix, matrix_translation):
        #each of the matrices/arrays should be numpy arrays

        
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
        
        #for vertex in self.pixel_vertices:
            #vertex.transform(translation_matrix, transform_matrix, matrix_translation)
        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            if vertices:
                top_left_vertex = vertices[0]
                bottom_right_vertex = vertices[1]
                top_right_vertex = vertices[2]
                bottom_left_vertex = vertices[3]

                if top_left_vertex.been_transformed == False:
                    top_left_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                if bottom_right_vertex.been_transformed == False:
                    bottom_right_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                if top_right_vertex.been_transformed == False:
                    top_right_vertex.transform(translation_matrix, transform_matrix, matrix_translation)
                if bottom_left_vertex.been_transformed == False:
                    bottom_left_vertex.transform(translation_matrix, transform_matrix, matrix_translation)

        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            if vertices:
                top_left_vertex = vertices[0]
                bottom_right_vertex = vertices[1]
                top_right_vertex = vertices[2]
                bottom_left_vertex = vertices[3]

                top_left_vertex.been_transformed = False

                bottom_right_vertex.been_transformed = False
     
                top_right_vertex.been_transformed = False
                    
                bottom_left_vertex.been_transformed = False
                    
        #self.pixel_vertices = [vtx.transform(translation_matrix, transform_matrix, matrix_translation) for vtx in self.pixel_vertices]

    def coord_to_str(self, x, y):
        return str(x) + '|' + str(y)
    
    def str_to_coord(self, string):
        if '|' in string:
            x, y = map(int, string.split('|'))
            return x, y
        return 0, 0

    def get_temp_pixels(self):
        return self.temp_pixels
    
    def get_temp_colors(self):
        return self.temp_colors

    #https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    #https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa

    def rgb_to_hex(self, r,g,b):
        hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)
        return hexcode
    
    def hex_to_rgb(self, hexcode, alpha = False):
        hexcode = hexcode[1:]
        rgb = list(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
        if alpha:
            rgb.append(255)
            return rgb 
        return rgb 
    
    def invert_color(self, color):
        rgb = self.hex_to_rgb(color)
            
        rgb[0] = 255 - rgb[0]
        rgb[1] = 255 - rgb[1]
        rgb[2] = 255 - rgb[2]
        

        r, g, b = rgb
        _hex = self.rgb_to_hex(r, g, b)
        return _hex
   
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

    def pixel_to_pil_image(self, bg_color = [255, 255, 255, 0]):
        #print("pixel image")

        #print(self.pixel_canvas_width, self.pixel_canvas_height)
        #print(len(self.pixel_grid[0]), len(self.pixel_grid))
        #initialization with a clear blank cell
        grid_pixel = [[  bg_color  ] * len(self.pixel_grid[0]) for _ in range(len(self.pixel_grid))]
        keys = list(self.pixel_coords.keys())
        while keys:
            key = keys.pop()
            x_pixel, y_pixel = self.str_to_coord(key)
            x, y = int(x_pixel), int(y_pixel)
            if self.pixel_grid[y][x] != None:
                grid_pixel[y][x] = self.hex_to_rgb(self.pixel_grid[y][x], True)
            else:
                current_coord = self.coord_to_str(x, y)
                if self.pixel_coords.get(current_coord):
                    del self.pixel_coords[current_coord]
        '''
        for y in range(len(self.pixel_grid)):
            grid_pixel.append([])
            for x in range(len(self.pixel_grid[0])):
                #each in rgb alpha
                if self.pixel_grid[y][x] != None:
                    grid_pixel[y].append(self.hex_to_rgb(self.pixel_grid[y][x], True))
                else:
                    grid_pixel[y].append([255, 255, 255, 0])
                    current_coord = self.coord_to_str(x, y)
                    if self.pixel_coords.get(current_coord):
                        del self.pixel_coords[current_coord]
        ''' 
        #self.display_2d(grid_pixel)
        im = np.array(grid_pixel, dtype=np.uint8)
        im = Image.fromarray(im)
        return im

    def alter_array_dimensions(self, arr2d, new_width, new_height, filler, anchor, canvas, borders):
        #https://www.w3schools.com/python/numpy/trypython.asp?filename=demo_numpy_array_slicing_2d3
        #https://www.w3schools.com/python/numpy/numpy_array_slicing.asp
        #https://www.w3schools.com/python/numpy/numpy_array_join.asp
        #https://www.w3schools.com/python/numpy/trypython.asp?filename=demo_numpy_array_join2
        #order padding 
        #first columns then rows
        #note: axis in np.concatenate 1 is rowwise, 0, the default, is columnwise
        #anchor possiblities NE, N, NW, E, (C)enter, W, SE, S, SW
        new_array = np.array(arr2d)

        
        cur_height, cur_width = new_array.shape
        #og_width = cur_width


        #NE keeps top left, SE bottom left, SW bottom right, NW top right
        #The others are toss ups

        if cur_width >= new_width:
            #if the width needs to be reduced
            if anchor == "W" or anchor == "SW" or anchor == "NW":
                new_array  = new_array[0 : cur_height, 0:new_width]


                
            elif anchor == "E" or anchor == "SE" or anchor == "NE":
                new_array  = new_array[0 : cur_height, -new_width:]

            elif anchor == "C" or  anchor == "N" or anchor == "S" :
                part_one = new_width//2
                part_two = cur_width - part_one
                new_array = new_array[0 : cur_height, part_one:part_one+new_width]
                
            cur_width = new_array.shape[1]
        else:
            #if the width needs to be expanded
            if anchor == "W" or anchor == "SW" or anchor == "NW":
                #Expands to the right
                temp = np.full((cur_height, abs(new_width - cur_width)), [filler])
                new_array = np.concatenate((new_array, temp), axis=1)

            elif anchor == "E" or anchor == "SE" or anchor == "NE":
                #Expands to the left
                temp = np.full((cur_height, abs(new_width - cur_width)), [filler])
                new_array = np.concatenate((temp, new_array), axis=1)

            elif anchor == "C" or  anchor == "N" or anchor == "S" :
                #Expands to the right and left
                part_one = round((abs(new_width - cur_width))/2)
                part_two = abs(new_width - cur_width) - part_one

                temp_one = np.full((cur_height, part_one), [filler])
                temp_two = np.full((cur_height, part_two), [filler])
                
                #left
                new_array = np.concatenate((temp_one, new_array), axis=1)

                #right
                new_array = np.concatenate((new_array, temp_two), axis=1)

            cur_width = new_array.shape[1]
            
        
            
        if cur_height >= new_height:
            #if the height needs to be reduced
            if anchor == "N" or anchor == "NW" or anchor == "NE":
                new_array  = new_array[0:new_height]

            elif anchor == "S" or anchor == "SW" or anchor == "SE":
                new_array  = new_array[-new_height:]

            elif anchor == "C" or  anchor == "W" or anchor == "E" :
                part_one = new_height//2
                part_two = cur_height - part_one
                new_array = new_array[part_one:part_one+new_height]

        else:
            #if the height needs to be expanded
            if anchor == "N" or anchor == "NW" or anchor == "NE":
                #Expands to the bottom
                temp = np.full((abs(new_height - cur_height), cur_width), [filler])
                new_array = np.concatenate((new_array, temp), axis=0)



            elif anchor == "S" or anchor == "SW" or anchor == "SE":
                #Exapnds the top
                temp = np.full((abs(new_height - cur_height), cur_width), [filler])
                new_array = np.concatenate((temp, new_array), axis=0)


            elif anchor == "C" or  anchor == "W" or anchor == "E" :
                #Expands to the top and bottom
                part_one = round((abs(new_height - cur_height))/2)
                part_two = abs(new_height - cur_height) - part_one

                temp_one = np.full((part_one, cur_width), [filler])
                temp_two = np.full((part_two, cur_width), [filler])
                #top
                new_array = np.concatenate((temp_one, new_array), axis=0)

                #bottom
                new_array = np.concatenate((new_array, temp_two), axis=0)
        
        #comparing pixels of the old grid and the edited grid to get the new border dimensions

        
        self.pixel_coords.clear()
        self.pixel_grid.clear()

        canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
        self.pixel_canvas_width, self.pixel_canvas_height = new_width, new_height
        #self.borders = self.set_borders(canvas_width, canvas_height, self.pixel_canvas_width, self.pixel_canvas_height)
        #self.set_scaling(canvas)
        #print(new_array)

        new_pixel_grid = new_array.tolist()

        
                
        
        self.pixel_grid = new_pixel_grid
        canvas.delete("all")
        for y in range(len(new_pixel_grid)):
            for x in range(len(new_pixel_grid[0])):
                if new_pixel_grid[y][x]:
                    self.draw_pixel(canvas, self.coord_to_str(x, y), new_pixel_grid[y][x], new_pixel_grid[y][x], self.coord_to_str(x, y), borders)
        #self.render_grid(canvas, borders)

    def get_grid_colors(self):
        set_of_colors = {col for row in self.pixel_grid for col in row if col != None}
        return set_of_colors
    
    def resize_canvas(self, canvas, offset_x, offset_y, scale_x, scale_y):
        keys = list(self.pixel_coords.keys())
        while keys:
            key = keys.pop()
            x_pixel, y_pixel = self.str_to_coord(key)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                if self.pixel_grid[y_pixel][x_pixel] == None:

                    #if the color of the grid cell is None
                    current_coord = self.coord_to_str(x_pixel, y_pixel)
                    if self.pixel_coords.get(current_coord):
                        del self.pixel_coords[current_coord]
            else:
                #if the color of the grid cell is None
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                if self.pixel_coords.get(current_coord):
                    del self.pixel_coords[current_coord]
        canvas.scale("all", offset_x, offset_y, scale_x, scale_y)
        

        #self.render_borders(canvas)   

    def render_grid(self, canvas, borders):
        #print("canvas render")
        #redraws the main canvas when a new cell is selected or when the pixels are resized

        #cx1, cy1 = 0, 0
        #cx2, cy2 = self.canvas_height, 0
        #cx3, cy3 = self.canvas_width, self.canvas_height
        #cx4, cy4 = 0, self.canvas_width
        #canvas_polygon = [cx1, cy1, cx2, cy2, cx3, cy3, cx4, cy4]

        #canvas.delete("all")
        #a = 0
        #b = 0
        #for key in self.pixel_coords:
        keys = list(self.pixel_coords.keys())
        while keys:
            key = keys.pop()
            x_pixel, y_pixel = self.str_to_coord(key)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                if self.pixel_grid[y_pixel][x_pixel]:
                    #current_polygon = self.pixel_to_canvas(x_pixel, y_pixel)
                    #print(canvas_polygon, "\n",current_polygon)
                    #a += 1
                    #occlusion culling
                    #woould work have to figure out moving canvas bounds vertices
                    #if rectangle_rectangle(cx1, cy1, cx3, cy3, current_polygon[0], current_polygon[1], current_polygon[6] - current_polygon[0], current_polygon[3] - current_polygon[1]):
                    
                    self.draw_pixel(canvas, key,  self.pixel_grid[y_pixel][x_pixel],  self.pixel_grid[y_pixel][x_pixel], key, borders) 
                        #b += 1

                else:
                    #if the color of the grid cell is None
                    current_coord = self.coord_to_str(x_pixel, y_pixel)
                    if self.pixel_coords.get(current_coord):
                        del self.pixel_coords[current_coord]
            else:
                #if the color of the grid cell is None
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                if self.pixel_coords.get(current_coord):
                    del self.pixel_coords[current_coord]
        #print(f"total pixels: {a} rendered pixels: {b}")
        #self.render_borders(canvas)    

    def grid_to_coords(self, borders):
        border_x = borders[0]
        border_y = borders[1]
        
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = min(true_pixel_width, true_pixel_height)

        top_left_x, top_left_y = borders[0], borders[1]

        self.temp_pixels = [ [col, row] for row in range(len(self.pixel_grid)) for col in range(len(self.pixel_grid[0])) if self.pixel_grid[row][col] ]
        for pxl in self.temp_pixels:
            grid_x, grid_y = pxl
            #grid_x, grid_y = math.floor(grid_x), math.floor(grid_y)
            key_coord = self.coord_to_str(grid_x, grid_y)

            

            
            top_left_x = border_x + border_width  * (grid_x/len(self.pixel_grid[0]))
            top_left_y = border_y + border_height * (grid_y/len(self.pixel_grid))

            bottom_right_x = top_left_x + scale
            bottom_right_y = top_left_y + scale

            bottom_left_x = top_left_x
            bottom_left_y = top_left_y + scale

            top_right_x = top_left_x + scale
            top_right_y = top_left_y 

            
            
            top_left, top_right, bottom_right, bottom_left = self.recycle_vertices(grid_x, grid_y,
                Vertex(top_left_x, top_left_y), Vertex(top_right_x, top_right_y), Vertex(bottom_right_x, bottom_right_y),  Vertex(bottom_left_x, bottom_left_y)
            )
            #print(key_coord)
            self.pixel_coords[key_coord] = [top_left, top_right, bottom_right, bottom_left]
        #print(self.pixel_coords)
        self.temp_pixels.clear()

        return self.pixel_coords


    def recycle_vertices(self, grid_x, grid_y, left_top, right_top, right_bottom, left_bottom):
        #print("recycle")
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
        #temp = Vertex(-1, -1)
        #The vertices of CC

        top_left  = left_top
        top_right  = right_top
        bottom_right = right_bottom
        bottom_left = left_bottom

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


        
        for i in range(len(bottom_right_vectors)):
            if in_bounds(grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1])
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    
                    if i == 0: #East
                        n_bottom_left  = vertices[3]
                        bottom_right = n_bottom_left
                        
                    elif i == 1: #South East
                        n_top_left = vertices[0]
                        bottom_right = n_top_left
                    elif i == 2: #South
                        n_top_right  = vertices[1]
                        bottom_right = n_top_right

            

            if in_bounds(grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1])
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

                    
            if in_bounds(grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1])
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

                 
                    
            if in_bounds(grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1],)
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
  

    
        return top_left, top_right, bottom_right, bottom_left  

    def canvas_to_pixel(self, canvas, mouse_x, mouse_y, borders):
        canvas.delete("lines")
        #print("canvas2pixel")

        top_left_x, top_left_y = borders[0], borders[1]
        

        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        
        distance = distance_to(mouse_x, mouse_y, top_left_x, top_left_y) 
        radians =  angle_to(top_left_x, top_left_y, mouse_x, mouse_y) #+ degrees_to_radians(180)
        distance_x = distance_to(top_left_x + math.cos(radians) * distance, top_left_y, top_left_x, top_left_y)
        distance_y = distance_to(top_left_x, top_left_y + math.sin(radians) * distance, top_left_x, top_left_y)
        x_offset = -1 if mouse_x < top_left_x else 1
        y_offset = -1 if mouse_y < top_left_y else 1

        grid_x = math.floor((distance_x/border_width * x_offset) * self.pixel_canvas_width)
        grid_y = math.floor((distance_y/border_height * y_offset) * self.pixel_canvas_height)
        
        if False:
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x + math.cos(radians) * distance, top_left_y + math.sin(radians) * distance,
                    
                    fill = "cyan",
                    tags="lines"
                )
            
            
            
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x, top_left_y + math.sin(radians) * distance,
                    
                    fill = "yellow",
                    tags="lines"
                )
            
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x + math.cos(radians) * distance, top_left_y,
                    
                    fill = "magenta",
                    tags="lines"
                )
        

        return [grid_x, grid_y]

    def pixel_to_canvas(self, pixel_x, pixel_y):
        #print("pixel2canvas")
        key_coord = self.coord_to_str(pixel_x, pixel_y)
        if self.pixel_coords.get(key_coord):
            vertices = self.pixel_coords[key_coord]
            #if vertices:
            #canvas.delete(key)
            #color = self.pixel_grid[y_pixel][x_pixel]

            #pixel polygon vertices not sheet
            top_left_x, top_left_y = vertices[0].get_X(), vertices[0].get_Y()
            top_right_x, top_right_y = vertices[1].get_X(), vertices[1].get_Y()
            bottom_right_x, bottom_right_y = vertices[2].get_X(), vertices[2].get_Y()
            bottom_left_x, bottom_left_y = vertices[3].get_X(), vertices[3].get_Y()

            return [
                top_left_x, top_left_y,
                top_right_x, top_right_y,
                bottom_right_x, bottom_right_y,
                bottom_left_x, bottom_left_y
            ]
        return [
                0, 0,
                0, 0,
                0, 0,
                0, 0,
              
            ]
        
    def draw_pixel(self, canvas, key_coord, fill, outline, tag, borders):
        #print("draw pix")
        
        if self.pixel_coords.get(key_coord):
            vertices = self.pixel_coords[key_coord]
            #if vertices:
            #canvas.delete(key)
            #color = self.pixel_grid[y_pixel][x_pixel]

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
            
            canvas.create_polygon(polygon,
                                fill = fill,
                                outline=outline,
                                tags=(tag)
                                )
            
            #return polygon
            #self.pixel_grid[y_pixel][x_pixel] = color
        else:
            
            grid_x, grid_y = self.str_to_coord(key_coord)
            canvas.delete("lines")

            top_left_x, top_left_y = borders[0], borders[1]

            border_x = borders[0]
            border_y = borders[1]
            border_width = borders[4] - borders[0]
            border_height = borders[5] - borders[1]
            true_pixel_width = border_width/self.pixel_canvas_width
            true_pixel_height = border_height/self.pixel_canvas_height
            scale = true_pixel_width
            
            top_left_x = border_x + border_width  * (grid_x/len(self.pixel_grid[0]))
            top_left_y = border_y + border_height * (grid_y/len(self.pixel_grid))

            bottom_right_x = top_left_x + scale
            bottom_right_y = top_left_y + scale

            bottom_left_x = top_left_x
            bottom_left_y = top_left_y + scale

            top_right_x = top_left_x + scale
            top_right_y = top_left_y 

            
            
            top_left, top_right, bottom_right, bottom_left = self.recycle_vertices(grid_x, grid_y,
                Vertex(top_left_x, top_left_y), Vertex(top_right_x, top_right_y), Vertex(bottom_right_x, bottom_right_y),  Vertex(bottom_left_x, bottom_left_y)
            )
                                                                    
                                                                        
            

            

            polygon = [
                        top_left.get_X(),     top_left.get_Y(),
                        top_right.get_X(),    top_right.get_Y(),
                        bottom_right.get_X(), bottom_right.get_Y(),
                        bottom_left.get_X(),  bottom_left.get_Y()  
                    ]
            


            self.pixel_coords[key_coord] = [top_left, top_right, bottom_right, bottom_left]

            #print(top_left)
            #self.pixel_grid[grid_y][grid_x] = fill
            
            canvas.create_polygon(polygon,
                                fill = fill,
                                outline=outline,
                                tags=(tag)
                                )
            
            #return polygon
            #print(self.pixel_scale)
            #print(grid_x, grid_y)

    def start_stroke(self, x, y, canvas, color, borders):
        #print("stroke")
        #drawing an undecided line between two points

        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                if not self.is_drawing_line:
                    self.first_pixel.clear()
                    
                    self.first_pixel.append(x_pixel)
                    self.first_pixel.append(y_pixel)

                    self.is_drawing_line = True
                else:
                    
                    
                    canvas.delete("stroke_line")
                    #if polygon_point(self.borders, self.first_pixel[0], self.first_pixel[1]):
                    #if self.in_bounds(self.first_pixel[0], self.first_pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    current_coord = self.coord_to_str(self.first_pixel[0], self.first_pixel[1])
                    if self.stroke_pixels:
                        #first pixel
                        self.draw_pixel(canvas, current_coord, color, color, "stroke_line", borders) 
                        
                        
                        
                    self.stroke_pixels = DDA(self.first_pixel[0], self.first_pixel[1], x_pixel, y_pixel)
                    for pixel in self.stroke_pixels:
  
                        self.draw_pixel(canvas, self.coord_to_str(pixel[0], pixel[1]), color, color, "stroke_line", borders) 

    def end_stroke(self, x, y, canvas, color, borders):
        #print("stroke")
        if self.is_drawing_line:
            #print("running")
            self.is_drawing_line = False
            
            if self.stroke_pixels:
                #first pixel
                current_coord = self.coord_to_str(self.first_pixel[0], self.first_pixel[1])
                
                self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 

            #other pixels
            #self.stroke_pixels = self.DDA(self.first_pixel[0], self.first_pixel[1], x_pixel, y_pixel)
            for pixel in self.stroke_pixels:
                #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))

                #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    self.pixel_grid[pixel[1]][pixel[0]] = color
                
                    current_coord = self.coord_to_str(pixel[0], pixel[1])
                    
                    
                    self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
            canvas.update_idletasks()
            canvas.delete("stroke_line")

    def hover_pixel(self, x, y, canvas, color, borders):
        #print("hover")
        #this can't work because tkinter only recognizes clicks and presses on the canvas, rather than hovering
        canvas.delete("pixel_hover")

        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                color_under_cursor = self.pixel_grid[y_pixel][x_pixel]
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                if color_under_cursor != None:
                    inverted_color = self.invert_color(color)
                
                    self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "pixel_hover", borders) 
                    
                else:
                    inverted_color = self.invert_color(color_under_cursor)
                    self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "pixel_hover", borders) 

    def pick_color(self, x, y, canvas, borders):
        #print("pick")
        if polygon_point(borders, x, y):
        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                color_under_cursor = self.pixel_grid[y_pixel][x_pixel]
                #print(color_under_cursor)
                if color_under_cursor:
                    
                    return color_under_cursor
                    
                else:

                    return "#000000"
                
    def shape_click(self, x, y, canvas, color, borders):
        #for rectangle cirdle and select
        #print("recircle")
        #self.image_pos_mouse_label.config(text = f"Image MX:{x} Image MY:{y}")
        if polygon_point(borders, x, y):
            self.rect_x = x
            self.rect_y = y
            canvas.delete("shape")
            # create rectangle if not yet exist
            if not self.rect:
                #pass
                self.rect = canvas.create_rectangle(x, y, 1, 1, outline=color, tags=("shape")) 
    
    def shape_release(self, x, y, canvas, color, borders):
        #print("recircletemp")
        canvas.delete("lasso")
        canvas.delete("lassoline")
        canvas.delete("shape")
        #for pixel in self.temp_pixels:
        for i in range(len(self.temp_pixels)):
            pixel = self.temp_pixels[i]
            if not in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height): 
                continue
            coord = self.coord_to_str(pixel[0], pixel[1])

            if len(self.temp_colors) == 0:
                #print("L")
                self.pixel_grid[pixel[1]][pixel[0]] = color
                self.draw_pixel(canvas, coord, color, color, coord, borders)
            else:
                #print("O")
                self.pixel_grid[pixel[1]][pixel[0]] = self.temp_colors[i]
                self.draw_pixel(canvas, coord, self.temp_colors[i], self.temp_colors[i], coord, borders)

        self.temp_pixels.clear()
        self.temp_colors.clear()

    def rectangle_press(self, x, y, canvas, color, borders):
        #print("rec")
        if polygon_point(borders, x, y):
            # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
            
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #print(f"RX {rx} RY {ry} MX {x} MY {y}")
            #if canvas.delete("shape") is put before create_rectangle the rectangle will be seen
            canvas.delete("shape")
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=color, tags=("shape"))
            
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            if not in_bounds(top_left[0], top_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(top_right[0], top_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_left[0], bottom_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_right[0], bottom_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return

            left_rect_side = DDA(
                top_left[0], top_left[1],
                bottom_left[0], bottom_left[1]
            )

            right_rect_side = DDA(
                top_right[0], top_right[1],
                bottom_right[0], bottom_right[1]
            )

            top_rect_side = DDA(
                top_left[0], top_left[1],
                top_right[0], top_right[1]
            )

            bottom_rect_side = DDA(
                bottom_left[0], bottom_left[1],
                bottom_right[0], bottom_right[1]
            )


            if self.temp_pixels:
                self.temp_pixels.clear()



            self.draw_pixel(canvas, self.coord_to_str(top_left[0], top_left[1]), color, color, "shape", borders)
            self.temp_pixels.append(top_left)

            #going down each side as each parrellel side should be congruent
            for i in range(len(left_rect_side)):
                left_coord = self.coord_to_str(left_rect_side[i][0], left_rect_side[i][1])
                right_coord = self.coord_to_str(right_rect_side[i][0], right_rect_side[i][1])
                self.temp_pixels.append(left_rect_side[i])
                self.temp_pixels.append(right_rect_side[i])
                self.draw_pixel(canvas, left_coord, color, color, "shape", borders)
                self.draw_pixel(canvas, right_coord, color, color, "shape", borders)

            for i in range(len(top_rect_side)):
                top_coord = self.coord_to_str(top_rect_side[i][0], top_rect_side[i][1])
                bottom_coord = self.coord_to_str(bottom_rect_side[i][0], bottom_rect_side[i][1])
                self.temp_pixels.append(top_rect_side[i])
                self.temp_pixels.append(bottom_rect_side[i])
                self.draw_pixel(canvas, top_coord, color, color, "shape", borders)
                self.draw_pixel(canvas, bottom_coord, color, color, "shape", borders)

    def circle_press(self, x, y, canvas, color, borders):
        #print("circle")
        #midpoint ellipse 
        # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
        if polygon_point(borders, x, y):
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #if canvas.delete("shape") is put before create_rectangle the rectangle will be seen
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=color, tags=("shape"))
            canvas.delete("shape")
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            if not in_bounds(top_left[0], top_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(top_right[0], top_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_left[0], bottom_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_right[0], bottom_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
                

            if self.temp_pixels:
                self.temp_pixels.clear()
            
            try:
                rect_center = line_line_intersection(bottom_right[0], bottom_right[1], top_left[0], top_left[1], top_right[0], top_right[1], bottom_left[0], bottom_left[1])
                
                if rect_center:
                    rect_center[0] = math.floor(rect_center[0])
                    rect_center[1] = math.floor(rect_center[1])
                    
          
                    crw = math.floor(abs(top_right[0] - top_left[0])/2)
                    crh = math.floor(abs(bottom_left[1] - top_left[1])/2)
                    #print(top_left, top_right, bottom_left, bottom_right, rect_center, crw, crh)
     
                    ellipse_points = ellipse(rect_center[0], rect_center[1], crw, crh)
                    
                    #print(ellipse_points)
                    for point in ellipse_points:
                        circle_coord = self.coord_to_str(point[0], point[1])
                        self.temp_pixels.append(point)
                        self.draw_pixel(canvas, circle_coord, color, color, "shape", borders)
            except:
                #print(top_left)
                self.temp_pixels = [top_left] + DDA(top_left[0], top_left[1], bottom_right[0], bottom_right[1])
                #self.temp_pixels.extend()
                for point in self.temp_pixels:
                    circle_coord = self.coord_to_str(point[0], point[1])
                    self.draw_pixel(canvas, circle_coord, color, color, "shape", borders)
                #print("Zero Divide")

    def select_press(self, x, y, canvas, color, borders):
        #print("select")
        #standard rectangular select
        if polygon_point(borders, x, y):

            # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
            
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #print(f"RX {rx} RY {ry} MX {x} MY {y}")
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=color, tags=("shape"))
            canvas.delete("shape")
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            

            left_rect_side = DDA(
                top_left[0], top_left[1],
                bottom_left[0], bottom_left[1]
            )

            right_rect_side = DDA(
                top_right[0], top_right[1],
                bottom_right[0], bottom_right[1]
            )

            top_rect_side = DDA(
                top_left[0], top_left[1],
                top_right[0], top_right[1]
            )

            bottom_rect_side = DDA(
                bottom_left[0], bottom_left[1],
                bottom_right[0], bottom_right[1]
            )

            if self.temp_pixels:
                self.temp_pixels.clear()

            self.draw_pixel(canvas, self.coord_to_str(top_left[0], top_left[1]), '', color, "shape", borders)

            #going down each side as each parrellel side should be congruent
            #selecting the filled pixels, hench color_under_cursor
            #it would return either None or a Hexcode string
            #also
            for i in range(len(left_rect_side)):
                left_coord = self.coord_to_str(left_rect_side[i][0], left_rect_side[i][1])
                right_coord = self.coord_to_str(right_rect_side[i][0], right_rect_side[i][1])
                

                if in_bounds(left_rect_side[i][0], left_rect_side[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                    color_under_cursor = self.pixel_grid[ left_rect_side[i][1] ][ left_rect_side[i][0] ]
                    if color_under_cursor:
                        self.temp_pixels.append(left_rect_side[i])
                        
                        inverted_color = self.invert_color(color_under_cursor)
                        self.draw_pixel(canvas, left_coord, inverted_color, inverted_color, "shape", borders)
                    else:
                        self.draw_pixel(canvas, left_coord, "", color, "shape", borders)


                if in_bounds(right_rect_side[i][0], right_rect_side[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                    color_under_cursor = self.pixel_grid[right_rect_side[i][1]][right_rect_side[i][0]]
                    if color_under_cursor:
                        self.temp_pixels.append(right_rect_side[i])
                        inverted_color = self.invert_color(color_under_cursor)
                        self.draw_pixel(canvas, right_coord, inverted_color, inverted_color, "shape", borders)
                    else:
                        self.draw_pixel(canvas, right_coord, "", color, "shape", borders)



                line_between = DDA(left_rect_side[i][0], left_rect_side[i][1], right_rect_side[i][0], right_rect_side[i][1])
                for j in range(len(line_between)):
                    coord = self.coord_to_str(line_between[j][0], line_between[j][1])


                    if in_bounds(line_between[j][0], line_between[j][1], self.pixel_canvas_width, self.pixel_canvas_height):
                        color_under_cursor = self.pixel_grid[ line_between[j][1] ][ line_between[j][0] ]
                        if color_under_cursor:
                            self.temp_pixels.append(line_between[j])
                            inverted_color = self.invert_color(color_under_cursor)
                            self.draw_pixel(canvas, coord, inverted_color, inverted_color, "shape", borders)
                        
                        else:
                            #this would grid every pixel in the thing without the if
                            #as of now it just does the top and the bottom
                            if i == 0 or i == len(left_rect_side) - 1:
                                self.draw_pixel(canvas, coord, "", color, "shape", borders)

            #repetitive as going right to left covers most of not all of the area
            '''
            for i in range(len(top_rect_side)):
                top_coord = self.coord_to_str(top_rect_side[i][0], top_rect_side[i][1])
                bottom_coord = self.coord_to_str(bottom_rect_side[i][0], bottom_rect_side[i][1])
                
                
                

                line_between = DDA(top_rect_side[i][0], top_rect_side[i][1], bottom_rect_side[i][0], bottom_rect_side[i][1])

                color_under_cursor = self.pixel_grid[ top_rect_side[i][1] ][ top_rect_side[i][0] ]
                if color_under_cursor:
                    self.temp_pixels.append(top_rect_side[i])
                    inverted_color = self.color_inversion(top_rect_side[i][0], top_rect_side[i][1])
                    self.draw_pixel(canvas, left_coord, '', inverted_color, "shape", borders)
                else:
                    self.draw_pixel(canvas, top_coord, '', color, "shape", borders)

                color_under_cursor = self.pixel_grid[ bottom_rect_side[i][1] ][ bottom_rect_side[i][0] ]
                if color_under_cursor:
                    self.temp_pixels.append(bottom_rect_side[i])
                    inverted_color = self.color_inversion(bottom_rect_side[i][0], bottom_rect_side[i][1])
                    self.draw_pixel(canvas, left_coord, '', inverted_color, "shape", borders)

                else:
                    self.draw_pixel(canvas, bottom_coord, '', color, "shape", borders)

                    
                
                for j in range(len(line_between)):
                    coord = self.coord_to_str(line_between[j][0], line_between[j][1])
                    #self.draw_pixel(canvas, coord, '', color, "shape", borders)
                    

                    color_under_cursor = self.pixel_grid[line_between[j][1]][line_between[j][0]]
                    if color_under_cursor:
                        self.temp_pixels.append(line_between[j])
                    #this would grid every pixel in the thing
                    #else:
                    #    self.draw_pixel(canvas, coord, "", color, "shape", borders)

                '''
    
    def select_release(self, x, y, canvas, color, borders):
        #canvas.delete("shape")
        #print("select")
        self.last_pixel.clear()
        if polygon_point(borders, x, y):
            self.temp_colors = [self.pixel_grid[pxl[1]][pxl[0]] for pxl in self.temp_pixels]

    def lasso_click(self, x, y, canvas, color, borders):
        #keeps tract of start
        #DDA line between start and current
        #Fill in area edges
        print("lasso")

        #drawing an undecided line between two points
        self.last_pixel.clear()
        self.temp_pixels.clear()
        self.temp_colors.clear()
        
        #self.render_borders(canvas)
        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                self.temp_pixels.append([x_pixel, y_pixel])
                if self.pixel_grid[y_pixel][x_pixel]:
                    inverted_color = self.invert_color(self.pixel_grid[y_pixel][x_pixel])
                    self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                else:
                    self.draw_pixel(canvas, current_coord, "", color, "lasso", borders)
                
                #self.pixel_grid[y_pixel][x_pixel] = color

    def lasso_press(self, x, y, canvas, color, borders):
        #print("lasso")
        if polygon_point(borders, x, y):
            
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    #first pixel
                    current_coord = self.coord_to_str(x_pixel, y_pixel)
                    #
                    if self.pixel_grid[y_pixel][x_pixel]:
                        inverted_color = self.invert_color(self.pixel_grid[y_pixel][x_pixel])
                        self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                    else:
                        self.draw_pixel(canvas, current_coord, "", color, "lasso", borders) 

                    canvas.delete("lassoline")
                    #beginning to end line
                    for pixel in self.stroke_pixels:
                        px = pixel[0]
                        py = pixel[1]
                        current_coord = self.coord_to_str(pixel[0], pixel[1])
                        
                    if self.temp_pixels:
                        self.stroke_pixels = DDA(self.temp_pixels[0][0], self.temp_pixels[0][1], self.temp_pixels[-1][0], self.temp_pixels[-1][1])
                        for pixel in self.stroke_pixels:
                            current_coord = self.coord_to_str(pixel[0], pixel[1])
                            if self.pixel_grid[pixel[1]][pixel[0]]:
                                inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                                self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lassoline", borders)
                            else:
                                self.draw_pixel(canvas, current_coord, "", color, "lassoline", borders)

                        #draw drag
                        if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                            between = DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])
                            for pixel in between:
                                #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))

                                #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                                #self.pixel_grid[pixel[1]][pixel[0]] = color     
                                self.temp_pixels.append([pixel[0], pixel[1]])
                                current_coord = self.coord_to_str(pixel[0], pixel[1])
                                if self.pixel_grid[pixel[1]][pixel[0]]:
                                    inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                                    self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lassoline", borders) 
                                else:
                                    self.draw_pixel(canvas, current_coord, "", color, "lassoline", borders) 
                            
            #canvas.delete("lassoline")
                            
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]
         
    def lasso_release(self, x, y, canvas, color, borders):
        #print("lasso")
        if self.temp_pixels:
           
            #print(self.temp_pixels)
            #drawing a line between the beginning and end pixel
            self.temp_pixels.extend(self.stroke_pixels)
            #sorting by y coordinate
            self.temp_pixels = sorted(self.temp_pixels, key=lambda pair: pair[1])
            #print(self.temp_pixels)
            lines = []
            i = 0
            j = 0
            #getting the coordinates of the empty space in in the lasso
            while j < len(self.temp_pixels):
                #detects when y changes and makes a line between the coordinate with smallest x value and the largest. 
                if self.temp_pixels[i][1] != self.temp_pixels[j][1]:
                    lines.extend([self.temp_pixels[i]] + DDA(self.temp_pixels[i][0], self.temp_pixels[i][1], self.temp_pixels[j - 1][0], self.temp_pixels[j - 1][1]))
                    i = j

                    
                j = j + 1

            
            

            #filling out the missed spots
            filled_pixels = []
            self.temp_pixels.extend(lines)
            for pixel in self.temp_pixels:
                if in_bounds(pixel[0] , pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    current_coord = self.coord_to_str(pixel[0], pixel[1])
                    color_under_cursor = self.pixel_grid[ pixel[1] ][ pixel[0] ]
                    
                    if color_under_cursor:
                        if pixel not in filled_pixels:
                            filled_pixels.append(pixel)
                            inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                            self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders) 
                    
                    #this was to show all the pixels in temp pixels
                    #self.draw_pixel(canvas, self.coord_to_str(pixel[0], pixel[1]), "", color, "lasso", borders) 
            
            self.temp_pixels = filled_pixels
 
            
            self.temp_colors = [self.pixel_grid[pxl[1]][pxl[0]] for pxl in self.temp_pixels]
            self.last_pixel.clear()
            self.stroke_pixels.clear()

    #with the selection fucntions temp colors should be filled after their released and their pixels moved accordingly
    #moves the selected and the lasso selected
    def select_move_click(self, x, y, canvas, color, borders):
        #print("selectmove")
        if polygon_point(borders, x, y):
            canvas.delete("lasso")
            canvas.delete("lassoline")
            canvas.delete("shape")
            #so it just doesn't duplicate pixels
            for i in range(len(self.temp_pixels)):
                pixel = self.temp_pixels[i]        
                px = pixel[0]
                py = pixel[1] 
                current_coord = self.coord_to_str(px, py)
                canvas.delete(current_coord)
                current_color = self.pixel_grid[py][px]
                if current_color:
                    inverted_color = self.invert_color(current_color)
                    self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "shape", borders)
                    self.pixel_grid[py][px] = None
                    current_coord = self.coord_to_str(px, py)
                    if self.pixel_coords.get(current_coord):
                        del self.pixel_coords[current_coord]

    def move_click(self, x, y, canvas, color, borders):
        #print("move")
        self.last_pixel.clear()
        if polygon_point(borders, x, y):
            '''
            self.temp_colors.clear()
            self.temp_pixels.clear()
            self.temp_pixels = [[x, y] for y in range(len(self.pixel_grid)) for x in range(len(self.pixel_grid[y])) if self.pixel_grid[y][x]]
            self.temp_colors = [self.pixel_grid[pxl[1]][pxl[0]] for pxl in self.temp_pixels]
            '''
            self.temp_colors.clear()
            self.temp_pixels.clear()
            canvas.delete("all")
            for y in range(len(self.pixel_grid)):
                for x in range(len(self.pixel_grid[y])):
                    if self.pixel_grid[y][x]:
                        current_coord = self.coord_to_str(x, y)
                        current_color = self.pixel_grid[y][x]
                        self.draw_pixel(canvas, current_coord, current_color, current_color, "shape", borders)
                        self.temp_pixels.append([x, y])
                        self.temp_colors.append(current_color)
                    else:
                        continue
                        

            #x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y)

    def move_press(self, x, y, canvas, color, borders):
        #print("move")
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            #making sure current pixel and last pixel are in pixel coords so line_line_intersect works
            #gets deleted by render_grid
            
            del_coord = self.coord_to_str(x_pixel, y_pixel)
            self.draw_pixel(canvas, del_coord, "", "", "zip", borders) 
            if self.last_pixel:
                del_coord = self.coord_to_str(self.last_pixel[0], self.last_pixel[1])
                self.draw_pixel(canvas, del_coord, "", "", "zip", borders) 

            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                        
                        if self.last_pixel:
                            #strange error temp pixels forgotten
                            #print(len(self.temp_pixels))
                            x1, y1, x2, y2, x3, y3, x4, y4 = self.pixel_to_canvas(self.last_pixel[0], self.last_pixel[1])
                            cx1, cy1 = line_line_intersection(
                                x1, y1,
                                x3, y3,
                                x2, y2,
                                x4, y4 
                            )

                            x1, y1, x2, y2, x3, y3, x4, y4 = self.pixel_to_canvas(x_pixel, y_pixel)
                            cx2, cy2 = line_line_intersection(
                                x1, y1,
                                x3, y3,
                                x2, y2,
                                x4, y4 
                            )

                            #real canvas coordinates
                            dx, dy = cx2 - cx1, cy2 - cy1
                            canvas.move("shape", dx, dy)
                        

                        
                        
                            #pixel grid coordinates
                            dx, dy = x_pixel - self.last_pixel[0], y_pixel - self.last_pixel[1] 
                            
                            for i in range(len(self.temp_pixels)):
                                pixel = self.temp_pixels[i]
                                new_px = pixel[0] + dx
                                new_py = pixel[1] + dy
                                
                                old_px = pixel[0]
                                old_py = pixel[1]

                                pixel[0] = new_px
                                pixel[1] = new_py

                                

                                if not in_bounds(old_px, old_py, self.pixel_canvas_width, self.pixel_canvas_height): 
                                    continue

                                if not in_bounds(new_px, new_py, self.pixel_canvas_width, self.pixel_canvas_height): 
                                    continue


                                if color:
                                    #moves all pixels
                                    self.pixel_grid[old_py][old_px] = None
                                    
                                    
                                else:
                                    #moves selected pixels
                                    if not self.pixel_grid[old_py][old_px] and not self.pixel_grid[new_py][new_px]:
                                    
                                        #current_coord = self.coord_to_str(old_px, old_py)
                                        #if self.pixel_coords.get(current_coord):
                                        #    del self.pixel_coords[current_coord]
                                        self.pixel_grid[old_py][old_px] = None

                                '''
                                current_coord = self.coord_to_str(old_px, old_py)
                                if self.pixel_coords.get(current_coord):
                                    new_coord = self.coord_to_str(new_px, new_py)
                                    for key in self.pixel_coords[current_coord]:

                                    self.pixel_coords[new_coord] = 
                                    del self.pixel_coords[current_coord]
                                '''
                            canvas.update_idletasks()
                            
            canvas.delete("zip")
            
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]
 
    def move_release(self, x, y, canvas, color, borders):
        canvas.delete("lasso")
        canvas.delete("lassoline")
        canvas.delete("shape")

        #print("move")
        for i in range(len(self.temp_pixels)):
            pixel = self.temp_pixels[i]
            px = pixel[0]
            py = pixel[1]
            current_color = self.temp_colors[i]
            if in_bounds(px, py, self.pixel_canvas_width, self.pixel_canvas_height): 
                self.pixel_grid[py][px] = current_color
                current_coord = self.coord_to_str(px, py)
                self.draw_pixel(canvas, current_coord, current_color, current_color, current_coord, borders) 

        self.temp_pixels.clear()
        self.temp_colors.clear()
        self.last_pixel.clear()
  
    def brush_click(self, x, y, canvas, color, borders):
        #print("draw erase 1")
        self.last_pixel.clear()
        #print(self.canvas_to_pixel(canvas, x, y))
        #self.render_borders(canvas)
        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            #
            
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                
                
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                
                #print(x_pixel, y_pixel)
                
               
                
                #the a normal color is a hexcode while the background color is a color name
                
                if color:
                    
                    self.pixel_grid[y_pixel][x_pixel] = color
                    self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
                    #self.draw_pixel(canvas, current_coord, '', color, current_coord) 
                else:
                    #pass
                    self.pixel_grid[y_pixel][x_pixel] = None
                    if self.pixel_coords.get(current_coord):
                        del self.pixel_coords[current_coord]
                    
                    canvas.delete(current_coord)
                    #self.draw_pixel(canvas, current_coord, color[:7], color[:7], current_coord, borders) 
                
    def brush_press(self, x, y, canvas, color, borders):
        #print(x, y)
        #print("draw erase")
        #print(self.last_pixel, " ", [x_pixel, y_pixel])
        #print(self.canvas_to_pixel(canvas, x, y))
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    current_coord = self.coord_to_str(x_pixel, y_pixel)
                    if color:
                        self.pixel_grid[y_pixel][x_pixel] = color
                        self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
                    else:
                        self.pixel_grid[y_pixel][x_pixel] = None
                        if self.pixel_coords.get(current_coord):
                            del self.pixel_coords[current_coord]
                        canvas.delete(current_coord)
                        
                    #self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
                    #if x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                    
                    if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                        between = DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])
                        for pixel in between:
                            #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))

                            #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                            current_coord = self.coord_to_str(pixel[0], pixel[1])
                            
                            if color:
                                self.pixel_grid[pixel[1]][pixel[0]] = color  
                                self.draw_pixel(canvas, current_coord, color, color, current_coord, borders)
                            else:
                                self.pixel_grid[pixel[1]][pixel[0]] = None
                                if self.pixel_coords.get(current_coord):
                                    del self.pixel_coords[current_coord]
                                canvas.delete(current_coord)
                                #self.draw_pixel(canvas, current_coord, color[:7], color[:7], current_coord, borders) 
                               
                            

                            
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]

    def place_anchor(self, x, y, canvas, color, borders):
        self.anchor_pixel.clear()
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if len(self.anchor_pixel) == 0:
                self.anchor_pixel = [x_pixel, y_pixel]
                self.canvas.delete("anchor")
                cx1 = x - 10 
                cy1 =  y - 10
                cx2 = cx1 + 10  * 2
                cy2 = cy1 + 10  * 2
                
                self.canvas.create_oval(
                                    cx1, cy1, 
                                    cx2, cy2, 
                                    outline=color,
                                    tags=("anchor")
                                    )

        if self.temp_pixels:
            pass
            

    def bucket_fill(self, x, y, canvas, color, borders):
        #an edited version of the flood fill

        if not polygon_point(borders, x, y):
            return
        
        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width

        x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)

        color_under_cursor = self.pixel_grid[y_pixel][x_pixel]

        if color_under_cursor == color:
            return


        #BFS flood fill
        #queue
        print("W:{} H:{} X:{} Y:{} XPix:{} YPix:{}".format(self.canvas_width, self.canvas_height , x, y, x_pixel, y_pixel))
        visited = {}
        queue = []
        queue.append((x_pixel, y_pixel))
        
        #print(queue)
        i = 0
        max_area = 32 * 32
        while queue and len(visited) < max_area:
            #print(queue)
            
            
            #print("inside")
            cur = queue.pop(0)
            
            if not in_bounds(cur[0], cur[1], self.pixel_canvas_width, self.pixel_canvas_height) or self.pixel_grid[ cur[1] ][ cur[0] ] != color_under_cursor: 
                continue
            else:
                #if i == (self.pixel_canvas_width - 1) * (self.pixel_canvas_height - 1):
                #    break
                #print("doin")
                current_coord = self.coord_to_str(cur[0], cur[1])

                north_coord = self.coord_to_str(cur[0], cur[1] + 1)
                south_coord = self.coord_to_str(cur[0], cur[1] - 1)
                east_coord = self.coord_to_str(cur[0] + 1, cur[1])
                west_coord = self.coord_to_str(cur[0] - 1, cur[1])

             

                #self.display_2d(self.pixel_grid)
                
                if not visited.get(east_coord):
                    queue.append((cur[0] + 1, cur[1]))

                if not visited.get(west_coord):
                    queue.append((cur[0] - 1, cur[1]))

                if not visited.get(north_coord):
                    queue.append((cur[0], cur[1] + 1))

                if not visited.get(south_coord):
                    queue.append((cur[0], cur[1] - 1))

      
                
                
                #if not visited.get(current_coord):
                visited[current_coord] = True
                self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
                self.pixel_grid[cur[1]][cur[0]] = color
                
                
            

                
                canvas.update_idletasks()
            
                #print(i, self.color, cur)
                #i += 1

        
        visited.clear()

        #updates the canvas likely makes it so not as much in memory
            
        #self.update_idletasks()
            
    

class Animator(ttk.Frame):
    def __init__(self, parent, c_width, c_height, p_width, p_height):
        super().__init__(parent)
        #the color selection palette


        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        self.canvas_width = c_width
        self.canvas_height = c_height
        #the reason this has an underscore is to 
        self.canvas_color = "#808080"
        self.bg_color = "#FFFFFF"
        self.pixels_to_paste = []
        self.colors_to_paste = []
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #The main canvas
        self.main_frame = tk.Frame(self) 
        self.canvas = tk.Canvas(self.main_frame, 
                                width=c_width,
                                height=c_height, 
                                bg=self.canvas_color) 
        self.canvas_s_barv = tk.Scrollbar(self.main_frame, orient='vertical')
        self.canvas_s_barh = tk.Scrollbar(self.main_frame, orient='horizontal')

        self.canvas_s_barv.config(command=self.canvas.yview)
        self.canvas_s_barh.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.canvas_s_barv.set)
        self.canvas.config(xscrollcommand=self.canvas_s_barh.set)
        self.canvas.config(scrollregion=(0,0,c_width,c_height))

        self.angle = 180
        self.rotation_lbl = tk.Label(text="Rotation")
        self.rotation_iv = tk.IntVar(value=0)
        self.rotation_scl = tk.Scale(self.main_frame, variable=self.rotation_iv, to=360, from_=0, orient="vertical")
        self.rotation_widgets = [self.rotation_lbl, self.rotation_scl]

        #self.scaling_dv = tk.DoubleVar()
        #self.scaling_scl = tk.Scale(self.main_frame)
        
        

        self.color = "#000000"
        

        self.frame_idx = 0
        self.key_frame_collection = []
        self.current_key_frame = self.get_key_frame(self.frame_idx)
        
        
        



        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        self.options_frame = tk.Frame(self)

        self.onion_iv = tk.BooleanVar(value=True)
        self.onion_next = 3
        self.onion_prev = 3
        self.onion_prev_lbl = ttk.Label(self.options_frame, text="Onion Prev")
        self.onion_next_lbl = ttk.Label(self.options_frame, text="Onion Next")
        self.onion_prev_sb = ttk.Spinbox(self.options_frame, from_ = 0, to = 3, increment=1, width=10, command=self.render_canvas)
        self.onion_next_sb = ttk.Spinbox(self.options_frame, from_ = 0, to = 3, increment=1, width=10, command=self.render_canvas)
        self.onion_prev_sb.set(1)
        self.onion_next_sb.set(1)
        self.onion_cb = ttk.Checkbutton(self.options_frame, text="Onion Skin", variable=self.onion_iv, command=self.render_canvas)


        self.debug_btn = ttk.Button(self.options_frame, text="Debug", command=self.debug)
        self.clear_btn = ttk.Button(self.options_frame, text="Clear Frame", command=self.clear_frame)
        self.wipeout_btn = ttk.Button(self.options_frame, text="Clear All", command=self.clear_frames)
        self.save_btn = ttk.Button(self.options_frame, text="Save Frame", command=self.save_frame)
        self.gif_btn = ttk.Button(self.options_frame, text="Save Gif", command=self.save_gif)
        self.color_btn = ttk.Button(self.options_frame, text="Color", command=self.choose_color)
        self.canvas_color_btn = ttk.Button(self.options_frame, text="Canvas Color", command=self.change_canvas_color)
        self.resize_btn = ttk.Button(self.options_frame, text="Resize", command=self.on_pixel_grid_resize)
        self.open_btn = ttk.Button(self.options_frame, text="Import", command=self.open_file)

        self.bg_color_iv = tk.BooleanVar(value=False)
        self.bg_color_cb = ttk.Checkbutton(self.options_frame, text="Save Color", variable=self.bg_color_iv, command=self.render_canvas)
        self.bg_color_btn = tk.Button(self.options_frame, text="BG Color", command=self.change_bg_color, bg=self.bg_color, fg=self.current_key_frame.invert_color(self.bg_color))

        #self.nav_frame = ttk.Frame(self)
        self.cpy_btn =  ttk.Button(self.options_frame, 
                                   text="Clone Frame", 
                                   command=self.duplicate_key_frame
                                   )
        self.next_btn = ttk.Button(self.options_frame,
                                   text="Next Frame",
                                   command=self.next_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.prev_btn = ttk.Button(self.options_frame,
                                   text="Prev Frame", 
                                   command=self.prev_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.delete_btn = ttk.Button(self.options_frame,
                                   text="Delete Frame",
                                   command=self.delete_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.add_btn = ttk.Button(self.options_frame, 
                                   text="Add Frame", 
                                   command=self.add_key_frame, 
                                   #width=c_width/16
                                   
                                   #state="disabled"
                                   )
      
        

        
        options_arrangement = [

            [self.color_btn, self.canvas_color_btn],#self.debug_btn
            [self.clear_btn, self.wipeout_btn],
            [self.prev_btn,  self.next_btn],
            [self.delete_btn, self.add_btn],
            [self.debug_btn, self.cpy_btn],
            [self.save_btn, self.gif_btn ],
            [self.resize_btn, self.open_btn],
            [self.bg_color_cb, self.bg_color_btn],
            [self.onion_cb, None],
            [self.onion_prev_lbl, self.onion_prev_sb],
            [self.onion_next_lbl, self.onion_next_sb],
            


         
           
        ]




        

        
        
        
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        #https://blog.teclado.com/tkinter-scrollable-frames/
        #the widget below the only widget that has to be gridded in arrangement
        self.timeline_frame = tk.Frame(self)

        self.timeline_cell_size = 100
        self.timeline_canvas = tk.Canvas(self.timeline_frame, width=self.timeline_cell_size, height=c_height) #about the width of a listbox with no specificied width and heoght
        self.timeline_sb_y = ttk.Scrollbar(self.timeline_frame, orient='vertical', command=self.timeline_canvas.yview)
        self.timeline_scroll_frame = tk.Frame(self.timeline_canvas)
        
        
        #below keeps track for the dynamic checkboxes generated
        #will be the edges and whether they're connected tp other edges,
        # a dictionary of dictionarys and bools 
        self.timeline_widget_list = []
        #collection of th shown checkbox, deleted and regenerated frequently
        self.timeline_img_list = []
        
        
        self.timeline_scroll_frame.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(
                scrollregion=self.timeline_canvas.bbox("all")
            )
        )
        
        self.timeline_canvas.create_window((0, 0), window=self.timeline_scroll_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.timeline_sb_y.set)
        #self.edge_scrollbar_y.config(command=self.self.edge_canvas.yview)
        
        #self.timeline_canvas.pack(fill="y", expand=True) #.grid(row=0, column=0)
        #self.timeline_sb_y.pack(fill="y", expand=True)  #.grid(row=0, column=1, sticky="NS")
        
        self.timeline_canvas.pack(side="left", fill="y", expand=True)
        self.timeline_sb_y.pack(side="left", fill="y", expand=True)
        
        #Test
        '''
        options = ["Option " + str(i) for i in range(1,50)]
        colors = {
            "AliceBlue": "#F0F8FF",
            "AntiqueWhite": "#FAEBD7",
            "Aqua": "#00FFFF",
            "Aquamarine": "#7FFFD4",
            "Azure": "#F0FFFF",
            "Beige": "#F5F5DC",
            "Bisque": "#FFE4C4",
            "Black": "#000000",
            "BlanchedAlmond": "#FFEBCD",
            "Blue": "#0000FF",
            "BlueViolet": "#8A2BE2",
            "Brown": "#A52A2A",
            "BurlyWood": "#DEB887",
            "CadetBlue": "#5F9EA0",
            "Chartreuse": "#7FFF00",
            "Chocolate": "#D2691E",
            "Coral": "#FF7F50",
            "CornflowerBlue": "#6495ED",
            "Cornsilk": "#FFF8DC",
            "Crimson": "#DC143C",
            "Cyan": "#00FFFF",
            "DarkBlue": "#00008B",
            "DarkCyan": "#008B8B",
            "DarkGoldenRod": "#B8860B",
            "DarkGray": "#A9A9A9",
            "DarkGreen": "#006400",
            "DarkKhaki": "#BDB76B",
            "DarkMagenta": "#8B008B",
            "DarkOliveGreen": "#556B2F",
            "DarkOrange": "#FF8C00",
            "DarkOrchid": "#9932CC",
            "DarkRed": "#8B0000",
            "DarkSalmon": "#E9967A",
            "DarkSeaGreen": "#8FBC8F",
            "DarkSlateBlue": "#483D8B",
            "DarkSlateGray": "#2F4F4F",
            "DarkTurquoise": "#00CED1",
            "DarkViolet": "#9400D3",
            "DeepPink": "#FF1493",
            "DeepSkyBlue": "#00BFFF",
            "DimGray": "#696969",
            "DodgerBlue": "#1E90FF",
            "FireBrick": "#B22222",
            "FloralWhite": "#FFFAF0",
            "ForestGreen": "#228B22",
            "Fuchsia": "#FF00FF",
            "Gainsboro": "#DCDCDC",
            "GhostWhite": "#F8F8FF",
            "Gold": "#FFD700",
            "GoldenRod": "#DAA520"
        }


        i = 0
        ckeys = list(colors.keys())
        for option in options:
            var = tk.BooleanVar()
            #chk = tk.Checkbutton(self.timeline_scroll_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
            chk = tk.Canvas(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.anim_canvas_height, bg=random.choice(ckeys)).grid(row=i, column=1)
            #chk = tk.Button(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.anim_canvas_height, bg=random.choice(ckeys)).grid(row=i, column=1)
            i += 1
        '''
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #Preview Canvas
        self.preview_frame = tk.Frame(self)
        self.preview_canvas = tk.Canvas(self.preview_frame, width=self.timeline_cell_size * 2, height=self.timeline_cell_size * 2, bg=self.canvas_color)
        self.fps_iv = tk.IntVar(value=1)
        self.fps_lbl = tk.Label(self.preview_frame, text="FPS")
        self.fps_scl = tk.Scale(self.preview_frame, from_=1, to=24, variable=self.fps_iv,orient="horizontal", command=None, state="active")
        self.play_img = tk.PhotoImage(file="icons\\play_arrow_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(6, 6)
        self.playing = True
        self.play_btn = tk.Button(self.preview_frame, text="Play", image=self.play_img, command=self.play_preview) 
        self.preview_idx = 0
        self.preview_id = ""
        self.preview_img_list = []
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #Drawing Button Type
        self.btn_frame = tk.Frame(self)
        
        self.pen_img = tk.PhotoImage(file="icons\\edit_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.pen_bn = tk.Button(self.btn_frame, 
                                 text="Draw", 
                                 image=self.pen_img,
                                 ) 
        CreateToolTip(self.pen_bn, "Pen Tool")
        
        self.fill_img = tk.PhotoImage(file="icons\\format_color_fill_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.fill_bn = tk.Button(self.btn_frame, 
                                 text="Bucket", 
                                 image=self.fill_img
                                 ) 
        CreateToolTip(self.fill_bn, "Bucket Tool")
        
        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_bn = tk.Button(self.btn_frame, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_bn, "Eraser Tool")
        

        
        self.rect_img = tk.PhotoImage(file="icons\\rectangle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_bn = tk.Button(self.btn_frame,  
                                 text="Rectangle", 
                                 image=self.rect_img
                                 ) 
        CreateToolTip(self.rect_bn, "Rectangle Tool")
        
        self.circ_img = tk.PhotoImage(file="icons\\circle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.circ_bn = tk.Button(self.btn_frame, 
                                 text="Circle", 
                                 image=self.circ_img
                                 ) 
        CreateToolTip(self.circ_bn, "Circle Tool")
        
        self.move_img = tk.PhotoImage(file="icons\\back_hand_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.move_bn = tk.Button(self.btn_frame, 
                                 text="Move", 
                                 image=self.move_img
                                 ) 
        CreateToolTip(self.move_bn, "Move Tool")
        
        self.lasso_sel_img = tk.PhotoImage(file="icons\\lasso_select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.lasso_sel_bn = tk.Button(self.btn_frame, 
                                 text="Lasso", 
                                 image=self.lasso_sel_img
                                 ) 
        CreateToolTip(self.lasso_sel_bn, "Lasso Selection")
        
        self.rect_sel_img = tk.PhotoImage(file="icons\\select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_sel_bn = tk.Button(self.btn_frame, 
                                 text="Select", 
                                 image=self.rect_sel_img
                                 ) 
        CreateToolTip(self.rect_sel_bn, "Rectangle Selection")
        
        self.line_img = tk.PhotoImage(file="icons\\border_color_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.line_bn = tk.Button(self.btn_frame, 
                                 text="Stroke", 
                                 image=self.line_img 
                                 ) 
        CreateToolTip(self.line_bn, "Stroke Tool")
        
        self.picker_img = tk.PhotoImage(file="icons\\colorize_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.picker_bn = tk.Button(self.btn_frame,  
                                 text="Picker", 
                                 image=self.picker_img
                                 ) 
        CreateToolTip(self.picker_bn, "Color Picker")

        self.shear_h_img = tk.PhotoImage(file="icons\\arrow_range_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shear_h_bn = tk.Button(self.btn_frame,  
                                 text="H-Shear", 
                                 image=self.shear_h_img
                                 ) 
        CreateToolTip(self.shear_h_bn, "Shear Horizontal \n(Mousewheel)")

        self.shear_v_img = tk.PhotoImage(file="icons\height_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shear_v_bn = tk.Button(self.btn_frame,  
                                 text="V-Shear", 
                                 image=self.shear_v_img
                                 ) 
        CreateToolTip(self.shear_v_bn, "Shear Vertical \n(Mousewheel)")

        self.rotate_img = tk.PhotoImage(file="icons\\rotate_left_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rotate_bn = tk.Button(self.btn_frame,  
                                 text="Rotate", 
                                 image=self.rotate_img
                                 ) 
        CreateToolTip(self.rotate_bn, "Rotate \n(Mousewheel)")

        

        self.palette_img = tk.PhotoImage(file="icons\\palette_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.palette_bn = tk.Button(self.btn_frame,  
                                 text="Draw", 
                                 image=self.palette_img,
                                 state="disabled",
                                 bg = self.color
                                 ) 
        CreateToolTip(self.palette_bn, "Selected Color")
        
        self.pen_bn.config(command=lambda:self.select_mode(self.pen_bn))
        self.erase_bn.config(command=lambda:self.select_mode(self.erase_bn))
        self.rect_bn.config(command=lambda:self.select_mode(self.rect_bn))
        self.rect_sel_bn.config(command=lambda:self.select_mode(self.rect_sel_bn))
        self.picker_bn.config(command=lambda:self.select_mode(self.picker_bn))
        self.line_bn.config(command=lambda:self.select_mode(self.line_bn))
        self.move_bn.config(command=lambda:self.select_mode(self.move_bn))
        self.circ_bn.config(command=lambda:self.select_mode(self.circ_bn))
        self.lasso_sel_bn.config(command=lambda:self.select_mode(self.lasso_sel_bn))
        self.fill_bn.config(command=lambda:self.select_mode(self.fill_bn))
        self.shear_h_bn.config(command=lambda:self.select_mode(self.shear_h_bn))
        self.shear_v_bn.config(command=lambda:self.select_mode(self.shear_v_bn))
        self.rotate_bn.config(command=lambda:self.select_mode(self.rotate_bn))


        self.drawing_widgets = [
            self.pen_bn     , self.line_bn,
            self.erase_bn   , self.move_bn,
            self.rect_bn    , self.circ_bn,
            self.rect_sel_bn, self.lasso_sel_bn,
            self.picker_bn  ,  self.fill_bn,
            self.shear_h_bn, self.shear_v_bn,
            self.rotate_bn
        ]

        btn_arrangement = [

            [self.pen_bn     , self.line_bn],
            [self.erase_bn   , self.move_bn],
            [self.rect_bn    , self.circ_bn],
            [self.rect_sel_bn, self.lasso_sel_bn],
            [self.picker_bn  ,  self.fill_bn],
            [self.shear_h_bn, self.shear_v_bn],
            [self.rotate_bn,     self.palette_bn]
        ]

        

        #states
        self.mode = "Draw"
        self.direction = ""
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #grid, pack, and place
        arrange_widgets(options_arrangement)
        arrange_widgets(btn_arrangement)
        self.sub_wn = None
        
        

       
        
        
        self.btn_frame.pack(side="left", fill="y")
        self.timeline_frame.pack(side="left", fill="y")
        self.main_frame.pack(side="left", fill="both", expand=True)
        self.preview_frame.pack(side="top", fill="both", anchor="center")
        self.options_frame.pack(side="top", fill="both", anchor="center")
        
        #Preview frame widgets
        self.preview_canvas.pack(side="top", anchor="center")
        self.play_btn.pack(side="left", anchor="center")
        self.fps_lbl.pack(side="left", anchor="center")
        self.fps_scl.pack(side="left", fill="x", expand=True)
        
        
        #main frame's widgets: I used pack to have them expand
        #main widget parts: the order they were backed in matters
        #the other frame's widgets were gridded with grid
        #self.scaling_scl.pack(side="bottom", fill="x")
        
        self.canvas_s_barh.pack(side="bottom", fill="x")
        #packing the rotation scale under the canvas horizontal scrollwheel, packed and unpacked based on 
        #whether the anchor/rotation button is selected
        
        self.canvas.pack(side="left", fill="both", anchor= "center",expand=True)
        self.canvas_s_barv.pack(side="left", fill="y")
        #self.rotation_scl.pack(side="bottom", fill="y")
        #self.rotation_lbl.pack(side="bottom", fill="y", expand=True)
        

        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        
        self.pivot_matrix = np.eye(3, dtype=np.float64)
        self.matrix_pivot = np.eye(3, dtype=np.float64)

        
        self.select_mode(self.pen_bn)

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_lmb_release)

        self.canvas.bind("<ButtonPress-3>", self.on_canvas_rmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        self.canvas.bind("<ButtonRelease-3>", self.on_canvas_rmb_release)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel_scroll)
        #self.canvas.bind("<ButtonRelease-2>", self.on_mousewheel_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.undo_stack = []
        self.redo_queue = []
        
        
        '''
         variable=self.rotation_angle,
            from_ = 0,
            to = 360,
            orient = "horizontal",
            length=
            command = lambda:self.resize_pixels()
        '''

        
        
        
        
        
        #self.canvas.config()
        

        
        
        #thr following attributes are for the four borders, anything else is temporary
        self.top_left = Vertex(
            -1,
            -1,
        )

        self.bottom_left = Vertex(
            
            -1,
            -1,
        )

        self.bottom_right = Vertex(
            -1,
            -1,
        )

        

        self.top_right = Vertex(
            -1,
            -1,
        )
        
        self.borders = []
        
        self.borders = self.set_borders(c_width, c_height, p_width, p_height)
        
        self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale = self.set_scaling(self.canvas)
        self.pixel_scale_og = self.pixel_scale
        #adding the first frame to the timeline
        #self.update_animation_timeline()
        
        self.update_key_frame(self.frame_idx)
        self.render_borders()
        print("Scales Max, Current, Min: ", self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale)
    
        #Turns playing false to true and true to false
        self.play_preview()
        #self.scaling_dv.set(self.pixel_scale)
        #self.scaling_scl.config(from_=self.min_pixel_scale, to=self.max_pixel_scale, variable=self.scaling_dv,orient="horizontal", command=self.resize_pixels)

        self.current_directory = os.getcwd()
        #self.selected_file = ""
       
    def set_scaling(self, canvas):
        min_scale, scale, max_scale = -1, -1, -1
        border_x = self.borders[0]
        border_y = self.borders[1]
        border_width = self.borders[4] - self.borders[0]
        border_height = self.borders[5] - self.borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width
        min_scale = 1
        max_scale = 100 #min(self.canvas_width, self.canvas_height)
        self.max_pixel_scale, self.pixel_scale, self.min_pixel_scale = max_scale, scale, min_scale
        return max_scale, scale, min_scale

    #border focused methods

    def set_borders(self,canvas_width, canvas_height, pixel_width, pixel_height):
        #these exists so pixels are always square
        c_dimension = max(canvas_width, canvas_height)
        diagonal =  math.sqrt(pixel_width ** 2 + pixel_height ** 2) #distance_to(0, 0, pixel_width, pixel_height) 
        ratio_x = (pixel_width/diagonal) 
        ratio_y = (pixel_height/diagonal)
        #the rest of the area iis space for rotations

        
        #top left
        x0 = canvas_width  * (1 - ratio_x)/2
        y0 = canvas_height * (1 - ratio_y)/2
        #bottom left
        x1 = x0 
        y1 = y0 + c_dimension * ratio_y
        #bottom right
        x2 = x0 + c_dimension * ratio_x
        y2 = y0 + c_dimension * ratio_y
        #top right
        x3 = x0 + c_dimension * ratio_x
        y3 = y0 

        #

 

        self.top_left.set_coords(
            x0,
            y0,
        )

        self.bottom_left.set_coords(
            
            x1,
            y1,
        )

        self.bottom_right.set_coords(
            x2,
            y2,
        )

        

        self.top_right.set_coords(
            x3,
            y3,
        )


        
        
        self.pixel_vertices = []
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]

    def get_borders(self):
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]

    def get_borders_center(self):
        return line_line_intersection(
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        )
    
    def render_borders(self, fill = ''):
        #self.canvas.delete("shapes")
        self.borders = self.get_borders()
        self.canvas.create_polygon(self.borders,
                                    fill = fill,
                                    outline='blue',
                                    #tags=("shapes")
                                    )
        
    

    def transform_borders(self, translation_matrix, transform_matrix, matrix_translation):
        
        self.top_left.transform(translation_matrix, transform_matrix, matrix_translation)
        self.top_right.transform(translation_matrix, transform_matrix, matrix_translation)
        self.bottom_left.transform(translation_matrix, transform_matrix, matrix_translation)
        self.bottom_right.transform(translation_matrix, transform_matrix, matrix_translation)
        self.top_left.been_transformed = False
        self.top_right.been_transformed = False
        self.bottom_left.been_transformed = False
        self.bottom_right.been_transformed = False
       
    #button focused methods

    def select_mode(self, clicked_widget):
        
        for widget in self.drawing_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
                
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")
                '''
                if self.mode == "Anchor":
                    print("yep")
                    for wdgt in self.rotation_widgets:
                        show_pack_widget(wdgt)
                    
                else:
                    for wdgt in self.rotation_widgets:
                        hide_pack_widget(wdgt)
                '''
                    



    def select_direction(self, clicked_widget, widget_array):
        
        for widget in widget_array:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="yellow")
                self.direction = widget.cget("text").strip().upper()

    

    def on_canvas_resize(self, event):
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        self.canvas_height = event.height
        self.canvas_width = event.width
       

        canvas_center = line_line_intersection(0, 0, self.canvas_width, self.canvas_height, 0, self.canvas_height, self.canvas_width, 0)
        frame_center = self.get_borders_center()

        cx, cy = -1, -1 #self.canvas_width/2, self.canvas_height/2
        fx, fy = -1, -1
        
        if frame_center:
            fx = frame_center[0]
            fy = frame_center[1]

        if canvas_center:
            cx = canvas_center[0]
            cy = canvas_center[1]

        if frame_center and canvas_center:
            self.canvas.delete("all")
            transform_matrix = np.eye(3)
            
            for key_frame in self.key_frame_collection:
                key_frame.canvas_width = event.width
                key_frame.canvas_height = event.height
                
                
                    
                    
                self.pivot_matrix[0, 2] = fx
                self.pivot_matrix[1, 2] = fx

                self.matrix_pivot[0, 2] = -fx
                self.matrix_pivot[1, 2] = -fx
                transform_matrix  = np.array(translation_matrix2D(cx - fx, cy - fy))
                key_frame.transform_vertices(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
            self.transform_borders(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
            self.borders = self.get_borders()

            
            self.render_onion_skin()
            
            self.current_key_frame.render_grid(self.canvas, self.borders)
            self.render_borders()
        # Example: Recalculate positions of elements on the canvas
        # canvas.coords(my_rectangle, 0, 0, event.width, event.height)

    def wn_open(self, window):
        #https://stackoverflow.com/questions/76940339/is-there-a-way-to-check-if-a-window-is-open-in-tkinter
        # window has been created an exists, so don't create again.
        return window is not None and window.winfo_exists()

    def resize_all_frames(self, width: str, height: str, pivot):
        #resizes the pixel grid for every frame
        #is negative
        if width.startswith("-"):
            return
        
        if height.startswith("-"):
            return
        
        #is the exact same
        if self.pixel_canvas_width == int(width):
            return
        
        if self.pixel_canvas_height == int(height):
            return

        if not width.isnumeric():
            return
        
        

        if not height.isnumeric():
            return
         
        #canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.pixel_canvas_width, self.pixel_canvas_height = int(width), int(height)
        self.borders = self.set_borders(self.canvas_width, self.canvas_height, self.pixel_canvas_width, self.pixel_canvas_height)
        self.set_scaling(self.canvas)

        self.render_borders()
        for i in range(len(self.key_frame_collection)):
            key_frame = self.key_frame_collection[i]
            key_frame.pixel_canvas_width = int(width)
            key_frame.pixel_canvas_height = int(height)
            
            key_frame.alter_array_dimensions(key_frame.pixel_grid, int(width), int(height), None, pivot, self.canvas, self.borders)
            self.update_key_frame(i)

            #key_frame.update_borders(pivot)
        
        

        self.sub_wn.destroy()
        
        
        #reason render canvas is commented is because doing so removes the negative colors of
        #both lasso and select
        #self.current_key_frame.render_grid(self.canvas)
        self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale = self.set_scaling(self.canvas)
        
        self.borders = self.get_borders()
        self.highlight_current_frame()
        #self.update_animation_timeline()
        #self.update_key_frame(self.frame_idx)
        self.pixel_canvas_width = int(width)
        self.pixel_canvas_height = int(height)
        self.render_borders()
        
    def on_pixel_grid_resize(self):
        #resizes pixel grid in every frame: connected to the resize button
        if self.wn_open(self.sub_wn):
            return

        
        #Pop up Window
        self.sub_wn = Toplevel()
        self.sub_wn.resizable(False, False)

        
        apply_resize_btn = tk.Button(self.sub_wn, text="Resize")
        width_frame = tk.Frame(self.sub_wn)
        height_frame = tk.Frame(self.sub_wn)
        sub_frame_1 = tk.Frame(self.sub_wn)
        sub_frame_2 = tk.Frame(self.sub_wn)
        sub_frame_3 = tk.Frame(self.sub_wn)

        NE_btn = tk.Button(sub_frame_1, text="NE")
        N_btn  = tk.Button(sub_frame_1, text="N ")
        NW_btn = tk.Button(sub_frame_1, text="NW")
        E_btn = tk.Button(sub_frame_2, text="E ")
        C_btn = tk.Button(sub_frame_2, text="C ")
        W_btn = tk.Button(sub_frame_2, text="W ")
        SE_btn = tk.Button(sub_frame_3, text="SE")
        S_btn = tk.Button(sub_frame_3, text="S ")
        SW_btn = tk.Button(sub_frame_3, text="SW")

        anchor_widgets = [
            NE_btn, N_btn, NW_btn,
            E_btn, C_btn, W_btn,
            SE_btn, S_btn, SW_btn,
        ]

        NE_btn.config(command=lambda:self.select_direction(NE_btn, anchor_widgets))
        N_btn.config(command=lambda:self.select_direction(N_btn, anchor_widgets))
        NW_btn.config(command=lambda:self.select_direction(NW_btn, anchor_widgets))
        E_btn.config(command=lambda:self.select_direction(E_btn, anchor_widgets))
        C_btn.config(command=lambda:self.select_direction(C_btn, anchor_widgets))
        W_btn.config(command=lambda:self.select_direction(W_btn, anchor_widgets))
        SE_btn.config(command=lambda:self.select_direction(SE_btn, anchor_widgets))
        S_btn.config(command=lambda:self.select_direction(S_btn, anchor_widgets))
        SW_btn.config(command=lambda:self.select_direction(SW_btn, anchor_widgets))

        self.select_direction(C_btn, anchor_widgets)

        width_lbl = tk.Label(width_frame, text="Width")
        width_px_lbl = tk.Label(width_frame, text="px")
        width_entry = tk.Entry(width_frame)

        w = self.pixel_canvas_width #self.current_key_frame.pixel_canvas_width
        width_entry.insert(tk.END, str(w))

        height_lbl = tk.Label(height_frame, text="Height")
        height_px_lbl = tk.Label(height_frame, text="px")
        height_entry = tk.Entry(height_frame)

        h = self.pixel_canvas_height #self.current_key_frame.pixel_canvas_height
        height_entry.insert(tk.END, str(h))

        apply_resize_btn.config(command=lambda:self.resize_all_frames(width_entry.get(), height_entry.get(), self.direction))

        '''
        direction_arrangement = [
            [NE_btn, N_btn, NW_btn],
            [E_btn, C_btn, W_btn],
            [SE_btn, S_btn, SW_btn],
        ]
        

        arrange_widgets(direction_arrangement)
        '''

        NW_btn.pack(fill="both", anchor="nw", side="left", expand=True)
        N_btn.pack(fill="both", anchor="n", side="left", expand=True)
        NE_btn.pack(fill="both", anchor="ne", side="left", expand=True)

        W_btn.pack(fill="both", anchor="w",side="left", expand=True)
        C_btn.pack(fill="both", anchor="center",side="left", expand=True)
        E_btn.pack(fill="both", anchor="e",side="left", expand=True)
        
        
        SW_btn.pack(fill="both", anchor="sw",side="left", expand=True)
        S_btn.pack(fill="both", anchor="s",side="left", expand=True)
        SE_btn.pack(fill="both", anchor="se",side="left", expand=True)
        

        width_lbl.pack(fill="both",side="left", expand=True)
        width_entry.pack(fill="both", side="left", expand=True)
        width_px_lbl.pack(fill="both",side="left", expand=True)

        height_lbl.pack(fill="both",side="left", expand=True)
        height_entry.pack(fill="both", side="left", expand=True)
        height_px_lbl.pack(fill="both",side="left", expand=True)

        #main frames
        width_frame.pack(side="top", fill="both", expand=True)
        height_frame.pack(side="top", fill="both", expand=True)
        sub_frame_1.pack(side="top", fill="both", expand=True)
        sub_frame_2.pack(side="top", fill="both", expand=True)
        sub_frame_3.pack(side="top", fill="both", expand=True)
        apply_resize_btn.pack(side="top", fill="both", expand=True)



        #above tkinter windows
        self.sub_wn.lift()
        self.sub_wn.title("Resize") 
        #app.geometry("800x600")
        self.sub_wn.geometry("250x300")
        self.sub_wn.mainloop()

        
        self.render_canvas()
        #self.render_onion_skin()

        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.update_key_frame(self.frame_idx)
        #self.update_animation_timeline()


    
    #Shortcuts 


    def paste_pixels(self, *args):
        for i in range(len(self.pixels_to_paste)):
            pixel = self.pixels_to_paste[i]
            color = self.colors_to_paste[i]
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = color
                self.current_key_frame.draw_pixel(self.canvas, current_coord, color, color, current_coord, self.borders)
                self.canvas.delete(current_coord)


        self.render_canvas()
        #draw_pixel(self, canvas, key_coord, fill, outline, tag, borders):
        
        self.update_key_frame(self.frame_idx)

    def copy_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
        
        self.pixels_to_paste = [pixel for pixel in temp_pixels]
        self.colors_to_paste = [color for color in temp_colors]
        
        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()

        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        self.render_canvas()

        self.update_key_frame(self.frame_idx)


    def cut_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
        
        for pixel in temp_pixels:
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = None
                if self.current_key_frame.pixel_coords.get(current_coord):
                    del self.current_key_frame.pixel_coords[current_coord]
                self.canvas.delete(current_coord)
        
        self.pixels_to_paste = [pixel for pixel in temp_pixels]
        self.colors_to_paste = [color for color in temp_colors]

        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()
        
        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        self.render_canvas()

        self.update_key_frame(self.frame_idx)

    def delete_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
    
        for pixel in temp_pixels:
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = None
                if self.current_key_frame.pixel_coords.get(current_coord):
                    del self.current_key_frame.pixel_coords[current_coord]
                self.canvas.delete(current_coord)

        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()
        

        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        self.render_canvas()

        self.update_key_frame(self.frame_idx)
        
    #Canvas Interaction

    def resize_pixels(self, *args):
        #connected to the resize slider
        
        transform_matrix = np.eye(3, dtype=np.float64)
       
        
        #scaling_change = 1 + (abs(event.delta)//event.delta)/10
        prev_scale = self.pixel_scale

        self.pixel_scale = self.scaling_scl.get()
        
        
        #overall scale change
        old_scale = (prev_scale / self.pixel_scale_og) * self.pixel_scale_og
        
        
        cur_scale = (self.pixel_scale / self.pixel_scale_og) * self.pixel_scale_og
        
        
        #scale relative percentage change
        inc_percent = (cur_scale - old_scale)/prev_scale + 1
        
            

        #self.pixel_scale = self.pixel_scale * scaling_change
        #print(self.max_pixel_scale, self.min_pixel_scale, prev_scale, self.pixel_scale, scaling_change)
        if self.pixel_scale < self.min_pixel_scale:
            self.pixel_scale = prev_scale
        if self.pixel_scale >= self.max_pixel_scale:
            self.pixel_scale = prev_scale

        if prev_scale != self.pixel_scale:
            
            transform_matrix = np.array(scale_matrix2D(inc_percent, inc_percent))

        
        #start = time.time()

        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2


        self.pivot_matrix[0, 2] = cx
        self.pivot_matrix[1, 2] = cy

        self.matrix_pivot[0, 2] = -cx
        self.matrix_pivot[1, 2] = -cy

        #print(self.current_key_frame.get_borders())
        self.transform_borders(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
        self.borders = self.get_borders()
        ltx, lty, rtx, rty, rbx, rby, lbx, lby = self.get_borders()
        self.render_onion_skin()
        self.canvas.config(scrollregion=(ltx, lty, rbx, rby))
        for key_frame in self.key_frame_collection:
            key_frame.pixel_scale = self.pixel_scale
            key_frame.transform_vertices(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
        
        #print("Transfrom Time {}".format(time.time() - start))
        
        #self.current_key_frame.render_grid(self.canvas)
        self.current_key_frame.resize_canvas(self.canvas, cx, cy, inc_percent, inc_percent)


    def on_mousewheel_scroll(self, event):
        #applies transformations to the canvas or to pixels
        #connect to the mousewheel
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        transform_matrix = np.eye(3, dtype=np.float64)

        if self.mode == "H-Shear":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(shear_matrix2D(sign, 0)) #np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            #self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
            self.update_key_frame(self.frame_idx)
        elif self.mode == "V-Shear":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(shear_matrix2D(0 , sign)) #np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            #self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
            self.update_key_frame(self.frame_idx)
        elif self.mode == "Rotate":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            angle_inc = 20
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            #self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
            self.update_key_frame(self.frame_idx)
        else:
        
            #resizing pixels
        
       
        
            scaling_change = 1 + (abs(event.delta)//event.delta)/5
            prev_scale = self.pixel_scale

            self.pixel_scale = self.pixel_scale * scaling_change
            #self.scaling_scl.set(self.pixel_scale)
            #print(self.max_pixel_scale, self.min_pixel_scale, prev_scale, self.pixel_scale, scaling_change)

            if self.pixel_scale < self.min_pixel_scale:
                self.pixel_scale = prev_scale
            if self.pixel_scale >= self.max_pixel_scale:
                self.pixel_scale = prev_scale

            if prev_scale != self.pixel_scale:
                
                transform_matrix = np.array(scale_matrix2D(scaling_change, scaling_change))
            else:
                scaling_change = 1
            
            #start = time.time()

            #cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            cx, cy = x, y

            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            #print(self.current_key_frame.get_borders())
            
            self.transform_borders(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
            self.borders = self.get_borders()
            ltx, lty, rtx, rty, rbx, rby, lbx, lby = self.get_borders()
            self.render_onion_skin()
            self.canvas.config(scrollregion=(ltx, lty, rbx, rby))

            for key_frame in self.key_frame_collection:
                key_frame.pixel_scale = self.pixel_scale
                key_frame.transform_vertices(self.matrix_pivot, transform_matrix,  self.pivot_matrix)

            self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
        #self.current_key_frame.render_grid(self.canvas, self.borders)

    def on_mousewheel_release(self, event):
        print("mousewheel relased")

    def render_canvas(self):
        
        
        self.canvas.delete("all")
        if self.bg_color_iv.get():
            #render borders is first used as a potential background
            self.render_borders(self.bg_color)
            self.preview_canvas.config(bg=self.bg_color)
        else:
            self.preview_canvas.config(bg=self.canvas_color)
            
        self.render_onion_skin()
        self.current_key_frame.render_grid(self.canvas, self.borders)
        self.render_borders()

    def render_onion_skin(self):
        if self.onion_iv.get():
            #print("yeap")
            '''
            def rgb_to_hex(self, r,g,b):
                hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)
                return hexcode
            '''
            self.canvas.delete("onion")
            for i in range(self.frame_idx - int(self.onion_prev_sb.get()), self.frame_idx + int(self.onion_next_sb.get()) + 1):
                #if current_frame < len(self.key_frame_collection):
                key_frame = None
                
                #key_frame = self.key_frame_collection[current_frame]
                #using current_key_frame's 
                for y in range(self.pixel_canvas_height):
                    for x in range(self.pixel_canvas_width):

                        if i < self.frame_idx:
                            #previous frame in onion skin
                            if i > -1:
                                key_frame = self.key_frame_collection[i]
                                coord_key = key_frame.coord_to_str(x, y)
                                if key_frame.pixel_grid[y][x]:
                                    #key_frame.draw_pixel(self.canvas, coord_key, "green", "green", "onion", self.borders)
                                   
                                    current_color = key_frame.rgb_to_hex(0, int(200 * ((self.frame_idx - i)/self.onion_prev)), 0)
                                    
                                    key_frame.draw_pixel(
                                                        self.canvas, 
                                                        coord_key, 
                                                        "", 
                                                        current_color,  
                                                        "onion", 
                                                        self.borders
                                                         )
                        elif i > self.frame_idx:
                            #next frame in onion skin
                            if i < len(self.key_frame_collection):
                                key_frame = self.key_frame_collection[i]
                                coord_key = key_frame.coord_to_str(x, y)
                                if key_frame.pixel_grid[y][x]:
                                    #key_frame.draw_pixel(self.canvas, coord_key, "red", "red", "onion", self.borders)
                                    current_color = key_frame.rgb_to_hex(int(200 * ((i - self.frame_idx)/self.onion_next)), 0, 0)
                                    
                                    key_frame.draw_pixel(
                                                        self.canvas, 
                                                        coord_key, 
                                                        "",  
                                                        current_color,  
                                                        "onion", 
                                                        self.borders
                                                         )

    def on_canvas_lmb_click(self, event):
        if self.wn_open(self.sub_wn):
            return
        
        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return


        #self.render_onion_skin()
        #print('yep')
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mode == "Draw":
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Bucket":
            self.current_key_frame.bucket_fill(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Erase":
            self.current_key_frame.brush_click(x, y, self.canvas, "", self.borders)
        elif self.mode == "Rectangle":
            self.current_key_frame.shape_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Circle":
            self.current_key_frame.shape_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Move":
            #self.canvas.delete("all")
            self.current_key_frame.move_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Lasso":
            self.current_key_frame.lasso_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Select":
            self.current_key_frame.shape_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Stroke":
            self.current_key_frame.start_stroke(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Picker":
            self.color = self.current_key_frame.pick_color(x, y, self.canvas, self.borders)
            self.palette_bn.config(bg=self.color)


    def on_canvas_lmb_press(self, event):
        if self.wn_open(self.sub_wn):
            return
        

        
        self.render_onion_skin()

        if self.mode == "R-Shear":
            return
        
        if self.mode == "L-Shear":
            return

        if self.mode == "Rotate":
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mode == "Draw":
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_press(x, y, self.canvas, self.color, self.borders)
            
        elif self.mode == "Bucket":
            pass
        elif self.mode == "Erase":
            #print("press")
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_press(x, y, self.canvas, "", self.borders)
            
        elif self.mode == "Rectangle":
            self.current_key_frame.rectangle_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Circle":
            self.current_key_frame.circle_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Move":
            #this was to test the difference between this file and PixAnimate3.py's speed
            #start = time.time()
            self.current_key_frame.move_press(x, y, self.canvas, self.color, self.borders)
            #print(f"Transform Time {time.time() - start}")
        elif self.mode == "Lasso":
            #print("L")
            self.current_key_frame.lasso_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Select":
            self.current_key_frame.select_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Stroke":
            self.current_key_frame.start_stroke(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Picker":
            pass

        
        self.render_borders()
        

    def on_canvas_lmb_release(self, event):
        if self.wn_open(self.sub_wn):
            return
        
        
        self.render_onion_skin()

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mode == "Stroke":
            self.current_key_frame.end_stroke(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Rectangle":
            self.current_key_frame.shape_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Circle":
            self.current_key_frame.shape_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Lasso":
            #print("L")
            self.current_key_frame.lasso_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Move":
            self.current_key_frame.move_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Select":
            self.current_key_frame.select_release(x, y, self.canvas, self.color, self.borders)



        #self.update_animation_timeline()
        self.update_key_frame(self.frame_idx)
        #reason render canvas is commented is because doing so removes the negative colors of
        #both lasso and select
        #self.current_key_frame.render_grid(self.canvas)
        self.render_borders()
        #pass
    
    def on_canvas_rmb_click(self, event):
        if self.wn_open(self.sub_wn):
            return
        
        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return
        #self.render_onion_skin()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mode == "Select" or self.mode == "Lasso":
            self.current_key_frame.select_move_click(x, y, self.canvas, self.color, self.borders)
    
    def on_canvas_rmb_press(self, event):
        if self.wn_open(self.sub_wn):
            return

        
        self.render_onion_skin()

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return
        #print("hm")
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mode == "Select" or self.mode == "Lasso":
            self.current_key_frame.move_press(x, y, self.canvas, "", self.borders)
        self.render_borders()

    def on_canvas_rmb_release(self, event):
        if self.wn_open(self.sub_wn):
            return
        
        
        self.render_onion_skin()

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.mode == "Select" or self.mode == "Lasso":
            self.current_key_frame.shape_release(x, y, self.canvas, self.color, self.borders)
        #self.update_animation_timeline()
        self.update_key_frame(self.frame_idx)
        #reason render canvas is commented is because doing so removes the negative colors of
        #both lasso and select
        #self.current_key_frame.render_grid(self.canvas)
        self.render_borders()

    def fps_to_ms(self, fps):
        return 1000/fps

    #saving and importing files

    def load_frames(self, image: Image, mode='RGBA'):
        #https://stackoverflow.com/questions/74731252/fastest-way-to-load-an-animated-gif-in-python-into-a-numpy-array
        return [
            np.array(frame.convert(mode)).tolist()
            for frame in ImageSequence.Iterator(image)
        ]
    

    def open_file(self):

        filetypes = [

                        ("png files", "*.png"),
                        ("gif files", "*.gif"),
    
                    ]
        

        selected_file = filedialog.askopenfilename(
            title='Open files',
            initialdir=self.current_directory,
            filetypes=filetypes
            )
        
        if selected_file:
            self.current_directory = "\\".join(selected_file.split('/')[:-1]) + "\\"
            
            

            self.timeline_img_list.clear()
            for widget in self.timeline_widget_list:
                delete_widget(widget)

            self.timeline_widget_list.clear()
            self.preview_img_list.clear()
            self.key_frame_collection.clear()

            self.canvas.delete("all")
            #self.timeline_canvas.delete("all")
            self.preview_canvas.delete("all")

            #self.timeline_canvas.create_window((0, 0), window=self.timeline_scroll_frame, anchor="nw")
            #self.timeline_canvas.configure(yscrollcommand=self.timeline_sb_y.set)
            
            self.canvas.config(state="disabled")
            if selected_file.split(".")[-1].lower() == "gif":
                #print(selected_file)
                img = [] #Image.open(selected_file)
                
                total_frames = 0
                rgba_grids = []
                selected_file = path_correction(selected_file)
                with Image.open(selected_file) as img:
                    rgba_frames = self.load_frames(img)
          
                    total_frames = img.n_frames
                    self.pixel_canvas_width, self.pixel_canvas_height = img.size 
                
                for i in range(total_frames):
                    #print(i)
                    #img.seek(i)
                    #can't just convert a frame of a gif as an RGBA numpy array
                    #rgba_array = self.load_frames(img) #np.array(img).tolist() 
                    #print(rgba_frames[i])
                    new_frame = KeyFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
                    #if it's a clear pixel put None in the 2D array, otherwise a hexcode
                    #evil 2d list comprehension, downright devious
                    new_frame.pixel_grid = [
                                                [
                                                    new_frame.rgb_to_hex(col[0], col[1], col[2]) if col != [255, 255, 255, 0] else None for col in row
                                                ] for row in rgba_frames[i]
                                            ]
                    new_frame.pixel_coords = new_frame.grid_to_coords(self.borders)
                    self.key_frame_collection.append(new_frame)
                    #img.save(target_folder + f'/frame_{i:03d}.png')
                
                
            else:
                #print(selected_file)
                img = Image.open(selected_file)
                self.pixel_canvas_width, self.pixel_canvas_height = img.size 
                rgba_array = np.array(img).tolist() 
                #self.temp_pixels = [ [col, row] for row in range(len(self.pixel_grid)) for col in range(len(self.pixel_grid[0])) if self.pixel_grid[row][col] ]
                #print(rgba_array)
                new_frame = KeyFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
                #if it's a clear pixel put None in the 2D array, otherwise a hexcode
                #evil 2d list comprehension, downright devious
                new_frame.pixel_grid = [
                                            [
                                                new_frame.rgb_to_hex(col[0], col[1], col[2]) if col != [255, 255, 255, 0] else None for col in row
                                            ] for row in rgba_array 
                                        ]
                new_frame.pixel_coords = new_frame.grid_to_coords(self.borders)
                self.key_frame_collection.append(new_frame)
                
            self.frame_idx = 0
            self.current_key_frame = self.get_key_frame(self.frame_idx)
            self.render_canvas()
            self.highlight_current_frame()
            self.update_animation_timeline()
            self.canvas.config(state="normal")

    def save_gif(self):
        filetypes = [
                    #("All files", "*.*"),
                    ("gif files", "*.gif"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = self.current_directory, #os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        
        #https://stackoverflow.com/questions/60948028/python-pillow-transparent-gif-isnt-working
        if save_path:
            key_frame_images = []
            if self.bg_color_iv.get():

                r, g, b = self.current_key_frame.hex_to_rgb(self.bg_color)
                key_frame_images = [key_frame.pixel_to_pil_image([r, g, b, 255]) for key_frame in self.key_frame_collection]
                key_frame_images[0].save(
                                            save_path, 
                                            format = "GIF", 
                                            save_all=True, 
                                            append_images=key_frame_images[1:],  
                                            duration = self.fps_to_ms(self.fps_scl.get()), 
                                            loop=0, 
                                            disposal=2
                                            
                                        )

                
                
            else:

                key_frame_images = [key_frame.pixel_to_pil_image() for key_frame in self.key_frame_collection]
                key_frame_images[0].save(
                                            save_path, 
                                            format = "GIF", 
                                            save_all=True, 
                                            append_images=key_frame_images[1:],  
                                            duration = self.fps_to_ms(self.fps_scl.get()), 
                                            loop=0, 
                                            disposal=2
                                        )

    def save_frame(self):
        #saves an individual frame
        filetypes = [
                    #("All files", "*.*"),
                    ("png files", "*.png"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = self.current_directory, #os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        if save_path:
            print(save_path)
            if self.bg_color_iv.get():
                r, g, b = self.current_key_frame.hex_to_rgb(self.bg_color)
                self.current_key_frame.pixel_to_pil_image([r, g, b, 255]).save(save_path)
                
            else:
                self.current_key_frame.pixel_to_pil_image().save(save_path)
         
    def clear_frame(self):
        for y in range(self.current_key_frame.pixel_canvas_height):
            for x in range(self.current_key_frame.pixel_canvas_width):
                self.current_key_frame.pixel_grid[y][x] = None
                coord_key = self.current_key_frame.coord_to_str(x, y)
        
        d_keys = list(self.current_key_frame.pixel_coords.keys())
        while d_keys:
            del self.current_key_frame.pixel_coords[d_keys.pop()]

        self.canvas.delete('all')

        self.current_key_frame.pixel_vertices.clear()
        self.current_key_frame.last_pixel = []
        self.current_key_frame.stroke_pixels = []
        self.current_key_frame.temp_pixels = []
        self.current_key_frame.temp_colors = []
        self.current_key_frame.first_pixel = []
        self.current_key_frame.render_grid(self.canvas, self.borders)

        self.update_key_frame(self.frame_idx)
        self.render_borders()
        #self.update_animation_timeline()

    def clear_frames(self):
        for i in range(len(self.key_frame_collection)):
            key_frame = self.key_frame_collection[i]
            for y in range(key_frame.pixel_canvas_height):
                for x in range(key_frame.pixel_canvas_width):
                    key_frame.pixel_grid[y][x] = None
                    coord_key = key_frame.coord_to_str(x, y)
        
            d_keys = list(key_frame.pixel_coords.keys())
            while d_keys:
                del key_frame.pixel_coords[d_keys.pop()]
            self.update_key_frame(i)


            key_frame.pixel_vertices.clear()
            key_frame.last_pixel = []
            key_frame.stroke_pixels = []
            key_frame.temp_pixels = []
            key_frame.temp_colors = []
            key_frame.first_pixel = []

        self.canvas.delete('all')
        self.current_key_frame.render_grid(self.canvas, self.borders)
        
        self.render_borders()
        #self.update_animation_timeline()

    def debug(self):
        print("yep")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        print("Unique Vertices\n")
        print(f"Length:{len(self.current_key_frame.pixel_vertices)}")

        '''
        for key in self.current_key_frame.pixel_coords:
                        
            vertices = self.current_key_frame.pixel_coords[key]
            
            if vertices:

                print(f"Top Left: {vertices[0]}\nTop Right: {vertices[1]}\nBottom Right: {vertices[2]}\nBottom Left: {vertices[3]}\n")
        '''
        print("Pixel Coords Len", len(self.current_key_frame.pixel_coords))
        print(f"Sizes:\n Images {len(self.timeline_img_list)} Preview {len(self.preview_img_list)} Timeline: {len(self.timeline_widget_list)}")
        self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        
    def choose_color(self):
        print("pixel grid")
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        print(color_code)
        if color_code[1]:
            print(len(color_code[1]))
            self.color = color_code[1]
            self.palette_bn.config(bg=self.color)

    def change_canvas_color(self):
        #print("pixel grid")
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        #print(color_code)
        if color_code[1]:
            #color_code index 1 is a hex code, index 0 is an rgb tuble
            
            #this is so erasing works
            self.canvas_color = color_code[1] 
            self.canvas.config(bg=self.canvas_color)
            
            
            
        self.render_canvas()

    def change_bg_color(self):
        #bg color saved
        #print("pixel grid")

        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        #print(color_code)
        if color_code[1]:
            #color_code index 1 is a hex code, index 0 is an rgb tuble
            
            #this is so erasing works
            self.bg_color = color_code[1] 
            self.bg_color_btn.config(bg=self.bg_color, fg=self.current_key_frame.invert_color(self.bg_color))
            

        
        self.render_canvas()
            
        

    def get_canvas_colors(self):
        set_of_colors = {col for row in self.current_key_frame.pixel_grid for col in row if col != None}
        return set_of_colors


    #Preview Controling Widgets
    def update_preview_canvas(self):
        #after(2000, task)
        #self.current_key_frame.update_canvas(self.canvas)
        #cnvs = tk.Canvas(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.anim_canvas_height)
        '''
        cnvs.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=self.timeline_img_list[0],        # Display image data
            tags = ("image")
        )
        cnvs.pack()#grid(row=0, column=1)
        '''

        #print("update")
        
        if self.preview_idx > len(self.preview_img_list) - 1:
            self.preview_idx = 0

        #print(type(self.preview_img_list[self.preview_idx]), type(self.timeline_img_list[self.preview_idx]))
        self.preview_canvas.delete("all")
        
        
        self.preview_canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=self.preview_img_list[self.preview_idx],      # Display image data
            tags = ("image")
        )

        
        self.preview_idx += 1
        self.preview_id = self.after(int(self.fps_to_ms(self.fps_scl.get())),lambda:self.update_preview_canvas())

    def play_preview(self):
        #so you can only chang the fps when the playing is false
    
        #https://stackoverflow.com/questions/66361332/creating-a-timer-with-tkinter
        if self.playing == True:
            #print("fps scale on")
            self.play_btn.config(bg="SystemButtonFace")
            self.fps_scl.config(state="normal", bg="SystemButtonFace")
            self.playing = False
            self.update()
            if self.preview_id:
                self.preview_id = self.after_cancel(self.preview_id)
        else:
            #print("fps scale off")
            self.play_btn.config(bg="yellow")
            self.fps_scl.config(state="disabled", bg="gray")
            
            self.playing = True
            #forcing the buttons to update
            self.update()
            #makes the preview_canvas continually update
            self.preview_id = self.after(int(self.fps_to_ms(self.fps_scl.get())),lambda:self.update_preview_canvas())
            #print(f"FPS to Millisecond {self.fps_to_ms(self.fps_scl.get())}")
    
    ##Timeline controlling widgets
    
    def get_key_frame(self, idx):
        if not self.key_frame_collection:
            new_frame = KeyFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height,
                            )
            self.key_frame_collection.append(new_frame)
            #allows the key_frame to delete selected pixels
            #self.bind("<Delete>", lambda:new_frame.select_delete(self, self.canvas))
            
            return self.key_frame_collection[idx]
        else:
            return self.key_frame_collection[idx]
            
    def next_key_frame(self, *args):
        #self.canvas.delete("all")
        self.frame_idx += 1
        if self.frame_idx == len(self.key_frame_collection):
            self.frame_idx = len(self.key_frame_collection) - 1
        
        self.current_key_frame = self.get_key_frame(self.frame_idx)

        self.render_canvas()
        self.highlight_current_frame()

    def prev_key_frame(self, *args):
        #self.canvas.delete("all")
        self.frame_idx -= 1
        if self.frame_idx < 0:
            self.frame_idx = 0

        self.current_key_frame = self.get_key_frame(self.frame_idx)

        self.render_canvas()
        self.highlight_current_frame()

    def highlight_current_frame(self):
        for i in range(len(self.timeline_widget_list)):
            widget = self.timeline_widget_list[i]
    
            if i == self.frame_idx:
                
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="Azure3")

    def duplicate_key_frame(self):
        
        #new_len = len(self.key_frame_collection)
        new_frame = KeyFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
        
        

        new_frame.pixel_scale = self.pixel_scale
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_width):
                if self.current_key_frame.pixel_grid[y][x]:
                    new_frame.pixel_grid[y][x] = self.current_key_frame.pixel_grid[y][x]

        
        if len(self.key_frame_collection) - 1 == self.frame_idx:
        

            self.key_frame_collection.append(new_frame)
            self.update_animation_timeline()
            #clones the image to the timeline
            self.timeline_widget_list[self.frame_idx + 1].config(image=self.timeline_img_list[self.frame_idx])
        else:
            self.key_frame_collection.insert(self.frame_idx + 1, new_frame)
            self.update_animation_timeline()
            #clones the image to the timeline
            self.timeline_widget_list[self.frame_idx + 1].config(image=self.timeline_img_list[self.frame_idx])
        

        self.render_canvas()


    def add_key_frame(self):
        
        #new_len = len(self.key_frame_collection)
        new_frame = KeyFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
        
        
  
        new_frame.pixel_scale = self.pixel_scale
        

        
        if len(self.key_frame_collection) - 1 == self.frame_idx:
        

            self.key_frame_collection.append(new_frame)
        else:
            self.key_frame_collection.insert(self.frame_idx + 1, new_frame)
        
 
        self.update_animation_timeline()
    
   

    def delete_key_frame(self, *args):
        if len(self.key_frame_collection) > 1:
            
            if self.frame_idx >= len(self.key_frame_collection) - 1:

                self.key_frame_collection.pop(self.frame_idx)
                self.timeline_img_list.pop(self.frame_idx)
                self.preview_img_list.pop(self.frame_idx)
                delete_widget(self.timeline_widget_list.pop(self.frame_idx))
                self.frame_idx = len(self.key_frame_collection) - 1

                
            else:
                
                self.key_frame_collection.pop(self.frame_idx)
                self.timeline_img_list.pop(self.frame_idx)
                self.preview_img_list.pop(self.frame_idx)
                delete_widget(self.timeline_widget_list.pop(self.frame_idx))
                
 
            
            
            
            self.current_key_frame = self.get_key_frame(self.frame_idx)
            self.render_canvas()

            self.update_animation_timeline()
            

    def select_key_frame(self, string_idx : str):
        print("selected",string_idx)
        self.canvas.delete("all")
        self.frame_idx = int(string_idx)

        
      

        self.current_key_frame = self.get_key_frame(self.frame_idx)
        self.render_canvas()
        #self.current_key_frame.borders = self.key_frame_collection[0].borders
        if self.timeline_widget_list:
           
            self.highlight_current_frame()
            
    def update_key_frame(self, idx):
        '''
        item = self.canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=im,        # Display image data
            tags = ("image")
            
        )
        '''
        key_frame = self.get_key_frame(idx) #self.key_frame_collection[idx]
            
        #https://note.nkmk.me/en/python-pillow-paste/
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        display_img = None


        img = key_frame.pixel_to_pil_image()
        im_width, im_height = img.size  
        canvas_size = self.timeline_cell_size
        mx_dim = max(im_width, im_height)
        mn_dim = min(im_width, im_height)
        scale_dim = canvas_size/mx_dim

        #button/canvas background image, will have the scaled image pasted on top of it
        blank_image = Image.new("RGBA", (canvas_size, canvas_size), "#000000")

        ratio_x = im_width/mx_dim - 1
        ratio_y = im_height/mx_dim - 1

        ix = 0
        iy = 0
        if ratio_x != 0:
            ix = round((abs(ratio_x) * canvas_size)/2)

        if ratio_y != 0:
            iy = round((abs(ratio_y) * canvas_size)/2)

        #Timeline display image
        #scaling the image for the button/canvas size 
        #LANCZOS looks better on larger pixel grids while Nearest Looks better on smaller pixel grids
        #3000 is the area of 50 * 60 pixels
        if self.pixel_canvas_height * self.pixel_canvas_width > 3000:
            scaled_img = img.resize((round(scale_dim * im_width), round(scale_dim * im_height)),  Image.Resampling.LANCZOS)
            blank_image.paste(scaled_img, (ix, iy))
        else:
            scaled_img = img.resize((round(scale_dim * im_width), round(scale_dim * im_height)),  Image.Resampling.NEAREST)
            blank_image.paste(scaled_img, (ix, iy))
        #print(scaled_img.size)
        display_img = ImageTk.PhotoImage(blank_image)

        #Preview display image
        #10000 is the area of 100 * 100 pixels
        preview_img = None
        if self.pixel_canvas_height * self.pixel_canvas_width > 10000:
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.LANCZOS))
        else:
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))



        #initialization
        if len(self.timeline_img_list) <= idx:
            #print("a")
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))
            self.preview_img_list.append(preview_img)
            self.timeline_img_list.append(display_img)
        else:
            #print("b")
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))
            self.preview_img_list[idx] = preview_img
            self.timeline_img_list[idx] = display_img
            
        #initialization
        if len(self.timeline_widget_list) <= idx:
            #print("c")
            #the reason timeline_img_list is used is because without a container keeping track of an image, widget, or whatever, it will be garbage collected and not show up
            w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        bg="Azure3",
                        text = str(idx),
                        command=lambda:self.select_key_frame(str(idx))
                        )

            w.grid(row=idx, column=0)
            self.timeline_widget_list.append(w)
            #w.config(command=self.select_key_frame(w.cget("text")))
            
        else:
            #print("d")
            delete_widget(self.timeline_widget_list[idx])
            w = None
            if idx == self.frame_idx:
                w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        bg="SystemButtonFace",
                        text = str(idx),
                        command=lambda:self.select_key_frame(str(idx))
                        )
            else:
                w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        text = str(idx),
                        bg="Azure3",
                        command=lambda:self.select_key_frame(str(idx))
                        )
            #self.timeline_widget_list[idx] = w
            #w.config(command=self.select_key_frame(w.cget("text")))
        
        
        

            
            self.timeline_widget_list[idx] = w
            self.timeline_widget_list[idx].grid(row=idx, column=0)



    
    
    
        

        #chk = tk.Canvas(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.anim_canvas_height, bg="gray").grid(row=self.current_key_frame, column=1)
        #self.update()
        #self.update_idletasks()

    def update_animation_timeline(self):
        #matches the 
        
        
        for i in range(len(self.key_frame_collection)):
            self.update_key_frame(i)
            widget = self.timeline_widget_list[i]
        
            if i == self.frame_idx:
                
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="Azure3")
            

    
    
                    
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #frame.bind('<Left>', leftKey)
        #frame.bind('<Right>', rightKey)
        "<Left>"
        "<Right>"
        "<Control-z>"
        "<Control-y>"
        #self.bind("<Down>", self.t2d_poly.undo)
        #self.bind("<Up>", self.t2d_poly.redo)
        
        IKs = Animator(self, 500, 500, 96, 84)
        IKs.pack(side="top", fill="both", expand=True)

        self.bind("<Up>", IKs.prev_key_frame)
        self.bind("<Down>", IKs.next_key_frame)
        self.bind("<Delete>", IKs.delete_pixels)
        self.bind("<Control-c>", IKs.copy_pixels)
        self.bind("<Control-v>", IKs.paste_pixels)
        self.bind("<Control-x>", IKs.cut_pixels)
        self.bind("<Control-d>", IKs.delete_key_frame)
        self.bind("<Control-z>", lambda a:print("Undo not implemented"))
        self.bind("<Control-y>", lambda a:print("Redo not implemented"))
        

    


if __name__ == "__main__":
    #9 13 25 problems
    #duplicate works but doesn't update the timeline DONE
    #pixels that don't exist in the grid not being moved or deleted when selected
    #resize grid sometimes not working
    # Need to add animation preview DONE
    # onion skin spinboxes on prev and next DONE
    # palette import from pixelplacer3.py
    # impor images and gifs
    # Xaolin's Woo's antialiasing
    # different brush sizes
    # rotation and anchoring DONE

    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    #app.resizable()
    app.mainloop()
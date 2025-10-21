from MatrixMath import *
from collisions import *
import numpy as np
from numpy import radians as to_radians
from PIL import Image


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
    
    def wand_click(self, x, y, canvas, color, borders):
        if not polygon_point(borders, x, y):
            return
        
        self.temp_colors.clear()
        self.temp_pixels.clear()
        
        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width

        x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)

        color_under_cursor = self.pixel_grid[y_pixel][x_pixel]


        if not color_under_cursor:
            return


        #BFS flood fill
        #queue
        print("W:{} H:{} X:{} Y:{} XPix:{} YPix:{}".format(self.canvas_width, self.canvas_height , x, y, x_pixel, y_pixel))
        visited = set()
        queue = []
        queue.append((x_pixel, y_pixel))
        
        #print(queue)
        i = 0
        max_area = 32 * 32
        while queue and len(visited) < max_area:
            #print(queue)
            
            
            #print("inside")
            cur = queue.pop(0)
            
            if not in_bounds(cur[0], cur[1], self.pixel_canvas_width, self.pixel_canvas_height) or self.pixel_grid[ cur[1] ][ cur[0] ] != color_under_cursor or (cur[0], cur[1]) in visited: 
                continue
            else:

                current_coord = self.coord_to_str(cur[0], cur[1])


                if (cur[0] + 1, cur[1]) not in visited:
                    queue.append((cur[0] + 1, cur[1]))

                if (cur[0] - 1, cur[1]) not in visited:
                    queue.append((cur[0] - 1, cur[1]))

                if (cur[0], cur[1] + 1) not in visited:
                    queue.append((cur[0], cur[1] + 1))

                if (cur[0], cur[1] - 1) not in visited:
                    queue.append((cur[0], cur[1] - 1))

      
                
                if (cur[0], cur[1]) not in visited:
                    if self.pixel_grid[cur[1]][cur[0]]:
                        if color_under_cursor == self.pixel_grid[cur[1]][cur[0]]:
                            
                            inverted_color = self.invert_color(self.pixel_grid[cur[1]][cur[0]])
                            self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, current_coord, borders) 
                            self.temp_pixels.append([cur[0], cur[1]])
                            self.temp_colors.append(self.pixel_grid[cur[1]][cur[0]])

                #if (cur[0], cur[1]) not in visited:
                visited.add((cur[0], cur[1]))

                
                canvas.update_idletasks()
            
                #print(i, self.color, cur)
                #i += 1

        
        visited.clear()

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
        visited = set()
        queue = []
        queue.append((x_pixel, y_pixel))
        
        #print(queue)
        i = 0
        max_area = 32 * 32
        while queue and len(visited) < max_area:
            #print(queue)
            
            
            #print("inside")
            cur = queue.pop(0)
            
            if not in_bounds(cur[0], cur[1], self.pixel_canvas_width, self.pixel_canvas_height) or self.pixel_grid[ cur[1] ][ cur[0] ] != color_under_cursor or (cur[0], cur[1]) in visited: 
                continue
            else:
                #if i == (self.pixel_canvas_width - 1) * (self.pixel_canvas_height - 1):
                #    break
                #print("doin")
                current_coord = self.coord_to_str(cur[0], cur[1])

                if (cur[0] + 1, cur[1]) not in visited:
                    queue.append((cur[0] + 1, cur[1]))

                if (cur[0] - 1, cur[1]) not in visited:
                    queue.append((cur[0] - 1, cur[1]))

                if (cur[0], cur[1] + 1) not in visited:
                    queue.append((cur[0], cur[1] + 1))

                if (cur[0], cur[1] - 1) not in visited:
                    queue.append((cur[0], cur[1] - 1))

      
                
                
                if (cur[0], cur[1]) not in visited:
                    visited.add((cur[0], cur[1]))
                self.draw_pixel(canvas, current_coord, color, color, current_coord, borders) 
                self.pixel_grid[cur[1]][cur[0]] = color
                
                
            

                
                canvas.update_idletasks()
            
                #print(i, self.color, cur)
                #i += 1

        
        visited.clear()

        #updates the canvas likely makes it so not as much in memory
            
        #self.update_idletasks()
            
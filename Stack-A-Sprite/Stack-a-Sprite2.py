import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from Matrix_Math import *
from MatrixMath import *
from collisions import *
from numpy import eye, dot, linalg, array, uint8
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
        self.x = x
        self.y = y

    def __str__(self):
        return "X {} Y {}".format(self.x, self.y)

        
        
class MainCanvas(ttk.Frame):
    def __init__(self, parent, c_dimension, p_width, p_height, p_layers, *args, **kwargs):
        super().__init__(parent)

        
        ''' 
        0 - pixel sheet is an array containing a level's the drawable area
        1 - pixel grid is a 2D array/list of Hex Codes, that represent the pixels in an image, and empty cell/pixel is denoted by None instead of a hexcode
        2 -pixel coords is a dictionary of vertex coordinates 
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
        4 - pixel sheet is the box the cells of the grid inhabit, cells roate around it's center

        5 - pixel mesh is a array containing the pixel vertices of a level
        6 - pixel lattice is an array containing each hexcolor pixel grid for each layer
        7 - pixel stack is an array of the individual pixel sheets

        '''
        #DATA
        self.pixel_level = 0

        self.pixel_grid = []
        self.pixel_coords = {}
        self.pixel_vertices = []
        self.pixel_sheet = []
        

        self.pixel_lattice = []
        self.pixel_area = []
        self.pixel_mesh = []
        self.pixel_stack = []


        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        self.pixel_canvas_layers = p_layers

        self.pixel_scale = 0
        self.max_pixel_scale = 0
        self.min_pixel_scale = 1
        self.pixel_level_spacing = 0

        self.focus_grid_color = "purple"
        self.canvas_bg_color = 'gray'
        self.canvas = tk.Canvas(self, width=c_dimension, height=c_dimension, bg=self.canvas_bg_color) 
        
        
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
        
        self.level_label = tk.Label(self, text="Level")
        self.level = tk.IntVar(value=0)
        self.level_slider = tk.Scale(
            self,
            variable=self.level,
            from_ = 0,
            to = self.pixel_canvas_layers - 1,
            orient = "vertical",
            length=c_dimension,
            command = self.set_stack_level
        )

        self.sheet_spacing = 1
        self.spacing_label = tk.Label(self, text="Spacing")
        self.spacing = tk.IntVar(value=0)
        self.spacing_slider = tk.Scale(
            self,
            variable=self.spacing,
            from_ = 0,
            to = self.pixel_canvas_height,
            orient = "vertical",
            length=c_dimension,
            command = self.space_sprite_stack
        )

        
        self.brush_size = 1
        self.selected_color = "#000000" #"black" 
        #print(self.hex_to_rbg(self.selected_color))
        
        arrangement = [
                [None                , self.level_label , self.spacing_label  ],
                [self.canvas         , self.level_slider, self.spacing_slider ],
                [self.rotation_label , self.color_button, self.clear_button   ],
                [self.rotation_slider, self.save_button , self.data_buttom    ]
        ]

        arrange_widgets(arrangement)
        



        self.canvas.bind("<B1-Motion>", self.draw) 
        self.canvas.bind("<B3-Motion>", self.erase) 
        
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
            vertices = []
            grid = []
            coords = {}
            
            #(c_dimension - pixel_sheet)/2
            
            #top left
            x0 = (c_dimension * (1 - ratio_x)/2) 
            y0 = 0 + self.pixel_scale * z
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

            
            self.canvas.create_polygon(sheet,
                                        fill = '',
                                        outline='blue',
                                        tags=("shapes")
                                        )
        
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
                    grid.append([])

                for x in range(self.pixel_canvas_width + 1):
                    
                    vx = x_start + x * x_space
                    
                    v = Vertex(round(vx), round(vy))
                    vertices.append(v)
                    
                    if x < self.pixel_canvas_width:
                        if y < self.pixel_canvas_height:
                            grid[y].append(None)
                            coords.update({self.coord_str(x, y, z) : []})
                        
                    if y > 0:
                        if x > 0:
                            #print(len(vertices))
                            br_i = len(vertices) - 1
                            bl_i = len(vertices) - 2
                            tr_i = br_i - self.pixel_canvas_width - 1
                            tl_i = bl_i - self.pixel_canvas_width - 1 


                            top_left  = vertices[tl_i]
                            top_right  = vertices[tr_i]
                            bottom_left = vertices[bl_i]
                            bottom_right = vertices[br_i]
                            

                            s = self.coord_str(x - 1, y - 1, z)
                            #print(s)
                            #append order is top left, bottom left, bottom right, top right to make a proper convex polygon
                            #print(top_left, top_right, bottom_right, bottom_left)
                            '''
                            self.canvas.create_text(
                                (bottom_right.x - x_space/2),
                                (bottom_right.y - y_space/2),
                                text=s
                            )
                            '''
                            
                            self.canvas.create_polygon(
                                                        [
                                                            top_left.x, top_left.y, 
                                                            top_right.x, top_right.y,
                                                            bottom_right.x, bottom_right.y,
                                                            bottom_left.x, bottom_left.y
                                                        ],

                                                        fill = '',
                                                        outline='blue',
                                                        tags=("shapes")
                                                        )
                            
                    

                            coords[s] = [
                                            top_left, 
                                            top_right,
                                            bottom_right,
                                            bottom_left
                                        ]
                            

                                #vertices.clear()
            #self.pixel_vertices = vertices
            self.pixel_mesh.append(vertices)
            self.pixel_stack.append(sheet)
            self.pixel_lattice.append(grid)
            self.pixel_area.append(coords)
        
        #print(self.pixel_stack)
        #print(len(self.pixel_area), len(self.pixel_lattice), len(self.pixel_stack), len(self.pixel_area))
        self.set_stack_level()
        print("Vertices", len(vertices))   

    def set_stack_level(self, *args):
        self.pixel_grid  = self.pixel_lattice[self.level.get()]
        self.pixel_coords = self.pixel_area[self.level.get()]
        self.pixel_vertices = self.pixel_mesh[self.level.get()]
        self.pixel_sheet = self.pixel_stack[self.level.get()]

        #self.render_other_levels()
        #self.render_selected_level()
        self.render_stack_levels()

    def degrees_to_radians(self, deg):
        return (deg * math.pi)/180

    
    def render_stack_levels(self):
        self.canvas.delete("all")
        cur_level = self.level.get()
        for i in range(len(self.pixel_area)):
            
            for key in self.pixel_area[i]:
                
                vertices = self.pixel_area[i][key]
                self.canvas.delete(key)
                x_pixel, y_pixel, z_level = self.str_coord(key)
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
                #print(top_left)
                fill = ''
                if self.pixel_lattice[i][y_pixel][x_pixel] != None:
                    fill = self.pixel_lattice[i][y_pixel][x_pixel]
                
                
                if i == cur_level:

                    self.canvas.create_polygon(polygon,
                                        fill = fill,
                                        outline="black",
                                        tags=(key)
                                        )
                    
                   
                else:
                    
                    self.canvas.create_polygon(polygon,
                                                fill = fill,
                                                outline=fill,
                                                tags=(key)
                                                )
                    

            if i == cur_level:
                self.canvas.create_polygon(self.pixel_stack[i],
                                    fill = '',
                                    outline='blue',
                                    #tags=("shapes")
                                    )

    

  

    def apply_stack_transformations(self, is_rotating, is_scaling, is_spacing, angle_change, scaling_change, spacing_change):
        
        cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
        for i in range(len(self.pixel_stack)):
            sheet = self.pixel_stack[i]
            if is_scaling:
                pass
            elif is_spacing:
                cx, cy = line_line_intersection(
                    self.pixel_stack[0][0], self.pixel_stack[0][1],
                    self.pixel_stack[0][4], self.pixel_stack[0][5],
                    self.pixel_stack[0][2], self.pixel_stack[0][3],
                    self.pixel_stack[0][6], self.pixel_stack[0][7]
                ) 
            elif is_rotating:
                cx, cy = line_line_intersection(
                    sheet[0], sheet[1],
                    sheet[4], sheet[5],
                    sheet[2], sheet[3],
                    sheet[6], sheet[7]
                )

            for j in range(0, len(sheet), 2):
                x, y = translate_2D(-cx, -cy, sheet[j], sheet[j + 1])

                if is_scaling:
                    x, y = scale_2D(scaling_change, scaling_change ,x, y)
                elif is_rotating:
                    x, y = rotate_2D(angle_change, x, y)
                elif is_spacing:
                    x, y = translate_2D(0, spacing_change, x, y)

                sheet[j], sheet[j + 1] = translate_2D(cx, cy, x, y)

            #print(self.pixel_sheet)
            
            
            for vert in self.pixel_mesh[i]:
                #translate to origin
                x, y = translate_2D(-cx, -cy, vert.x, vert.y)

                #scale
                if is_scaling and not is_rotating:
                    x, y = scale_2D(scaling_change, scaling_change ,x, y)
                elif is_rotating:
                    x, y = rotate_2D(angle_change, x, y)
                elif is_spacing:
                    x, y = translate_2D(0, spacing_change, x, y)

                #move back
                vert.x, vert.y = translate_2D(cx, cy, x, y)


        #self.render_other_levels()
        #self.render_selected_level()
        self.render_stack_levels()

    def scale_sprite_stack(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx, cy = (canvas_width/2), (canvas_height/2)
        scaling_change = 1 + (abs(event.delta)//event.delta)/10
        prev_scale = self.pixel_scale

        self.pixel_scale = self.pixel_scale * scaling_change
        if self.pixel_scale < self.min_pixel_scale:
            self.pixel_scale = prev_scale
        if self.pixel_scale >= self.max_pixel_scale:
            self.pixel_scale = prev_scale

        if prev_scale != self.pixel_scale:
            self.apply_stack_transformations(False, True, False, 0, scaling_change, 0)
            
    def rotate_sprite_stack(self, *args):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        prev_angle = self.angle
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)

        self.apply_stack_transformations(True, False, False, angle_change, 0, 0)

    def space_sprite_stack(self, *args):
        prev_spacing = self.sheet_spacing
        self.sheet_spacing = self.spacing_slider.get()
        
        sign = 1 if prev_spacing - self.sheet_spacing > 0 else -1

        spacing_change = (prev_spacing - self.sheet_spacing) * self.pixel_scale
        self.apply_stack_transformations(False, False, True, 0, 0, spacing_change)


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
        
    def coord_str(self, x, y, z):
        return str(x) + '-' + str(y) + '-' + str(z)
    
    def str_coord(self, string):
        if '-' in string:
            x, y, z = map(int, string.split('-'))
            return x, y, z
        return 0, 0, 0
         
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
        for y in range(self.pixel_canvas_height):
            grid_pixel.append([])
            for x in range(self.pixel_canvas_height):
                #each in rgb alpha
                if self.pixel_grid[y][x] != None:
                    grid_pixel[y].append(self.hex_to_rbg(self.pixel_grid[y][x]))
                else:
                    grid_pixel[y].append([255, 255, 255, 0])
                    
        #self.display_2d(grid_pixel)
        im = array(grid_pixel, dtype= uint8)
        im = Image.fromarray(im , 'RGBA')
        
        im.save(save_path)
                           
    def choose_color(self):
        print("pixel grid")
        self.display_2d(self.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        print(color_code)
        if color_code[1]:
            self.selected_color = color_code[1]
    
    def display_data(self):
        print("Data")
        self.display_2d(self.pixel_grid)
        for key in self.pixel_coords:
            print(key, list(map(str, self.pixel_coords[key])))
            break
        
        print(self.selected_color)
        #for vert in self.pixel_vertices:
        #    print(vert)

    def get_pixel_grid_coords(self, mouse_x, mouse_y, canvas_width, canvas_height):
        '''
        Never uncomment this is a guide
        #top left
        x0 = (c_dimension * (1 - ratio_x)/2) 
        y0 = (c_dimension * (1 - ratio_y)/2) #- (c_dimension * (1 - ratio_y)/2) 
        #bottom left
        x1 = x0 
        y1 = y0 + c_dimension * ratio_y
        #bottom right
        x2 = x0 + c_dimension * ratio_x
        y2 = y0 + c_dimension * ratio_y
        #top right
        x3 = x0 + c_dimension * ratio_x
        y3 = y0 
        self.pixel_sheet = [
            #x, y, x, y, x etc
            x0, y0,
            x1, y1,
            x2, y2,
            x3, y3,

        ]
        '''

        
        line_len_x = canvas_width
        line_len_y = canvas_height

        
        
        self.canvas.delete("lines")
        
        #top 
        self.canvas.create_line(
            mouse_x, mouse_y,
            mouse_x + math.cos(-self.degrees_to_radians(90 - self.angle)) * line_len_x, mouse_y + math.sin(self.degrees_to_radians(90 - self.angle)) * line_len_y, 
            fill = "yellow",
            tags="lines"
        )
        
        #left
        self.canvas.create_line(
            mouse_x, mouse_y,
            mouse_x + math.cos(self.degrees_to_radians(-self.angle)) * line_len_x, mouse_y + math.sin(self.degrees_to_radians(-self.angle)) * line_len_y, 
            fill = "purple",
            tags="lines"
        )
        
        intersect_x = line_line_intersection(
            #current point
            mouse_x, mouse_y,
            #directly above the point at starting degrees
            mouse_x + math.cos(-self.degrees_to_radians(90 - self.angle)) * line_len_x, mouse_y + math.sin(self.degrees_to_radians(90 - self.angle)) * line_len_y, 
            #top left of drawable area at starting degrees
            self.pixel_sheet[0], self.pixel_sheet[1],
            #top right
            self.pixel_sheet[6], self.pixel_sheet[7]
        )

        intersect_y = line_line_intersection(
            #current point
            mouse_x, mouse_y,
            #directly to the left of point at starting degrees
            mouse_x + math.cos(self.degrees_to_radians(-self.angle)) * line_len_x, mouse_y + math.sin(self.degrees_to_radians(-self.angle)) * line_len_y, 
            #top left of drawable area at starting degrees
            self.pixel_sheet[0], self.pixel_sheet[1],
            #bottom left
            self.pixel_sheet[2], self.pixel_sheet[3]
        )

        #print(intersect_x, intersect_y)
        #the current x, y mouse position is the bottom right, 
        #intersection_x  the top right
        #intersection_y the bottom left, 
        #the first and second index of the pixel sheet being the top left
        #together these make a rectangle that takes of different fractions of the area of the current size of the pixel sheet
        #this fraction is used to calculate the grid area

        distance_x = math.sqrt((intersect_x[0] - self.pixel_sheet[0]) ** 2 + (intersect_x[1] - self.pixel_sheet[1]) ** 2)
        distance_y = math.sqrt((intersect_y[0] - self.pixel_sheet[0]) ** 2 + (intersect_y[1] - self.pixel_sheet[1]) ** 2)
        max_distance_x = (self.pixel_canvas_width * self.pixel_scale)
        max_distance_y = (self.pixel_canvas_height * self.pixel_scale) 

        grid_x = math.floor((distance_x/max_distance_x) * self.pixel_canvas_width)
        grid_y = math.floor((distance_y/max_distance_y) * self.pixel_canvas_height)

        return grid_x, grid_y

    def clear(self):
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_height):
                self.canvas.delete(self.coord_str(x, y, self.level.get()))
                self.pixel_grid[y][x] = None
               
        #self.canvas.delete('all')
        self.last_pixel = None
 
    def erase(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.pixel_sheet, x, y):
            #print('yep')
            grid_x, grid_y = self.get_pixel_grid_coords(x, y, canvas_width, canvas_height)
            key_coord = self.coord_str(grid_x, grid_y, self.level.get())
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
                self.pixel_grid[grid_x][grid_y] = None
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
        
        if polygon_point(self.pixel_sheet, x, y):
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
                    
    def draw(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []
        if polygon_point(self.pixel_sheet, x, y):
            #print('yep')
            grid_x, grid_y = self.get_pixel_grid_coords(x, y, canvas_width, canvas_height)
            key_coord = self.coord_str(grid_x, grid_y, self.level.get())
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
                self.pixel_grid[grid_y][grid_x] = self.selected_color
                self.canvas.create_polygon(polygon,
                                            fill = self.selected_color,
                                            outline=self.selected_color,
                                            tags=(key_coord)
                                            )
            if not self.last_pixel:
                self.last_pixel = [grid_x, grid_y]
            
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
    
        
class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Simple Pixel Art App") 

        
        self.mn_canvas = MainCanvas(self, 512, 16, 16, 16)
        self.mn_canvas.grid()
        
if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    app.resizable()
    app.mainloop()
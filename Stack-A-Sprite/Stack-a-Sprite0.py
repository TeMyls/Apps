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
        self.focus_grid_color = "purple"
        self.canvas_bg_color = 'gray'
        self.canvas = tk.Canvas(self, width=c_dimension, height=c_dimension, bg=self.canvas_bg_color) 
        
        #rectangle diagonal
        #these exists so pixels are always square
        diagonal = math.sqrt(p_width ** 2 + p_height ** 2)
        ratio_x = (p_width/diagonal) 
        ratio_y = (p_height/diagonal)
        #the rest of the area iis space for rotations

        

        self.canvas.grid(row=0, column=0)
        #(c_dimension - drawable_area)/2
        
        #top left
        x0 = (c_dimension * (1 - ratio_x)/2) #+ (c_dimension * (1 - ratio)/2)
        y0 = (c_dimension * (1 - ratio_y)/2) #+ (c_dimension * (1 - ratio)/2)
        #bottom left
        x1 = x0 
        y1 = y0 + c_dimension * ratio_y
        #bottom right
        x2 = x0 + c_dimension * ratio_x
        y2 = y0 + c_dimension * ratio_y
        #top right
        x3 = x0 + c_dimension * ratio_x
        y3 = y0 

        
        
        self.drawable_area = [
            #x, y, x, y, x etc
            x0, y0,
            x1, y1,
            x2, y2,
            x3, y3,

        ]

        
        self.canvas.create_polygon(self.drawable_area,
                                    fill = '',
                                    outline='blue',
                                    tags=("shapes")
                                    )
    

        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        
        
        ''' 
        
        pixel grid is a 2D array/list of Hex Codes, that represent the pixels in an image, and empty cell/pixel is denoted by None instead of a hexcode
        pixel coords is a dictionary of vertex coordinates 
            say for instance a 4x4 grid
            "X-Y" as a string that is a key to a dictionary/hashmap
            Each of these keys would have an array linking to their vertex coordinates 
                [V1, V2, V3, V4] of their polygon 
            'V' is an x, y vertex
            'N' and 'M' are it's respective dimensions 
            For a 4x4 cell grid both M and N would be 4

                        M
    
            V-----V-----V-----V-----V
            | 0-0 | 0-1 | 0-2 | 0-3 |
            V-----V-----V-----V-----V
            | 1-0 | 1-1 | 1-2 | 1-3 |
       N    V-----V-----V-----V-----V
            | 2-0 | 2-1 | 2-2 | 2-3 | 
            V-----V-----V-----V-----V
            | 3-0 | 3-1 | 3-2 | 3-3 |
            V-----V-----V-----V-----V

            
            

        pixel vertices is a list of the vertices in an area, the vertices that are values in pixel coords are the same objects  in this list
        The amount of unique vertices are as follows
            4 outside vertices with 2 neighbors
            2(M - 1) + 2(N - 1) vertices with 3 neighbors
            (M - 1 ) * (N - 1) vettices with 4 neighbors

        For a 4x4 grid it's 4 + (2(4 - 1) + 2(4 - 1)) +  ((4 - 1) * (4 - 1)) which equals 25 vertices
        Why? Computationally more efficient. 16 rectangle polygons with 4 vertices each totaling 48 vertices with many sharing the same coordinates doesn't scale well.
        With each vertex being an object, updating them once will change all of them in whatever data structure their in
        '''
        
        
        self.pixel_grid = []
        self.pixel_coords = {}
        self.pixel_vertices = []
        
        self.last_pixel = None
    
        drawable_x = x2 - x0
        drawable_y = y2 - y0
        
        x_start = x0 
        y_start = y0
        x_space = (drawable_x/self.pixel_canvas_width) 
        y_space = (drawable_y/self.pixel_canvas_height) 

        print("spacing", x_space, y_space)
        self.pixel_scale = x_space
        self.max_pixel_scale = x_space
        self.min_pixel_scale = 1
        vertices = []
        
        for y in range(self.pixel_canvas_height + 1):
        
            vy = y_start + y * y_space
            if y < self.pixel_canvas_height:
                self.pixel_grid.append([])

            for x in range(self.pixel_canvas_width + 1):
                
                
                
                
                
                vx = x_start + x * x_space
                
                v = Vertex(round(vx), round(vy))
                vertices.append(v)
                
                if x < self.pixel_canvas_width:
                    if y < self.pixel_canvas_height:
                        self.pixel_grid[y].append(None)
                        self.pixel_coords.update({self.coord_str(x, y) : []})
                    
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
                        

                        s = self.coord_str(x - 1, y - 1)
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
                        
                

                        self.pixel_coords[s] = [
                                                top_left, 
                                                top_right,
                                                bottom_right,
                                                bottom_left
                                            ]
                           

                            #vertices.clear()
        self.pixel_vertices = vertices
        
        print("Vertices", len(vertices))
            
                
        
        #for key in self.pixel_coords:
        #    print(key, list(map(str, self.pixel_coords[key])))
       
             

        #print(len(self.pixel_grid))
        #self.display_2d(self.pixel_grid)

        self.color_button = ttk.Button(self, text="Change Color", command=self.choose_color)
        self.clear_button = ttk.Button(self, text="clear", command=self.clear)
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.data_buttom = ttk.Button(self, text="Console Data", command=self.display_data)

        self.angle = 180
        self.rotation_angle = tk.IntVar()
        self.rotation_slider = tk.Scale(
            self,
            variable=self.rotation_angle,
            from_ = 0,
            to = 360,
            orient = "horizontal",
            length=c_dimension,
            command = self.rotate_sprite_layer
        )
        self.rotation_angle.set(self.angle)
        
        
        self.brush_size = 1
        self.selected_color = "#000000" #"black" 
        #print(self.hex_to_rbg(self.selected_color))
        
        
        self.rotation_slider.grid(row=1, column=0)
        self.color_button.grid(row=1,column=1)
        self.clear_button.grid(row=2,column=1)
        self.save_button.grid(row=3,column=1)
        self.data_buttom.grid(row=4, column=1)
        
        self.canvas.bind("<B1-Motion>", self.draw) 
        self.canvas.bind("<B3-Motion>", self.erase) 
        
        self.canvas.bind("<ButtonPress-1>", self.draw)
        #self.canvas.bind("<ButtonPress-3>", self.erase) 
        self.canvas.bind("<MouseWheel>", self.scale_sprite_layer)
        
        self.canvas.bind("<Return>", self.griddy) 

        
    def degrees_to_radians(self, deg):
        return (deg * math.pi)/180

    def render_polygons(self):
        for key in self.pixel_coords:
            vertices = self.pixel_coords[key]
            self.canvas.delete(key)
            x_pixel, y_pixel = self.str_coord(key)
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
            if self.pixel_grid[y_pixel][x_pixel]:
                fill = self.selected_color
            
            
            
            self.canvas.create_polygon(polygon,
                                        fill = fill,
                                        outline='blue',
                                        tags=(key)
                                        )


    def rotate_drawable_area(self, *args):
        self.canvas.delete("shapes")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        prev_angle = self.angle
        cx, cy = (canvas_width/2), (canvas_height/2)
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)
        #print(angle_change)

        

    def scale_sprite_layer(self, event):
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx, cy = (canvas_width/2), (canvas_height/2)
        dir = 1 + (abs(event.delta)//event.delta)/10
        
        prev_scale = self.pixel_scale

        self.pixel_scale = self.pixel_scale * dir
        if self.pixel_scale < self.min_pixel_scale:
            self.pixel_scale = prev_scale
        if self.pixel_scale >= self.max_pixel_scale:
            self.pixel_scale = prev_scale

        if prev_scale != self.pixel_scale:
            self.canvas.delete("shapes")
            #Uses Matrix_Math.py functions
            for vert in self.pixel_vertices:

                #translate to origin
                x, y = translate_2D(-cx, -cy, vert.x, vert.y)
                #rotate
                x, y = scale_2D(dir, dir,x, y)
                #move back
                vert.x, vert.y = translate_2D(cx, cy, x, y)

            self.render_polygons()

            
    def rotate_sprite_layer(self, *args):
        #start = time.time()

        self.canvas.delete("shapes")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        prev_angle = self.angle
        cx, cy = (canvas_width/2), (canvas_height/2)
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)
        draw_area = False

        #Uses Matrix_Math.py functions
        for vert in self.pixel_vertices:
            #translate to origin
            x, y = translate_2D(-cx, -cy, vert.x, vert.y)
            
            #rotate
            x, y = rotate_2D(angle_change, x, y)
            
            #move back

            vert.x, vert.y = translate_2D(cx, cy, x, y)

        #print(time.time() - start)
        

        self.render_polygons()

        if draw_area:
            for i in range(0, len(self.drawable_area), 2):
                x, y = translate_2D(-cx, -cy, self.drawable_area[i], self.drawable_area[i + 1])
                x, y = rotate_2D(angle_change, x, y)
                self.drawable_area[i], self.drawable_area[i + 1] = translate_2D(cx, cy, x, y)

            #print(self.drawable_area)
            self.canvas.create_polygon(self.drawable_area,
                                        fill = '',
                                        outline='blue',
                                        tags=("shapes")
                                        )

        
    '''
    def rotate_sprite_layer_numpy(self, *args):
        #start = time.time()

        self.canvas.delete("shapes")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        prev_angle = self.angle
        cx, cy = (canvas_width/2), (canvas_height/2)
        self.angle = self.rotation_slider.get()
        angle_change = self.degrees_to_radians(prev_angle - self.angle)

        #From MatrixMath Functions
        anchor_pivot = array(translation_matrix2D(-cx, -cy))
        pivot_anchor = array(translation_matrix2D(cx, cy))
        mat_rotate = array(rotation_matrix2D(angle_change))

        for vert in self.pixel_vertices:
            xny_coords = array(set_matrix2D(vert.x, vert.y))
            #translate to origin
            xny_coords = dot(anchor_pivot, xny_coords)
            #rotate
            xny_coords = dot(mat_rotate, xny_coords)
            #move back
            xny_coords = dot(pivot_anchor, xny_coords)
            
            vert.x, vert.y = xny_coords[0, 0], xny_coords[1 , 0]

        #print(time.time() - start)

        self.render_polygons()
    '''
        

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
        
    def coord_str(self, x, y):
        return str(x) + '-' + str(y)
    
    def str_coord(self, string):
        if '-' in string:
            x, y = map(int, string.split('-'))
            return x, y
        return 0, 0
         
    def griddy(self, event):
        print("yep")
        self.display_2d(self.pixel_grid)  
         
    def save(self):

        '''
        filetypes = [
                    #("All files", "*.*"),
                    ("png files", "*.png"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        '''
        grid_pixel = []
        for y in range(self.pixel_canvas_height):
            grid_pixel.append([])
            for x in range(self.pixel_canvas_height):
                #each in rgb alpha
                if self.pixel_grid[y][x] != None:
                    grid_pixel[y].append(self.hex_to_rbg(self.pixel_grid[y][x]))
                else:
                    grid_pixel[y].append([255, 255, 255, 0])
                    
        self.display_2d(grid_pixel)
        '''
        im = array(grid_pixel, dtype= uint8)
        im = Image.fromarray(im , 'RGBA')
        
        im.save(save_path)
        ''' 
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

        
        print(self.selected_color)
        #for vert in self.pixel_vertices:
        #    print(vert)

    def clear(self):
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_height):
                self.pixel_grid[y][x] = None
                #self.pixel_coords.update({self.coord_str(x, y) : False})
        self.canvas.delete('all')
        self.last_pixel = None
 
    def erase(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []

        #print('yep')
        for key in self.pixel_coords:
            #if not has_collided:
            x_pixel, y_pixel = self.str_coord(key)
            if self.pixel_grid[y_pixel][x_pixel]:
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

                
                #if not self.pixel_grid[y_pixel][x_pixel]:
                if polygon_point(polygon, x, y):
                    #current_coord = self.coord_str(x_pixel, y_pixel)
                    #print(key)
                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    #has_collided = True
                    
                    self.pixel_grid[y_pixel][x_pixel] = ''
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = self.canvas_bg_color,
                                                outline='',
                                                tags=(key)
                                                )
                    
                    break
        
   
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
                    x_pixel, y_pixel = self.str_coord(key)

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
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = None
        for key in self.pixel_coords:
            x_pixel, y_pixel = self.str_coord(key)
            if self.pixel_grid[y_pixel][x_pixel]:
            
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
                if polygon_point(polygon, x, y):
                    #current_coord = self.coord_str(x_pixel, y_pixel)

                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    
                    
                    self.pixel_grid[y_pixel][x_pixel] = None
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = '',
                                                outline='',
                                                tags=(key)
                                                )
        '''
                         
    def draw_drag(self, event): 

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        


        #if self.last_pixel:
            
        between = self.DDA(x, y, self.last_pixel[0], self.last_pixel[1])
        #print(len(between))
        self.last_pixel.clear()
        self.last_pixel = [x, y]

            
        if len(between) >= 2:
            while between:
                point = between.pop()
                px = point[0]
                py = point[1]
                for key in self.pixel_coords:
                    x_pixel, y_pixel = self.str_coord(key)

                    #if self.pixel_grid[y_pixel][x_pixel]:
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
                        self.pixel_grid[y_pixel][x_pixel] = self.selected_color
                        #self.pixel_coords[current_coord] = True
                        #self.display_2d(self.pixel_grid)

                        self.canvas.create_polygon(polygon,
                                                    fill = self.selected_color,
                                                    outline=self.selected_color,
                                                    tags=(key)
                                                    )
                        break
        
        '''
        print('yep')
        for key in self.pixel_coords:
            #if not has_collided:
            x_pixel, y_pixel = self.str_coord(key)
            if not self.pixel_grid[y_pixel][x_pixel]:
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

                
                #if not self.pixel_grid[y_pixel][x_pixel]:
                if polygon_point(polygon, x, y):
                    #current_coord = self.coord_str(x_pixel, y_pixel)
                    print(key)
                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    #has_collided = True
                    
                    self.pixel_grid[y_pixel][x_pixel] = self.selected_color
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = self.selected_color,
                                                outline=self.selected_color,
                                                tags=(key)
                                                )

                break
        
        
        #print(self.last_pixel, " ", [x_pixel, y_pixel])
        if self.last_pixel != [x_pixel, y_pixel] and self.last_pixel != None:
           
            #if x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
            
            if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                between = self.DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])
                for pixel in between:
                    #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))
                
                    rx1 = pixel[0] * x_space
                    ry1 = pixel[1] * y_space
                    rx2 = rx1 + x_space
                    ry2 = ry1 + y_space
                    
                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    self.pixel_grid[pixel[1]][pixel[0]] = self.selected_color
                    
                    current_coord = self.coord_str(pixel[0], pixel[1])
                    self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)
                    self.canvas.create_rectangle(
                                        rx1,
                                        ry1,
                                        rx2,
                                        ry2,
                                        fill=self.selected_color,
                                        outline=self.selected_color,
                                        tags=(current_coord)
                                        )
            self.last_pixel = None
           
        if self.last_pixel == None:
            self.last_pixel = [x_pixel, y_pixel]
        
        '''

    def draw(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.last_pixel = []

        #print('yep')
        for key in self.pixel_coords:
            #if not has_collided:
            x_pixel, y_pixel = self.str_coord(key)
            if not self.pixel_grid[y_pixel][x_pixel]:
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

                
                #if not self.pixel_grid[y_pixel][x_pixel]:
                if polygon_point(polygon, x, y):
                    #current_coord = self.coord_str(x_pixel, y_pixel)
                    #print(key)
                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    #has_collided = True
                    
                    self.pixel_grid[y_pixel][x_pixel] = self.selected_color
                    #self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)

                    self.canvas.create_polygon(polygon,
                                                fill = self.selected_color,
                                                outline=self.selected_color,
                                                tags=(key)
                                                )
        if not self.last_pixel:
            self.last_pixel = [x, y]
        
    def edit_layer(self):
        pass
            
    def flood_fill(self, row, col, selected_color):
        w = len(self.pixel_grid)
        h = len(self.pixel_grid[0])
        #BFS flood fill
        #queue
        
        visited = []
        kyu = []
        kyu.append((row,col))
        while kyu:
            #print(kyu)
            
            
            
            cur = kyu.pop(0)
            
            
            if cur[0] >= w or cur[0] < 0 or cur[1] >= h or cur[1] < 0 or self.pixel_grid[cur[0]][cur[1]] != 0:
                continue
            else:
                '''
                current_coord = self.coord_str(x_pixel, y_pixel)
                self.pixel_coords[current_coord] = True
                #self.display_2d(self.pixel_grid)
                self.canvas.create_rectangle(
                                    rx1,
                                    ry1,
                                    rx2,
                                    ry2,
                                    fill=self.selected_color,
                                    outline=self.selected_color,
                                    tags=(current_coord)
                                )
                '''
                self.pixel_grid[cur[0]][cur[1]] = 1
                kyu.append((cur[0] + 1, cur[1]))
                kyu.append((cur[0] - 1, cur[1]))
                kyu.append((cur[0], cur[1] + 1))
                kyu.append((cur[0], cur[1] - 1))
                
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

        
        self.mn_canvas = MainCanvas(self, 512, 5, 5 , 12)
        self.mn_canvas.grid()
        
if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    app.resizable()
    app.mainloop()
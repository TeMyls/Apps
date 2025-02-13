import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
import numpy as np
import math


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

class FrameArrangement(ttk.Frame):
    def __init__(self, parent, arrangement, *args, **kwargs):
        super().__init__(parent)

        arrange_widgets(arrangement)


class MainCanvas(ttk.Frame):
    def __init__(self, parent, c_width, c_height, p_width, p_height, *args, **kwargs):
        super().__init__(parent)
        #the color selection palette
        self.selection_palette = None
        self.draw_tools = None

        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        
        #pixel grid is a 2D array of Hex Codes, thatg represent the pixels in an image
        #pixel coords is a dictionary of coordinates saying whether they are filled or not
        self.pixel_grid = []
     
        self.pixel_coords = {}
        #this is an array of the last pixel encountered
        self.last_pixel = []

        self.canvas_width = c_width
        self.canvas_height = c_height
        self.x_spacing = self.canvas_width//self.pixel_canvas_width
        self.y_spacing = self.canvas_height//self.pixel_canvas_height

        print(f"{self.canvas_width} {self.canvas_height}")
    
        self.mode = "Draw"
        #rectangle vars
        self.rect = None
        self.rect_x = None
        self.rect_y = None
        self.rect_w = None
        self.rect_h = None

        for y in range(p_height):
            self.pixel_grid.append([])
            for x in range(p_width):
                self.pixel_grid[y].append(None)
                self.pixel_coords.update({self.coord_str(x, y) : False})
        
        #print(len(self.pixel_grid))
        #self.display_2d(self.pixel_grid)

        self.debug_button = ttk.Button(self, text="Debug", command=self.debug)
        self.clear_button = ttk.Button(self, text="clear", command=self.clear)
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg='gray') 
        self.brush_size = 1
        #The hexadecimal color black initially
        self.color = "#000000" 
        #print(self.hex_to_rbg(self.color))

        #line stroke drawinf vars
        self.is_drawing_line = False
        self.start_xy = []
        self.stroke_pixels = []
        
        
        self.canvas.grid(row=0, column=0)
        self.debug_button.grid(row=1,column=1)
        self.clear_button.grid(row=2,column=1)
        self.save_button.grid(row=3,column=1)
        
        self.canvas.bind("<B1-Motion>", self.on_left_mouse_drag) 
        self.canvas.bind("<ButtonPress-1>", self.on_left_mouse_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_mouse_release)


        self.canvas.bind("<B3-Motion>", self.hover_pixel) 
        self.canvas.bind("<ButtonPress-3>", self.hover_pixel) 
        
        #self.canvas.bind("<Return>", self.griddy) 
        
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

    def set_selection_palette(self, selection_palette):
        self.selection_palette = selection_palette

    def set_draw_tools(self, draw_tools):
        self.draw_tools = draw_tools

    def get_canvas_colors(self):
        set_of_colors = {col for row in self.pixel_grid for col in row if col != None}
        return set_of_colors

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
            grid_pixel = []
            for y in range(self.pixel_canvas_height):
                grid_pixel.append([])
                for x in range(self.pixel_canvas_height):
                    #each in rgb alpha
                    if self.in_pixel_bounds(x, y, self.pixel_canvas_width, self.pixel_canvas_height):
                        if self.pixel_grid[y][x] != None:
                            grid_pixel[y].append(self.selection_palette.hex2rgb(self.pixel_grid[y][x], True))
                        else:
                            grid_pixel[y].append([255, 255, 255, 0])
                        
            #self.display_2d(grid_pixel)
            im = np.array(grid_pixel, dtype=np.uint8)
            im = Image.fromarray(im , 'RGBA')
            
            im.save(save_path)
         
    def clear(self):
        for y in range(self.pixel_canvas_height):
            for x in range(self.pixel_canvas_height):
                self.pixel_grid[y][x] = None
                #self.pixel_coords.update({self.coord_str(x, y) : False})
        self.canvas.delete('all')
        self.last_pixel = []
        
    def coord_str(self, x, y):
        return str(x) + '-' + str(y)
         
    def debug(self):
        print("yep")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        print(self.color)
        s = ''
        
        for index, (key, value) in enumerate( self.pixel_coords.items()):
            s = s + "{}:{}_".format(key, value)
            
            if (index + 1) % canvas_width == 0:
                print(s)
                s = ''
        
        self.display_2d(self.pixel_grid)

    def on_button_clear(self, event):
        self.canvas.delete("rect")
        
    def in_pixel_bounds(self, pixel_x, pixel_y, grid_w, grid_h):
        return 0 <= pixel_x < grid_w and 0 <= pixel_y < grid_h
    
    def on_left_mouse_release(self, event):

        #updating current colors
        colors = self.get_canvas_colors()
        self.selection_palette.set_current_colors(colors)
        #print(colors)
        if self.is_drawing_line:
            #print("running")
            self.is_drawing_line = False
            

            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
            y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)


            a = self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height)
            b = self.in_pixel_bounds(self.start_xy[0], self.start_xy[1], self.pixel_canvas_width, self.pixel_canvas_height)
            if a and b:
                #print("passed")
                if self.stroke_pixels:
                    #first pixel
                    current_coord = self.coord_str(self.start_xy[0], self.start_xy[1])
                    self.canvas.create_rectangle(
                                self.start_xy[0] * self.x_spacing,
                                self.start_xy[1] * self.y_spacing,
                                self.start_xy[0] * self.x_spacing + self.x_spacing,
                                self.start_xy[1] * self.y_spacing + self.y_spacing,
                                fill=self.color,
                                outline=self.color,
                                tags=(current_coord)
                                )
                    self.pixel_coords[current_coord] = True

                self.stroke_pixels = self.DDA(self.start_xy[0], self.start_xy[1], x_pixel, y_pixel)
                for pixel in self.stroke_pixels:
                    #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))
                
                    rx1 = pixel[0] * self.x_spacing
                    ry1 = pixel[1] * self.y_spacing
                    rx2 = rx1 + self.x_spacing
                    ry2 = ry1 + self.y_spacing
                    
                    #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                    self.pixel_grid[pixel[1]][pixel[0]] = self.color
                    
                    current_coord = self.coord_str(pixel[0], pixel[1])
                    self.pixel_coords[current_coord] = True
                    #self.display_2d(self.pixel_grid)
                    self.canvas.create_rectangle(
                                        rx1,
                                        ry1,
                                        rx2,
                                        ry2,
                                        fill=self.color,
                                        outline=self.color,
                                        tags=(current_coord)
                                        )
                    
            self.canvas.delete("stroke_line")

    def on_left_mouse_click(self, event):
        if self.mode == "Draw":
            self.draw(event)
        elif self.mode == "Bucket":
            self.flood_fill(event)
        elif self.mode == "Erase":
            self.erase(event)
        elif self.mode == "Rectangle":
            pass
        elif self.mode == "Circle":
            pass
        elif self.mode == "Move":
            pass
        elif self.mode == "Lasso":
            pass
        elif self.mode == "Select":
            pass
        elif self.mode == "Stroke":
            self.line_between_points(event)
        elif self.mode == "Picker":
            self.pick_color(event)


    def on_left_mouse_drag(self, event):


        if self.mode == "Draw":
            self.draw_drag(event)
        elif self.mode == "Bucket":
            pass
        elif self.mode == "Erase":
            self.erase(event)
        elif self.mode == "Rectangle":
            pass
        elif self.mode == "Circle":
            pass
        elif self.mode == "Move":
            pass
        elif self.mode == "Lasso":
            pass
        elif self.mode == "Select":
            pass
        elif self.mode == "Stroke":
            self.line_between_points(event)
        elif self.mode == "Picker":
            pass
        #self.__old_event = event
               

    def line_between_points(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing

        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            
            
            if not self.is_drawing_line:
                self.start_xy.clear()
                
                
                self.start_xy.append(x_pixel)
                self.start_xy.append(y_pixel)
                self.is_drawing_line = True
            else:
                
                
                self.canvas.delete("stroke_line")

   
                
                if self.in_pixel_bounds(self.start_xy[0], self.start_xy[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    if self.stroke_pixels:
                        #first pixel
                        self.canvas.create_rectangle(
                                    self.start_xy[0] * self.x_spacing,
                                    self.start_xy[1] * self.y_spacing,
                                    self.start_xy[0] * self.x_spacing + self.x_spacing,
                                    self.start_xy[1] * self.y_spacing + self.y_spacing,
                                    fill=self.color,
                                    outline=self.color,
                                    tags=("stroke_line")
                                    )
                    self.stroke_pixels = self.DDA(self.start_xy[0], self.start_xy[1], x_pixel, y_pixel)
                    for pixel in self.stroke_pixels:
                        #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))
                    
                        rx1 = pixel[0] * self.x_spacing
                        ry1 = pixel[1] * self.y_spacing
                        rx2 = rx1 + self.x_spacing
                        ry2 = ry1 + self.y_spacing
                        
                        #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                        #self.pixel_grid[pixel[1]][pixel[0]] = self.color
                        
                        #current_coord = self.coord_str(pixel[0], pixel[1])
                        #self.pixel_coords[current_coord] = True
                        #self.display_2d(self.pixel_grid)
                        self.canvas.create_rectangle(
                                            rx1,
                                            ry1,
                                            rx2,
                                            ry2,
                                            fill=self.color,
                                            outline=self.color,
                                            tags=("stroke_line")
                                            )


    def hover_pixel(self, event):
        self.canvas.delete("pixel_hover")
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        #canvas_width = self.canvas.winfo_width()
        #canvas_height = self.canvas.winfo_height()
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        #x_space = (canvas_width//self.pixel_canvas_width)
        #y_space = (canvas_height//self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing

        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            color_under_cursor = self.pixel_grid[y_pixel][x_pixel]
            if color_under_cursor != None:
                rgb = self.selection_palette.hex2rgb(color_under_cursor)
                
                for color in rgb:
                    color = 255 - color

                
                r, g, b = rgb
                _hex = self.selection_palette.rgb2hex(r, g, b)
            
            
                self.canvas.create_rectangle(
                                        rx1,
                                        ry1,
                                        rx2,
                                        ry2,
                                        #fill=self.color,
                                        outline=_hex,
                                        tags=("pixel_hover")
                                    )
            else:
                self.canvas.create_rectangle(
                                        rx1,
                                        ry1,
                                        rx2,
                                        ry2,
                                        #fill=self.color,
                                        outline=self.color,
                                        tags=("pixel_hover")
                                )   

    def pick_color(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing
        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            color_under_cursor = self.pixel_grid[y_pixel][x_pixel]
            if color_under_cursor:
                #print("Current Color {}".format(self.color))
                #print("Color under cursor {}".format(color_under_cursor))
                self.color = color_under_cursor
                #print(" 1 New Current Color is {}".format(self.color))
                self.mode = "Draw"
                #print(" 2 New Current Color is {}".format(self.color))
                self.selection_palette.set_selected_color(color_under_cursor)
                #print(" 3 New Current Color is {}".format(self.color))
                self.draw_tools.set_mode(self.mode)
                #print(" 4 New Current Color is {}".format(self.color))
                
            else:
                #print("gida")
                self.mode = "Draw"
                self.selection_palette.set_selected_color("#000000")
                self.draw_tools.set_mode(self.mode)
                self.color = "#000000"
            
            
        
    def rectangle_start(self, event):
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        #self.position_mouse_label.config(text= f"Canvas MX: {x} Canvas MY: {y}")
        
        
        
        
        
        #self.rect_x, self.rect_y, self.rect_w, self.rect_h = 0, 0, 0, 0
        
        self.rect_x = self.canvas.canvasx(event.x)
        self.rect_y = self.canvas.canvasx(event.y)
        
        #self.image_pos_mouse_label.config(text = f"Image MX:{x} Image MY:{y}")
        

        self.canvas.delete("rect")
        # create rectangle if not yet exist
        if not self.rect:
            #pass
            self.rect = self.canvas.create_rectangle(self.rect_x, self.rect_y, 1, 1, outline='black', tags=("rect")) 
    
    def rectangle_drag(self, event):
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        
        

        '''
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9*w:
            self.canvas.xview_scroll(1, 'units') 
        elif event.x < 0.1*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.canvas.yview_scroll(1, 'units') 
        elif event.y < 0.1*h:
            self.canvas.yview_scroll(-1, 'units')

        '''
        # expand rectangle as you drag the mouse
        # expand rectangle as you drag the mouse
        
        rw = curX - self.rect_x
        rh = curY - self.rect_y
        rx = self.rect_x
        ry = self.rect_y
        
        if rw < 0:
            rx = abs(rx + rw)
            rw = abs(rw)
        if rh < 0:
            ry = abs(ry + rh)
            rh = abs(rh)

        self.canvas.delete("rect")
            
        self.rect = self.canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline='black', tags=("rect"))

    def erase(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing
        
        
        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            current_coord = self.coord_str(x_pixel, y_pixel)
            if self.pixel_coords[current_coord] == True:
                #Returns true
                
                self.pixel_grid[y_pixel][x_pixel] = None
                #self.display_2d(self.pixel_grid)
                self.canvas.delete(current_coord)
                self.pixel_coords[current_coord] = False
                               
    def draw_drag(self, event): 
        #fills in gaps when the mouse moves too fast over the canvas
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing
        
        

        #print(self.last_pixel, " ", [x_pixel, y_pixel])
        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            
            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
            
                #if x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                
                if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                    between = self.DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])
                    for pixel in between:
                        #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))
                    
                        rx1 = pixel[0] * self.x_spacing
                        ry1 = pixel[1] * self.y_spacing
                        rx2 = rx1 + self.x_spacing
                        ry2 = ry1 + self.y_spacing
                        
                        #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                        self.pixel_grid[pixel[1]][pixel[0]] = self.color
                        
                        current_coord = self.coord_str(pixel[0], pixel[1])
                        self.pixel_coords[current_coord] = True
                        #self.display_2d(self.pixel_grid)
                        self.canvas.create_rectangle(
                                            rx1,
                                            ry1,
                                            rx2,
                                            ry2,
                                            fill=self.color,
                                            outline=self.color,
                                            tags=(current_coord)
                                            )
            self.last_pixel.clear()
            
        if len(self.last_pixel) == 0:
            self.last_pixel = [x_pixel, y_pixel]
                    
    def draw(self, event): 
        #print(self.color)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing
        
        self.last_pixel.clear()
        #if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
        if self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            current_coord = self.coord_str(x_pixel, y_pixel)
            #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
            
            
            self.pixel_grid[y_pixel][x_pixel] = self.color
            self.pixel_coords[current_coord] = True
            #self.display_2d(self.pixel_grid)
            self.canvas.create_rectangle(
                                rx1,
                                ry1,
                                rx2,
                                ry2,
                                fill=self.color,
                                outline=self.color,
                                tags=(current_coord)
                            )
            
    def flood_fill(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_pixel = math.floor((x/self.canvas_width) * self.pixel_canvas_width)
        y_pixel = math.floor((y/self.canvas_height) * self.pixel_canvas_height)
        rx1 = x_pixel * self.x_spacing
        ry1 = y_pixel * self.y_spacing
        rx2 = rx1 + self.x_spacing
        ry2 = ry1 + self.y_spacing

        if not self.in_pixel_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            return

        color_under_cursor = self.pixel_grid[y_pixel][x_pixel]

        if color_under_cursor == self.color:
            return


        #BFS flood fill
        #queue
        print("W:{} H:{} X:{} Y:{} XPix:{} YPix:{}".format(self.canvas_width, self.canvas_height , x, y, x_pixel, y_pixel))
        visited = {}
        kyu = []
        kyu.append((y_pixel, x_pixel))
        
        print(kyu)
        i = 0
        while kyu:
            #print(kyu)
            
            
            #print("inside")
            cur = kyu.pop(0)
            
            if not self.in_pixel_bounds(cur[1], cur[0], self.pixel_canvas_width, self.pixel_canvas_height) or self.pixel_grid[ cur[0] ][ cur[1] ] != color_under_cursor: 
                continue
            else:
                #if i == (self.pixel_canvas_width - 1) * (self.pixel_canvas_height - 1):
                #    break
                #print("doin")
                current_coord = self.coord_str(cur[0], cur[1])
                north_coord = self.coord_str(cur[0], cur[1] + 1)
                south_coord = self.coord_str(cur[0], cur[1] - 1)
                east_coord = self.coord_str(cur[0] + 1, cur[1])
                west_coord = self.coord_str(cur[0] - 1, cur[1])


                rx1 = cur[1] * self.x_spacing
                ry1 = cur[0] * self.y_spacing
                rx2 = rx1 + self.x_spacing
                ry2 = ry1 + self.y_spacing
                
                #self.display_2d(self.pixel_grid)
                
                if not visited.get(east_coord):
                    kyu.append((cur[0] + 1, cur[1]))

                if not visited.get(west_coord):
                    kyu.append((cur[0] - 1, cur[1]))

                if not visited.get(north_coord):
                    kyu.append((cur[0], cur[1] + 1))

                if not visited.get(south_coord):
                    kyu.append((cur[0], cur[1] - 1))

      
                
                
                if not visited.get(current_coord):
                    visited[current_coord] = True
                    self.canvas.create_rectangle(
                        rx1,
                        ry1,
                        rx2,
                        ry2,
                        fill=self.color,
                        outline=self.color,
                        tags=(current_coord)
                    )
                    self.pixel_grid[cur[0]][cur[1]]= self.color
                    self.pixel_coords[current_coord] = True
                    self.update_idletasks()
                #print(i, self.color, cur)
                #i += 1

        
        visited.clear()

            #updates the canvas likely makes it so not as much in memory
            
        self.update_idletasks()
        
            
    def bresenham_circle(self, x0, y0, radius):
        x = radius
        y = 0
        err = 3 - 2 * radius
        #5 / 4 - radius
        #3 - 2 * radius

        points = []

        while x >= y:
            points.append((x0 + x, y0 + y))
            points.append((x0 + y, y0 + x))
            points.append((x0 - y, y0 + x))
            points.append((x0 - x, y0 + y))
            points.append((x0 - x, y0 - y))
            points.append((x0 - y, y0 - x))
            points.append((x0 + y, y0 - x))
            points.append((x0 + x, y0 - y))

            y += 1
            err += 1 + 2 * y
            if 2*(err-x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

        return points

    def DDA(self, x0, y0, x1, y1):
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
    


class PaletteFrame(ttk.Frame):
    def __init__(self, parent):
        
        super().__init__(parent)
        #The main drawing canvas
        self.drawing_canvas = None
        #Data
        #dictionary arranged in filename: list of colors
        self.palette_hexdict = {"Current Colors":[]}
        #keeps track of the dynamically generated checkboxes
            #main checkboxes
        self.og_check_dict = {}
            #pop up checkboxes
        self.wn_check_dict = {}
            
        #the color that will be sent ot the main drawing canvas- a hexidecimal color
        self.og_selected_color = ''
        self.wn_selected_color = '' 

        

        #Widgets
        self.palette_options = ["Current Colors"]
        self.palette_label = ttk.Label(self, text="Palette", anchor="center")

        self.selected_palette = tk.StringVar(value=self.palette_options[0])
        
        self.current_palette_cb = ttk.Combobox(self, 
                                                values=self.palette_options, 
                                                textvariable=self.selected_palette,
                                                background="SystemButtonFace" 
                                                

                                                )

        #https://www.iconfinder.com/
        #self.current_palette_cb["values"] = list(range(0, 100))
        self.current_palette_cb.bind("<<ComboboxSelected>>", self.regenerate_checks)

        
        #https://stackoverflow.com/questions/22200003/tkinter-button-not-showing-image
        self.import_palette_img = tk.PhotoImage(file="icons\\211878_plus_icon.png")#.subsample(3,3)
        self.import_palette_bn = tk.Button(self, 
                                        #text=" + ", 
                                        command= lambda:self.manage_palette("Create Palette", False), 
                                        image=self.import_palette_img, 
                                        
                                        )
        CreateToolTip(self.import_palette_bn, "Create a new palette")
        
        self.edit_palette_img = tk.PhotoImage(file="icons\\3671689_edit_pencil_icon.png")
        self.edit_palette_bn = tk.Button(self, 
                                        #text="+?", 
                                        command=lambda:self.manage_palette("Edit Palette", True), 
                                        image=self.edit_palette_img,
                                        
                                        )
        CreateToolTip(self.edit_palette_bn, "Manage Palette")
        
        
        self.mn_w = 250
        self.mn_h = 150
        #https://blog.teclado.com/tkinter-scrollable-frames/
        #the widget below the only widget that has to be gridded in arrangement
        self.mn_frame = ttk.Frame(self)
        #mn frame childern
        self.mn_canvas = tk.Canvas(self.mn_frame, width=self.mn_w, height=self.mn_h) #about the width of a listbox with no specificied width and heoght
        self.mn_scrollbar_y = ttk.Scrollbar(self.mn_frame, orient='vertical', command=self.mn_canvas.yview)
        self.mn_scrollbar_x = ttk.Scrollbar(self.mn_frame, orient='horizontal', command=self.mn_canvas.xview)
        #mn canvas childern, scrollable frame
        self.mn_scrl_frame = ttk.Frame(self.mn_canvas)

        
        
        '''
        #Test
        options = ["Option " + str(i) for i in range(0,18)]
        print(len(options))
        i = 0
        j = 0
        rows = 9
        for option in options:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.mn_scrl_frame, 
                                #text=option, 
                                variable=var, 
                                command=None,
                                font = 11
                                ).grid(row=i, column=j)#pack()
            if j == rows - 1:
                j = -1
                i += 1
                

            
            j += 1
        '''
        
        
        self.mn_scrl_frame.bind(
            "<Configure>",
            lambda e: self.mn_canvas.configure(
                scrollregion=self.mn_canvas.bbox("all")
            )
        )
        
        self.mn_canvas.create_window((0, 0), window=self.mn_scrl_frame, anchor="nw")
        self.mn_canvas.configure(yscrollcommand=self.mn_scrollbar_y.set)
        self.mn_canvas.configure(xscrollcommand=self.mn_scrollbar_x.set)

        
        #gridded inside mn_frame, if mn_frame isn't gridded these won't show up as well.
        self.mn_canvas.grid(row=0, column=0)#pack(side="left", fill="both", expand=True)
        self.mn_scrollbar_y.grid(row=0, column=1, sticky="NS")#pack(side="right", fill="y")
        self.mn_scrollbar_x.grid(row=1, column=0,  sticky="EW")

        #palette window
        self.palette_wn = None
        
        self.arrangement = [
            [None               , self.palette_label,      None],
            [self.import_palette_bn, self.current_palette_cb, self.edit_palette_bn],
            [None               , self.mn_frame     ,    None  ]


        ]



        arrange_widgets(self.arrangement)

        


        #self.mn_frame.grid(row=1,column=0)

    def disable_multiple_widgets(self, widget_arr):
        self.current_palette_cb.config(state="disabled")

    def enable_multiple_widgets(self, widget_arr):
        self.current_palette_cb.config(state="normal")

    


    def palette_wn_open(self):
        #https://stackoverflow.com/questions/76940339/is-there-a-way-to-check-if-a-window-is-open-in-tkinter
        # window has been created an exists, so don't create again.
        return self.palette_wn is not None and self.palette_wn.winfo_exists()
            

    def manage_palette(self, title = "Window", is_editing = False):
        if self.palette_wn_open():
            return
        
        #self.disable_multiple_widgets(self.arrangement)

        self.palette_wn = Toplevel()
        self.palette_wn.resizable(False, False)
        #above tkinter windows
        self.palette_wn.lift()
        
        #above all windows
        #self.palette_wn.attributes('-topmost', 1)
        #self.palette_wn.attributes('-topmost', 0)

        rgb = [0, 0, 0]
        hex_label = tk.Label(self.palette_wn, text=self.rgb2hex(0, 0, 0))
        #Canvas the indicates the color of the sliders
        color_canvas = tk.Canvas(
                                self.palette_wn, 
                                 width=100, height=100, 
                                 background=self.rgb2hex(0, 0, 0)
                                )
        
        red = tk.IntVar()
        red_label = tk.Label(self.palette_wn, text="R", anchor="e")
        red_slider = ttk.Scale(
            self.palette_wn,
            variable=red,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=color_canvas.winfo_width()
         
        )
        
        green = tk.IntVar()
        green_label = tk.Label(self.palette_wn, text="G", anchor="e")
        green_slider = ttk.Scale(
            self.palette_wn,
            variable=green,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=color_canvas.winfo_width()
        )
        
        blue = tk.IntVar()
        blue_label = tk.Label(self.palette_wn, text="B", anchor="e")
        blue_slider = ttk.Scale(
            self.palette_wn,
            variable=blue,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=color_canvas.winfo_width()
        )

        
        

        

        

        

        #the widget below the only widget that has to be gridded in arrangement
        checkbox_frame = ttk.Frame(self.palette_wn)
        #checkbox frame childern
        checkbox_canvas = tk.Canvas(checkbox_frame, width=self.mn_w, height=self.mn_h) #about the width of a listbox with no specificied width and heoght
        checkbox_scrollbar_y = ttk.Scrollbar(checkbox_frame, orient='vertical', command=checkbox_canvas.yview)
        checkbox_scrollbar_x = ttk.Scrollbar(checkbox_frame, orient='horizontal', command=checkbox_canvas.xview)
        #checkbox canvas childern, scrollable frame
        checkbox_scrl_frame = ttk.Frame(checkbox_canvas)


        

        
        
        checkbox_scrl_frame.bind(
            "<Configure>",
            lambda e: checkbox_canvas.configure(
                scrollregion=checkbox_canvas.bbox("all")
            )
        )
        


        checkbox_canvas.create_window((0, 0), window=checkbox_scrl_frame, anchor="nw")
        checkbox_canvas.configure(yscrollcommand=checkbox_scrollbar_y.set)
        checkbox_canvas.configure(xscrollcommand=checkbox_scrollbar_x.set)

        
        
        #gridded inside mn_frame, if mn_frame isn't gridded these won't should up as well.
        checkbox_canvas.grid(row=0, column=0)#pack(side="left", fill="both", expand=True)
        checkbox_scrollbar_y.grid(row=0, column=1, sticky="NS")#pack(side="right", fill="y")
        checkbox_scrollbar_x.grid(row=1, column=0,  sticky="EW")

        palette_label = tk.Label(self.palette_wn, text="Name")
        palette_entry = tk.Entry(self.palette_wn)

        
        
        

        expand_palette = tk.Button(self.palette_wn, 
                                   text="Add Color", 
                                   command=lambda:self.add_color(checkbox_canvas ,checkbox_scrl_frame, red.get(), green.get(), blue.get(), palette_entry.get(), self.wn_check_dict)
                                   )
        
        shrink_palette = tk.Button(self.palette_wn, 
                                   text="Remove Color", 
                                   command=lambda:self.remove_color(checkbox_canvas, checkbox_scrl_frame, palette_entry.get(), self.wn_check_dict)
                                   )
   
        
        import_del_pal = None
        view_update_pal = None
        if is_editing:
            palette_entry.insert(tk.END, self.selected_palette.get())
            palette_entry.config(state="disabled")
            
            import_del_pal = tk.Button(self.palette_wn, 
                                   text="Delete Palette", 
                                   command=lambda:self.delete_palette(self.current_palette_cb.get())
                                   )
            
            view_update_pal = tk.Button(self.palette_wn, 
                                   text="Edit Palette", 
                                   command=lambda:self.edit_palette(checkbox_canvas, checkbox_scrl_frame, self.current_palette_cb , self.wn_check_dict)
                                   )
            
            
        else:
            palette_entry.insert(tk.END, "New Palette Name")
            import_del_pal = tk.Button(self.palette_wn, 
                                   text="Import Palette", 
                                   command=lambda:self.import_palette(checkbox_canvas, checkbox_scrl_frame, palette_entry, self.wn_check_dict)
                                   )
            '''
            view_update_pal = tk.Button(self.palette_wn, 
                                   text="Update Palette", 
                                   command=lambda:self.edit_palette(checkbox_canvas, checkbox_scrl_frame, self.current_palette_cb , self.wn_check_dict)
                                   )
            '''

            
            
        cancel_palette = tk.Button(self.palette_wn, 
                                   text="Cancel", 
                                   command=self.palette_wn.destroy)
        
        save_palette = tk.Button(self.palette_wn, 
                                 text="Save", 
                                 command=lambda:self.save_palette(checkbox_canvas, checkbox_scrl_frame, palette_entry, self.wn_check_dict)
                                 )
            
        
        #changing the selected rbg slide color based on the selected checkbutton color

        

        
        self.palette_wn.bind("<ButtonPress-1>", lambda _ :self.set_rgb_sliders(
                                                                    color_canvas,
                                                                    red,
                                                                    green,
                                                                    blue,
                                                                    hex_label,
                                                                    palette_entry.get(),
                                                                    red_label,
                                                                    green_label,
                                                                    blue_label
                                                                
                                                                    )
                                                                )
        
            

        #Changing the canvas color based on the rgb sliderss
        change_canvas_color = lambda _:self.set_color_configs(
                                            color_canvas,
                                            red,
                                            green,
                                            blue,
                                            hex_label,
                                            palette_entry.get(),
                                            red_label,
                                            green_label,
                                            blue_label,
                                            checkbox_scrl_frame,
                                            self.wn_check_dict
                                            )
        
        red_slider.config(command=change_canvas_color)
        blue_slider.config(command=change_canvas_color)
        green_slider.config(command=change_canvas_color)
        
        
       
        
        

        
        

        arrangement = [
            [palette_label , palette_entry    ,import_del_pal    , view_update_pal],
            [None          , checkbox_frame   ,color_canvas      , None        ],
            [None          , None             , hex_label        , None        ],
            [None          ,red_label         ,red_slider        ,None,expand_palette],
            [None          ,green_label       ,green_slider      ,None,shrink_palette],
            [None          ,blue_label        ,blue_slider       ,None,cancel_palette],
            [None          ,None              , None             ,None  , save_palette]
        ]

        arrange_widgets(arrangement)

        
        
        #self.palette_wn.geometry("200x150")
        self.palette_wn.title(title)
        self.palette_wn.mainloop()

        #print("mainloop")
        
        
        #self.enable_multiple_widgets(self.arrangement)
        


    #https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    #https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
    def rgb2hex(self, r,g,b):
        hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)

        return hexcode
    
    def hex2rgb(self, hexcode, alpha = False):
        hexcode = hexcode[1:]
        rgb = list(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
        if alpha:
            rgb.append(255)
            return rgb 

        return rgb 
        
    

    def color_select(self, check_dict):
        #selects a color tp return to the main drawing canvas
        #so the check mark of a selected color is always visible
        changed_cb = None
        changed_bool = None
        changed_key = ''
        
        for key in check_dict:
            
            #print(data)
            
            data = check_dict[key]
            var = data[0]
            chk = data[1]
            is_chkd = data[2]

            if var.get() and not is_chkd:
                changed_cb = chk
                changed_key = key
                
                data[2] = True
                changed_bool = data[2]
                data[1].config(background = "Green" )
                #print('turned on ', key)
                break
            else:
                data[2] = False
                #print('turned off ', key)
            

        for key in check_dict:
           if key != changed_key:
               data = check_dict[key]
               data[0].set(False)
               data[2] = False
               data[1].config(background = "SystemButtonFace" )

        
            
        #print(changed_key)
        if self.palette_wn_open:
            if check_dict == self.wn_check_dict:
                self.wn_selected_color = changed_key

        if check_dict == self.og_check_dict:
            self.og_selected_color = changed_key

        
        if self.drawing_canvas != None:
            #print(self.og_selected_color)
            if self.og_selected_color:
                self.drawing_canvas.color = self.og_selected_color
            
    def regenerate_checks(self, *args):
        #called by the palette combobox every time a different palette is selected
        if self.current_palette_cb.get() == "Current Colors":
            #scans colors of the main drawing canvas
            if len(self.palette_hexdict) > 1:
                disable_widget(self.import_palette_bn)
                disable_widget(self.edit_palette_bn)

            self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
            self.create_checkboxes(self.mn_scrl_frame, self.current_palette_cb.get(), self.og_check_dict)
        elif self.palette_hexdict.get(self.current_palette_cb.get()):
            if len(self.palette_hexdict) > 1:
                enable_widget(self.import_palette_bn)
                enable_widget(self.edit_palette_bn)
            
            self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
            self.create_checkboxes(self.mn_scrl_frame, self.current_palette_cb.get(), self.og_check_dict)

    def read_colors_from_image(self, entry_widget=None):
        #gets all of the colors from an image as hexcolors
        #always includes black hexcolor #000000
        #colors are stored in a dictionary arranged filename:[hexcolor1, hwxcolor2, etc]

        filetypes = [
            
                    ("png files", "*.png"),
                    ("jpg files", ".jpg .jpeg")

                    ]
        file_path = filedialog.askopenfilename(title="Open Text File", 
                                                filetypes=filetypes
                                                )
        if file_path:
            
            #https://stackoverflow.com/questions/56722800/how-to-get-set-of-colours-in-an-image-using-python-pil
            #https://shegocodes.medium.com/extracting-all-colors-in-images-with-python-2e36eb8a67d2
            img = Image.open(file_path)
            colors = []
            filename = file_path.split("/")[-1]
            if filename == "Current Colors":
                return
            #scan colors of the main drawing canvas
            
            #colors = img.convert('RGB').getcolors() #maxcolors=256
            colors = img.quantize().getpalette()
            #print(colors)
            temp = []
            #if filename not in self.palette_hexdict:
            prev_color = []
            current_color = [colors[0], colors[1], colors[2]]
            if self.palette_hexdict.get(filename):
                self.palette_hexdict[filename].clear()
            self.palette_hexdict[filename] = []

            for i in range(0, len(colors), 3):
                prev_color = current_color

                hex_color = self.rgb2hex(colors[i], colors[i + 1], colors[i + 2])
                if hex_color not in self.palette_hexdict[filename]:
                    self.palette_hexdict[filename].append(hex_color)
                if i >= 3:
                    temp.append(prev_color)
                    current_color = [colors[i], colors[i + 1], colors[i + 2]]
                    if current_color == prev_color:
                        #could cut off black (0,0,0) from colors that end with cmyk
                        #self.palette_hexdict[filename].pop()
                        break
            
            #print(self.palette_hexdict)
            
            if entry_widget != None:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(tk.END, filename)
                           
    def add_color(self, canvas, scrl_frame, r, g ,b, palette_name,  check_dict):
        #adds color checkbuttons to a canvas 
        if palette_name != "Current Colors":
            
            hex_color = self.rgb2hex(r, g, b)
            
            if check_dict.get(hex_color) == None:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(scrl_frame, 
                                    #text=txt, 
                                    variable=var,
                                    command= self.color_select,
                                    onvalue=True,
                                    offvalue=False,
                                    selectcolor= hex_color,
                                    
                                    )
                rows = 9
                chk.grid(
                        row=len(check_dict)//(rows), 
                        column=len(check_dict)%(rows), 
                        sticky="NWES"
                        )
                
                check_dict[hex_color] = [var, chk, False]
              

                if self.palette_hexdict.get(palette_name):
                    if hex_color not in self.palette_hexdict[palette_name]:
                        self.palette_hexdict[palette_name].append(hex_color)
                else:
                    self.palette_hexdict[palette_name] = [hex_color]
                self.clear_checkboxes(canvas, scrl_frame, check_dict)
                self.create_checkboxes(scrl_frame, palette_name, check_dict)
                

        #print(self.palette_hexdict)

    def remove_color(self, canvas, scrl_frame, palette_name, check_dict):
        #removes color checkbuttons from a canvas 
        if palette_name != "Current Colors":
            
            if self.wn_selected_color:
                
                
                data = check_dict[self.wn_selected_color]
                var = data[0]
                chk = data[1]
                
                if isinstance(chk, tk.Checkbutton):
                    var.set(False)
                    chk.destroy()
                check_dict.pop(self.wn_selected_color)

                if self.palette_hexdict.get(palette_name):
                    if self.wn_selected_color in self.palette_hexdict[palette_name]:
                        if len(self.palette_hexdict[palette_name]) > 1:
                            self.palette_hexdict[palette_name].remove(self.wn_selected_color)

                self.clear_checkboxes(canvas, scrl_frame, check_dict)
                self.create_checkboxes(scrl_frame, palette_name, check_dict)
    
    def delete_palette(self, palette_name):
        if self.palette_hexdict.get(palette_name) and palette_name != "Current Colors":
            self.palette_hexdict.pop(palette_name)
            

            self.palette_options.remove(palette_name)
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette.set(self.palette_options[-1])
            delete_warning = True
            #The Original Window
            self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
            self.create_checkboxes(self.mn_scrl_frame, self.selected_palette.get(), self.og_check_dict)
            self.palette_wn.destroy()

    def save_palette(self, canvas, scrl_frame, entry, check_dict):
        self.update_listbox(entry.get())
        

        #The Original Window
        self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
        self.create_checkboxes(self.mn_scrl_frame, entry.get(), self.og_check_dict)

        #The Pop-Up Window
        self.clear_checkboxes(canvas, scrl_frame, check_dict)
        self.create_checkboxes(scrl_frame, entry.get(), check_dict)
        
        self.wn_selected_color = '#000000'

        
        #self.palette_wn.destroy()
         
    def import_palette(self, canvas, scrl_frame, entry, check_dict):
        
        self.read_colors_from_image(entry)
        #The Pop-Up Window
        self.clear_checkboxes(canvas, scrl_frame, check_dict)
        self.create_checkboxes(scrl_frame, entry.get(), check_dict)

        #The Original Window
        #self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
        #self.create_checkboxes(self.mn_scrl_frame, entry.get(), self.og_check_dict)

        #Raising up about base window
        self.palette_wn.lift()
         
    def edit_palette(self, canvas, scrl_frame, cb, check_dict):
        #The Pop-Up Window
        self.clear_checkboxes(canvas, scrl_frame, check_dict)
        self.create_checkboxes(scrl_frame, cb.get(), check_dict)

        #The Original Window
        #self.clear_checkboxes(self.mn_canvas, self.mn_scrl_frame, self.og_check_dict)
        #self.create_checkboxes(self.mn_scrl_frame, entry.get(), self.og_check_dict)

    def clear_checkboxes(self, canvas, scrl_frame, check_dict):
        if check_dict:
            for key in check_dict:
                data = check_dict[key]
                var = data[0]
                chk = data[1]
                if isinstance(chk, tk.Checkbutton):
                    var.set(False)
                    chk.destroy()

        check_dict.clear()
        canvas.delete("all")
        canvas.create_window((0, 0), window=scrl_frame, anchor="nw")

    def create_checkboxes(self, scrl_frame, palette_name, check_dict):
        if self.palette_hexdict.get(palette_name):
            i = 0
            j = 0
            rows = 9
            for hex_color in self.palette_hexdict[palette_name]:
                
                #print(f"Hexcode: {hex_color}")
                color = self.hex2rgb(hex_color)
                #print(f"Color RGB: {color}, Hexcode: {hex_color}")
                
                var = tk.BooleanVar()
                chk = tk.Checkbutton(
                                    scrl_frame, 
                                    #text=txt, 
                                    variable=var,
                                    command= lambda:self.color_select(check_dict),
                                    onvalue=True,
                                    offvalue=False,
                                    selectcolor= hex_color,
                                    )
                chk.grid(row=i, column=j, sticky="NWES")#pack()
                if j == rows - 1:
                    j = -1
                    i += 1
                
                check_dict[hex_color] = [var, chk, False]
                j += 1

    def update_listbox(self, palette_name):
        if palette_name not in self.palette_options:
            self.palette_options.append(palette_name)
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette.set(self.palette_options[-1])

    def set_rgb_sliders(self, c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label):
        #sets the rgb sliders to match the selected color
        if self.palette_hexdict.get(palette_name):
            if self.wn_selected_color in self.palette_hexdict[palette_name]:
                self.update_idletasks()
                ind = self.palette_hexdict[palette_name].index(self.wn_selected_color)
                val = self.palette_hexdict[palette_name][ind]
                #hex_color = self.rgb2hex(r,g,b)
                c_canvas.config(bg=val)
                label.config(text=val)
                rgb = self.hex2rgb(val)
                r.set(rgb[0])
                g.set(rgb[1])
                b.set(rgb[2])
                
                r_label.config(text="R:{}".format(rgb[0]))
                g_label.config(text="G:{}".format(rgb[1]))
                b_label.config(text="B:{}".format(rgb[2]))
                
                
                #updates all checkboxes, unfeasible for large color palette editing
                #self.clear_checkboxes(o_canvas, scrl_frame, check_dict)
                #self.create_checkboxes(o_canvas, scrl_frame, check_dict)
  
    def set_color_configs(self, c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label, scrl_frame, check_dict):
        #self.set_rgb_sliders(c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label)
        #allows the color canvas color to be changed 
        # and the selected color buttons to be as well
        #using ethe rgb color sliders
        

        #changing to new hex
        hex_color = self.rgb2hex(r.get(),g.get(),b.get())
        c_canvas.config(bg=hex_color)
        label.config(text=hex_color)
        
        
        r_label.config(text="R:{}".format(r.get()))
        g_label.config(text="G:{}".format(g.get()))
        b_label.config(text="B:{}".format(b.get()))
        if self.palette_hexdict.get(palette_name):
            if self.wn_selected_color in self.palette_hexdict[palette_name]:
                if hex_color not in self.palette_hexdict[palette_name]:
                    #print("running")
                    ind = self.palette_hexdict[palette_name].index(self.wn_selected_color)
                    self.palette_hexdict[palette_name][ind] = hex_color
                    
                    #updates all checkboxes, unfeasible for large color palette editing
                    #self.clear_checkboxes(o_canvas, scrl_frame, check_dict)
                    #self.create_checkboxes(o_canvas, scrl_frame, check_dict)
                    

                    #The selected checkbox in the pop-up window 
                    #replacing a single checkbox with a new one
                    
                    
                    if self.wn_check_dict.get(self.wn_selected_color):
                        #print("runsa")
                        data = self.wn_check_dict.pop(self.wn_selected_color)
                        var = data[0]
                        chk = data[1]
                        booln = data[2]

                        #destroying and recreating check box
                        c_grid_info = chk.grid_info() #config(selectcolor=hex_color)
                        c_row = c_grid_info['row']
                        c_col = c_grid_info['column']
                        chk.destroy()
                        nu_chk = tk.Checkbutton(
                                        scrl_frame, 
                                        #text=txt, 
                                        variable=var,
                                        command= lambda:self.color_select(check_dict),
                                        onvalue=True,
                                        offvalue=False,
                                        selectcolor= hex_color,
                                        background = "Green" 
                                        )
                        
                        nu_chk.grid(row=c_row, column=c_col, sticky="NWES")
                        #nu_chk['selectcolor']=hex_color
                        
                        

                        self.wn_check_dict[hex_color] = [var, nu_chk, booln]

                        scrl_frame.update()
                        scrl_frame.update_idletasks()
                    self.wn_selected_color = hex_color

    def set_drawing_canvas(self, main_canvas):
        self.drawing_canvas = main_canvas

    def set_selected_color(self, color):
        
        palette_name = self.selected_palette.get()
        #clears the original window checkbox selection
        for key in self.og_check_dict:
            data = self.og_check_dict[key]
            var = data[0]
            
            chk = data[1]
            is_chkd = data[2]
            var.set(False)
            data[1].config(background = "SystemButtonFace")

        
        if self.palette_hexdict.get(palette_name):
            if color in self.palette_hexdict.get(palette_name):
                
                
                
                #updates all checkboxes, unfeasible for large color palette editing
                #self.clear_checkboxes(o_canvas, scrl_frame, check_dict)
                #self.create_checkboxes(o_canvas, scrl_frame, check_dict)
                

                #The selected checkbox in the pop-up window 
                #replacing a single checkbox with a new one
                
                
                if self.og_check_dict.get(color):
                    #print("runsa")

                    
                    data = self.og_check_dict[color]
                    var = data[0]
                    chk = data[1]
                    booln = data[2]

                    #destroying and recreating check box
                    c_grid_info = chk.grid_info() #config(selectcolor=hex_color)
                    c_row = c_grid_info['row']
                    c_col = c_grid_info['column']
                    chk.destroy()
                    nu_chk = tk.Checkbutton(
                                    
                                    self.mn_scrl_frame, 
                                    #text=txt, 
                                    variable=var,
                                    command= lambda:self.color_select(self.og_check_dict),
                                    onvalue=True,
                                    offvalue=False,
                                    selectcolor= color,
                                    background = "Green" 
                                    )
                    
                    nu_chk.grid(row=c_row, column=c_col, sticky="NWES")
                    var.set(True)
                    #nu_chk['selectcolor']=hex_color
                    self.og_selected_color = color
                    

                    self.og_check_dict[color] = [var, nu_chk, booln]

    def set_current_colors(self, colors_set):
        self.palette_hexdict["Current Colors"].clear()
        self.palette_hexdict["Current Colors"] = list(colors_set)
        palette_name = self.selected_palette.get()
        if palette_name == "Current Colors":
            #self.clear_checkboxes(o_canvas, scrl_frame, check_dict)
            #self.create_checkboxes(o_canvas, scrl_frame, check_dict)
            pass



class BrushSize(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pass              
                
class ManipulationOptions(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pref_val = tk.BooleanVar(value=False)
        self.pref_cb = tk.Checkbutton(self, 
                                      text="Preferences", 
                                      variable=self.pref_val,
                                      ) 
        self.pref_sub_bn = tk.Button(self, text="Test")
        self.pref_widgets = [
            self.pref_sub_bn
        ]

        self.resize_val = tk.BooleanVar(value=False)
        self.resize_cb = tk.Checkbutton(self, 
                                        text="Resize",
                                        variable=self.resize_val
                                        )  
        self.resize_sub_bn = tk.Button(self, text="Test")
        self.resize_widgets = [
            self.resize_sub_bn
        ]
        

        self.save_val = tk.BooleanVar(value=False)
        self.save_cb = tk.Checkbutton(self, 
                                      text="Resize",
                                      variable=self.save_val
                                      )  
        self.save_sub_bn = tk.Button(self, text="Test")
        self.save_widgets = [
            self.save_sub_bn
        ]

        self.imp_val = tk.BooleanVar(value=False)
        self.imp_cb = tk.Checkbutton(self,
                                    text="Import",
                                    variable=self.imp_val
                                    )  
        self.imp_sub_bn = tk.Button(self, text="Test")
        self.imp_widgets = [
            self.imp_sub_bn
        ]

        self.exp_val = tk.BooleanVar(value=False)
        self.exp_cb = tk.Checkbutton(self, 
                                    text="Export",
                                    variable=self.exp_val
                                    )  
        self.exp_sub_bn = tk.Button(self, text="Test")
        self.exp_widgets = [
            self.exp_sub_bn
        ]

        

        self.manip_widgets = [
            [self.pref_cb, self.pref_val],
            [self.resize_cb, self.resize_val],
            [self.save_cb, self.save_val],
            [self.imp_cb, self.imp_val],
            [self.exp_cb, self.exp_val] 
        ]

        arrangement = [
            [self.pref_cb],
            [self.resize_cb],
            [self.save_cb],
            [self.imp_cb],
            [self.exp_cb] 
        ]

        self.pref_cb.config(command=lambda:self.manage_widget_group(self.pref_cb))
        self.resize_cb.config(command=lambda:self.manage_widget_group(self.resize_cb))
        self.save_cb.config(command=lambda:self.manage_widget_group(self.save_cb))
        self.imp_cb.config(command=lambda:self.manage_widget_group(self.imp_cb))
        self.exp_cb.config(command=lambda:self.manage_widget_group(self.exp_cb))


        arrange_widgets(arrangement)



    
    
    def manage_widget_group(self,  clicked_widget):
        for widget_bv_g in self.manip_widgets:
            widget = widget_bv_g[0]
            bv = widget_bv_g[1]

            if widget != clicked_widget:
                bv.set(False)
            else:
                bv.set(True)

                

class DrawingTools(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.drawing_canvas = None
        self.mode = ""

        self.pen_img = tk.PhotoImage(file="icons\\edit_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.pen_bn = tk.Button(self, 
                                 text="Draw", 
                                 image=self.pen_img,
                                 ) 
        CreateToolTip(self.pen_bn, "Pen Tool")
        
        self.fill_img = tk.PhotoImage(file="icons\\format_color_fill_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.fill_bn = tk.Button(self, 
                                 text="Bucket", 
                                 image=self.fill_img
                                 ) 
        CreateToolTip(self.fill_bn, "Bucket Tool")
        
        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_bn = tk.Button(self, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_bn, "Eraser Tool")
        

        
        self.rect_img = tk.PhotoImage(file="icons\\rectangle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_bn = tk.Button(self, 
                                 text="Rectangle", 
                                 image=self.rect_img
                                 ) 
        CreateToolTip(self.rect_bn, "Rectangle Tool")
        
        self.circ_img = tk.PhotoImage(file="icons\\circle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.circ_bn = tk.Button(self, 
                                 text="Circle", 
                                 image=self.circ_img
                                 ) 
        CreateToolTip(self.circ_bn, "Circle Tool")
        
        self.move_img = tk.PhotoImage(file="icons\\back_hand_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.move_bn = tk.Button(self, 
                                 text="Move", 
                                 image=self.move_img
                                 ) 
        CreateToolTip(self.move_bn, "Move Tool")
        
        self.lasso_sel_img = tk.PhotoImage(file="icons\\lasso_select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.lasso_sel_bn = tk.Button(self, 
                                 text="Lasso", 
                                 image=self.lasso_sel_img
                                 ) 
        CreateToolTip(self.lasso_sel_bn, "Lasso Selection")
        
        self.rect_sel_img = tk.PhotoImage(file="icons\\select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_sel_bn = tk.Button(self, 
                                 text="Select", 
                                 image=self.rect_sel_img
                                 ) 
        CreateToolTip(self.rect_sel_bn, "Rectangle Selection")
        
        self.line_img = tk.PhotoImage(file="icons\\border_color_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.line_bn = tk.Button(self, 
                                 text="Stroke", 
                                 image=self.line_img 
                                 ) 
        CreateToolTip(self.line_bn, "Stroke Tool")
        
        self.picker_img = tk.PhotoImage(file="icons\\colorize_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.picker_bn = tk.Button(self, 
                                 text="Picker", 
                                 image=self.picker_img
                                 ) 
        CreateToolTip(self.picker_bn, "Color Picker")
        
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


        self.drawing_widgets = [
            self.pen_bn     , self.line_bn,
            self.erase_bn   , self.move_bn,
            self.rect_bn    , self.circ_bn,
            self.rect_sel_bn, self.lasso_sel_bn,
            self.picker_bn  ,  self.fill_bn,
        ]

        arrangement = [

            [self.pen_bn     , self.line_bn],
            [self.erase_bn   , self.move_bn],
            [self.rect_bn    , self.circ_bn],
            [self.rect_sel_bn, self.lasso_sel_bn],
            [self.picker_bn  ,  self.fill_bn],
           
        ]

        arrange_widgets(arrangement)
        #self.select_mode(self.pen_bn)

    def select_mode(self, clicked_widget):
        for widget in self.drawing_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")
                #print(self.mode)
                if self.drawing_canvas:
                    self.drawing_canvas.mode = self.mode

    def set_drawing_canvas(self, drawing_canvas):
        self.drawing_canvas = drawing_canvas
        self.drawing_canvas.mode = self.mode

    def set_mode(self, mode):
        self.mode = mode
        for widget in self.drawing_widgets:
            if widget.cget("text") == mode:
                self.mode = mode
                widget.config(bg="yellow")
            else:
                widget.config(bg="SystemButtonFace")
        
    def get_mode(self):
        return self.mode

        
         


class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Simple Pixel Art App") 

        self.file_manip = ManipulationOptions(self)
        
        self.drawing_canvas = MainCanvas(self, 512, 512, 250, 250)
        self.drawing_tools = DrawingTools(self)
        self.palette = PaletteFrame(self)

        
        self.drawing_canvas.set_selection_palette(self.palette)
        self.drawing_canvas.set_draw_tools(self.drawing_tools)

        self.drawing_tools.set_mode("Draw")
        self.drawing_tools.set_drawing_canvas(self.drawing_canvas)
        self.palette.set_drawing_canvas(self.drawing_canvas)
        
        #self.frame_1 = FrameArrangement(self, [self.drawing_tools])

        #self.palette.grid()
        arrangement = [
            [self.drawing_tools, self.drawing_canvas, self.palette, self.file_manip],
            [None, None]
        ]

        arrange_widgets(arrangement)    


 
if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    app.resizable()
    app.mainloop()
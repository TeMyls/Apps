import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
import math
import random 

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

def delete_widget(widget):
    widget.destroy()

def to_radians(degrees):
    return (degrees* math.pi)/180


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

class Vertex():
    def __init__(self, x , y):
        self.v = set_matrix2D(x, y)
        


    def get_X(self):
        return self.v[0][0]
    
    def get_Y(self):
        return self.v[1][0]

    def __str__(self):
        return "X {} Y {}".format(self.get_X(), self.get_Y())
    
    def set_coords(self, x, y):

        self.v[0][0] = x
        self.v[1][0] = y
        self.v[2][0] = 1




    

class ShapeCollisions(ttk.Frame):
    def __init__(self, parent, c_width, c_height):
        super().__init__(parent)
        self.hitting = False
        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        self.canvas_width = c_width #self.canvas.winfo_width()
        self.canvas_height = c_height #self.canvas.winfo_height()
        #self.canvas.grid(row = 0, column = 0, sticky = "N")



        

        


        


        

        
        #-----------------------------------------------------------------------------------------------------------------------
        #Shapes 1
        #-----------------------------------------------------------------------------------------------------------------------
        self.btn_1_frm = ttk.Frame(self)
        self.color_1 = "cyan"

        self.point_img = tk.PhotoImage(file="shape_icons\\arrow_insert_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.circle_img = tk.PhotoImage(file="shape_icons\\circle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_img = tk.PhotoImage(file="shape_icons\\check_box_outline_blank_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.line_img = tk.PhotoImage(file="shape_icons\\pen_size_1_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.poly_img = tk.PhotoImage(file="shape_icons\\star_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)

        self.point_1_btn = tk.Button(self.btn_1_frm, 
                                 text="Point", 
                                 image=self.point_img,
                                 ) 
        

        
        self.circle_1_btn = tk.Button(self.btn_1_frm, 
                                 text="Circle", 
                                 image=self.circle_img,
                                 ) 
        

        
        self.rect_1_btn = tk.Button(self.btn_1_frm, 
                                 text="Rectangle", 
                                 image=self.rect_img
                                 ) 
        


        

        
        self.line_1_btn = tk.Button(self.btn_1_frm, 
                                 text="Line", 
                                 image=self.line_img
                                 ) 
        


       
        self.poly_1_btn = tk.Button(self.btn_1_frm, 
                                 text="Polygon", 
                                 image=self.poly_img
                                 ) 
        

        CreateToolTip(self.point_1_btn, "Point")
        CreateToolTip(self.circle_1_btn, "Circle")
        CreateToolTip(self.rect_1_btn, "Rectangle")

        CreateToolTip(self.line_1_btn, "Line")
        CreateToolTip(self.poly_1_btn, "Polygon")

        

        self.shape_1_widgets = [
            self.point_1_btn,
            self.circle_1_btn,
            self.rect_1_btn,
            self.poly_1_btn,
            self.line_1_btn
        ]

        self.point_1_btn.config(command=lambda:self.select_mode(self.point_1_btn, self.shape_1_widgets, self.color_1))
        self.circle_1_btn.config(command=lambda:self.select_mode(self.circle_1_btn, self.shape_1_widgets, self.color_1))
        self.rect_1_btn.config(command=lambda:self.select_mode(self.rect_1_btn, self.shape_1_widgets, self.color_1))
        self.line_1_btn.config(command=lambda:self.select_mode(self.line_1_btn, self.shape_1_widgets, self.color_1))
        self.poly_1_btn.config(command=lambda:self.select_mode(self.poly_1_btn, self.shape_1_widgets, self.color_1))

        btn_1_arrangement = [
            [self.point_1_btn, self.circle_1_btn],
            [self.rect_1_btn , self.poly_1_btn   ],
            [self.line_1_btn , None              ]     
        ]

        arrange_widgets(btn_1_arrangement)

        #-----------------------------------------------------------------------------------------------------------------------
        #Shapes 2
        #-----------------------------------------------------------------------------------------------------------------------
        self.btn_2_frm = ttk.Frame(self)
        self.color_2 = "magenta"

        self.point_2_btn = tk.Button(self.btn_2_frm, 
                                 text="Point", 
                                 image=self.point_img,
                                 ) 
        

        
        self.circle_2_btn = tk.Button(self.btn_2_frm, 
                                 text="Circle", 
                                 image=self.circle_img,
                                 ) 
        

        
        self.rect_2_btn = tk.Button(self.btn_2_frm, 
                                 text="Rectangle", 
                                 image=self.rect_img
                                 ) 
        

        


        
        self.line_2_btn = tk.Button(self.btn_2_frm, 
                                 text="Line", 
                                 image=self.line_img
                                 ) 
        


       
        self.poly_2_btn = tk.Button(self.btn_2_frm, 
                                 text="Polygon", 
                                 image=self.poly_img
                                 ) 
        

        CreateToolTip(self.point_2_btn, "Point")
        CreateToolTip(self.circle_2_btn, "Circle")
        CreateToolTip(self.rect_2_btn, "Rectangle")
        CreateToolTip(self.line_2_btn, "Line")
        CreateToolTip(self.poly_2_btn, "Polygon")

        #-----------------------------------------------------------------------------------------------------------------------
        
        #-----------------------------------------------------------------------------------------------------------------------

        self.shape_2_widgets = [
            self.point_2_btn,
            self.circle_2_btn,
            self.rect_2_btn,
            self.poly_2_btn,
            self.line_2_btn
            
        ]

        self.point_2_btn.config(command=lambda:self.select_mode(self.point_2_btn, self.shape_2_widgets, self.color_2))
        self.circle_2_btn.config(command=lambda:self.select_mode(self.circle_2_btn, self.shape_2_widgets, self.color_2))
        self.rect_2_btn.config(command=lambda:self.select_mode(self.rect_2_btn, self.shape_2_widgets, self.color_2))
        self.line_2_btn.config(command=lambda:self.select_mode(self.line_2_btn, self.shape_2_widgets, self.color_2))
        self.poly_2_btn.config(command=lambda:self.select_mode(self.poly_2_btn, self.shape_2_widgets, self.color_2))

        btn_2_arrangement = [
            [self.point_2_btn, self.circle_2_btn],
            [self.rect_2_btn , self.poly_2_btn   ],
            [self.line_2_btn , None              ]   
        ]

        arrange_widgets(btn_2_arrangement)

        

        
        self.shape_vertices = {
            "Point": 1,
            "Circle": 1,
            "Rectangle": 4,
            "Line": 2,
            "Polygon": 7
        }
        #shapes 1
        self.shape_ls = ["Point", "Circle", "Rectangle", "Line", "Polygon"]

        #x, y, radius
        self.shape_vtx_1 = [Vertex(0, 0)]

        self.line_dist_1 = 40
        self.line_angle_1 = to_radians(random.randint(0, 360))
        self.rect_dist_1 = 40
        self.circle_radius_1 = 40
        self.poly_dist_1 = 40
        self.point_buffer_1 = 5

        self.shape_vtx_2 = [Vertex(0, 0)]

        self.circle_radius_2 = 40

        self.line_dist_2 = 40
        self.line_angle_2 = to_radians(random.randint(0, 360))
        self.rect_dist_2 = 40
        self.circle_radius_2 = 40
        self.poly_dist_2 = 40
        self.point_buffer_2 = 5


        


        #Drawing Initial Shapes

    

        


        arrangement = [
            [None           , None                   , None             ],
            [self.btn_1_frm   , self.canvas            , self.btn_2_frm   ],
            [None           , None                   , None             ]
        

        ]

        arrange_widgets(arrangement)

        
        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.canvas.bind("<ButtonRelease-3>", self.on_button_release)
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_rmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        



        #initialization
        self.shape_1 = "Line"
        self.shape_2 = "Point"
        self.shape_tag_1 = "1st"
        self.shape_tag_2 = "2nd"
        self.mx_1 = self.canvas_width * 0.25
        self.my_1 = self.canvas_height/2
        self.mx_2 = self.canvas_width * 0.75
        self.my_2 = self.canvas_height/2
        self.fill_1 = ""
        self.fill_2 = ""

        

        self.select_mode(self.line_1_btn, self.shape_1_widgets, self.color_1)
        self.select_mode(self.point_2_btn, self.shape_2_widgets, self.color_2)

        self.make_shape(self.mx_2, self.my_2, self.shape_vtx_2, self.color_2, self.shape_tag_2, self.shape_2, self.color_1)
        self.make_shape(self.mx_1, self.my_1, self.shape_vtx_1, self.color_1, self.shape_tag_1, self.shape_1, self.color_2)
        
        
        

    def on_canvas_lmb_click(self, event):
        self.mx_1 = self.canvas.canvasx(event.x)
        self.my_1 = self.canvas.canvasy(event.y)

        self.make_shape(self.mx_1, self.my_1, self.shape_vtx_1, self.color_1, self.shape_tag_1, self.shape_1, self.color_2)

    def on_canvas_lmb_press(self, event):
        self.mx_1 = self.canvas.canvasx(event.x)
        self.my_1 = self.canvas.canvasy(event.y)

        self.make_shape(self.mx_1, self.my_1, self.shape_vtx_1, self.color_1, self.shape_tag_1, self.shape_1, self.color_2)
    def on_canvas_rmb_click(self, event):
        self.mx_2 = self.canvas.canvasx(event.x)
        self.my_2 = self.canvas.canvasy(event.y)

        self.make_shape(self.mx_2, self.my_2, self.shape_vtx_2, self.color_2, self.shape_tag_2, self.shape_2, self.color_1)

    def on_canvas_rmb_press(self, event):
        self.mx_2 = self.canvas.canvasx(event.x)
        self.my_2 = self.canvas.canvasy(event.y)

        self.make_shape(self.mx_2, self.my_2, self.shape_vtx_2, self.color_2, self.shape_tag_2, self.shape_2, self.color_1)

    def select_mode(self, clicked_widget, widget_arr, color):
        
        for widget in widget_arr:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
            else:

                widget.config(bg=color)
                if color == self.color_1:
                    self.shape_1 = widget.cget("text")
                elif color == self.color_2:
                    self.shape_2 = widget.cget("text")


        
        self.make_shape(self.mx_1, self.my_1, self.shape_vtx_1, self.color_1, self.shape_tag_1, self.shape_1, self.color_2)
        self.make_shape(self.mx_2, self.my_2, self.shape_vtx_2, self.color_2, self.shape_tag_2, self.shape_2, self.color_1)
                


    def on_button_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.shape_1 == "Line":
            self.line_angle_1 = to_radians(random.randint(0, 360))
            self.make_shape(self.mx_1, self.my_1, self.shape_vtx_1, self.color_1, self.shape_tag_1, self.shape_1, self.color_2)
        elif self.shape_2 == "Line":
            self.line_angle_2 = to_radians(random.randint(0, 360))
            self.make_shape(self.mx_2, self.my_2, self.shape_vtx_2, self.color_2, self.shape_tag_2, self.shape_2, self.color_1)

        self.shape_vertices["Polygon"] = random.randint(3, 7)



    def get_polygon(self, vertex_ls):
        polygon = []
        for i in range(len(vertex_ls)): 
            vtx = vertex_ls[i]
            vx, vy = vtx.get_X(), vtx.get_Y()
            polygon.append(vx)
            polygon.append(vy)
        return polygon



    def is_colliding(self):
        one_colliding = False
        #shape 2
        x1, y1, x2, y2, x3, y3, x4, y4 = 1, 1, 1, 1, 1, 1, 1, 1
        #shape 1
        vx1, vy1, vx2, vy2, vx3, vy3, vx4, vy4 = 1, 1, 1, 1, 1, 1, 1, 1

        
        


        #The amount of vertices in each array
        if len(self.shape_vtx_2) > 0: 
            x1, y1 = self.shape_vtx_2[0].get_X(), self.shape_vtx_2[0].get_Y()
            
        if len(self.shape_vtx_2) > 1: 
            x2, y2 = self.shape_vtx_2[1].get_X(), self.shape_vtx_2[1].get_Y()
        
        if len(self.shape_vtx_2) > 2: 
            x3, y3 = self.shape_vtx_2[2].get_X(), self.shape_vtx_2[2].get_Y()
        
        if len(self.shape_vtx_2) > 3: 
            x4, y4 = self.shape_vtx_2[3].get_X(), self.shape_vtx_2[3].get_Y()



        if len(self.shape_vtx_1) > 0: 
            vx1, vy1 = self.shape_vtx_1[0].get_X(), self.shape_vtx_1[0].get_Y()
            
        if len(self.shape_vtx_1) > 1: 
            vx2, vy2 = self.shape_vtx_1[1].get_X(), self.shape_vtx_1[1].get_Y()
        
        if len(self.shape_vtx_1) > 2: 
            vx3, vy3 = self.shape_vtx_1[2].get_X(), self.shape_vtx_1[2].get_Y()
        
        if len(self.shape_vtx_1) > 3: 
            vx4, vy4 = self.shape_vtx_1[3].get_X(), self.shape_vtx_1[3].get_Y()

        if self.shape_1 == "Point" and self.shape_2 == "Point":
            #print(1)
            if point_point(self.mx_1, self.my_1, self.my_2, self.my_2, self.point_buffer_1):
                one_colliding = True
                return one_colliding
            
        if self.shape_1 == "Circle" and self.shape_2 == "Circle":   
            #print(2)     
            if circle_circle(self.mx_1, self.my_1, self.circle_radius_1, self.mx_2, self.my_2, self.circle_radius_2):
                one_colliding = True
                return one_colliding
            
        if self.shape_1 == "Line" and self.shape_2 == "Line": 
            #Shape 1: Line
            #Shape 2: Line
            #print(3)
            if line_line(vx1, vy1, vx2, vy2, x1, y1, x2, y2):
                
                one_colliding = True
                return one_colliding
            
        if self.shape_1 == "Rectangle" and self.shape_2 == "Rectangle": 
            #Shape 1: Rectangle
            #Shape 2: Rectangle
            print(4)
            if len(self.shape_vtx_1) > 3 and len(self.shape_vtx_2) > 3:
                if rectangle_rectangle(vx1, vy1, vx2 - vx1, vy4 - vy1, x1, y1, x2 - x1, y4 - y1):
                    one_colliding = True
                    
                    return one_colliding
            
        
        

            
        


        if self.shape_1 == "Point" and self.shape_2 == "Circle": 
            #print(7)
            if point_circle(self.mx_1, self.my_1, self.mx_2, self.my_2, self.circle_radius_2):
                one_colliding = True
                return one_colliding
        elif self.shape_1 == "Circle" and self.shape_2 == "Point": 
            #print(8)
            if point_circle(self.mx_2, self.my_2, self.mx_1, self.my_1, self.circle_radius_1):
                one_colliding = True
                return one_colliding

        if self.shape_1 == "Point" and self.shape_2 == "Line": 
            #Shape 1: Point 
            #Shape 2: Line
            #print(9)
            if line_point(x1, y1, x2, y2, self.mx_1, self.my_1, self.point_buffer_1):
                
                one_colliding = True
                return one_colliding
            
        elif self.shape_1 == "Line" and self.shape_2 == "Point": 
            #Shape 1: Line
            #Shape 2: Point
            #print(10)
            if line_point(vx1, vy1, vx2, vy2, self.mx_2, self.my_2, self.point_buffer_2):
                
                one_colliding = True
                return one_colliding


        
        if self.shape_1 == "Line" and self.shape_2 == "Circle": 
            #Shape 1: Line 
            #Shape 2: Circle
            #print(11)
            if line_circle(vx1, vy1, vx2, vy2, self.mx_2, self.my_2, self.circle_radius_2):
            
                one_colliding = True
                return one_colliding
        
        elif self.shape_1 == "Circle" and self.shape_2 == "Line": 
            #Shape 1: Circle
            #Shape 2: Line
            #print(12)
            if line_circle(x1, y1, x2, y2, self.mx_1, self.my_1, self.circle_radius_1):

                one_colliding = True
                return one_colliding
            


        
        if self.shape_1 == "Line" and self.shape_2 == "Rectangle":
            #Shape 1: Line
            #Shape 2: Rectangle
            #print(13)
            if line_rectangle(vx1, vy1, vx2, vy2, x1, y1, x3 - x4, y3 - y2):
                
                one_colliding = True
                '''
                self.canvas.create_rectangle(
                            x4, y4,
                            x6, y6,
                            fill=self.color_1,
                            tags=(self.shape_tag_1 )
                            )
                '''
                return one_colliding
        elif self.shape_1 == "Rectangle" and self.shape_2 == "Line":
            #Shape 1: Rectangle
            #Shape 2: Line
            #print(14)
            if line_rectangle(x1, y1, x2, y2, vx1, vy1, vx3 - vx4, vy3 - vy2):
                one_colliding = True
                
                return one_colliding
            


        if self.shape_1 == "Point" and self.shape_2 == "Rectangle":
            #print(15)
            if point_rectangle(self.mx_1, self.my_1, x1, y1, x3 - x4, y3 - y2):
                one_colliding = True
                
                return one_colliding
        elif self.shape_1 == "Rectangle" and self.shape_2 == "Point":
            #print(16)
            if point_rectangle(self.mx_2, self.my_2, vx1, vy1, vx3 - vx4, vy3 - vy2):
                one_colliding = True
                
                return one_colliding

        
        if self.shape_1 == "Rectangle" and self.shape_2 == "Circle":
            #Shape 1: Rectangle
            #Shape 2: Circle
            #print(17)
            if circle_rectangle(self.mx_2, self.my_2, self.circle_radius_2, vx1, vy1, vx3 - vx4, vy3 - vy2):
                one_colliding = True
                
                return one_colliding
        elif self.shape_1 == "Circle" and self.shape_2 == "Rectangle":
            #Shape 1: Circle
            #Shape 2: Rectangle
            #print(18)
            if circle_rectangle(self.mx_1, self.my_1, self.circle_radius_1, x1, y1, x3 - x4, y3 - y2):
                one_colliding = True
                
                return one_colliding

        
        


        

        if self.shape_1 == "Polygon" and self.shape_2 == "Line":
            #Shape 1: Polygon
            #Shape 2: Line
            #print(19)
            if polygon_line(self.get_polygon(self.shape_vtx_1), x1, y1, x2, y2):
                one_colliding = True
                return one_colliding
            
        elif self.shape_1 == "Line" and self.shape_2 == "Polygon":
            #Shape 1: Line
            #Shape 2: Polygon
            #print(20)
            if polygon_line(self.get_polygon(self.shape_vtx_2), vx1, vy1, vx2, vy2):
                
                one_colliding = True
                return one_colliding

        

        

        if self.shape_1 == "Polygon" and self.shape_2 == "Rectangle":
            #Shape 1: Polygon
            #Shape 2: Rectangle
            #print(21)
            if polygon_rectangle(self.get_polygon(self.shape_vtx_1), x1, y1, x3 - x4, y3 - y2):
                one_colliding = True
                
                return one_colliding
        elif self.shape_1 == "Rectangle" and self.shape_2 == "Polygon":
            #Shape 1: Polygon
            #Shape 2: Rectangle
            #print(22)
            if polygon_rectangle(self.get_polygon(self.shape_vtx_2), vx1, vy1, vx3 - vx4, vy3 - vy2):
                one_colliding = True
                return one_colliding
            


        
        if self.shape_1 == "Polygon" and self.shape_2 == "Circle":
            #Shape 1: Polygon
            #Shape 2: Circle
            #print(23)
            if polygon_circle(self.get_polygon(self.shape_vtx_1), self.mx_2, self.my_2, self.circle_radius_2):
                one_colliding = True
                return one_colliding
        elif self.shape_1 == "Circle" and self.shape_2 == "Polygon":
            #Shape 1: Circle
            #Shape 2: Polygon
            #print(24)
            if polygon_circle(self.get_polygon(self.shape_vtx_2), self.mx_1, self.my_1, self.circle_radius_1):
                one_colliding = True
                return one_colliding
            



        if self.shape_1 == "Polygon" and self.shape_2 == "Point":
            #Shape 1: Polygon
            #Shape 2: point
            #print(25)
            if polygon_point(self.get_polygon(self.shape_vtx_1), self.mx_2, self.my_2):
                one_colliding = True
                return one_colliding

        
        elif self.shape_1 == "Point" and self.shape_2 == "Polygon":
            #Shape 1: Point
            #Shape 2: Polygon
            #print(26)
            if polygon_point(self.get_polygon(self.shape_vtx_2), self.mx_1, self.my_1):
                one_colliding = True
                return one_colliding

        
        if self.shape_1 == "Polygon" and self.shape_2 == "Polygon":
            #Shape 1: Polygon
            #Shape 2: Rectangle
            #print(27)
            if polygon_polygon(self.get_polygon(self.shape_vtx_1), self.get_polygon(self.shape_vtx_2)):
                one_colliding = True
                return one_colliding
            

        

        return one_colliding
            


    def make_shape(self, x, y, vertex_ls, color, shape_tag, shape, filler):
        self.canvas.delete(shape_tag)
        
        
        vtx_len = len(vertex_ls)
        
        initial_angle = 0



        shades = ["slate blue", "magenta", "yellow", "green", "blue", "black", "orange", "purple", "pink"]

        polygon_1 = []
        if vtx_len > self.shape_vertices[shape]:
            vertex_ls = vertex_ls[:self.shape_vertices[shape]]
        else:
            padding = self.shape_vertices[shape] - vtx_len
            for i in range(padding):
                vertex_ls.append(Vertex(0, 0))

        if not self.hitting:
            filler = ""

        if shape == "Circle":
            
            vertex_ls[0].set_coords(x, y)
            vx, vy = vertex_ls[0].get_X(), vertex_ls[0].get_Y()
            vx1 = 0
            vy1 = 0
            vx2 = 0
            vy2 = 0

            if shape_tag == self.shape_tag_1 :
                vx1 = vx - self.circle_radius_1
                vy1 = vy - self.circle_radius_1
                vx2 = vx1 + self.circle_radius_1 * 2
                vy2 = vy1 + self.circle_radius_1 * 2
                
            elif shape_tag == self.shape_tag_2 :
                vx1 = vx - self.circle_radius_2
                vy1 = vy - self.circle_radius_2
                vx2 = vx1 + self.circle_radius_2 * 2
                vy2 = vy1 + self.circle_radius_2 * 2
                
                                        
            self.canvas.create_oval(
                                        vx1, vy1, 
                                        vx2, vy2, 
                                        fill=filler,
                                        outline=color,
                                        tags=(shape_tag)
                                        )
        elif shape == "Point":
            
            vertex_ls[0].set_coords(x, y)
            vx, vy = vertex_ls[0].get_X(), vertex_ls[0].get_Y()
            vx1 = 0
            vy1 = 0
            vx2 = 0
            vy2 = 0

            if shape_tag == self.shape_tag_1 :
                vx1 = vx - self.point_buffer_1
                vy1 = vy - self.point_buffer_1
                vx2 = vx1 + self.point_buffer_1 * 2
                vy2 = vy1 + self.point_buffer_1 * 2
                
            elif shape_tag == self.shape_tag_2 :
                vx1 = vx - self.point_buffer_2
                vy1 = vy - self.point_buffer_2
                vx2 = vx1 + self.point_buffer_2 * 2
                vy2 = vy1 + self.point_buffer_2 * 2
                
            
                                        
            self.canvas.create_oval(
                                        vx1, vy1, 
                                        vx2, vy2,  
                                        fill=filler,
                                        outline=color,
                                        tags=(shape_tag)
                                        ) 


        elif shape == "Line":

            initial_angle = 0
            if shape_tag == self.shape_tag_1 :
                initial_angle = self.line_angle_1

            elif shape_tag == self.shape_tag_2 :
                initial_angle = self.line_angle_2

            angle_inc = to_radians(360/self.shape_vertices[shape]) 

            for i in range(len(vertex_ls)):  
                vtx = vertex_ls[i]
                vx, vy = vtx.get_X(), vtx.get_Y()

                if shape_tag == self.shape_tag_1:
                    vx = x + self.line_dist_1  * math.cos(initial_angle)
                    vy = y + self.line_dist_1 * math.sin(initial_angle)
                elif shape_tag == self.shape_tag_2 :
                    vx = x + self.line_dist_2  * math.cos(initial_angle)
                    vy = y + self.line_dist_2  * math.sin(initial_angle)

                vtx.set_coords(vx, vy)
                initial_angle += angle_inc

            vx1, vy1 = vertex_ls[0].get_X(), vertex_ls[0].get_Y()
            vx2, vy2 = vertex_ls[1].get_X(), vertex_ls[1].get_Y()
            width = 0
            if filler != "":
                width = 5

            self.canvas.create_line(
                                        vx1, vy1,
                                        vx2, vy2,
                                        fill=color,
                                        width=width,
                                        tags=(shape_tag)
                                        )

                
            
        elif shape == "Rectangle":
            

            initial_angle = to_radians(225)
            angle_inc = to_radians(360/self.shape_vertices[shape]) 
           

            
            
            

            for i in range(0, len(vertex_ls)): 
                vtx = vertex_ls[i]
               
                vx, vy = vtx.get_X(), vtx.get_Y()
                if shape_tag == self.shape_tag_1 :
                    vx = x + self.rect_dist_1 * math.cos(initial_angle)
                    vy = y + self.rect_dist_1 * math.sin(initial_angle)
                    
                elif shape_tag == self.shape_tag_2 :
                    vx = x + self.rect_dist_2  * math.cos(initial_angle)
                    vy = y + self.rect_dist_2  * math.sin(initial_angle)
                vtx.set_coords(vx, vy)
                '''
                self.canvas.create_line(
                    x, y, vx, vy, 
                    fill=shades[i],
                    tags=(shape_tag)
                )
                '''
                initial_angle += angle_inc

            vx1, vy1 = vertex_ls[0].get_X(), vertex_ls[0].get_Y()
            vx2, vy2 = vertex_ls[1].get_X(), vertex_ls[1].get_Y()
            vx3, vy3 = vertex_ls[2].get_X(), vertex_ls[2].get_Y()
            vx4, vy4 = vertex_ls[3].get_X(), vertex_ls[3].get_Y()

            self.canvas.create_rectangle(
                                        vx1, vy1,
                                        vx3, vy3,
                                        fill=filler,
                                        outline=color,
                                        tags=(shape_tag)
                                        )
            

        elif shape == "Polygon":
            vx1, vy1 = vertex_ls[0].get_X(), vertex_ls[0].get_Y()

            initial_angle = to_radians(60)
            angle_inc = to_radians(360/self.shape_vertices[shape]) 
            
            for i in range(len(vertex_ls)): 
               
                vtx = vertex_ls[i]
                vx, vy = vtx.get_X(), vtx.get_Y()
                if shape_tag == self.shape_tag_1 :
                    vx = x + self.rect_dist_1  * math.cos(initial_angle)
                    vy = y + self.rect_dist_1 * math.sin(initial_angle)
                elif shape_tag == self.shape_tag_2 :
                    vx = x + self.rect_dist_2  * math.cos(initial_angle)
                    vy = y + self.rect_dist_2  * math.sin(initial_angle)
                vtx.set_coords(vx, vy)
                polygon_1.append(vx)
                polygon_1.append(vy)

                '''
                self.canvas.create_line(
                    x, y, vx, vy, 
                    fill=shades[i],
                    tags=(shape_tag)
                )
                '''

                initial_angle += angle_inc

            self.canvas.create_polygon(
                                    polygon_1,
                                    outline=color,
                                    fill=filler,
                                    tags=(shape_tag)
                                    )


        
        #print(")
        self.hitting = self.is_colliding()
        #print(f"{self.shape_1} {self.shape_2} {self.hitting}")
        
        

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        IKs = ShapeCollisions(self, 500, 500)
        IKs.grid()

    


if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    #app.resizable()
    app.mainloop()
        
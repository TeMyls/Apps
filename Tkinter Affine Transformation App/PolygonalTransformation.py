import tkinter as tk
from tkinter import ttk, filedialog, messagebox 
from MatrixMath import *


class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Polygon Transform App") 
        self.t2d_poly = TransformPolygon2D(self, 500, 400)
        self.t2d_poly.grid(sticky="")
        #self.main_canvas = MainCanvas(self)
        #self.main_canvas.grid()
        
class TransformPolygon2D(ttk.Frame):
    def __init__(self, parent, c_width, c_height,  *args, **kwargs):
        super().__init__(parent)

        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 

        self.poly_points = []
        

        
        
        self.anchor_size = 5
        
        self.anchor_point = [c_width//2, c_height//2]
        self.anchor_label = ttk.Label(self, text = "Anchor X:{} Y:{}".format(self.anchor_point[0], self.anchor_point[1]))
        self.anchor_x_var = tk.IntVar()
        self.anchor_y_var = tk.IntVar()
        self.anchor_x_slider = tk.Scale(
            self,
            variable=self.anchor_x_var,
            from_ = 0,
            to = c_width,
            orient = "horizontal",
            length=c_width,
            command = self.reanchor
            
        )
        
        
        
        
        
        self.anchor_y_slider = tk.Scale(
            self,
            variable=self.anchor_y_var,
            from_ = 0,
            to = c_height,
            orient = "vertical",
            length=c_height,
            command = self.reanchor
        )
        
        self.anchor_x_slider.set(c_width//2)
        self.anchor_y_slider.set(c_height//2)
        

        self.canvas.create_oval(
                            self.anchor_point[0] - self.anchor_size, 
                            self.anchor_point[1] - self.anchor_size,
                            self.anchor_point[0] + self.anchor_size, 
                            self.anchor_point[1] + self.anchor_size,
                            tags=("anchor")
                            )
        
        
        
        
        #ROTATION
        self.angle = 180
        self.rotate_var = tk.IntVar()
        self.rotate_label = ttk.Label(self, text = "Rotation Angle:{}".format(self.angle))
        self.rotate_slider = tk.Scale(
            self,
            variable=self.rotate_var,
            from_ = 0,
            to = 360,
            orient = "horizontal",
            length=c_width,
            command = self.apply_rotation,
            troughcolor='#fc671c'
        )
        
        self.rotate_slider.set(self.angle)
        
        self.rotate_widgets = [self.rotate_label, self.rotate_slider]
        
        #SHEARING
        self.shear_var_x = tk.DoubleVar()
        self.shear_var_y = tk.DoubleVar()
        
        self.shear_label = ttk.Label(self, text = "Shear X:{} Y:{}".format(c_width//2, c_height//2))
        self.shear_x_slider = tk.Scale(
            self,
            variable=self.shear_var_x,
            from_ = -10,
            to = 10,
            orient = "horizontal",
            length=c_width,
            command = self.apply_shear,
            resolution= 0.1,
            troughcolor='#2bd8ff'
            
        )
        
        
        
        
        self.shear_y_slider = tk.Scale(
            self,
            variable=self.shear_var_y,
            from_ = -10,
            to = 10,
            orient = "vertical",
            length= c_height,
            command = self.apply_shear,
            resolution= 0.1,
            troughcolor='#2bd8ff'
        )
        
        self.shear_x_slider.set(0)
        self.shear_y_slider.set(0)
        self.shear_x = 0
        self.shear_y = 0
        self.shear_og_x = 0
        self.shear_og_y = 0
        
        self.shear_widgets = [self.shear_label, self.shear_x_slider, self.shear_y_slider]
        
        #TRANSLATION
        self.translate_var_x = tk.IntVar()
        self.translate_var_y = tk.IntVar()
        self.translate_label = ttk.Label(self, text = "Translate X:{} Y:{}".format(1, 1))
        self.translate_x_slider = tk.Scale(
            self,
            variable=self.translate_var_x,
            from_ = -c_width//2,
            to = c_width//2,
            orient = "horizontal",
            length=c_width,
            command = self.apply_translation,
            troughcolor='#ffff19'
            
        )
        
        
        
        self.translate_y_slider = tk.Scale(
            self,
            variable=self.translate_var_y,
            from_ = -c_height//2,
            to = c_height//2,
            orient = "vertical",
            length= c_height,
            command = self.apply_translation,
            troughcolor='#ffff19'
        )
        
        self.translate_x_slider.set(1)
        self.translate_y_slider.set(1)
        
        self.translate_x = 1
        self.translate_y = 1
        self.translate_og_x = 1
        self.translate_og_y = 1
        
        self.translate_widgets = [self.translate_label, self.translate_x_slider, self.translate_y_slider]
        
        #REFLECTION
        self.reflect_var_x = tk.IntVar()
        self.reflect_var_y = tk.IntVar()
        self.reflect_label = ttk.Label(self, text = "Reflect X:{} Y:{}".format(1, 1))
        self.reflect_x_slider = tk.Scale(
            self,
            variable=self.reflect_var_x,
            from_ = -1,
            to = 1,
            orient = "horizontal",
            length=c_width,
            command = self.apply_reflection,
            resolution= 0.15,
            troughcolor='#bddbdb'
        )
        
        
        
        self.reflect_y_slider = tk.Scale(
            self,
            variable=self.reflect_var_y,
            from_ = -1,
            to = 1,
            orient = "vertical",
            length= c_height,
            command = self.apply_reflection,
            resolution= 0.15,
            troughcolor='#bddbdb'
        )
        
        self.reflect_x_slider.set(1)
        self.reflect_y_slider.set(1)
        self.reflect_x = 1
        self.reflect_y = 1
        self.reflect_og_x = 1
        self.reflect_og_y = 1
        
        self.reflect_widgets = [self.reflect_label, self.reflect_x_slider, self.reflect_y_slider]
        
        #SCALING
        self.scale_var_x = tk.DoubleVar()
        self.scale_var_y = tk.DoubleVar()
        self.scale_label = ttk.Label(self, text = "Scale X:{} Y:{}".format(c_width//2, c_height//2)) 
        self.scale_x_slider = tk.Scale(
            self,
            variable=self.scale_var_x,
            from_ = 0.1,
            to = 5,
            orient = "horizontal",
            length=c_width,
            command = self.apply_scale,
            resolution= 0.1,
            troughcolor='#2eb314'
        )
        
        
        
        self.scale_y_slider = tk.Scale(
            self,
            variable=self.scale_var_y,
            from_ = 0.1,
            to = 5,
            orient = "vertical",
            length= c_height,
            command = self.apply_scale,
            resolution= 0.1,
            troughcolor='#2eb314'
            
        )
        
        
        self.scale_x_slider.set(1)
        self.scale_y_slider.set(1)
        self.scale_x = 1
        self.scale_y = 1
        self.scale_og_x = 1
        self.scale_og_y = 1
        
        self.scale_widgets = [self.scale_label, self.scale_x_slider, self.scale_y_slider]
        
        
        
        self.transform_selection_label = ttk.Label(self, text = "Transform Type")
        self.transform_selection_svar = tk.StringVar()
        
        
        self.all_selection_radiobutton = ttk.Radiobutton(self, text="All", 
                                                           variable=self.transform_selection_svar,
                                                           value = "All",
                                                           command=self.widget_states)
        
        self.rotation_selection_radiobutton = ttk.Radiobutton(self, text="Rotation", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Rotation",
                                                           command=self.widget_states)
        self.shear_selection_radiobutton = ttk.Radiobutton(self, text="Shear", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Shear",
                                                           command=self.widget_states)
        self.translate_selection_radiobutton = ttk.Radiobutton(self, text="Translate", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Translate",
                                                           command=self.widget_states)
        self.scale_selection_radiobutton = ttk.Radiobutton(self, text="Scale", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Scale",
                                                           command=self.widget_states)
        
        self.reflect_selection_radiobutton = ttk.Radiobutton(self, text="Reflection", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Reflection",
                                                           command=self.widget_states)
        self.transform_selection_svar.set("Rotation")
        
        self.all_reset = ttk.Button()
        self.rotation_reset = ttk.Button()
       
        
        
        arrangement = [
            
            [self.anchor_y_slider  , self.canvas                   , self.shear_y_slider, self.translate_y_slider, self.scale_y_slider, self.reflect_y_slider, None],
            [self.anchor_label     , self.anchor_x_slider          , self.all_selection_radiobutton      , None, None, None, None],
            [self.rotate_label     , self.rotate_slider            , self.rotation_selection_radiobutton , None, None, None, None],
            [self.shear_label      , self.shear_x_slider           , self.shear_selection_radiobutton    , None, None, None, None],
            [self.translate_label  , self.translate_x_slider       , self.translate_selection_radiobutton, None, None, None, None],
            [self.scale_label      , self.scale_x_slider           , self.scale_selection_radiobutton    , None, None, None, None],
            [self.reflect_label    , self.reflect_x_slider         , self.reflect_selection_radiobutton  , None, None, None, None]
            
        ]
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):

                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                    #if isinstance(arrangement[ind_y][ind_x], tk.Label):
                    arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "W")

        self.canvas.bind("<ButtonPress-3>", self.clear_points)
        self.canvas.bind("<ButtonPress-1>", self.place_point)  
        self.canvas.bind("<MouseWheel>", None)  
        
        self.widget_states()
    
    
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
    
    def widget_states(self):
        transformation_type = self.transform_selection_svar.get()
        #if transformation_type == "ALL":
            #for widget in self.winfo_children():
        if transformation_type == "All":
            
            for widget in self.rotate_widgets:
                self.show_widget(widget)
            for widget in self.shear_widgets:
                self.show_widget(widget)
            for widget in self.translate_widgets:
                self.show_widget(widget)
            for widget in self.scale_widgets:
                self.show_widget(widget)
            for widget in self.reflect_widgets:
                self.show_widget(widget)
                
        elif transformation_type == "Rotation":
            
            for widget in self.rotate_widgets:
                self.show_widget(widget)
            for widget in self.shear_widgets:
                self.hide_widget(widget)
            for widget in self.translate_widgets:
                self.hide_widget(widget)
            for widget in self.scale_widgets:
                self.hide_widget(widget)
            for widget in self.reflect_widgets:
                self.hide_widget(widget)
                
        elif transformation_type == "Shear":
            
            for widget in self.rotate_widgets:
                self.hide_widget(widget)
            for widget in self.shear_widgets:
                self.show_widget(widget)
            for widget in self.translate_widgets:
                self.hide_widget(widget)
            for widget in self.scale_widgets:
                self.hide_widget(widget)
            for widget in self.reflect_widgets:
                self.hide_widget(widget)
                
        elif transformation_type == "Translate":
            
            for widget in self.rotate_widgets:
                self.hide_widget(widget)
            for widget in self.shear_widgets:
                self.hide_widget(widget)
            for widget in self.translate_widgets:
                self.show_widget(widget)
            for widget in self.scale_widgets:
                self.hide_widget(widget)
            for widget in self.reflect_widgets:
                self.hide_widget(widget)
                
        elif transformation_type == "Scale":
            
            for widget in self.rotate_widgets:
                self.hide_widget(widget)
            for widget in self.shear_widgets:
                self.hide_widget(widget)
            for widget in self.translate_widgets:
                self.hide_widget(widget)
            for widget in self.scale_widgets:
                self.show_widget(widget)
            for widget in self.reflect_widgets:
                self.hide_widget(widget)
                
        elif transformation_type == "Reflection":
            
            for widget in self.rotate_widgets:
                self.hide_widget(widget)
            for widget in self.shear_widgets:
                self.hide_widget(widget)
            for widget in self.translate_widgets:
                self.hide_widget(widget)
            for widget in self.scale_widgets:
                self.hide_widget(widget)
            for widget in self.reflect_widgets:
                self.show_widget(widget)
    
    def reanchor(self, *args):
        x = self.anchor_x_slider.get()
        y = self.anchor_y_slider.get()
        self.anchor_point[0] = x
        self.anchor_point[1] = y
        self.anchor_label.config(text = "Anchor X:{} Y:{}".format(round(self.anchor_point[0]), round(self.anchor_point[1])))
        self.canvas.delete("anchor")
        self.canvas.create_oval(
            self.anchor_point[0] - self.anchor_size, 
            self.anchor_point[1] - self.anchor_size,
            self.anchor_point[0] + self.anchor_size, 
            self.anchor_point[1] + self.anchor_size,
            tags=("anchor")
            )
           
    
    def degrees_to_radians(self, deg):
        return (deg * math.pi)/180
    

    def apply_rotation(self, *args):
        #canvas_width = self.canvas.winfo_width()
        #canvas_height = self.canvas.winfo_height()
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        
        
        if len(self.poly_points) > 2:
            prev_angle = self.angle
            self.angle = self.rotate_slider.get()
            #self.rotate_label.config(text = "Rotation Angle:{}".format(round(self.angle)))
            
            self.canvas.delete("shapes")
            
            current_anchor = translation_matrix2D(-cx, -cy)
            anchor_current = translation_matrix2D(cx, cy)
            rotation = rotation_matrix2D(self.degrees_to_radians(prev_angle - self.angle))#self.rotate_slider.get()))
            
            
            for i in range(0, len(self.poly_points), 2):

                xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
                xny_coords = matrix_multiply(current_anchor, xny_coords)
                xny_coords = matrix_multiply(rotation, xny_coords)
                xny_coords = matrix_multiply(anchor_current, xny_coords)
                #print(d)
                x, y = get_2D_vertices(xny_coords)
                if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                    self.poly_points[i] = x
                    self.poly_points[i + 1] = y
              
            '''     
            xny_list = "["
            for i in self.poly_points:
                xny_list = xny_list + f"{round(i)}"+ ", "
               
            xny_list = xny_list + "]"
            
            print(xny_list)
            ''' 
            
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            self.rotate_label.config(text = "Rotation Angle:{}".format(round(self.angle)))
            
    def apply_scale(self, *args):
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        
        
        
        
        
        if len(self.poly_points) > 2:
            prev_x_scale = self.scale_x
            prev_y_scale = self.scale_y
            
            self.scale_x = self.scale_x_slider.get()
            self.scale_y = self.scale_y_slider.get()
            
            
            #ternary if = 1 if self.scale_x - prev_x_scale < 0 else 1
            
            #overall scale change
            old_x_scale = (prev_x_scale / self.scale_og_x) * self.scale_og_x
            old_y_scale = (prev_y_scale / self.scale_og_y) * self.scale_og_y
            
            cur_x_scale = (self.scale_x / self.scale_og_x) * self.scale_og_x
            cur_y_scale = (self.scale_y / self.scale_og_y) * self.scale_og_y
            
            #scale relative percentage change
            inc_x_percent = (cur_x_scale - old_x_scale)/prev_x_scale + 1
            inc_y_percent = (cur_y_scale - old_y_scale)/prev_y_scale + 1
            

            
            #print('inc {}'.format(inc_x_percent))
            
            #self.scale_label.config(text = "Scale X:{} Y:{}".format(self.scale_x, self.scale_y))
            
            self.canvas.delete("shapes")
            current_anchor = translation_matrix2D(-cx, -cy)
            anchor_current = translation_matrix2D(cx, cy)
            

            
            
            scale = scale_matrix2D(inc_x_percent, inc_y_percent)  #rotation_matrix2D(self.degrees_to_radians(prev_angle - self.rotate_slider.get()))
        
            for i in range(0, len(self.poly_points), 2):

                xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
                xny_coords = matrix_multiply(current_anchor, xny_coords)
                xny_coords = matrix_multiply(scale, xny_coords)
                xny_coords = matrix_multiply(anchor_current, xny_coords)
                #print(d)
                x, y = get_2D_vertices(xny_coords)
                if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                    self.poly_points[i] = x
                    self.poly_points[i + 1] = y
            

                
              
            '''
            xny_list = "["
            for i in self.poly_points:
                xny_list = xny_list + f"{round(i)}"+ ", "
               
            xny_list = xny_list + "]"
            
            print(xny_list)
            '''
            
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            self.scale_label.config(text = "Scale X:{} Y:{}".format(self.scale_x, self.scale_y))
    
    def apply_shear(self, *args):
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        
        
        
        
        
        if len(self.poly_points) > 2:
            prev_x_shear = self.shear_x
            prev_y_shear = self.shear_y
            
            self.shear_x = self.shear_x_slider.get()
            self.shear_y = self.shear_y_slider.get()
            
            
            #ternary if = 1 if self.scale_x - prev_x_scale < 0 else 1
            
            inc_x = self.shear_x - prev_x_shear
            inc_y = self.shear_y - prev_y_shear

            #print('inc {} points {}'.format(inc_x, self.poly_points))
            
            #self.shear_label.config(text = "Shear X:{} Y:{}".format(self.shear_x, self.shear_y))
            
            self.canvas.delete("shapes")
            current_anchor = translation_matrix2D(-cx, -cy)
            anchor_current = translation_matrix2D(cx, cy)
            


            shear = shear_matrix2D(inc_x, inc_y)
            
            for i in range(0, len(self.poly_points), 2):

                xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
                xny_coords = matrix_multiply(current_anchor, xny_coords)
                xny_coords = matrix_multiply(shear, xny_coords)
                xny_coords = matrix_multiply(anchor_current, xny_coords)
                #print(d)
                x, y = get_2D_vertices(xny_coords)
                if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                    self.poly_points[i] = x
                    self.poly_points[i + 1] = y
            

                
              
            '''
            xny_list = "["
            for i in self.poly_points:
                xny_list = xny_list + f"{round(i)}"+ ", "
               
            xny_list = xny_list + "]"
            
            print(xny_list)
            '''
            
            
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            self.shear_label.config(text = "Shear X:{} Y:{}".format(self.shear_x, self.shear_y))
    
    def apply_translation(self, *args):
        
        
        
        
        if len(self.poly_points) > 2:
            cx = self.anchor_point[0]
            cy = self.anchor_point[1]
            
            prev_x_translate = self.translate_x
            prev_y_translate = self.translate_y
            
            self.translate_x = self.translate_x_slider.get()
            self.translate_y = self.translate_y_slider.get()

            
            
            inc_x = self.translate_x - prev_x_translate
            inc_y = self.translate_y - prev_y_translate
            
            
        

            #print('inc {} points {}'.format(inc_x, self.poly_points))
            #self.translate_label.config(text = "Translate X:{} Y:{}".format(self.translate_x, self.translate_y))
            
            
            self.canvas.delete("shapes")
            current_anchor = translation_matrix2D(-cx, -cy)
            anchor_current = translation_matrix2D(cx, cy)
            
            

            #shear = shear_matrix2D(inc_x, inc_y)
            #reflect = reflect_matrix2D(inc_x, inc_y)
            translate = translation_matrix2D(inc_x, inc_y)
            
            for i in range(0, len(self.poly_points), 2):

                xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
                xny_coords = matrix_multiply(current_anchor, xny_coords)
                xny_coords = matrix_multiply(translate, xny_coords)
                xny_coords = matrix_multiply(anchor_current, xny_coords)
                #print(d)
                x, y = get_2D_vertices(xny_coords)
                if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                    self.poly_points[i] = x
                    self.poly_points[i + 1] = y
            

                
              
            '''
            xny_list = "["
            for i in self.poly_points:
                xny_list = xny_list + f"{round(i)}"+ ", "
               
            xny_list = xny_list + "]"
            
            print(xny_list)
            '''
            
            
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            self.translate_label.config(text = "Translate X:{} Y:{}".format(self.translate_x, self.translate_y))
    
    def apply_reflection(self, *args):
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        
       
        
        
        
        if len(self.poly_points) > 2:
            prev_x_reflect = self.reflect_x
            prev_y_reflect = self.reflect_y
            
            self.reflect_x = self.reflect_x_slider.get()
            self.reflect_y = self.reflect_y_slider.get()
            
            sign_x = -1 if prev_x_reflect <= 0 else 1
            sign_y = -1 if prev_y_reflect <= 0 else 1
            
            
            #overall scale change
            old_x_reflect = (prev_x_reflect / self.reflect_og_x) * self.reflect_og_x
            old_y_reflect = (prev_y_reflect / self.reflect_og_y) * self.reflect_og_y
            
            cur_x_reflect = (self.reflect_x / self.reflect_og_x) * self.reflect_og_x
            cur_y_reflect = (self.reflect_y / self.reflect_og_y) * self.reflect_og_y
            
            
            #scale relative percentage change
            inc_x_percent =  (cur_x_reflect - old_x_reflect)/prev_x_reflect + 1
            inc_y_percent =  (cur_y_reflect - old_y_reflect)/prev_y_reflect + 1

            #print('inc {} points {}'.format(inc_x, self.poly_points))
            
            #self.reflect_label.config(text = "Reflect X:{} Y:{}".format(self.reflect_x, self.reflect_y))
            #if prev_x_reflect != 0 and prev_y_reflect != 0 
            
            self.canvas.delete("shapes")
            current_anchor = translation_matrix2D(-cx, -cy)
            anchor_current = translation_matrix2D(cx, cy)
            
            new_poly = []

            #shear = shear_matrix2D(inc_x, inc_y)
            reflect = reflect_matrix2D(inc_x_percent, inc_y_percent)
            
            for i in range(0, len(self.poly_points), 2):

                xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
                xny_coords = matrix_multiply(current_anchor, xny_coords)
                xny_coords = matrix_multiply(reflect, xny_coords)
                xny_coords = matrix_multiply(anchor_current, xny_coords)
                #print(d)
                x, y = get_2D_vertices(xny_coords)
                if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                    self.poly_points[i] = x
                    self.poly_points[i + 1] = y
            

                
              
            '''
            xny_list = "["
            for i in self.poly_points:
                xny_list = xny_list + f"{round(i)}"+ ", "
               
            xny_list = xny_list + "]"
            
            print(xny_list)
            '''
            
            
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            self.reflect_label.config(text = "Reflect X:{} Y:{}".format(self.reflect_x, self.reflect_y))
    
    

    def place_point(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.poly_points.append(x)
        self.poly_points.append(y)
        
        if len(self.poly_points) > 2:
            self.canvas.delete("shapes")
            print(self.poly_points)
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
                

            
    def clear_points(self, event):
        self.poly_points.clear()
        self.canvas.delete("shapes")
    
    
    
        
        

        
if __name__ == "__main__":
    app = App()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()
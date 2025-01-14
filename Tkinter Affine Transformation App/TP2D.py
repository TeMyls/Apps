import tkinter as tk
from tkinter import ttk
from MatrixMath import *
import math

#Testing Individually
'''
class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Polygon Transform App") 
        self.undo_button_2d = tk.Button(self, text = "undo")
        self.redo_button_2d = tk.Button(self, text = "redo")
        self.undo_button_2d.grid(row=0,column=0)
        self.redo_button_2d.grid(row=0,column=1)
        
        
        self.t2d_poly = TransformPolygon2D(self, 500, 400)
        self.t2d_poly.grid(row=1,column=2)
        
        self.bind("<Control-z>", self.t2d_poly.undo)
        self.bind("<Control-y>", self.t2d_poly.redo)
        
        
        self.undo_button_2d.config(command=self.t2d_poly.undo)
        self.redo_button_2d.config(command=self.t2d_poly.redo)
'''

class TransformPolygon2D(ttk.Frame):
    def __init__(self, parent, c_width, c_height,  *args, **kwargs):
        super().__init__(parent)
        
        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        
        self.undo_stack = []
        self.redo_queue = []
        
        
        self.poly_points = []
        

        
        #ANCHOR/PIVOT
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
        
        #RESET BUTTONS
        self.all_reset_btn = ttk.Button(self,
            text = "Reset All",
            command = self.clear_all
        )
        self.rotation_reset_btn = ttk.Button(self,
            text = "Reset Rotation",
            command = self.clear_rotation
        )
        self.shear_reset_btn = ttk.Button(self,
            text = "Reset Shear",
            command = self.clear_shearing
        )
        self.translate_reset_btn = ttk.Button(self,
            text = "Reset Translation",
            command = self.clear_translation
        )
        self.scale_reset_btn = ttk.Button(self,
            text = "Reset Scaling",
            command = self.clear_scaling
        )
        self.reflect_reset_btn = ttk.Button(self,
            text = "Reset Reflection",
            command = self.clear_reflection
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
        
        self.angle_og = 180
        self.rotate_slider.set(self.angle)
        

        self.rotate_slider.bind("<ButtonPress>", self.on_rotation)
        
        
        self.rotate_widgets = [self.rotate_label, self.rotate_slider, self.rotation_reset_btn]
        
        
        
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
            command = self.apply_shearing,
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
            command = self.apply_shearing,
            resolution= 0.1,
            troughcolor='#2bd8ff'
        )
        
        self.shear_x_slider.set(0)
        self.shear_y_slider.set(0)
        self.shear_x = 0
        self.shear_y = 0
        self.shear_og_x = 0
        self.shear_og_y = 0
        
        self.shear_x_slider.bind("<ButtonPress>", self.on_shearing)
        self.shear_y_slider.bind("<ButtonPress>", self.on_shearing)
        
        self.shear_widgets = [self.shear_label, self.shear_x_slider, self.shear_y_slider, self.shear_reset_btn]
        
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
        
        self.translate_x_slider.bind("<ButtonPress>", self.on_translation)
        self.translate_y_slider.bind("<ButtonPress>", self.on_translation)
        
        self.translate_widgets = [self.translate_label, self.translate_x_slider, self.translate_y_slider, self.translate_reset_btn]
        
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
        
        self.reflect_x_slider.bind("<ButtonPress>", self.on_reflection)
        self.reflect_y_slider.bind("<ButtonPress>", self.on_reflection)
        
        self.reflect_widgets = [self.reflect_label, self.reflect_x_slider, self.reflect_y_slider, self.reflect_reset_btn]
        
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
            command = self.apply_scaling,
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
            command = self.apply_scaling,
            resolution= 0.1,
            troughcolor='#2eb314'
            
        )
        
        
        self.scale_x_slider.set(1)
        self.scale_y_slider.set(1)
        self.scale_x = 1
        self.scale_y = 1
        self.scale_og_x = 1
        self.scale_og_y = 1
        
        self.scale_x_slider.bind("<ButtonPress>", self.on_reflection)
        self.scale_y_slider.bind("<ButtonPress>", self.on_reflection)
        
        self.scale_widgets = [self.scale_label, self.scale_x_slider, self.scale_y_slider, self.scale_reset_btn]
        
        
        
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
        
        
        
        
    
        
        
        arrangement = [
            
            [self.anchor_y_slider  , self.canvas                   , self.shear_y_slider                  , self.translate_y_slider , self.scale_y_slider , self.reflect_y_slider, None],
            [self.anchor_label     , self.anchor_x_slider          , self.all_selection_radiobutton       , self.all_reset_btn      , None                , None                 , None],
            [self.rotate_label     , self.rotate_slider            , self.rotation_selection_radiobutton  , self.rotation_reset_btn , None                , None                 , None],
            [self.shear_label      , self.shear_x_slider           , self.shear_selection_radiobutton     , self.shear_reset_btn    , None                , None                 , None],
            [self.translate_label  , self.translate_x_slider       , self.translate_selection_radiobutton , self.translate_reset_btn, None                , None                 , None],
            [self.scale_label      , self.scale_x_slider           , self.scale_selection_radiobutton     , self.scale_reset_btn    , None                , None                 , None],
            [self.reflect_label    , self.reflect_x_slider         , self.reflect_selection_radiobutton   , self.reflect_reset_btn  , None                , None                 , None]
            
        ]
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):

                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                    if isinstance(arrangement[ind_y][ind_x], tk.Button):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NEWS")
                    else:
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "W")

        #1 is left mouse button, 3 is right mouse button
        self.canvas.bind("<ButtonPress-3>", self.clear_points)
        self.canvas.bind("<ButtonPress-1>", self.place_point)  
        self.canvas.bind("<MouseWheel>", None)  
        
        self.widget_states()

    def undo(self, *args):
        print(self.undo_stack)
        if len(self.undo_stack) > 0:
            
            self.canvas.delete("shapes")
            
            
            point_poly = self.undo_stack.pop()
            self.redo_queue.insert(0, point_poly)
            print(point_poly)
            print("undid")
            
            self.canvas.create_polygon(point_poly, tags=("shapes"))
            self.poly_points = point_poly
        else:
            print("nothing to undo")
            
    def redo(self, *args):
        if len(self.redo_queue) > 0:
            self.canvas.delete("shapes")
            point_poly = self.redo_queue.pop(-1)
            
            self.canvas.create_polygon(point_poly, tags=("shapes"))
            self.poly_points = point_poly
        else:
            print("nothing to redo")
    
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
                 
    def on_rotation(self, *args):        
        if len(self.poly_points) > 2:
            self.undo_stack.append(self.poly_points.copy())
  
    def on_shearing(self, *args):
        if len(self.poly_points) > 2:
            self.undo_stack.append(self.poly_points.copy())
        
    def on_translation(self, *args):
        if len(self.poly_points) > 2:
            self.undo_stack.append(self.poly_points.copy())
        
    def on_scaling(self, *args):
        if len(self.poly_points) > 2:
            self.undo_stack.append(self.poly_points.copy())
        
    def on_reflection(self, *args):
        if len(self.poly_points) > 2:
            self.undo_stack.append(self.poly_points.copy())
    
    def clear_all(self, *args):
        self.clear_rotation()
        self.clear_shearing()
        self.clear_translation()
        self.clear_scaling()
        self.clear_reflection()
        
    def clear_rotation(self, *args):
        self.rotate_slider.set(self.angle_og)
        self.apply_rotation()
        
    def clear_shearing(self, *args):
        self.shear_x_slider.set(self.shear_og_x)
        self.shear_y_slider.set(self.shear_og_y)
        self.apply_shearing()
    
    def clear_translation(self, *args):
        self.translate_x_slider.set(self.translate_og_x)
        self.translate_y_slider.set(self.translate_og_y)
        self.apply_translation()
    
    def clear_scaling(self, *args):
        self.scale_x_slider.set(self.scale_og_x)
        self.scale_y_slider.set(self.scale_og_y)
        self.apply_scaling()
    
    def clear_reflection(self, *args):
        self.reflect_x_slider.set(self.reflect_og_x)
        self.reflect_y_slider.set(self.reflect_og_y)
        self.apply_reflection()
    
    def degrees_to_radians(self, deg):
        return (deg * math.pi)/180
    
    def apply_rotation(self, *args):
        if len(self.poly_points) > 2:
            prev_angle = self.angle
            
            self.angle = self.rotate_slider.get()

            rotation = rotation_matrix2D(self.degrees_to_radians(prev_angle - self.angle))
            self.apply_transformation(rotation, self.rotate_label, "Rotation", self.angle)
    
    def apply_scaling(self, *args):
        
        if len(self.poly_points) > 2:
            prev_x_scale = self.scale_x
            prev_y_scale = self.scale_y
            
            self.scale_x = self.scale_x_slider.get()
            self.scale_y = self.scale_y_slider.get()
            
            #overall scale change
            old_x_scale = (prev_x_scale / self.scale_og_x) * self.scale_og_x
            old_y_scale = (prev_y_scale / self.scale_og_y) * self.scale_og_y
            
            cur_x_scale = (self.scale_x / self.scale_og_x) * self.scale_og_x
            cur_y_scale = (self.scale_y / self.scale_og_y) * self.scale_og_y
            
            #scale relative percentage change
            inc_x_percent = (cur_x_scale - old_x_scale)/prev_x_scale + 1
            inc_y_percent = (cur_y_scale - old_y_scale)/prev_y_scale + 1
            
            scale = scale_matrix2D(inc_x_percent, inc_y_percent)  
            self.apply_transformation(scale, self.scale_label, "Scale", self.scale_x, self.scale_y)
        
    def apply_shearing(self, *args):
        
        if len(self.poly_points) > 2:
            prev_x_shear = self.shear_x
            prev_y_shear = self.shear_y
            
            self.shear_x = self.shear_x_slider.get()
            self.shear_y = self.shear_y_slider.get()
            
            inc_x = self.shear_x - prev_x_shear
            inc_y = self.shear_y - prev_y_shear
            
            shear = shear_matrix2D(inc_x, inc_y)
            self.apply_transformation(shear, self.shear_label, "Shear", self.shear_x, self.shear_y)
            
    def apply_translation(self, *args):
        
        if len(self.poly_points) > 2:            
            prev_x_translate = self.translate_x
            prev_y_translate = self.translate_y
            
            self.translate_x = self.translate_x_slider.get()
            self.translate_y = self.translate_y_slider.get()

            inc_x = self.translate_x - prev_x_translate
            inc_y = self.translate_y - prev_y_translate
            
            translate = translation_matrix2D(inc_x, inc_y)
            self.apply_transformation(translate, self.translate_label, "Translation", self.translate_x, self.translate_y)
            
    def apply_reflection(self, *args):
        
        if len(self.poly_points) > 2:
            prev_x_reflect = self.reflect_x
            prev_y_reflect = self.reflect_y
            
            self.reflect_x = self.reflect_x_slider.get()
            self.reflect_y = self.reflect_y_slider.get()
            
            #overall scale change
            old_x_reflect = (prev_x_reflect / self.reflect_og_x) * self.reflect_og_x
            old_y_reflect = (prev_y_reflect / self.reflect_og_y) * self.reflect_og_y
            
            cur_x_reflect = (self.reflect_x / self.reflect_og_x) * self.reflect_og_x
            cur_y_reflect = (self.reflect_y / self.reflect_og_y) * self.reflect_og_y
            
            #scale relative percentage change
            inc_x_percent =  (cur_x_reflect - old_x_reflect)/prev_x_reflect + 1
            inc_y_percent =  (cur_y_reflect - old_y_reflect)/prev_y_reflect + 1
            
            reflect = reflect_matrix2D(inc_x_percent, inc_y_percent)
            self.apply_transformation(reflect, self.reflect_label, "Reflect", self.reflect_x, self.reflect_y)

    def apply_transformation(self, transform_matrix, label, text, x_val, y_val = None):  
        self.canvas.delete("shapes")
        
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        
        current_anchor = translation_matrix2D(-cx, -cy)
        anchor_current = translation_matrix2D(cx, cy)
        
        for i in range(0, len(self.poly_points), 2):

            xny_coords = set_matrix2D(self.poly_points[i], self.poly_points[i + 1])
            xny_coords = matrix_multiply(current_anchor, xny_coords)
            xny_coords = matrix_multiply(transform_matrix, xny_coords)
            xny_coords = matrix_multiply(anchor_current, xny_coords)
            #print(d)
            x, y = get_2D_vertices(xny_coords)
            if i < len(self.poly_points) and i + 1 < len(self.poly_points):
                self.poly_points[i] = round(x, 2)
                self.poly_points[i + 1] = round(y, 2)
        

            
            
        '''
        xny_list = "["
        for i in self.poly_points:
            xny_list = xny_list + f"{round(i)}"+ ", "
            
        xny_list = xny_list + "]"
        
        print(xny_list)
        '''
        
        
        self.canvas.create_polygon(self.poly_points, tags=("shapes"))
        if y_val != None:
            label.config(text = "{} X:{} Y:{}".format(text, x_val, y_val))
        else:
            label.config(text = "{} Angle:{}".format(text, x_val))

    def place_point(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.poly_points.append(x)
        self.poly_points.append(y)
        
        if len(self.poly_points) > 2:
            if self.redo_queue:
                self.redo_queue.clear()
            
            self.canvas.delete("shapes")
            #print(self.poly_points)
            #self.undo_stack.append(self.poly_points.copy())
            self.canvas.create_polygon(self.poly_points, tags=("shapes"))
            
         
    def clear_points(self, event):
        self.poly_points.clear()
        self.canvas.delete("shapes")

#Testing Individually
'''
if __name__ == "__main__":
    app = App()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()
'''
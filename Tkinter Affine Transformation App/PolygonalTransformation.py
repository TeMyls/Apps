import tkinter as tk
#from TP2D import *
#from TP3D import *
#import tkinter as tk
from tkinter import ttk
from MatrixMath import *
from tkinter import colorchooser


class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Polygon Transform App") 
        
        #2D Widgets 
        self.undo_button_2d = tk.Button(self, text = "undo")
        self.redo_button_2d = tk.Button(self, text = "redo")
        self.undo_button_2d.grid(row=0,column=0)
        self.redo_button_2d.grid(row=0,column=1)
        
        
        self.t2d_poly = TransformPolygon2D(self, 500, 500)
        self.t2d_poly.grid(row=1,column=2)
        
        self.bind("<Control-z>", self.t2d_poly.undo)
        self.bind("<Control-y>", self.t2d_poly.redo)
        
        
        self.undo_button_2d.config(command=self.t2d_poly.undo)
        self.redo_button_2d.config(command=self.t2d_poly.redo)
        
        self.widgets_2d = [self.undo_button_2d, self.redo_button_2d, self.t2d_poly]
        
        #any keybinding
        #tkinterexamples.com key bindings
        self.bind('z', lambda _ : self.t3d_poly.DDA_raycast_3D())

        #2D Widgets 
        
        self.cf3d = CanvasFrame3d(self, 500, 500)
        self.t3d_poly = TransformPolyhedron3d(self, self.cf3d)
        self.t3d_poly.grid(row=0, column=1, sticky="N")
        self.cf3d.grid(row=0, column=0,sticky="N")
        
        self.widgets_3d = [self.t3d_poly, self.cf3d]
        
        #https://tkdocs.com/tutorial/menus.html
        #https://www.geeksforgeeks.org/python-menu-widget-in-tkinter/
        #https://pythonassets.com/posts/menubar-in-tk-tkinter/
        # Creating Menubar 
        self.menubar = tk.Menu(self) 
       
        
        # Adding Settings and commands 
        self.settings_menu = tk.Menu(self.menubar, tearoff =False)  
        self.mode_menu = tk.Menu(self.menubar, tearoff = False)
        self.mode_type = tk.IntVar()
        self.mode_type.set(2)
        self.mode_menu.add_radiobutton(
            label = "2D",
            variable=self.mode_type,
            value = 1,
            command=self.set_frame_visibility
            
        )
        self.mode_menu.add_radiobutton(
            label = "3D",
            variable=self.mode_type,
            value = 2,
            command=self.set_frame_visibility
            
        )
        # Adding Help Menu 
        self.help_menu = tk.Menu(self.menubar, tearoff = False) 
        self.help_m2D = tk.Menu(self.menubar, tearoff = False)
        self.help_m2D.add_command(label = "Mouse Click: Left to place points, Right to clear")
        self.help_m3D = tk.Menu(self.menubar, tearoff = False)
        self.help_m3D.add_command(label = "Hold Left Click to position, Right to add a point, \nand Scroll to set depth, Z to color faces")


        

        # Menu Placement
        self.menubar.add_cascade(label ='Mode', menu = self.settings_menu) 
        self.settings_menu.add_cascade(label="2D or 3D", menu=self.mode_menu)
        self.menubar.add_cascade(label = "Help", menu=self.help_menu)
        self.help_menu.add_cascade(label="2D", menu=self.help_m2D)
        self.help_menu.add_cascade(label="3D", menu=self.help_m3D)
        
        # display Menu 
        self.config(menu = self.menubar) 
        
        
        self.set_frame_visibility()
             
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
    
    def set_frame_visibility(self):
        key_mode = {
            1:"2D",
            2:"3D"
        }
        if key_mode[self.mode_type.get()] == "2D":
            for widget in self.widgets_2d:
                self.show_widget(widget) 
            for widget in self.widgets_3d:
                self.hide_widget(widget) 
                
            self.bind("<Control-z>", self.t2d_poly.undo)
            self.bind("<Control-y>", self.t2d_poly.redo)
        elif  key_mode[self.mode_type.get()] == "3D":
            
            for widget in self.widgets_2d:
                self.hide_widget(widget) 
            for widget in self.widgets_3d:
                self.show_widget(widget) 
                
            self.bind("<Control-z>", None)
            self.bind("<Control-y>", None)
            
            
            
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
        
        
class CanvasFrame3d(ttk.Frame):  
    def __init__(self, parent, c_width, c_height):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        self.canvas_width = c_width #self.canvas.winfo_width()
        self.canvas_height = c_height #self.canvas.winfo_height()
        self.canvas.grid(row = 0, column = 0, sticky = "N")

    def get_width(self):
        return self.canvas_width
    
    def get_height(self):
        return self.canvas_height
    
    def get_canvas(self):
        return self.canvas
         

class TransformPolyhedron3d(ttk.Frame):
    def __init__(self, parent, canvas_frame,  *args, **kwargs):

        
        #https://webglfundamentals.org/webgl/lessons/webgl-3d-orthographic.html
        #https://webglfundamentals.org/webgl/lessons/webgl-3d-perspective.html
        #https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/projection-matrix-GPU-rendering-pipeline-clipping.html
        #http://www.songho.ca/opengl/gl_projectionmatrix.html
        
        super().__init__(parent)
        
        self.canvas = canvas_frame.get_canvas()
        self.canvas_width = canvas_frame.get_width()  #c_width #self.canvas.winfo_width()
        self.canvas_height = canvas_frame.get_height() #self.canvas.winfo_height()
    
        
        
        self.undo_stack = []
        self.redo_queue = []
        
        #3D DATA
        #A List of vertices
        #Example
        #x1, y1, z1, x2, y2, z2, x3, etc 
        self.vertices = []
        #An Dictionary/Adjacency List of edges
        #The keys are the x indexes of vertices 
        #The values are a list of vertex connections
        #Example
        #{0: [], 6: [1, 2, 0, 3], 3: [0, 2], 1: [2, 0], 5: [0, 3, 4], 4: [1, 2]}
        self.edges = {}
        # A List of lists of vertices forming faces from their egdes
        # uses in the same x indexes vertices as above
        #Formed from a Depth First Search Graph Cycle Detecton Algorithm on the edges
        #or Triangles from the Vertex and it's edge
        #Example
        #[[0, 2, 3], [1, 4, 5], [0, 2, 7], [0, 3, 6], [1, 4, 8], [1, 5, 9], etc]
        self.faces = []
        
        #depth cirle size
        self.z_size = 1
        self.z_min = 1
        self.z_max = 10
        
        #camera planes 
        self.near = 1
        self.far = -1
        self.scale = 1
        
        #orthographic screen coordinates
        self.top = 1
        self.left = -1
        self.right = 1
        self.bottom = -1

        
        #x y z
        self.camera_position = [0.0, 0.0, -self.far/2]
        
        
        #actual z value
        self.zed = round((self.z_size/(self.z_max - self.z_min)) * (self.far - self.near))
        
        

        #MATRICES
        

        a = 2/(self.right - self.left)
        b = 2/(self.top - self.bottom) 
        c = -2/(self.far - self.near)
        d = -1 * (self.far + self.near)/(self.far - self.near)
        e = -1 * (self.top + self.bottom)/(self.top - self.bottom)
        f = -1 * (self.right + self.left)/(self.right - self.left)
        #OpenGL Orthographic Matrix
        self.ortho_perspective_matrix = [
                    [a, 0, 0, f], #x
                    [0, b, 0, e], #y
                    [0, 0, c, d], #z 
                    [0, 0, 0, 1] 
        ]
        
        
        
        #screen coordinates perspective
        self.fov = 110
        self.fov_radians = (self.fov * math.pi)/180
        self.aspect_ratio = self.canvas_width/self.canvas_height
        
        
        self.top = math.tan(self.fov_radians/2) * self.near
        self.left = -self.top * self.aspect_ratio
        self.right = self.top * self.aspect_ratio
        self.bottom = -self.top
        
        
        
        a = (2*self.near)/(self.right - self.left) #1/(self.aspect_ratio*math.tan(self.fov_radians/2))
        b = (2*self.near)/(self.top - self.bottom) #1/math.tan(self.fov_radians/2)
        c = -1 * ( self.far + self.near)/(self.far - self.near)
        d = -1 * ( 2 * self.far * self.near)/(self.far - self.near)
        e = (self.top + self.bottom)/(self.top - self.bottom)
        f = (self.right + self.left)/(self.right - self.left)
        
        
        #OpenGL perspective matrix
        self.true_perspective_matrix = [
                    [a, 0, f, 0], #x
                    [0, b, e, 0], #y
                    [0, 0, c, d], #z 
                    [0, 0,-1, 0] 
        ]
        
        #Handled by switch matrix states
        self.current_matrix = None
        
        #VISIBILITY OPTIONS

        #Vertex 
        self.vert_vis_checkvar = tk.IntVar()
        self.vert_vis_checkvar.set(0)
        self.vert_vis_checkbutton = tk.Checkbutton(self, text = "Vertex Visibility",
                                                    variable=self.vert_vis_checkvar,
                                                    onvalue = 1,
                                                    offvalue= 0,
                                                    command=self.vert_vis_states
        )
        
        
        self.vert_style_svar = tk.StringVar()
        self.vert_style_svar.set("Circle")
        self.vert_circ_radiobutton = ttk.Radiobutton(self, text="Circle", 
                                                    variable=self.vert_style_svar,
                                                    value = "Circle",
                                                    command=self.update_viewport
                                                           )
        
        self.vert_pixel_radiobutton = ttk.Radiobutton(self, text="Pixel", 
                                                    variable=self.vert_style_svar,
                                                    value = "Pixel",
                                                    command=self.update_viewport
                                                           )
        self.vert_ind_radiobutton = ttk.Radiobutton(self, text="Index", 
                                                    variable=self.vert_style_svar,
                                                    value = "Index",
                                                    command=self.update_viewport
                                                           )
        
        self.vert_none_radiobutton = ttk.Radiobutton(self, text="None", 
                                                    variable=self.vert_style_svar,
                                                    value = "None",
                                                    command=self.update_viewport
                                                           )
        
        self.vertex_color = "#0000FF"
        self.vertext_color = "#0000FF"
        self.vertex_color_button = tk.Button(self, text = "Vertex Color",                      
                                                    #state="disabled",
                                                    command=self.vertex_color_chooser,
                                                    bg = self.vertex_color
                                                    )
        self.vertext_color_button = tk.Button(self, text = "Vertex Text Color",                      
                                                    #state="disabled",
                                                    command=self.vertext_color_chooser,
                                                    bg = self.vertext_color
                                                    )
        
        self.vertex_vis_widgets = [
                                    self.vert_circ_radiobutton, 
                                    self.vert_pixel_radiobutton,
                                    self.vert_ind_radiobutton, 
                                    self.vert_none_radiobutton,
                                    self.vertex_color_button,
                                    self.vertext_color_button
                                    ]

        #Edge
        
        self.edge_vis_checkvar = tk.IntVar()
        self.edge_vis_checkvar.set(0)
        self.edge_vis_checkbutton = tk.Checkbutton(self, text = "Edge Visibility",
                                                    variable=self.edge_vis_checkvar,
                                                    onvalue = 1,
                                                    offvalue= 0,
                                                    command=self.edge_vis_states
        )
        
        
        self.edge_style_svar = tk.StringVar()
        self.edge_style_svar.set("Solid")
        self.edge_solid_radiobutton = ttk.Radiobutton(self, text="Solid", 
                                                    variable=self.edge_style_svar,
                                                    value = "Solid",
                                                    command=self.update_viewport
                                                           )
        
        self.edge_dotted_radiobutton = ttk.Radiobutton(self, text="Dotted", 
                                                    variable=self.edge_style_svar,
                                                    value = "Dotted",
                                                    command=self.update_viewport
                                                           )
        self.edge_none_radiobutton = ttk.Radiobutton(self, text="None", 
                                                    variable=self.edge_style_svar,
                                                    value = "None",
                                                    command=self.update_viewport
                                                           )
        

        self.edge_color = "#00FF00"
        self.edge_color_button = tk.Button(self, text = "Edge Color",                      
                                                    #state="disabled",
                                                    command=self.edge_color_chooser,
                                                    bg = self.edge_color
                                                    )


        self.edge_vis_widgets = [

            self.edge_solid_radiobutton,
            self.edge_dotted_radiobutton,
            self.edge_none_radiobutton,
            self.edge_color_button

        ]
        
        #Grid
        
        
        self.grid_vis_checkvar = tk.IntVar()
        self.grid_vis_checkvar.set(0)
        self.grid_vis_checkbutton = tk.Checkbutton(self, text = "Grid Visibility",
                                                    variable=self.grid_vis_checkvar,
                                                    onvalue = 1,
                                                    offvalue=0,
                                                    command=self.grid_vis_states)
        
        
        self.grid_text_intvar= tk.IntVar()
        self.grid_text_intvar.set(0)
        self.grid_text_checkbutton = tk.Checkbutton(self, text = "Display Text",
                                                    variable=self.grid_text_intvar,
                                                    onvalue = 1,
                                                    offvalue=0, 
                                                    command=self.update_viewport
                                                           )
        
        self.grid_lines_boolvar = tk.BooleanVar()
        self.grid_lines_boolvar.set(False)
        self.grid_lines_checkbutton = tk.Checkbutton(self, text = "Display Grid",
                                                    variable=self.grid_lines_boolvar,
                                                    onvalue = True,
                                                    offvalue= False, 
                                                    command=self.update_viewport
                                                           )
        
        self.grid_rotation_boolvar = tk.BooleanVar()
        self.grid_rotation_boolvar.set(True)
        self.grid_rotation_cb = tk.Checkbutton(self, text = "Rotate Grid",
                                                    variable=self.grid_rotation_boolvar,
                                                    onvalue = True,
                                                    offvalue= False, 
                                                    command=self.update_viewport
                                                    )
        
        self.grid_thickness_boolvar = tk.BooleanVar()
        self.grid_thickness_boolvar.set(True)
        self.grid_thickness_cb = tk.Checkbutton(self, text = "Line Depth",
                                                    variable=self.grid_thickness_boolvar,
                                                    onvalue = True,
                                                    offvalue= False, 
                                                    command=self.update_viewport
                                                    )

        self.grid_reset_btn = tk.Button(self, text = "Reset Grid",                      
                                                    #state="disabled",
                                                    command=self.reset_grid_states
                                                    )
       
        self.grid_vis_widgets = [

            self.grid_text_checkbutton,
            self.grid_lines_checkbutton,
            self.grid_rotation_cb,
            self.grid_thickness_cb,
            self.grid_reset_btn

        ]
        
        #Transformations Visibility
        #self.transform_selection_label = ttk.Label(self, text = "Transform Type")
        self.transform_selection_svar = tk.StringVar()
        self.transform_selection_svar.set("Rotation")
        
        self.anchor_radiobutton = ttk.Radiobutton(self, text="Anchor", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Anchor",
                                                           command=self.transform_widget_states)
        
        
        self.rotate_radiobutton = ttk.Radiobutton(self, text="Rotation", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Rotation",
                                                           command=self.transform_widget_states)
        
        self.shear_radiobutton = ttk.Radiobutton(self, text="Shear", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Shear",
                                                           command=self.transform_widget_states)
        
        self.translate_radiobutton = ttk.Radiobutton(self, text="Translation", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Translation",
                                                           command=self.transform_widget_states)
        
        self.reflect_radiobutton = ttk.Radiobutton(self, text="Reflection", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Reflection",
                                                           command=self.transform_widget_states)
        
        self.scale_radiobutton = ttk.Radiobutton(self, text="Scaling", 
                                                           variable=self.transform_selection_svar,
                                                           value = "Scaling",
                                                           command=self.transform_widget_states)
        

        
            
        
        #TRANSFORM WIDGETS
        #ANCHOR/PIVOT
        f = self.far #negative
        t = self.near #positibe
        self.anchor_point = [0.0, 0.0, 0.0]
        self.anchor_label = ttk.Label(self, text = "Pivot Point XYZ")
        self.anchor_x_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.draw_anchor

        )
        self.anchor_x_spinbox.set(self.anchor_point[0])
        
        self.anchor_y_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.draw_anchor

        )
        self.anchor_y_spinbox.set(self.anchor_point[1])
        
        self.anchor_z_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.draw_anchor

        )
        self.anchor_z_spinbox.set(self.anchor_point[2])
        
        self.anchor_widgets = [self.anchor_x_spinbox, self.anchor_y_spinbox, self.anchor_z_spinbox]
        
        #ROTATION
        f = 0
        t = 360
        self.angle = 180
        self.angle_x = 180
        self.angle_y = 180
        self.angle_z = 180
        self.rotate_label = ttk.Label(self, text = "Rotation Angle XYZ")
        self.rotate_x_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            state="readonly",
            command = self.apply_rotation_x

        )
        self.rotate_x_spinbox.set(self.angle)

        self.rotate_y_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            state="readonly",
            command = self.apply_rotation_y


        )
        self.rotate_y_spinbox.set(self.angle)
        
        self.rotate_z_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            state="readonly",
            command = self.apply_rotation_z,
          

        )
        self.rotate_z_spinbox.set(self.angle)

        self.rotate_reset_btn = tk.Button(self, text = "Return to Defaults",
                                    command=self.rotate_reset,
                                    )
        
        self.rotate_widgets = [self.rotate_x_spinbox, self.rotate_y_spinbox, self.rotate_z_spinbox, self.rotate_reset_btn]
        
        #SHEARING
        f = -3
        t = 3

        self.shear_xy = 0.0
        self.shear_xz = 0.0
        self.shear_yz = 0.0
        self.shear_yx = 0.0
        self.shear_zx = 0.0
        self.shear_zy = 0.0

        self.shear_label = ttk.Label(self, text = "Shear\nXY-XZ-YZ-YX-ZX-ZY")
        self.shear_xy_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_xy
        )
        self.shear_xy_spinbox.set(self.shear_xy)

        self.shear_xz_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_xz
        )
        self.shear_xz_spinbox.set(self.shear_xz)

        self.shear_yz_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_yz
        )
        self.shear_yz_spinbox.set(self.shear_yz)

        self.shear_yx_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_yx
        )
        self.shear_yx_spinbox.set(self.shear_yx)
        
        self.shear_zx_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_zx
        )
        self.shear_zx_spinbox.set(self.shear_zx)

        self.shear_zy_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            width=10,
            state="readonly",
            command = self.apply_shearing_zy
        )
        self.shear_zy_spinbox.set(self.shear_zy)

        self.shear_reset_btn = tk.Button(self, text = "Return to Defaults",
                                    command=self.shear_reset,
                                    )
        
        self.shear_widgets = [self.shear_xy_spinbox, 
                              self.shear_xz_spinbox, 
                              self.shear_yx_spinbox, 
                              self.shear_yz_spinbox,
                              self.shear_zx_spinbox,
                              self.shear_zy_spinbox,
                              self.shear_reset_btn]
        #TRANSLATE
        f = self.far #negative
        t = self.near #positibe


        self.translate_x = 0.0
        self.translate_y = 0.0
        self.translate_z = 0.0
        self.translate_label = ttk.Label(self, text = "Translation XYZ")
        self.translate_x_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_translation_x

        )
        self.translate_x_spinbox.set(self.translate_x)

        self.translate_y_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_translation_y

        )
        self.translate_y_spinbox.set(self.translate_y)
        
        self.translate_z_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_translation_z

        )
        self.translate_z_spinbox.set(self.translate_z)

        self.translate_reset_btn = tk.Button(self, text = "Return to Defaults",
                                    command=self.translate_reset,
                                    )
        
        self.translate_widgets = [self.translate_x_spinbox, self.translate_y_spinbox, self.translate_z_spinbox, self.translate_reset_btn]
        #REFLECTION

        f = -1 #negative
        t = 1 #positibe


        self.reflect_x = 1.0
        self.reflect_y = 1.0
        self.reflect_z = 1.0
        self.reflect_label = ttk.Label(self, text = "Reflection XYZ")
        self.reflect_x_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.33,
            state="readonly",
            command = self.apply_reflection_x

        )
        self.reflect_x_spinbox.set(self.reflect_x)

        self.reflect_y_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.33,
            state="readonly",
            command = self.apply_reflection_y

        )
        self.reflect_y_spinbox.set(self.reflect_y)
        
        self.reflect_z_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.33,
            state="readonly",
            command = self.apply_reflection_z

        )
        self.reflect_z_spinbox.set(self.reflect_z)

        self.reflect_reset_btn = tk.Button(self, text = "Return to Defaults",
                                    command=self.reflect_reset,
                                    )
        
        self.reflect_widgets = [self.reflect_x_spinbox, self.reflect_y_spinbox, self.reflect_z_spinbox, self.reflect_reset_btn]

        #SCALING

        f = 0.1 
        t = 5.0


        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        self.scale_label = ttk.Label(self, text = "Scaling XYZ")
        self.scale_x_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_scaling_x

        )
        self.scale_x_spinbox.set(self.scale_x)

        self.scale_y_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_scaling_y

        )
        self.scale_y_spinbox.set(self.scale_y)
        
        self.scale_z_spinbox = ttk.Spinbox(
            self,
            from_ = f,
            to = t,
            increment=0.1,
            state="readonly",
            command = self.apply_scaling_z

        )
        self.scale_z_spinbox.set(self.scale_z)

        self.scale_reset_btn = tk.Button(self, text = "Return to Defaults",
                                    command=self.scale_reset,
                                    )
        
        self.scale_widgets = [self.scale_x_spinbox, self.scale_y_spinbox, self.scale_z_spinbox, self.scale_reset_btn]

        #
        #VERTEX
        self.vertex_label = ttk.Label(self, text="Vertices")
        self.vertex_scrollbar_y = ttk.Scrollbar(self, orient='vertical')
        self.vertex_scrollbar_x = ttk.Scrollbar(self, orient='horizontal')
        self.vertex_listbox = tk.Listbox(self, 
                                        yscrollcommand = self.vertex_scrollbar_y.set,
                                        xscrollcommand = self.vertex_scrollbar_x.set,
                                        selectmode="single", 
                                        exportselection=False
                                        )
        
        self.vertex_scrollbar_y.config(command=self.vertex_listbox.yview)
        self.vertex_scrollbar_x.config(command=self.vertex_listbox.xview)
        
        self.vertex_select_button = tk.Button(self, text="Select Vertex", command=self.select_vertex)
        self.vertex_delete_button = tk.Button(self, text="Delete Selected", command=self.remove_vertex)
        self.vertex_del_last_btn = tk.Button(self, text="Delete Last", command=self.delete_vertex)
        self.vertex_clear_button = tk.Button(self, text="Clear", command=self.clear_vertices)
        
    
        
        #EDGES
        
        self.edge_label = ttk.Label(self, text="Vertex:? - Edges")
        
        
        #https://blog.teclado.com/tkinter-scrollable-frames/
        #the widget below the only widget that has to be gridded in arrangement
        self.edge_mn_frame = ttk.Frame(self)
        self.edge_canvas = tk.Canvas(self.edge_mn_frame, width=100, height=150) #about the width of a listbox with no specificied width and heoght
        self.edge_scrollbar_y = ttk.Scrollbar(self.edge_mn_frame, orient='vertical', command=self.edge_canvas.yview)
        self.edge_scrl_frame = ttk.Frame(self.edge_canvas)
        
        self.edge_ind = 0
        self.edge_keys_ls = None #self.edges.keys()
        #below keeps track for the dynamic checkboxes generated
        #will be the edges and whether they're connected tp other edges,
        # a dictionary of dictionarys and bools 
        self.edge_options = {} 
        #collection of th shown checkbox, deleted and regenerated frequently
        self.edge_checklist = []
        
        
        self.edge_scrl_frame.bind(
            "<Configure>",
            lambda e: self.edge_canvas.configure(
                scrollregion=self.edge_canvas.bbox("all")
            )
        )
        
        self.edge_canvas.create_window((0, 0), window=self.edge_scrl_frame, anchor="nw")
        self.edge_canvas.configure(yscrollcommand=self.edge_scrollbar_y.set)
        #self.edge_scrollbar_y.config(command=self.self.edge_canvas.yview)
        
        self.edge_canvas.grid(row=0, column=0)#pack(side="left", fill="both", expand=True)
        self.edge_scrollbar_y.grid(row=0, column=1, sticky="NS")#pack(side="right", fill="y")
        
        
        '''
        #Test
        options = ["Option " + str(i) for i in range(1,50)]
        i = 0
        for option in options:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.edge_scrl_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
            i += 1
        '''
        
        
        
    
        self.edge_next = tk.Button(self,
                                   text="Next Vertex",
                                   command=self.next_vertex,
                                   #state="disabled"
                                   )
        self.edge_prev = tk.Button(self, 
                                   text="Prev Vertex", 
                                   command=self.prev_vertex, 
                                   #state="disabled"
                                   )
        #FACES

        self.face_label = ttk.Label(self, text="Faces")

        self.face_mn_frame = ttk.Frame(self)
        self.face_canvas = tk.Canvas(self.face_mn_frame, width=100, height=150) #about the width of a listbox with no specificied width and heoght
        self.face_scrollbar_y = ttk.Scrollbar(self.face_mn_frame, orient='vertical', command=self.face_canvas.yview)
        self.face_scrollbar_x = ttk.Scrollbar(self.face_mn_frame, orient='horizontal', command=self.face_canvas.xview)
        self.face_scrl_frame = ttk.Frame(self.face_canvas)
        
        
        #below keeps track for the dynamic checkboxes generated
        

        #collection of th shown checkbox, deleted and regenerated frequently
        self.face_checklist = []
        #Dictionary of the face vertex indexes as lists of X Y Z vertices, the face color, and the z average of faces
        self.faces_data = {}
        
        self.face_scrl_frame.bind(
            "<Configure>",
            lambda e: self.face_canvas.configure(
                scrollregion=self.face_canvas.bbox("all")
            )
        )
        
        self.face_canvas.create_window((0, 0), window=self.face_scrl_frame, anchor="nw")
        self.face_canvas.configure(yscrollcommand=self.face_scrollbar_y.set)
        self.face_canvas.configure(xscrollcommand=self.face_scrollbar_x.set)
        
        self.face_canvas.grid(row=0, column=0)#pack(side="left", fill="both", expand=True)
        self.face_scrollbar_y.grid(row=0, column=1, sticky="NS")#pack(side="right", fill="y")
        self.face_scrollbar_x.grid(row=1, column=0, sticky="EW")
        
        #Test
        '''
        options = ["Option " + str(i) for i in range(1,10)]
        i = 0
        for option in options:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.face_scrl_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
            i += 1
        '''
  
        
        
        #SCREEN AND WORLD MOUSE COORDINATES
        self.screen_xy = [self.canvas_width/2, self.canvas_height/2]
        self.screen_xy_label = ttk.Label(self, text = "Screen \nX:{} Y: {}".format(self.screen_xy[0], self.screen_xy[1]))

        self.world_xyz = [0.0, 0.0, self.zed]
        self.world_xyz_label = ttk.Label(self, text = "World \nX:{} Y:{} Z:{}".format(self.world_xyz[0], self.world_xyz[1], round(self.world_xyz[2],3)))
        
        self.selected_point = [0, 0, 0]
        
        #PERSPECTIVE OPTIONS
        self.perspective_sel = tk.StringVar()
        self.perspective_sel.set("Orthographic")
        
        self.ortho_radiobutton = ttk.Radiobutton(self, text="Orthographic", 
                                                           variable=self.perspective_sel,
                                                           value = "Orthographic",
                                                           command=self.switch_matrix_states
                                                           )
        
        
        self.true_persp_radiobutton = ttk.Radiobutton(self, text="Perspective", 
                                                           variable=self.perspective_sel,
                                                           value = "Perspective-T",
                                                           command=self.switch_matrix_states
                                                           )
        
        
        
        
        
        
        #CANVAS METHODS
        #self.canvas.bind("<Double-Button-1>", self.remove_point)

        #if mouse is pressed and released, for some reason button press fires more than once
        self.pressed = False

        #1 is left mouse button, 3 is right mouse button
        #self.canvas.bind("<ButtonRelease-3>", self.reset_pressed)
        self.canvas.bind("<ButtonPress-3>", self.place_vertex)  
        
        #self.canvas.bind("<Double-Button-1>", self.place_vertex)
        self.canvas.bind("<B1-Motion>", self.z_pos) # <B1-Motion>
        self.canvas.bind("<MouseWheel>", self.set_depth)  
        
        
        #GRIDLINES
        self.grid_lines_x = []
        self.grid_lines_z = []
        self.reset_grid_states()

        #Debug
        self.debug_button = tk.Button(self, text="Display Data", command=self.display_data)


        #Placement
        
        
        arrangement = [
                        #[None                   , None                   , None                  , None                 , None                  , None ],
                       
                        #Data Panels
                        [self.world_xyz_label   , None                   , self.screen_xy_label, None                              , None, None],
                        [self.ortho_radiobutton , None                   , self.true_persp_radiobutton, None                       , None, None],
                        [self.vertex_label      , None                   , self.edge_label     , None                              , self.face_label, None],
                        [self.vertex_listbox    , self.vertex_scrollbar_y, self.edge_mn_frame  , None                              , self.face_mn_frame, None],
                        [self.vertex_scrollbar_x, None                   , None                , None                              , None, None],
                        [self.vertex_select_button,None                  , self.edge_next      , None                              , self.debug_button, None],
                        [self.vertex_delete_button,None                  , self.edge_prev      , None                              , None, None],
                        [self.vertex_del_last_btn, None                  , None                , None                              , None, None],
                        [self.vertex_clear_button, None                  , None                , None                              , None, None],

                        #Visibility Panels
                        [self.vert_vis_checkbutton, None                 , self.edge_vis_checkbutton, None, self.grid_vis_checkbutton, None        ],
                        [self.vert_circ_radiobutton, self.vert_ind_radiobutton, self.edge_dotted_radiobutton, self.edge_solid_radiobutton, self.grid_lines_checkbutton, self.grid_rotation_cb],
                        [self.vert_pixel_radiobutton, self.vert_none_radiobutton, self.edge_none_radiobutton, self.edge_color_button, self.grid_text_checkbutton,self.grid_thickness_cb],
                        [self.vertex_color_button , self.vertext_color_button, None, None, self.grid_reset_btn              , None                 ],

                        #Transform Widgets
                        [self.rotate_label      ,None                    , self.shear_label, None                      , self.anchor_label    ,None  ],
                        [self.rotate_radiobutton,None                    , self.shear_radiobutton, None                , self.anchor_radiobutton,None],
                        [self.rotate_x_spinbox  ,None                    , self.shear_xy_spinbox, self.shear_xz_spinbox, self.anchor_x_spinbox , None],
                        [self.rotate_y_spinbox  ,None                    , self.shear_yx_spinbox, self.shear_yz_spinbox, self.anchor_y_spinbox , None],
                        [self.rotate_z_spinbox  ,None                    , self.shear_zx_spinbox, self.shear_zy_spinbox, self.anchor_z_spinbox , None],
                        [self.rotate_reset_btn  , None                   , self.shear_reset_btn , None                 , None                  , None ],
                        [self.translate_label  , None                    , self.reflect_label , None                   , self.scale_label     , None ],
                        [self.translate_radiobutton, None                , self.reflect_radiobutton , None             , self.scale_radiobutton, None],
                        [self.translate_x_spinbox, None                  , self.reflect_x_spinbox  , None              , self.scale_x_spinbox , None ],
                        [self.translate_y_spinbox , None                 , self.reflect_y_spinbox   , None             , self.scale_y_spinbox , None ],
                        [self.translate_z_spinbox , None                 , self.reflect_z_spinbox  , None              , self.scale_z_spinbox , None ],
                        [self.translate_reset_btn , None                 , self.reflect_reset_btn  , None              , self.scale_reset_btn , None ]

                    ]
        
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):

                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                    if isinstance(arrangement[ind_y][ind_x], tk.Scrollbar):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NEWS")
                    else:
                        #if isinstance(arrangement[ind_y][ind_x], tk.Label):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NW")

        
        
        
        self.switch_matrix_states()
        self.grid_vis_states()
        self.vert_vis_states()
        self.edge_vis_states()

        self.transform_widget_states()
        self.draw_anchor()
        self.update_viewport()
    
    #VISIBILITY
    
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
        
    def delete_widget(self, widget):
        widget.destroy()
        
    def display_widget_groups(self, show_widget_arr, hide_widget_arr_arr):
        for widget in show_widget_arr:
            self.show_widget(widget)
        for arr in hide_widget_arr_arr:
            for widget in arr:
                self.hide_widget(widget)

    def transform_widget_states(self):
        transformation_type = self.transform_selection_svar.get()
        all_widget_groups = [
                            self.shear_widgets, 
                            self.rotate_widgets,   
                            self.anchor_widgets, 
                            self.translate_widgets,
                            self.reflect_widgets,
                            self.scale_widgets
                            ]
        #if transformation_type == "ALL":
            #for widget in self.winfo_children():
        if transformation_type == "Anchor":
            ind = all_widget_groups.index(self.anchor_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )
        elif transformation_type == "Rotation":
            ind = all_widget_groups.index(self.rotate_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )

        elif transformation_type == "Shear":
            ind = all_widget_groups.index(self.shear_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )
        elif transformation_type == "Translation":
            ind = all_widget_groups.index(self.translate_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )
        elif transformation_type == "Reflection":
            ind = all_widget_groups.index(self.reflect_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )

        elif transformation_type == "Scaling":
            ind = all_widget_groups.index(self.scale_widgets)
            widget_arr = all_widget_groups.pop(ind)
            self.display_widget_groups(
                widget_arr,
                all_widget_groups,
            )
   
    def reset_grid_states(self):
        #X AXIS SPANNING Z PLANE
        divides = 10
        #The total amount of space occupied by clip space on the x y and z plane 
        total_space = abs(self.far - self.near)
        spacing = total_space/divides
        #spacing multipliers
        sxm, szm, exm, ezm = 1, 1, 1, 1
        
        #ugliest list comprehension
        self.grid_lines_x = [
            #x spanning, points are xyz pairs of lines 
            #world space
            #start x, y,z end x, y, z
            [round(x * spacing + -1, 2) * sxm, 
             0.0, 
             self.near * szm, 
             round(x * spacing + -1, 2) * exm, 
             0.0, 
             self.far * ezm] for x in range(divides + 1)
        ]
        
        #print(self.grid_lines_x)
        
        #flattening the 2d array
        self.grid_lines_x = [
            xyz for coord in self.grid_lines_x for xyz in coord
        ]
        
        #print(self.grid_lines_x)
        #print()
        
        #Z AXIS SPANNING X PLANE
        sxm, szm, exm, ezm = 1, 1, 1, 1
        self.grid_lines_z = [
            #z spanning, points are xyz pairs of lines 
            #world space
            #start x, y,z end x, y, z
            [1 * sxm, 
             0.0, 
             round(z * spacing + -1, 2) * szm, 
             -1 * exm, 
             0.0, 
             round(z * spacing + -1, 2) * ezm] for z in range(divides + 1)
        ]
        
        #print(self.grid_lines_z)
        
        #flattening the 2d array
        self.grid_lines_z = [
            xyz for coord in self.grid_lines_z for xyz in coord
        ]
        
        #print(self.grid_lines_z)
        #print()
        #print(self.canvas_height, self.canvas_width)
        
        self.update_viewport()
             
    def vert_vis_states(self):
        
        vert_vis_check = self.vert_vis_checkvar.get()
        if vert_vis_check == self.vert_vis_checkbutton.cget('onvalue'):
            
            for widget in self.vertex_vis_widgets:
                self.show_widget(widget) 

            
        else:
            for widget in self.vertex_vis_widgets:
                self.hide_widget(widget) 
            
    def edge_vis_states(self):
        edge_vis_check = self.edge_vis_checkvar.get()
        if edge_vis_check == self.edge_vis_checkbutton.cget('onvalue'):
            
            for widget in self.edge_vis_widgets:
                self.show_widget(widget) 

            
        else:
            for widget in self.edge_vis_widgets:
                self.hide_widget(widget) 

    def grid_vis_states(self):
        grid_vis_check = self.grid_vis_checkvar.get()
        if grid_vis_check == self.grid_vis_checkbutton.cget('onvalue'):

            for widget in self.grid_vis_widgets:
                self.show_widget(widget) 

        else:

            for widget in self.grid_vis_widgets:
                self.hide_widget(widget) 
             
    def display_data(self):
        print("Vertices\n", self.vertices)
        print("Edges\n", self.edges)
        print("Edge Options\n", self.edge_options)
        print("Edge Checks\n", self.edge_checklist)
        print("Faces\n", self.faces)
        #print("Vertices\n", self.faces_data)

    def switch_matrix_states(self):
        #Perspective Display
        persp_val = self.perspective_sel.get()
        if persp_val == "Orthographic":
            self.current_matrix = self.ortho_perspective_matrix.copy()
        elif persp_val == "Perspective-T":
            self.current_matrix = self.true_perspective_matrix.copy()
        
        self.update_viewport()
        
    def update_viewport(self):
        
        #Grid Display
        self.canvas.delete("gridlinelabels")
        self.canvas.delete("gridlines")
        self.draw_grid_lines(self.grid_lines_z, -1)
        self.draw_grid_lines(self.grid_lines_x)
            

        #Vertex Display
        self.draw_projected_vertices()
        self.draw_edge_lines()
                   
    #COORDINATE SPACE TRANSFORMATIONS
    
    def world_to_screen(self, x, y, z):
        #this is the function that projects 3d points from the world to the screen
        xyz_coords = set_matrix3D(x, y, z)
        projected_points = matrix_multiply(self.current_matrix, xyz_coords)
        gx, gy, gz = get_3D_vertices(projected_points)
        return ((gx + 1)/2)*self.canvas_width, (abs(gy - 1)/2) * self.canvas_height
    
    def screen_to_world(self, x, y):
        #for mouse to world detection, based of the OpenGL 2d clip space
        #https://webglfundamentals.org/webgl/lessons/webgl-fundamentals.html
        #y 1 would be top center -1 bottom center
        #x 1 would be right center -1 left center
        #the center of the screen would be the orgin 0, 0
        return  round((x/self.canvas_width)  * 2 - 1, 6),  round((y/self.canvas_height) * -2 + 1, 6), self.zed
    
    def z_pos(self, event):
        #
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        

        self.screen_xy[0], self.screen_xy[1] = x, y
        self.world_xyz[0], self.world_xyz[1], self.world_xyz[2] = self.screen_to_world(self.screen_xy[0], self.screen_xy[1])
        

        oval_size = 3
        self.canvas.delete("s-coords")
        self.canvas.create_oval(
                        x - oval_size, 
                        y - oval_size,
                        x + oval_size,
                        y + oval_size,
                        fill = "yellow",
                        tags=("s-coords")
                        )
        
        x, y = self.world_to_screen(self.world_xyz[0], self.world_xyz[1], self.world_xyz[2])
        
        oval_size = (1 - (self.zed - 1)/(self.far - self.near)) * self.z_max
        self.canvas.delete("w-coords")
        self.canvas.create_oval(
                        x - oval_size, 
                        y - oval_size,
                        x + oval_size,
                        y + oval_size,
                        fill = "green",
                        tags=("w-coords")
                        )
        

        deci = 2
        rwx, rwy, rwz = round(self.world_xyz[0], deci), round(self.world_xyz[1], deci), round(self.world_xyz[2], deci)
        sx, sy = round(self.screen_xy[0], deci), round(self.screen_xy[1], deci)
        self.world_xyz_label.config(text = "World \nX:{} Y:{} Z:{}".format(rwx, rwy, rwz))
        self.screen_xy_label.config(text = "Screen \nX:{} Y:{}".format(sx, sy))
  
    def set_depth(self, event):
        z_inc = -1 * event.delta/3600
        
        if z_inc < 0:
            if self.z_size > self.z_min:
                self.z_size = self.z_size + z_inc
            else:
                self.z_size = self.z_min
                
        if z_inc > 0:
            if self.z_size < self.z_max:
                self.z_size = self.z_size + z_inc
            else:
                self.z_size = self.z_max
                
        self.zed = 1 + (self.z_size/(self.z_max - self.z_min)) * (self.far - self.near)  + 0.22
        
        self.world_xyz[2] = self.zed
        
        deci = 2
        rwx, rwy, rwz = round(self.world_xyz[0], deci), round(self.world_xyz[1], deci), round(self.world_xyz[2], deci)
        sx, sy = round(self.screen_xy[0], deci), round(self.screen_xy[1], deci)
        self.world_xyz_label.config(text = "World \nX:{} Y:{} Z:{}".format(rwx, rwy, rwz))
        self.screen_xy_label.config(text = "Screen \nX:{} Y:{}".format(sx, sy))

        
        x, y = self.screen_xy[0], self.screen_xy[1]
        oval_size = 3
        self.canvas.delete("s-coords")
        self.canvas.create_oval(
                        x - oval_size, 
                        y - oval_size,
                        x + oval_size,
                        y + oval_size,
                        fill = "yellow",
                        tags=("s-coords")
                        )
        
        x, y = self.world_to_screen(self.world_xyz[0], self.world_xyz[1], self.world_xyz[2])
        oval_size = (1 - (self.world_xyz[2] - 1)/(self.far - self.near)) * self.z_max
        self.canvas.delete("w-coords")
        self.canvas.create_oval(
                        x - oval_size, 
                        y - oval_size,
                        x + oval_size,
                        y + oval_size,
                        fill = "green",
                        tags=("w-coords")
                        )
        
    def reset_pressed(self, event):
        if self.pressed == True:
            self.pressed = False

    #TRANSFORMATION METHODS
        
    def degrees_to_radians(self, deg):
        return (deg * math.pi)/180   
    
    def rotate_reset(self):
        self.angle_x = 180
        self.angle_y = 180
        self.angle_z = 180
        self.rotate_x_spinbox.set(self.angle_x)
        self.rotate_y_spinbox.set(self.angle_y)
        self.rotate_z_spinbox.set(self.angle_z)

    def shear_reset(self):
        self.shear_xy = 0.0
        self.shear_xz = 0.0
        self.shear_yx = 0.0
        self.shear_yz = 0.0
        self.shear_zx = 0.0
        self.shear_zy = 0.0
        self.shear_xy_spinbox.set(0)
        self.shear_xz_spinbox.set(0)
        self.shear_yx_spinbox.set(0)
        self.shear_yz_spinbox.set(0)
        self.shear_zx_spinbox.set(0)
        self.shear_zy_spinbox.set(0)

    def translate_reset(self):
        self.translate_x = 0.0
        self.translate_y = 0.0
        self.translate_z = 0.0
        self.translate_x_spinbox.set(self.translate_x)
        self.translate_y_spinbox.set(self.translate_y)
        self.translate_z_spinbox.set(self.translate_z)

    def reflect_reset(self):
        self.reflect_x = 1.0
        self.reflect_y = 1.0
        self.reflect_z = 1.0
        self.reflect_x_spinbox.set(self.reflect_x)
        self.reflect_y_spinbox.set(self.reflect_y)
        self.reflect_z_spinbox.set(self.reflect_z)

    def scale_reset(self):
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        self.scale_x_spinbox.set(self.scale_x)
        self.scale_y_spinbox.set(self.scale_y)
        self.scale_z_spinbox.set(self.scale_z)

    



    def apply_rotation_x(self, *args):
        self.angle_x = self.apply_rotation(self.angle_x, self.rotate_x_spinbox, x_rotation_matrix3D)
                 
    def apply_rotation_y(self, *args):
        self.angle_y = self.apply_rotation(self.angle_y, self.rotate_y_spinbox, y_rotation_matrix3D)
        
    def apply_rotation_z(self, *args):
        self.angle_z = self.apply_rotation(self.angle_z, self.rotate_z_spinbox, z_rotation_matrix3D)   

    def apply_rotation(self, axis_angle, axis_spinbox, axis_matrix_3D):
        prev_angle = axis_angle
        current_angle = int(axis_spinbox.get())
        rotation = axis_matrix_3D(self.degrees_to_radians(prev_angle - current_angle))
        self.apply_transformation(rotation, True)
        return current_angle

    def apply_grid_rotation(self, line_grid, rotation, current_anchor, anchor_current, *args):
        #if self.grid_lines_boolvar.get():
        if self.grid_rotation_boolvar.get():
            start_point = []
            start_ind = []
            end_point = []
            end_ind = []
            
            for i in range(0, len(line_grid), 3):
                
                gx, gy, gz = line_grid[i], line_grid[i + 1], line_grid[i + 2]
                ix, iy, iz = i, i + 1, i + 2
                
                if len(start_point) > 0 and len(end_point) == 0:
                    #print('y')
                    #x y z
                    end_point = [gx, gy, gz]
                    end_ind = [ix, iy, iz]
                if len(start_point) == 0:
                    #print('n')
                    #x y z
                    start_point = [gx, gy, gz]
                    start_ind = [ix, iy, iz]
                    
                if len(start_point) > 0 and len(end_point) > 0:
                    #print('m')
                    #print(start_point)
                    #print(end_point)
                    #print() 
                    xyz_coords = set_matrix3D(start_point[0], start_point[1], start_point[2])
                    xyz_coords = matrix_multiply(current_anchor, xyz_coords)
                    xyz_coords = matrix_multiply(rotation, xyz_coords)
                    xyz_coords = matrix_multiply(anchor_current, xyz_coords)
                    x, y, z = get_3D_vertices(xyz_coords)
                    
                    line_grid[start_ind[0]] = x
                    line_grid[start_ind[1]] = y
                    line_grid[start_ind[2]] = z
                    
                    xyz_coords = set_matrix3D(end_point[0], end_point[1], end_point[2])
                    xyz_coords = matrix_multiply(current_anchor, xyz_coords)
                    xyz_coords = matrix_multiply(rotation, xyz_coords)
                    xyz_coords = matrix_multiply(anchor_current, xyz_coords)
                    x, y, z = get_3D_vertices(xyz_coords)
                    
                    line_grid[end_ind[0]] = x
                    line_grid[end_ind[1]] = y
                    line_grid[end_ind[2]] = z
                

                
                    start_point.clear()
                    end_point.clear()
                    start_ind.clear()
                    end_ind.clear()
                
                
            start_point.clear()
            end_point.clear()
            start_ind.clear()
            end_ind.clear()
               
    def apply_shearing_xy(self, *args):
        self.shear_xy = self.apply_shearing(self.shear_xy, self.shear_xy_spinbox, 1)
        
    def apply_shearing_xz(self, *args):
        self.shear_xz = self.apply_shearing(self.shear_xz, self.shear_xz_spinbox, 2)

    def apply_shearing_yz(self, *args):
        self.shear_yz = self.apply_shearing(self.shear_yz, self.shear_yz_spinbox, 3)

    def apply_shearing_yx(self, *args):
        self.shear_yx = self.apply_shearing(self.shear_yx, self.shear_yx_spinbox, 4)

    def apply_shearing_zx(self, *args):
        self.shear_zx = self.apply_shearing(self.shear_zx, self.shear_zx_spinbox, 5)

    def apply_shearing_zy(self, *args):
        self.shear_zy = self.apply_shearing(self.shear_zy, self.shear_zy_spinbox, 6)

    def apply_shearing(self, axis_shear, axis_spinbox, arg_ind):
        
        prev_shear = axis_shear
        current_shear = float(axis_spinbox.get())
        inc = current_shear - prev_shear
        shear_dict = {

                        1: shear_matrix3D(inc, 0, 0, 0, 0, 0),
                        2: shear_matrix3D(0, inc, 0, 0, 0, 0),
                        3: shear_matrix3D(0, 0, inc, 0, 0, 0),
                        4: shear_matrix3D(0, 0, 0, inc, 0, 0),
                        5: shear_matrix3D(0, 0, 0, 0, inc, 0),
                        6: shear_matrix3D(0, 0, 0, 0, 0, inc)
                        
                        }
        
        shear = shear_dict[arg_ind]
        self.apply_transformation(shear)
        return current_shear
    
    def apply_translation_x(self, *args):
        self.translate_x = self.apply_translation(self.translate_x, self.translate_x_spinbox, 1)

    def apply_translation_y(self, *args):
        self.translate_y = self.apply_translation(self.translate_y, self.translate_y_spinbox, 2)

    def apply_translation_z(self, *args):
        self.translate_z = self.apply_translation(self.translate_z, self.translate_z_spinbox, 3)

    def apply_translation(self, axis_translation, axis_spinbox, arg_ind):
        
        prev_translation = axis_translation
        current_translation = float(axis_spinbox.get())
        inc = current_translation - prev_translation 

        translation_dict = {

                        1: translation_matrix3D(inc, 0, 0),
                        2: translation_matrix3D(0, inc, 0),
                        3: translation_matrix3D(0, 0, inc)

                        }   

        translation = translation_dict[arg_ind]
        
        self.apply_transformation(translation, False)
        return current_translation
    
    def apply_reflection_x(self, *args):
        self.reflect_x = self.apply_reflection(self.reflect_x, self.reflect_x_spinbox, 1)

    def apply_reflection_y(self, *args):
        self.reflect_y = self.apply_reflection(self.reflect_y, self.reflect_y_spinbox, 2)

    def apply_reflection_z(self, *args):
        self.reflect_z = self.apply_reflection(self.reflect_z, self.reflect_z_spinbox, 3)

    def apply_reflection(self, axis_reflection, axis_spinbox, arg_ind):
        
        prev_reflection = (axis_reflection / 1) * 1
        current_reflection = (float(axis_spinbox.get()) / 1) * 1

        #print("PR {} CR {}".format(prev_reflection, current_reflection))

        inc = (current_reflection - prev_reflection)/(prev_reflection) + 1 

        #print("PR {} CR {} inc{}\n".format(prev_reflection, current_reflection, inc))
        reflection_dict = {

                        1: reflection_matrix3D(inc, 1, 1),
                        2: reflection_matrix3D(1, inc, 1),
                        3: reflection_matrix3D(1, 1, inc)

                        }   

        reflection = reflection_dict[arg_ind]
        
        self.apply_transformation(reflection, False)
        return current_reflection
        
    def apply_scaling_x(self, *args):
        self.scale_x = self.apply_scaling(self.scale_x, self.scale_x_spinbox, 1)

    def apply_scaling_y(self, *args):
        self.scale_y = self.apply_scaling(self.scale_y, self.scale_y_spinbox, 2)

    def apply_scaling_z(self, *args):
        self.scale_z = self.apply_scaling(self.scale_z, self.scale_z_spinbox, 3)

    def apply_scaling(self, axis_scaling, axis_spinbox, arg_ind):

        prev_scaling = (axis_scaling / 1) * 1
        current_scaling = (float(axis_spinbox.get()) / 1) * 1

        inc = (current_scaling - prev_scaling)/prev_scaling + 1
        scaling_dict = {

                        1: scale_matrix3D(inc, 1, 1),
                        2: scale_matrix3D(1, inc, 1),
                        3: scale_matrix3D(1, 1, inc)

                        }   

        scaling = scaling_dict[arg_ind]
        
        self.apply_transformation(scaling, False)
        return current_scaling

    def apply_transformation(self, transform_matrix_3D, is_rotating = False):
        cx = self.anchor_point[0]
        cy = self.anchor_point[1]
        cz = self.anchor_point[2]
    
        current_anchor = translation_matrix3D(-cx, -cy, -cz)
        anchor_current = translation_matrix3D(cx, cy, cz)
        if is_rotating:
            self.apply_grid_rotation(self.grid_lines_z, transform_matrix_3D, current_anchor, anchor_current)
            self.apply_grid_rotation(self.grid_lines_x, transform_matrix_3D, current_anchor, anchor_current)
            
            self.canvas.delete("gridlinelabels")
            self.canvas.delete("gridlines")
            self.draw_grid_lines(self.grid_lines_z, -1)
            self.draw_grid_lines(self.grid_lines_x)
    
        self.draw_anchor()

        if len(self.vertices) > 0:
            
            self.apply_vertex_transformation(transform_matrix_3D, current_anchor, anchor_current)
            
            self.update_faces_data()
            self.draw_faces()
            self.draw_projected_vertices()
            self.draw_edge_lines()
            #self.print_vertices()

    def apply_vertex_transformation(self, transform_matrix, anchor_matrix, matrix_anchor):
        for i in range(0, len(self.vertices), 3):
    
            xyz_coords = set_matrix3D(self.vertices[i], self.vertices[i + 1], self.vertices[i + 2])
            xyz_coords = matrix_multiply(anchor_matrix, xyz_coords)
            xyz_coords = matrix_multiply(transform_matrix, xyz_coords)
            xyz_coords = matrix_multiply(matrix_anchor, xyz_coords)
            
            x, y, z = get_3D_vertices(xyz_coords)
            if i < len(self.vertices) and i + 1 < len(self.vertices):
                self.vertices[i] = x
                self.vertices[i + 1] = y
                self.vertices[i + 2] = z

        self.draw_projected_vertices()
        #self.print_vertices()

    #CANVAS DRAWING METHODS     

    def draw_grid_lines(self, grid_lines, one_sign = 1):
        #Grid Lines
        if self.grid_lines_boolvar.get():
            start_point = []
            end_point = []
            
            line_num = len(grid_lines)
            for i in range(0, len(grid_lines), 3):
                
                gx, gy, gz = grid_lines[i], grid_lines[i + 1], grid_lines[i + 2]
                
                if len(start_point) > 0 and len(end_point) == 0:
                    #x y z
                    end_point = [gx, gy, gz]
                
                if len(start_point) == 0:
                    #x y z
                    start_point = [gx, gy, gz]
                    
                if len(start_point) > 0 and len(end_point) > 0:
                    #print(start_point)
                    #print(end_point)
                    #print()
                    
                    sx, sy = self.world_to_screen(start_point[0], start_point[1], start_point[2])
                    ex, ey = self.world_to_screen(end_point[0], end_point[1], end_point[2])
                    
                    line_size = 1
                    if self.grid_thickness_boolvar.get():
                        line_z_max = max(start_point[2], end_point[2])
                        thick_max = 3
                        z_percent = (1 - (line_z_max - 1)/(self.far - self.near))
                        line_size = round(z_percent * thick_max, 6)
                        pixel_spacing = line_num
                        #z percentage * distance formula calculation of gridline on screen
                        #dash_size = int(250 * z_percent + 1)
                        #print(dash_size)
                        #print(z_percent, dash_size, pixel_spacing)
                    
                    self.canvas.create_line(sx, sy, ex, ey,
                                            tags=("gridlines"),
                                            width=line_size
                                            #tuple(dash_size - pixel_spacing)
                                            #dash=(dash_size, 1)
                                            )
                    
                    start_point.clear()
                    end_point.clear()
        
        #Grid Text 
        #Grid Square Edges, 
        #The beginning x, y, z triplet in the gridlines array
        #The ending x, y, z triplet in gridlines array
        if self.grid_text_intvar.get() == self.grid_text_checkbutton.cget('onvalue'):
            if one_sign > 0:
                bx, by, bz = one_sign * grid_lines[0], one_sign * grid_lines[1], one_sign * grid_lines[2]
                ex, ey, ez = one_sign * grid_lines[-3], one_sign * grid_lines[-2], one_sign * grid_lines[-1]
                deci = 2
                color = "red"
                min_font_size = 8
                font_mult = 5
                
                
                tx1, ty1 = self.world_to_screen(bx, by, bz)
                tx2, ty2 = self.world_to_screen(ex, ey, ez)
            
            
                self.canvas.create_text(tx1, 
                                        ty1,
                                        text="x:{}\ny:{}\nz:{}".format(round(bx, deci), round(by, deci), round(bz, deci)),
                                        fill=color,
                                        font = ("Arial", round((1 - (bz - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                        tags=("gridlinelabels"))
                self.canvas.create_text(tx2, 
                                        ty2,
                                        text="x:{}\ny:{}\nz:{}".format(round(ex, deci), round(ey, deci), round(ez, deci)),
                                        fill=color,
                                        font = ("Arial", round((1 - (ez - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                        tags=("gridlinelabels"))
            else:
                #This is wrong it will be corrected, eventually
                bx, by, bz = one_sign * grid_lines[3], one_sign * grid_lines[4], one_sign * grid_lines[5]
                ex, ey, ez = one_sign * grid_lines[-6], one_sign * grid_lines[-5], one_sign * grid_lines[-4]
                deci = 2
                color = "red"
                min_font_size = 8
                font_mult = 5
                
                
                tx1, ty1 = self.world_to_screen(bx, by, bz)
                tx2, ty2 = self.world_to_screen(ex, ey, ez)
                self.canvas.create_text(tx1, 
                                        ty1,
                                        text="x:{}\ny:{}\nz:{}".format(round(bx, deci), round(by, deci), round(bz, deci)),
                                        fill=color,
                                        font = ("Arial", round((1 - (bz - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                        tags=("gridlinelabels"))
                self.canvas.create_text(tx2, 
                                        ty2,
                                        text="x:{}\ny:{}\nz:{}".format(round(ex, deci), round(ey, deci), round(ez, deci)),
                                        fill=color,
                                        font = ("Arial", round((1 - (ez - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                        tags=("gridlinelabels"))
                                       
    def draw_projected_vertices(self):
        if len(self.vertices) > 0:
            
            self.canvas.delete("verts")
            
            self.vertex_listbox.delete(0, tk.END)
            deci = 2
            for i in range(0, len(self.vertices), 3):
                
                x, y, z = self.vertices[i], self.vertices[i + 1], self.vertices[i + 2]
                #print(int((i + 3)//3) - 1)
                
                rx, ry, rz = round(x, deci), round(y, deci), round(z, deci)
                
                vert_ind = ((i + 3)//3) - 1
                
                #self.vertex_listbox.delete(vert_ind)
                self.vertex_listbox.insert(vert_ind, "V{}-x:{}:y:{}:z:{}".format(vert_ind, rx, ry, rz))
                
                x, y = self.world_to_screen(x, y, z)
                
                if  self.vert_style_svar.get() == "Circle":
                    oval_size = (1 - (z - 1)/(self.far - self.near)) * self.z_max
                    self.canvas.create_oval(
                                    x - oval_size, 
                                    y - oval_size, 
                                    x + oval_size, 
                                    y + oval_size, 
                                    fill = self.vertex_color,
                                    tags=("verts")
                                    )
                elif self.vert_style_svar.get() == "Pixel":
                    oval_size = 0.5
                    self.canvas.create_oval(
                                    x - oval_size, 
                                    y - oval_size, 
                                    x + oval_size, 
                                    y + oval_size, 
                                    fill = self.vertex_color,
                                    tags=("verts")
                                    )
                elif self.vert_style_svar.get() == "Index":
                    deci = 2
                    min_font_size = 5
                    font_mult = 8
                    self.canvas.create_text(x, 
                                            y,
                                            text="V{}".format(vert_ind),
                                            fill = self.vertext_color,
                                            font = ("Arial", round((1 - (z - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                            tags=("verts")
                                            )
                elif self.vert_style_svar.get() == "None":
                    pass
                                      
    def draw_edge_lines(self):
        if len(self.edges) > 0 and len(self.vertices) > 1:
            self.canvas.delete("edgelines")
            for key in self.edges:
                if len(self.edges[key]) > 0:
                    x_ind_1 = key * 3 
                    y_ind_1 = x_ind_1 + 1
                    z_ind_1 = y_ind_1 + 1
                    vx1, vy1, vz1 = self.vertices[x_ind_1], self.vertices[y_ind_1], self.vertices[z_ind_1]
                    #v_ind_2 = v_ind_1
                    for ele in self.edges[key]:
                        x_ind_2 = ele * 3
                        y_ind_2 = x_ind_2 + 1
                        z_ind_2 = y_ind_2 + 1
                        vx2, vy2, vz2 = self.vertices[x_ind_2], self.vertices[y_ind_2], self.vertices[z_ind_2]
                        
                        sx1, sy1 = self.world_to_screen(vx1, vy1, vz1)
                        sx2, sy2 = self.world_to_screen(vx2, vy2, vz2)
                        
                        if self.edge_style_svar.get() == "Solid":
                            self.canvas.create_line(sx1, sy1, sx2, sy2,
                                                    fill=self.edge_color,
                                                    tags=("edgelines"))
                        elif self.edge_style_svar.get() == "Dotted":
                            self.canvas.create_line(sx1, sy1, sx2, sy2,
                                                    dash = (4, 1),
                                                    fill=self.edge_color,
                                                    tags=("edgelines"))
                        elif self.edge_style_svar.get() == "None":
                            pass
          
    def draw_faces(self):
        face_polygons = {}
        self.canvas.delete("facepolys")
        h = 0
        for key in self.faces_data:
            z_avg = round(self.faces_data[key][2] * 100, 3)
            face_polygons[z_avg] = []
            for i in range(len(self.faces_data[key][0])):
                cur_face_vert = self.faces_data[key][0][i]
                x, y, z = cur_face_vert[0], cur_face_vert[1], cur_face_vert[2] 
                x, y = self.world_to_screen(x, y, z)
                face_polygons[z_avg].append(x)
                face_polygons[z_avg].append(y)

            color = self.faces_data[key][1]
            face_polygons[z_avg].append(color)

        #sorting by z value
        face_polygons = {ind:face_polygons[ind] for ind in sorted(face_polygons)}

        for key in face_polygons:
            if face_polygons[key][-1] != "#FFFFFF":
                self.canvas.create_polygon(
                                            face_polygons[key][:-1], 
                                            fill = face_polygons[key][-1], 
                                            tags=("facepolys")
                                            )
            
        #print(face_polygons.keys(),"\n")
        #print(self.face_checklist,"\n")
        #print(self.faces,"\n")

    def draw_anchor(self):
        ax = float(self.anchor_x_spinbox.get())
        ay = float(self.anchor_y_spinbox.get())
        az = float(self.anchor_z_spinbox.get())  
        self.anchor_point[0] = ax
        self.anchor_point[1] = ay
        self.anchor_point[2] = az
        
        ax, ay = self.world_to_screen(ax, ay, az)
        #oval_size = (1 - (self.world_xyz[2] + 1)/(self.far - self.near)) * self.z_max
        oval_size = (1 - (az - 1)/(self.far - self.near)) * self.z_max
        self.canvas.delete("anchors")
        self.canvas.create_oval(
                        ax - oval_size, 
                        ay - oval_size, 
                        ax + oval_size, 
                        ay + oval_size, 
                        fill = "red",
                        tags=("anchors")
                        )      
                   
    def place_vertex(self, event):
        #if self.pressed == False:
            #x = self.canvas.canvasx(event.x)
            #y = self.canvas.canvasy(event.y)
            
            wx, wy, wz = self.world_xyz[0], self.world_xyz[1], self.world_xyz[2]
            
            self.vertices.append(wx)
            self.vertices.append(wy)
            self.vertices.append(wz)
            
            deci = 2
            rwx, rwy, rwz = round(wx, deci), round(wy, deci), round(wz, deci)
            
            total_verts = (len(self.vertices)//3) - 1
            
            self.vertex_listbox.insert(tk.END, "V{}-x:{}:y:{}:z:{}".format(total_verts, rwx, rwy, rwz))
            if len(self.vertices) > 0:
                
                x, y = self.world_to_screen(wx, wy, wz)
                
                #Vertex Styles
                if  self.vert_style_svar.get() == "Circle":
                    oval_size = (1 - (wz - 1)/(self.far - self.near)) * self.z_max
                    self.canvas.create_oval(
                                    x - oval_size, 
                                    y - oval_size, 
                                    x + oval_size, 
                                    y + oval_size, 
                                    fill = self.vertex_color,
                                    tags=("verts")
                                    )
                elif self.vert_style_svar.get() == "Pixel":
                    oval_size = 0.5
                    self.canvas.create_oval(
                                    x - oval_size, 
                                    y - oval_size, 
                                    x + oval_size, 
                                    y + oval_size, 
                                    fill = self.vertex_color,
                                    tags=("verts")
                                    )
                elif self.vert_style_svar.get() == "Index":
                    deci = 2
                    min_font_size = 5
                    font_mult = 8
                    self.canvas.create_text(x, 
                                            y,
                                            text="V{}".format((len(self.vertices) - 3)//3),
                                            fill = self.vertext_color,
                                            font = ("Arial", round((1 - (wz - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                            tags=("verts")
                                            )
                    
                elif self.vert_style_svar.get() == "None":
                    pass
                
                self.edges[total_verts] = []
                self.update_edge_checkbuttons()
                
                
                #print("New Vertex x:{}:y:{}:z:{}".format(rwx, rwy, rwz))
                #print(self.vertices)
        #self.pressed = True
    
    #VERTEX BUTTON METHODS

    def destroy_vertex(self, v_ind):

        x_ind = v_ind * 3 
        y_ind = x_ind + 1
        z_ind = y_ind + 1
        
        self.vertices.pop(z_ind)
        self.vertices.pop(y_ind)
        self.vertices.pop(x_ind)
        self.vertex_listbox.delete(v_ind)
        
        #updating the edges list
        #self.edges is an adjcency list
        
        #print("remove vert")
        #getting rid of the deleted vertex in the dictionary
        self.edges.pop(v_ind)
        #self.edge_options.pop(v_ind)
        dict_new = {}
        if self.edge_ind >= v_ind:
            self.edge_ind = 0
    
        for key in self.edges:
            #getting rid of the deleted vertex in the vertex's array
            if v_ind in self.edges[key]:
                self.edges[key].remove(v_ind)
                #self.edge_options[key].pop(v_ind)
            #reorganizing the dictionary with updated indexes to reflect deletion
            for i in range(len(self.edges[key])):
                if self.edges[key][i] > v_ind:
                    self.edges[key][i] = self.edges[key][i] - 1
            #for child in self.edge_options[key]:
            #    if child > v_ind:
            #        child = child - 1
                
            #filling the replacement dictionary
        
            if key > v_ind:
                #print('ye')
                new_key = key - 1
                dict_new[new_key] = self.edges[key]
            else:
                #print('ne')
                dict_new[key] = self.edges[key]
                
            
                
                
        self.edges = dict_new    
            
        self.update_edge_checkbuttons()
                        
        self.draw_projected_vertices()
        self.draw_edge_lines()
        #print(self.vertices)
    
    def delete_vertex(self):
        #deletes the last vertex in the vertex listbox
        v_ind = self.vertex_listbox.size() - 1
        if len(self.vertices) > 0 and v_ind > 0:
            self.destroy_vertex(v_ind)

    def remove_vertex(self):
        #deleted any vertex in the vertex listbox
        v_lb_sc = self.vertex_listbox.curselection()
        if len(self.vertices) > 0 and len(v_lb_sc) > 0:
            v_ind = v_lb_sc[0]
            self.destroy_vertex(v_ind)
                          
    def clear_vertices(self):
        self.canvas.delete("verts")    
        self.vertex_listbox.delete(0, tk.END)
        self.vertices.clear()
        
        self.canvas.delete("edgelines")
        self.edges.clear()
        self.edge_ind = 0
        self.edge_canvas.delete("all")
        self.edge_canvas.create_window((0, 0), window=self.edge_scrl_frame, anchor="nw")
        self.edge_options.clear()
        if len(self.edge_checklist) > 0:
            for ele in self.edge_checklist:
                var = ele[0]
                chk = ele[1]
                if isinstance(chk, tk.Checkbutton):
                    var.set(False)
                    self.delete_widget(chk)
                
        self.edge_checklist.clear()

        self.canvas.delete("facepolys")
        self.faces.clear()
        self.faces_data.clear()
        
        self.face_canvas.delete("all")
        self.face_canvas.create_window((0, 0), window=self.face_scrl_frame, anchor="nw")
        if len(self.face_checklist) > 0:
                for ele in self.face_checklist:
                    var = ele[0]
                    chk = ele[1]
                    if isinstance(chk, tk.Checkbutton):
                        var.set(False)
                        self.delete_widget(chk)
                    
        self.face_checklist.clear()


        #self.update_edge_checkbuttons()
        
    def select_vertex(self):
        #selects a specific vertex for edge connecting
        v_lb_sc = self.vertex_listbox.curselection()
        if len(self.vertices) > 0 and len(v_lb_sc) > 0:
            self.edge_ind = v_lb_sc[0]
            #self.next_vertex()
            self.update_edge_checkbuttons()
    
    def vertex_color_chooser(self):
        color_code = colorchooser.askcolor(title ="Choose color")[1]
        self.vertex_color = color_code
        #print(self.faces_data)
        self.vertex_color_button.config(bg=color_code)
        self.update_viewport()

    def vertext_color_chooser(self):
        color_code = colorchooser.askcolor(title ="Choose color")[1]
        self.vertext_color = color_code
        #print(self.faces_data)
        self.vertext_color_button.config(bg=color_code)
        self.update_viewport()


    #EDGE BUTTONS METHODS 

    def create_edge_checkbuttons(self):
        #dynamically creating checkboxes for edges
        if len(self.edge_checklist) > 0:
            for ele in self.edge_checklist:
                var = ele[0]
                chk = ele[1]
                if isinstance(chk, tk.Checkbutton):
                    var.set(False)
                    self.delete_widget(chk)
                
        self.edge_checklist.clear()
        
        i = 0
        
        for key in self.edge_options[self.edge_ind]:
            if key != self.edge_ind:
                txt = "Vertex:" + str(key)
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.edge_scrl_frame, 
                                    text=txt, 
                                    variable=var,
                                    command=self.connect_vertices,
                                    onvalue=True,
                                    offvalue=False
                                    
                                    )
                
                var.set(self.edge_options[self.edge_ind][key])
                
                parent = self.edge_ind
                child = key
                
                self.edge_checklist.append([var, chk, parent, child])
                chk.grid(row=i, column=1)
                
                i = i + 1

    def update_edge_checkbuttons(self):
        if len(self.vertices) >= 3:
            #print("update edges")
            #updating the edge checkbuttons
            if len(self.vertices) == 0:
                self.edge_label.config(text="Vertex:? - Edges")
            
            #self.edge_options = {} 
            #below keeps track for the dynamic checkboxes generated
            #will be the edges and whether they're connected tp other edges, 
            # a dictionary of dictionarys and bools 
            
            self.edge_keys_ls = self.edges.keys()
            self.edge_canvas.delete("all")
            self.edge_canvas.create_window((0, 0), window=self.edge_scrl_frame, anchor="nw")
            self.edge_options.clear()
            self.edge_keys_ls = self.edges.keys()
            
            for key in self.edges:
                #rewriting edges
                self.edge_options[key] = {}
                for ele in self.edge_keys_ls:
                    if key != ele:
                        if ele in self.edges[key]:
                            self.edge_options[key][ele] = True
                        else:
                            self.edge_options[key][ele] = False


            self.edge_label.config(text="Vertex:" + f"{self.edge_ind} - Edges")

            self.create_edge_checkbuttons()      
            self.create_faces_from_edges()

    def connect_vertices(self):
        if len(self.vertices) > 3:
            #print("yep")
            if len(self.edge_checklist) > 0:
                for ele in self.edge_checklist:
                    var = ele[0]
                    chk = ele[1]
                    parent = ele[2]
                    child = ele[3]
                    
                    booln = var.get()
                    
                    if isinstance(chk, tk.Checkbutton):
                        self.edge_options[parent][child] = booln
                        self.edge_options[child][parent] = booln
                        #print(parent, child)

            
            for parent in self.edge_options:
                for child in self.edge_options[parent]:
                    if self.edge_options[parent][child] == True:
                        
                        #if self.edges.get(child):
                        
                        if child not in self.edges[parent]:
                            self.edges[parent].append(child)
                        if parent not in self.edges[child]:
                            self.edges[child].append(parent)
                     
                    else:
                        #if self.edges.get(parent):
                        if child in self.edges[parent]:
                            self.edges[parent].remove(child)
                            #self.edges[child].remove(parent)
                        if parent in self.edges[child]:
                            self.edges[child].remove(parent)
            #print(self.edges)
            #print(self.edge_options)   
                    
            self.create_faces_from_edges()            
            self.draw_edge_lines()    
  
    def next_vertex(self):
        #self.edge_label = ttk.Label(self, text="Vertex:? - Edges")
        if len(self.vertices) > 3:
            '''
            self.edge_keys_ls = None #self.edges.keys()
            self.edge_options = None #will be the edges and whether they're connected tp other edges, a dictionary of dictionarys and bools 
            
            '''
            self.edge_ind += 1
            if len(self.edge_keys_ls) - self.edge_ind == 0:
                self.edge_ind = 0
            self.edge_label.config(text="Vertex:" + f"{self.edge_ind} - Edges")

            self.create_edge_checkbuttons()
            
    def prev_vertex(self):
        #self.edge_label = ttk.Label(self, text="Vertex:? - Edges")
        if len(self.vertices) > 3:
            
            self.edge_ind -= 1
            if self.edge_ind < 0:
                self.edge_ind = (len(self.edge_keys_ls) - 1) 
            self.edge_label.config(text="Vertex:" + f"{self.edge_ind} - Edges")
            
            '''
            #Test
            options = ["Option " + str(i) for i in range(1,50)]
            i = 0
            for option in options:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.edge_scrl_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
                i += 1
            '''
            self.create_edge_checkbuttons()
            
    def edge_color_chooser(self):
        color_code = colorchooser.askcolor(title ="Choose color")[1]
        self.edge_color = color_code
        #print(self.faces_data)
        self.edge_color_button.config(bg=color_code)
        self.update_viewport()

    #FACE MANAGEMENT

    def update_faces_data(self):
        for key in self.faces_data:
            face_vert_ind = list(map(int, key.split('-')))
            z_avg = 0
            for i in range(len(self.faces_data[key][0])):
                x_ind = face_vert_ind[i] * 3
                y_ind = x_ind + 1
                z_ind = y_ind + 1

                cur_face_vert = self.faces_data[key][0][i]
                cur_face_vert[0] = self.vertices[x_ind]
                cur_face_vert[1] = self.vertices[y_ind]
                cur_face_vert[2] = self.vertices[z_ind]

                z_avg = z_avg + self.vertices[z_ind]

            z_avg = z_avg/len(face_vert_ind)
            self.faces_data[key][2] = z_avg

    def dfs(self, graph, start, end):
        fringe = [(start, [])]
        while fringe:
            state, path = fringe.pop()
            if path and state == end:
                yield path
                continue
            for next_state in graph[state]:
                if next_state in path:
                    continue
                fringe.append((next_state, path+[next_state]))
            
    def get_cycles(self, graph):
        #https://stackoverflow.com/questions/40833612/find-all-cycles-in-a-graph-implementation
        #https://yuminlee2.medium.com/detect-cycle-in-a-graph-4461b6000845
        #without the conditional it would count 0-1 as a cycle
        #with it it limits cycles to triangles and above 
        cycles = [[node]+path  for node in graph for path in self.dfs(graph, node, node) if len([node]+path) > 3]
        #print("unclean cycles")
        #print(cycles, len(cycles))
        #print("Cycle clean")
        c_cycles = []
        for cycle in cycles.copy():
            #first and last ele are the same
            last = cycle.pop()
            cycle = sorted(cycle)
            if cycle not in c_cycles:
                c_cycles.append(cycle)
            
        #print(c_cycles)
        #print(graph)
        return c_cycles

    def adj_list_tris(self, graph):
        triangles = []
        for key in graph:
            if len(graph[key]) > 1:
                #tris = []
                for i in range(len(graph[key]) - 1):
                    
                    a = sorted([key, graph[key][i], graph[key][ i + 1]])
                    #a = [key, graph[key][i], graph[key][ i + 1]]
                    if a not in triangles:
                        triangles.append(a)
        return triangles

    def create_faces_from_edges(self):
        edge_connect_count = sum([len(self.edges[key]) for key in self.edges])
        #print(edge_connect_count)
        if edge_connect_count >= 6:
            self.faces.clear()
            self.faces_data.clear()
            #self.faces_polygons.clear()
            #faces is a list of triangles from the edge adjcency list 
            self.faces = self.adj_list_tris(self.edges) #self.get_cycles(self.edges)
            #
            
            #print(face_colors_keys)
            #f_copy = face_colors_keys.copy()
            for face in self.faces:
                key = "-".join(list(map(str, face)))
                self.faces_data[key] = [[]]
                z_avg = 0
                for vertex in face:
                    x_ind = vertex * 3
                    y_ind = x_ind + 1
                    z_ind = y_ind + 1
                    x, y, z  = self.vertices[x_ind], self.vertices[y_ind] , self.vertices[z_ind] 
                    z_avg = z_avg + z
                    self.faces_data[key][0].append([x, y, z])

                z_avg= z_avg/len(face)
                #data in face data is arranged in a list containing
                # faces vertex coords lists [0] 
                # color [1] 
                # z_average of the face [2] 

                self.faces_data[key].append("#FFFFFF")
                self.faces_data[key].append(z_avg)
                

                                
            #print(self.faces_data.keys())
       
            
            #dynamically creating checkboxes for faces
            if len(self.face_checklist) > 0:
                for ele in self.face_checklist:
                    var = ele[0]
                    chk = ele[1]
                    if isinstance(chk, tk.Checkbutton):
                        var.set(False)
                        self.delete_widget(chk)
                    
            self.face_checklist.clear()
            
            
            i = 0
            
            for key in self.faces_data:
                #if key != self.edge_ind:
                txt = "Face:" + key
                var = tk.BooleanVar()
                is_checked = False
                chk = tk.Checkbutton(self.face_scrl_frame, 
                                    text=txt, 
                                    variable=var,
                                    #face color choosers
                                    command=self.face_color_chooser,
                                    onvalue=True,
                                    offvalue=False
                                    
                                    )
                
                
                var.set(False)
                
                self.face_checklist.append([var, chk, key, is_checked])
                chk.grid(row=i, column=1, sticky="W")

                i = i + 1

    def face_color_chooser(self):
        changed_cb = None
        changed_key = None
        changed_bool = None
        for data in self.face_checklist:
            #print(data)
        
            
            var = data[0]
            chk = data[1]
            key = data[2]
            is_chkd = data[3]

            #self.faces_data[key][2]
            booln = var.get()
            
            if booln and not is_chkd:
                changed_cb = chk
                changed_key = key
                changed_bool = booln
                data[3] = booln
                #print("neh")
            elif not booln and is_chkd:
                data[3] =  False
                changed_bool = data[3]
                
                #print('ye')
                changed_key = key
                changed_cb = chk
               
    
        if isinstance(changed_cb, tk.Checkbutton) and changed_bool == True and changed_key != None:  
            color_code = colorchooser.askcolor(title ="Choose color")[1]
            self.faces_data[changed_key][1] = color_code
            #print(self.faces_data)
            changed_cb.config(selectcolor=color_code)
            
        elif isinstance(changed_cb, tk.Checkbutton) and changed_bool == False: 
            #print("hmph")
            changed_cb.config(selectcolor="#FFFFFF")
            self.faces_data[changed_key][1] = "#FFFFFF"
        #print(checkboxes)    

        self.draw_faces()       

    def N_gon_collision(self, coord_arr):
        #https://www.jeffreythompson.org/collision-detection/poly-point.php
        collision = False
        #px, py = self.world_to_screen(px, py, self.world_xyz[2])
        #px, py = self.screen_xy[0], self.screen_xy[1]
        px, py = self.world_xyz[0], self.world_xyz[1]
        for v_ind in range(len(coord_arr)):
            
            nxt = 0 if v_ind + 1 > len(coord_arr) - 1 else v_ind + 1

            cur_coords = coord_arr[v_ind]
            
            cx = cur_coords[0]
            cy = cur_coords[1]
            cz = cur_coords[2]
            #cx, cy = self.world_to_screen(cx, cy, cz)

            nxt_coords = coord_arr[nxt]
            nx = nxt_coords[0]
            ny = nxt_coords[1]
            nz = nxt_coords[2]
            #nx, ny = self.world_to_screen(nx, ny, nz)

            #print(cur_coords)
            bool_1 = cy >= py and ny < py
            bool_2 = cy < py and ny >= py
            bool_3 = px < ((nx - cx) * (py - cy) / (ny - cy)) + cx

            if  ((cy >= py and ny < py) or (cy < py and ny >= py)) and  px < ((nx - cx) * (py - cy) / (ny - cy)) + cx:
                collision = not collision

        return collision

    def DDA_raycast_3D(self):#, x0, y0, z0, x1, y1, z1, precision):
        
        dz = self.far - self.near
        precision = 100
        
        z_inc = dz/100
        print(z_inc)

        z = self.near
        #print(x, y, z)
        print("Near:{}\n".format(self.near), "Far:{}".format(self.far))
        print("X:{} Y:{}".format(self.screen_xy[0], self.screen_xy[1]))
        prev_z = z
        print(self.world_xyz)
        print(self.screen_xy)
        while z > self.far:
            #print(z)
            #this is getting more negative as the far plane is negative -1 and the near plane is 1
            z += z_inc
            collided = False

            for key in self.faces_data:
                
                z_avg = self.faces_data[key][2] 
                face_vertices = self.faces_data[key][0]
                collided = self.N_gon_collision(face_vertices)
                #print(z_avg)
                if collided:
                    print(key, self.faces_data[key], self.world_xyz[0], self.world_xyz[1], " collision")
                    color_code = colorchooser.askcolor(title ="Choose color")[1]
                    self.faces_data[key][1] = color_code
                    for data in self.face_checklist:
                        #print(data) 
                        var = data[0]
                        chk = data[1]
                        k = data[2]
                        is_chkd = data[3]
                        if k == key:
                            data[3] = True
                            data[1].config(selectcolor=color_code)
                            data[0].set(True)
                            self.draw_faces()
                            return

                    return



            prev_z = z
        
        print("no collision")

    def print_vertices(self):
        #old debugger
        if False:
            print()
            for i in range(0, len(self.vertices), 3):
                print("Vertex {} X:{} Y:{} Z:{}".format(i/3, self.vertices[i], self.vertices[i + 1], self.vertices[i + 2]))
            print()

    def hex_to_rbg(self, hex_color):
        hex_color = hex_color.lstrip('#')
        arr = []
        for i in (0, 2, 4):
            arr.append(int(hex_color[i:i+2], 16))
        #alpha value
        arr.append(255)
        return arr

    

    
if __name__ == "__main__":
    app = App()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()



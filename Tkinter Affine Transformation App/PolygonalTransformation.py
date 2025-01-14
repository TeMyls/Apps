import tkinter as tk

from TP2D import *
from TP3D import *


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
            
            


    
if __name__ == "__main__":
    app = App()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()



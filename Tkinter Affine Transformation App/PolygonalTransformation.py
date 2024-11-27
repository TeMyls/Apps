import tkinter as tk
from TP2D import *
from TP3D import *


class App(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Polygon Transform App") 
        
        self.undo_button = tk.Button(self, text = "undo")
        self.redo_button = tk.Button(self, text = "redo")
        self.undo_button.grid(row=0,column=0)
        self.redo_button.grid(row=0,column=1)
        
        '''
        self.t2d_poly = TransformPolygon2D(self, 500, 400)
        self.t2d_poly.grid(row=1,column=2)
        
        self.bind("<Control-z>", self.t2d_poly.undo)
        self.bind("<Control-y>", self.t2d_poly.redo)
        
        
        self.undo_button.config(command=self.t2d_poly.undo)
        self.redo_button.config(command=self.t2d_poly.redo)
        '''
        
        
        
        #https://tkdocs.com/tutorial/menus.html
        #https://www.geeksforgeeks.org/python-menu-widget-in-tkinter/
        #https://pythonassets.com/posts/menubar-in-tk-tkinter/
        # Creating Menubar 
        self.menubar = tk.Menu(self) 
       
        
        # Adding Settings and commands 
        self.settings_menu = tk.Menu(self.menubar, tearoff =False)  
        self.mode_menu = tk.Menu(self.menubar, tearoff = False)
        self.mode_type = tk.IntVar()
        self.mode_type.set(1)
        self.mode_menu.add_radiobutton(
            label = "2D",
            variable=self.mode_type,
            value = 1,
            command=None
            
        )
        self.mode_menu.add_radiobutton(
            label = "3D",
            variable=self.mode_type,
            value = 2,
            command=None
            
        )
        
        

        
        # Menu Placement
        
        self.menubar.add_cascade(label ='Mode', menu = self.settings_menu) 
        self.settings_menu.add_cascade(label="2D or 3D", menu=self.mode_menu)
        
        
        
        # display Menu 
        self.config(menu = self.menubar) 
        
        
        
        
        
        
        #self.main_canvas = MainCanvas(self)
        #self.main_canvas.grid()
        
        
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
    

    
    
if __name__ == "__main__":
    app = App()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()
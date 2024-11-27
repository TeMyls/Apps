import tkinter as tk
from tkinter import ttk
from MatrixMath import *

class TransformPolyhedron3d(ttk.Frame):
    def __init__(self, parent, c_width, c_height,  *args, **kwargs):
        super().__init__(parent)
        
        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        
        self.undo_stack = []
        self.redo_queue = []
        
        
        self.poly_points = []
        
        self.canvas.bind("<ButtonPress-3>", self.clear_points)
        self.canvas.bind("<ButtonPress-1>", self.place_point)  
        self.canvas.bind("<MouseWheel>", None)  
        
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
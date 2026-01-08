import tkinter as tk
from tkinter import ttk
from WidgetUtils import *

# Modified version of the class in 
# https://blog.teclado.com/tkinter-scrollable-frames/
class ScrollableFrame(ttk.Frame):
    # ScrollableFrame
        # ScrollableFrame is a class that acts as a container for various Tkinter Widgets, both the original widgets and user created widgets
        # Parameters
        #   has_vertical: A boolean that enables a vertical scrollable frame, adding or removing widgets to rows, enables a vertical scrollbar
        #   has_horizontal: A boolean that enables a horizontal scrollable frame, adding or removing widgets to columns, enables a horizontal scrollbar
        #   is_column_wise: only works if both has_vertical and has_horizontal are true, adds widgets by column until the limit is reached if it's false it adds by row
        #   wrap_limit: only works if both has_vertical and has_horizontal are true, only lets a widget have a specified number of rows or columns in a grid
            
        # Methods
        # add_widget: adds a widget to the widget list
        #   Parameters
        #       idx: an integer, the index where a widget is mean't to be added to the list attribute -widget_list-
        # remove_widget: removes a widget from the widget list
        #   Parameters
        #       idx: the index where a widget is mean't to be removed to the list attribute -widget_list-, it does delete the widget itself
        # update_frame: updates an individual widget in the grid arrangement 
        #   Parameters
        #       idx: the index where an individual widget is mean't to be gridded onto the frame in a sequence, the order it does so 
        #           is dependent on the initial parameters of the class itself
        # update_grid_frame: updates the placement of every widget in widget list
        # Parameters
        #       None
        # set_wrap_limit: updates the placement of every widget in widget list
        # Parameters
        #       wrap_limit: lets a widget have a specified number of rows or columns in a grid, this changes the internal attribute 
        # 
        # Note: neither add_widget, remove_widget, or set_wrap_limit, visually update the frame. That is left to update_frame, and update_grid, frame

    def __init__(self, parent, has_vertical: bool, has_horizontal: bool, is_column_wise: bool, wrap_limit: int):
        super().__init__(parent)
        self.canvas_color = "#2F2F28"
        self.canvas = tk.Canvas(self, bg=self.canvas_color)
        self.vertical_sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.horizontal_sb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.vertical_sb.set)
        self.canvas.configure(xscrollcommand=self.horizontal_sb.set)


        if has_vertical:
            self.vertical_sb.pack(side="right", fill="y")
        if has_horizontal:
            self.horizontal_sb.pack(side="bottom", fill="x")
        self.canvas.pack(side="top", fill="both", expand=True)

        

        self.has_horizontal = has_horizontal
        self.has_vertical = has_vertical
        self.is_column_wise = is_column_wise
        self.wrap_limit = wrap_limit

        
        self.widget_list = []
  

    # My additions

    
    def add_widget(self, widget, idx: int):
        

        if idx < 0 or idx > len(self.widget_list):
            return

        if not self.has_horizontal and not self.has_vertical:
            return

        if self.widget_list:
            if widget not in self.widget_list:  
                #abs(idx % len(self.widget_list))
                self.widget_list.insert(idx, widget)
                
        else:
            if widget not in self.widget_list:  
                self.widget_list.append(widget)

        #self.widget_list.reverse()
        #print(self.widget_list)


    def remove_widget(self, idx: int):

        if not self.widget_list:
            return 
        
        if idx < 0 or idx > len(self.widget_list):
            return
        
        #idx = abs(idx % len(self.widget_list))
        widget = self.widget_list.pop(idx)
        delete_widget(widget)

        
        if len(self.widget_list) == 0:
            self.canvas.delete("all")
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.config(bg=self.canvas_color)

    def update_frame(self, idx: int):
        if self.has_vertical and self.has_horizontal:
            if self.is_column_wise:
                self.widget_list[idx].grid(row=idx//self.wrap_limit, column=idx % self.wrap_limit)
            else:
                self.widget_list[idx].grid(row=idx % self.wrap_limit, column=idx//self.wrap_limit)
        elif self.has_vertical:
            self.widget_list[idx].grid(row=idx, column=0)
        elif self.has_horizontal:
            self.widget_list[idx].grid(row=0, column=idx)
        else:
            self.canvas.delete("all")
        

    def update_grid_frame(self):
        for i in range(len(self.widget_list)):
            self.update_frame(i)

    def set_wrap_limit(self, wrap_limit):
        if self.has_vertical and self.has_horizontal:
            if self.wrap_limit > -1:
                self.wrap_limit = wrap_limit





    







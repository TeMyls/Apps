import tkinter as tk
from tkinter import ttk
from WidgetUtils import *
from Tool_tip import *
from Scrollable_Frame import *
import math

def angle_to(x1, y1, x2, y2):
    #in radians
    return math.atan2(y2 - y1, x2 - x1)

def distance_to(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    s = dx * dx + dy * dy
    return math.sqrt(s)

def in_bounds(x, y, w, h):
    return -1 < x < w and -1 < y < h

def clamp(x, lower, upper):
  if x < lower:
    return lower
  elif x > upper:
    return upper
  else:
    return x
  

def lerp(a, b, amount):
  return a + (b - a) * clamp(amount, 0, 1)

class TK_Tick(tk.Frame):
    def __init__(self, parent, c_width, c_height):
        super().__init__(parent)

     
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        # Main Frames
        #self.left_frame = tk.Frame(self)
        self.full_frame = tk.Frame(self)
        self.top_right_frame = tk.Frame(self.full_frame)
        self.bottom_right_frame = tk.Frame(self.full_frame)


        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        self.timer_width = 300
        self.timer_height = 300

        self.test_sf = ScrollableFrame(
                            self.top_right_frame,

                            #   has_vertical: A boolean that enables a vertical scrollable frame, adding or removing widgets to rows, enables a vertical scrollbar
                            False, 
                            #   has_horizontal: A boolean that enables a horizontal scrollable frame, adding or removing widgets to columns, enables a horizontal scrollbar
                            True,
                            #   is_column_wise: only works if both has_vertical and has_horizontal are true, adds widgets by column until the limit is reached if it's false it adds by row
                            True,
                            #   wrap_limit: only works if both has_vertical and has_horizontal are true, only lets a widget have a specified number of rows or columns in a grid
                            5
        )

        self.widget_control_frame = tk.Frame(self.bottom_right_frame)

        self.add_img = tk.PhotoImage(file="icons\\add_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.add_btn = tk.Button(
                                self.widget_control_frame,
                                image=self.add_img,
                                command=self.add_sf_widget,
                                
                                )
        CreateToolTip(self.add_btn, "Add New Timers")

        self.delete_img = tk.PhotoImage(file="icons\\delete_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.delete_btn = tk.Button(
                                    self.widget_control_frame,
                                    image=self.delete_img,
                                    command=self.delete_sf_widget,
        )
        CreateToolTip(self.delete_btn, "Delete Timers")


        btn_arrangement = [
            [self.add_btn, self.delete_btn]
        ]

        arrange_widgets(btn_arrangement, "SE")
        
        
        # main frames
        self.bottom_right_frame.pack(side="bottom", anchor="s", fill="x")
        #self.left_frame.pack(side="left", anchor="n")
        self.full_frame.pack(side="right", anchor="e", fill="both", expand=True)
        self.top_right_frame.pack(side="top", anchor="n", fill="both", expand=True)
       

        # inner frames
        self.widget_control_frame.pack(side="bottom", anchor="se")
        self.test_sf.pack(side="top", anchor="n", fill="both", expand=True)
        self.test_sf.bind("<Configure>", self.on_frame_resize)
        #self.select_mode(self.timer_btn)

    def on_frame_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        self.frame_height = event.height
        self.frame_width = event.width
        # with this commented out the wrap order specified in initialization will take effect normally
        # it's for widgets of a specified size 
        #if self.test_sf.widget_list:
        #    self.change_grid_order()
      
    def change_grid_order(self):
        print(self.test_sf.widget_list[0]["width"] )
        self.test_sf.set_wrap_limit(clamp(round(self.test_sf.widget_list[0]["width"]/self.timer_width), 1, 100))
        self.test_sf.update_grid_frame()

    def add_sf_widget(self):

        
        len_str = str(len(self.test_sf.widget_list))
        button_to_test_scrollable_frame = tk.Button(
                        self.test_sf.scrollable_frame, 
                        text=f"Button:{len_str}",
                        # Note: this value isn't in Pixels it's in Text Characters
                        width = 8,
                        height = 1
                    )
        button_to_test_scrollable_frame.config(command=lambda:print(f"Button:{len_str}"))
        
        self.test_sf.add_widget(
                        button_to_test_scrollable_frame,
                        len(self.test_sf.widget_list)
                    )

        self.test_sf.update_frame(len(self.test_sf.widget_list) - 1)
        #self.test_sf.update_grid_frame()

    def delete_sf_widget(self):
        self.test_sf.remove_widget(
            len(self.test_sf.widget_list) - 1
        )


        #self.test_sf.update_grid_frame()



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        time = TK_Tick(self, 300, 300)
        time.pack(side="top", fill="both", expand=True)
        
    
        

               

if __name__ == "__main__":



    app = App()
    
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    app.title("TK Tick")
    app.resizable()
    app.mainloop()
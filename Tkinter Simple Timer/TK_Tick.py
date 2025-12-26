import tkinter as tk
from tkinter import ttk
from WidgetUtils import *
from Tool_tip import *
from TimerWidget import Timer 
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

        self.frame_width = c_width
        self.frame_height = c_height
        #the reason this has an underscore is to 
        self.canvas_color = "#3A3A3A"
        self.mode = ""

        self.canvas = tk.Canvas(self, 
                                width=c_width,
                                height=c_height, 
                                bg=self.canvas_color)

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        # Main Frames
        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)
        self.top_right_frame = tk.Frame(self.right_frame)
        self.bottom_right_frame = tk.Frame(self.right_frame)

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        # Mode Buttons
        self.alarm_img = tk.PhotoImage(file="icons\\alarm_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.alarm_btn = tk.Button(
                                self.left_frame,
                                image=self.alarm_img,
                               #command=self.add_timer,
                                text="Alarm"
                                )
        CreateToolTip(self.alarm_btn, "Alarm")

        self.timer_img = tk.PhotoImage(file="icons\\hourglass_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.timer_btn = tk.Button(
                                    self.left_frame,
                                    image=self.timer_img,
                                    #command=self.delete_timer,
                                    text="Timer"
        )
        CreateToolTip(self.timer_btn, "Timer")

        self.stopwatch_img = tk.PhotoImage(file="icons\\timer_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.stopwatch_btn = tk.Button(
                                    self.left_frame,
                                    image=self.stopwatch_img,
                                    #command=self.delete_timer,
                                    text="Stopwatch"
        )
        CreateToolTip(self.stopwatch_btn, "Stopwatch")

        self.alarm_btn.config(command=lambda:self.select_mode(self.alarm_btn))
        self.timer_btn.config(command=lambda:self.select_mode(self.timer_btn))
        self.stopwatch_btn.config(command=lambda:self.select_mode(self.stopwatch_btn))

        self.option_widgets = [
            self.alarm_btn, self.timer_btn, self.stopwatch_btn
        ]

        options_arrangement = [
            [self.alarm_btn],
            [self.timer_btn],
            [self.stopwatch_btn],
        ]

        arrange_widgets(options_arrangement, "N")
        '''
        self.place_img = tk.PhotoImage(file="icons\\add_circle_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.place_btn = tk.Button(self.btn_frame, 
                                 text="Place", 
                                 image=self.place_img,
                                 ) 
        CreateToolTip(self.place_btn, "Place\nRMB:Preview Vertex\nLMB:Place Vertex\nScroll:Set Depth")
        '''
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        self.timer_width = 300
        self.timer_height = 300

        self.timer_frame = ScrollableFrame(
                                        self.top_right_frame,
                                        True, 
                                        True,
                                        True,
                                        3
                                           )

        self.timer_btn_frame = tk.Frame(self.bottom_right_frame)

        self.add_img = tk.PhotoImage(file="icons\\add_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.add_btn = tk.Button(
                                self.timer_btn_frame,
                                image=self.add_img,
                                command=self.add_timer,
                                
                                )
        CreateToolTip(self.add_btn, "Add New Timers")

        self.delete_img = tk.PhotoImage(file="icons\\delete_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.delete_btn = tk.Button(
                                    self.timer_btn_frame,
                                    image=self.delete_img,
                                    command=self.delete_timer,
        )
        CreateToolTip(self.delete_btn, "Delete Timers")


        btn_arrangement = [
            [self.add_btn, self.delete_btn]
        ]

        arrange_widgets(btn_arrangement, "SE")
        
        
        # main frames
        self.bottom_right_frame.pack(side="bottom", anchor="s", fill="x")
        self.left_frame.pack(side="left", anchor="n")
        self.right_frame.pack(side="right", anchor="e", fill="both", expand=True)
        self.top_right_frame.pack(side="top", anchor="n", fill="both", expand=True)
       

        # inner frames
        self.timer_btn_frame.pack(side="bottom", anchor="se")
        self.timer_frame.pack(side="top", anchor="n", fill="both", expand=True)
        self.timer_frame.bind("<Configure>", self.on_frame_resize)
        self.select_mode(self.timer_btn)

    def on_frame_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        self.frame_height = event.height
        self.frame_width = event.width
        # with this commented out the wrap order specified in initialization will take effect normally 
        #self.change_grid_order()
      
    def change_grid_order(self):
        self.timer_frame.set_wrap_limit(clamp(round(self.frame_width/self.timer_width), 1, 100))
        self.timer_frame.update_grid_frame()

    def add_timer(self):
        timer = Timer(
                        self.timer_frame.scrollable_frame, 
                        self.timer_width,
                        self.timer_height
                    )
        
        
        len_str = str(len(self.timer_frame.widget_list))
        button_to_test_scrollable_frame = tk.Button(
                        self.timer_frame.scrollable_frame, 
                        text=f"Button:{len_str}"
                    )
        button_to_test_scrollable_frame.config(command=lambda:print(f"Button:{len_str}"))
        
        self.timer_frame.add_widget(
                        button_to_test_scrollable_frame,
                        len(self.timer_frame.widget_list)
                    )

        self.timer_frame.update_frame(len(self.timer_frame.widget_list) - 1)
        #self.timer_frame.update_grid_frame()

    def delete_timer(self):
        self.timer_frame.remove_widget(
            len(self.timer_frame.widget_list) - 1
        )


        #self.timer_frame.update_grid_frame()

    def select_mode(self, clicked_widget):
        
        for widget in self.option_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
                
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")

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
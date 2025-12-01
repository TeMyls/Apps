import tkinter as tk
from tkinter import ttk
from WidgetUtils import *
from Tool_tip import *
import math
from playsound import playsound

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


class Timer(ttk.Frame):
    def __init__(self, parent, c_width, c_height):
        super().__init__(parent)
        #the color selection palette



        self.canvas_width = c_width
        self.canvas_height = c_height
        #the reason this has an underscore is to 
        self.canvas_color = "#808080"
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #The main canvas
        self.full_frame = tk.Frame(self) 

        self.upper_frame = tk.Frame(self.full_frame)

        self.hour_frame = tk.Frame(self.upper_frame)
        self.minute_frame = tk.Frame(self.upper_frame)
        self.second_frame = tk.Frame(self.upper_frame)

        self.lower_frame =  tk.Frame(self.full_frame)

        self.canvas = tk.Canvas(self.lower_frame, 
                                width=c_width,
                                height=c_height, 
                                bg=self.canvas_color)
        

        #self.canvas.bind("<Configure>", self.on_canvas_resize)
        #self.canvas.create_arc()

        self.play_img = tk.PhotoImage(file="icons\\play_arrow_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4, 4)
        self.playing = False
        self.play_btn = tk.Button(self.upper_frame, text="Start", image=self.play_img, command=self.start_timer) 
        CreateToolTip(self.play_btn, "Start")

        self.replay_img = tk.PhotoImage(file="icons\\replay_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4, 4)
        #self.playing = False
        self.replay_btn = tk.Button(self.upper_frame, text="Reset", image=self.replay_img, command=self.restart_timer) 
        CreateToolTip(self.replay_btn, "Reset")

        self.hour_lbl = tk.Label(self.hour_frame, text="Hours")
        self.minute_lbl = tk.Label(self.minute_frame, text="Min")
        self.second_lbl = tk.Label(self.second_frame, text="Sec")

        ent_width = 8
        self.hour_ent = tk.Entry(self.hour_frame, text="Hours", width=ent_width)
        self.minute_ent = tk.Entry(self.minute_frame, text="Min", width=ent_width)
        self.second_ent = tk.Entry(self.second_frame, text="Sec", width=ent_width)
        
        

        # the hour frame order
        self.hour_lbl.pack()
        self.hour_ent.pack()

        # the minute frame order
        self.minute_lbl.pack()
        self.minute_ent.pack()

        # the second frame order
        self.second_lbl.pack()
        self.second_ent.pack()

        
        # the upper frame order
        self.play_btn.pack(side="left")
        self.replay_btn.pack(side="left")
        self.hour_frame.pack(side="left")
        self.minute_frame.pack(side="left")
        self.second_frame.pack(side="left")

        # the upper frame itself 
        self.upper_frame.pack()

        # the lower frame order
        self.canvas.pack(side="left", fill="both", anchor= "center",expand=True)
        # the lower frame itself
        self.lower_frame.pack()
        



        # the full frame
        self.full_frame.pack()

        self.tick_id = ""


        self.hours = 0
        self.minutes = 0
        self.seconds = 1

        self.hour_ent.insert(tk.END, str(self.hours))
        self.minute_ent.insert(tk.END, str(self.minutes))
        self.second_ent.insert(tk.END, str(self.seconds))

        self.total_seconds = self.time_to_seconds(self.hours, self.minutes, self.seconds)
        self.og_total_seconds = self.total_seconds

        self.entry_widgets = [

            self.hour_ent, self.minute_ent, self.second_ent

        ]

        self.draw_arc()

        print(self.time_to_seconds(3, 4, 2))
        print(self.seconds_to_time(self.time_to_seconds(3, 4, 2)))

    def on_canvas_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        c_min = min(event.height, event.width)
        self.canvas_height = c_min
        self.canvas_width = c_min
        #self.last_pixel.clear()

        #canvas_center = line_line_intersection(0, 0, self.canvas_width, self.canvas_height, 0, self.canvas_height, self.canvas_width, 0)

    def draw_arc(self):
        #min_dim = min(self.canvas_width, self.canvas_height)
        #c_min = min(event.height, event.width)
        self.canvas.delete("arc")
        deci = 0.9
        coords = [
                    self.canvas_width - self.canvas_width * deci, 
                    self.canvas_height - self.canvas_height * deci, 
                    self.canvas_width * deci, 
                    self.canvas_height * deci
                ]

        self.canvas.create_arc(
                                coords, 
                                start=90, 
                                extent=self.total_seconds/self.og_total_seconds * -360,
                                fill="red",
                                outline="red",
                                tags=("arc")
                                )
        
        deci = deci - 0.1
        coords = [
                    self.canvas_width - self.canvas_width * deci, 
                    self.canvas_height - self.canvas_height * deci, 
                    self.canvas_width * deci, 
                    self.canvas_height * deci
                ]
        
        self.canvas.create_oval(
            coords,
            fill=self.canvas_color,
            outline=self.canvas_color,
            tags=("arc")

        )


    
    def refresh_time(self):
        self.hours, self.minutes, self.seconds = self.seconds_to_time(self.total_seconds)
        #print("H")
        self.refresh_hours()
        self.refresh_minutes()
        self.refresh_seconds()
    
    def refresh_seconds(self):
        self.second_ent.delete(0, tk.END)
        self.second_ent.insert(tk.END, str(self.seconds))

    def refresh_minutes(self):
        self.minute_ent.delete(0, tk.END)
        self.minute_ent.insert(tk.END, str(self.minutes))

    def refresh_hours(self):
        self.hour_ent.delete(0, tk.END)
        self.hour_ent.insert(tk.END, str(self.hours))

    def time_to_seconds(self, hours: int, minutes: int, seconds: int):
        return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_time(self, seconds: int):
        return seconds // 3600, (seconds % 3600) // 60, (seconds % 3600) % 60

    

    #Preview Controling Widgets
    def tick(self):
        
        #if self.preview_idx > len(self.preview_img_list) - 1:
        #    self.preview_idx = 0

        #print(type(self.preview_img_list[self.preview_idx]), type(self.timeline_img_list[self.preview_idx]))
        #self.preview_canvas.delete("all")
        
        '''
        self.preview_canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=self.preview_img_list[self.preview_idx],      # Display image data
            tags = ("image")
        )
        '''
        if self.total_seconds >= 1:

            self.total_seconds -= 1

            self.refresh_time()

            self.tick_id = self.after(500,lambda:self.tick())
            self.update()
            self.draw_arc()
        else:
            self.pause_countdown()

        

    def begin_countdown(self):
        #print("fps scale off")
        can_tick = self.hour_ent.get().isnumeric() and self.minute_ent.get().isnumeric() and self.second_ent.get().isnumeric()
        if not can_tick:
            return 
        

        ent_seconds = abs(int(self.second_ent.get()))
        ent_minutes = abs(int(self.minute_ent.get())) 
        ent_hours = abs(int(self.hour_ent.get()))

        all_zeros = ent_hours == 0 and ent_minutes == 0 and ent_seconds == 0

        if all_zeros:
            return

        hour_limit = 4
        
        self.play_btn.config(bg="yellow")

        self.total_seconds = self.time_to_seconds(ent_hours, ent_minutes, ent_seconds)
        if not self.playing:
            self.og_total_seconds = self.total_seconds
        self.refresh_time()

        #for widget in self.entry_widgets:
        #    disable_widget(widget) #widget.config(state="readonly")
        

        #self.total_seconds = self.time_to_seconds(self.hours, self.minutes, self.seconds)
        self.playing = True
        #forcing the buttons to update
        self.update()
        self.tick_id = self.after(500,lambda:self.tick())


    def pause_countdown(self):
        self.play_btn.config(bg="SystemButtonFace")

        #for widget in self.entry_widgets:
        #    enable_widget(widget) #widget.config(state="active")

        self.playing = False
        self.update()

        if self.tick_id:
            self.tick_id = self.after_cancel(self.tick_id)

    def restart_timer(self):
        self.hours, self.minutes, self.seconds = self.seconds_to_time(self.og_total_seconds)
        self.total_seconds = self.og_total_seconds

        self.refresh_hours()
        self.refresh_minutes()
        self.refresh_seconds()

    def start_timer(self):
        #so you can only chang the fps when the playing is false
        
        #https://stackoverflow.com/questions/66361332/creating-a-timer-with-tkinter
        if self.playing == True:
            self.pause_countdown()
        else:
            self.begin_countdown()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #https://stackoverflow.com/questions/71221471/python-bind-a-shift-key-press-to-a-command
        #frame.bind('<Left>', leftKey)
        #frame.bind('<Right>', rightKey)
        "<Left>"
        "<Right>"
        "<Control-z>"
        "<Control-y>"
        #self.bind("<Down>", self.t2d_poly.undo)
        #self.bind("<Up>", self.t2d_poly.redo)
        
        IKs = Timer(self, 300, 300)
        IKs.pack(side="top", fill="both", expand=True)
        
        '''
        self.bind("<Up>", IKs.prev_key_frame)
        self.bind("<Down>", IKs.next_key_frame)
        self.bind("<Delete>", IKs.delete_pixels)
        self.bind("<Control-c>", IKs.copy_pixels)
        self.bind("<Control-v>", IKs.paste_pixels)
        self.bind("<Control-x>", IKs.cut_pixels)
        self.bind("<Control-d>", IKs.delete_key_frame)

        self.bind("<KeyPress-Shift_L>", IKs.shift_press)
        self.bind("<KeyPress-Shift_R>", IKs.shift_press)
        self.bind("<KeyRelease-Shift_L>", IKs.shift_release)
        self.bind("<KeyRelease-Shift_R>", IKs.shift_release)
        
        self.bind("<Control-s>", lambda a:print("Quick Save not implemented"))
        self.bind("<Control-z>", lambda a:print("Undo not implemented"))
        self.bind("<Control-y>", lambda a:print("Redo not implemented"))
        '''
    
        

               

if __name__ == "__main__":



    app = App()
    
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    app.title("Simple Timer")
    app.resizable()
    app.mainloop()
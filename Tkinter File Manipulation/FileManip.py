#import os
from os import getcwd, path 
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip, vfx, afx
from proglog import ProgressBarLogger
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
#import cv2
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_POS_FRAMES, cvtColor, COLOR_BGR2RGB, imwrite, imread, resize, IMWRITE_JPEG_QUALITY
#import imageio
#from imageio import mimsave
from numpy import eye, dot, linalg




def path_correction(file_path):
    foward_slash = "/"
    back_slash = "\\"
    file_path = file_path.replace(foward_slash, back_slash)

    return file_path

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Edit App")
        #https://tkdocs.com/tutorial/menus.html
        #https://www.geeksforgeeks.org/python-menu-widget-in-tkinter/
        #https://pythonassets.com/posts/menubar-in-tk-tkinter/
        # Creating Menubar 
        self.menubar = tk.Menu(self) 
        # Adding File Menu and commands 
        self.file_menu = tk.Menu(self.menubar, tearoff = False) 
        #self.file_menu.add_command(label ='New File', command = None, accelerator="Ctrl+N") 
        self.file_menu.add_command(label ='Open', command = self.open_files, accelerator="Ctrl+O")  
        self.file_menu.add_command(label ='Save', command = self.save_files, accelerator="Ctrl+S") 
        self.file_menu.add_separator() 
        self.file_menu.add_command(label ='Exit', command = self.destroy) 
        
        # Adding Settings and commands 
        self.settings_menu = tk.Menu(self.menubar, tearoff =False)  
        self.mode_menu = tk.Menu(self.menubar, tearoff = False)
        self.mode_type = tk.IntVar()
        self.mode_type.set(1)
        self.mode_menu.add_radiobutton(
            label = "Single",
            variable=self.mode_type,
            value = 1,
            command=None
            
        )
        self.mode_menu.add_radiobutton(
            label = "Multiple",
            variable=self.mode_type,
            value = 2,
            command=None
            
        )
        
        
        # Adding Help Menu 
        self.help_menu = tk.Menu(self.menubar, tearoff = False) 
        
        self.help_menu.add_command(label ='Tk Help', command = None) 
        self.help_menu.add_command(label ='Demo', command = None) 
        self.help_menu.add_separator() 
        self.help_menu.add_command(label ='About Tk', command = None) 
        
        # Menu Placement
        self.menubar.add_cascade(label ='File', menu = self.file_menu)
        self.menubar.add_cascade(label ='Settings', menu = self.settings_menu) 
        self.settings_menu.add_cascade(label="Selection Type", menu=self.mode_menu)
        self.menubar.add_cascade(label ='Help', menu = self.help_menu) 
        
        
        # display Menu 
        self.config(menu = self.menubar) 
        
        
        
        #First Frame
        #General Info
        
        self.general_info = GenInfoFrame(self)
        
        
        
        #Fourth Frame
        #Progress Bar
        self.bar_progress = BarProgress(self)
        
        
        #Third Frame 
        #The Parameter Decider
        self.parameter_arbiter = ParameterSelection(self,
                                                    self.bar_progress)
        
        
        
        #Second Frame
        #The Canvas Flipper Frame
        self.frame_mavigator = MediaFrameNav(self, 
                                            500, 
                                            500,
                                            param_arbs = self.parameter_arbiter,
                                            info_gen = self.general_info
                                            )
        
        
        self.general_info.grid(row=0, column=0, sticky="N")
        self.frame_mavigator.grid(row=0, column=1, sticky="EW")
        self.parameter_arbiter.grid(row=0, column=2, sticky="N")
        self.bar_progress.grid(row=1, column=1)
        
        
        
        
        
       
        self.current_directory = getcwd()
        self.selected_file = ""
        self.selected_file_list = [] 
    
    
        
    
    def open_files(self):
        
        filetypes = [
                    #("All files", "*.*"),
                    ("mp4 files", "*.mp4"), 
                    ("mov files", "*.mov"), 
                    ("webm files", "*.webm"),
                    ("avi files", "*.avi"),
                    ("mkv files", ".mkv"),

                    ("gif files", "*.gif"),
       
                    ("jpg files", ".jpg .jpeg"),
                    ("png files", "*.png"),
                    ("webp files", "*.webp"),
                    ("tiff files", ".tiff .tif"),
                    ("bitmap files", "*.bmp")
                    
                    ]
        
        file_path_s = ""
        
        if self.mode_type.get() == 1:
            
            self.selected_file = filedialog.askopenfilename(
                title='Open files',
                initialdir=self.current_directory,
                filetypes=filetypes
                )
            
            if self.selected_file:
                #temp = file_path_list[0].split('/')
                #self.last_folder = "/".join(temp[:len(temp) - 1]) + "/"
                self.frame_mavigator.set_frame(self.selected_file)
                self.frame_mavigator.set_path_listbox(self.selected_file)
                
                self.current_directory = "\\".join(self.selected_file.split('/')[:-1]) + "\\"
                
                #closing all paramters
                self.parameter_arbiter.has_file = False
                self.parameter_arbiter.set_widget_states()
                
                self.parameter_arbiter.set_file(
                                                "\\".join(self.selected_file.split('/')[-1:]), 
                                                "\\".join(self.selected_file.split('/'))
                                                )
             
             
             
                self.selected_file = self.parameter_arbiter.selected_file
                
                #print(self.current_directory)
                #print(self.selected_file)
                #print(self.parameter_arbiter.selected_file)
                #print(self.parameter_arbiter.selected_file_path)
        else:
            
            messagebox.showerror("showinfo", "Multiple Files Not Implemented")
            '''
            file_path_s = filedialog.askopenfilenames(
                title='Open files',
                initialdir=self.current_directory,
                filetypes=filetypes
                )
            
            for ind in range(len(file_path_s)):
                   raw_file = file_path_s[ind]
                   #edited_file = raw_file.split('/')[-1]
               
            
        
            temp = file_path_s[0].split('/')
            self.last_folder = "/".join(temp[:len(temp) - 1]) + "/"
            '''
            
        
    def save_files(self):
        #self.save_path_listbox.insert(tk.END, self.last_folder)
        

        
        filetypes = [
                    ("All files", "*.*"),
      
                    
                    ]
        
        if self.mode_type.get() == 1:
        
            dext = self.parameter_arbiter.get_extension()
            save_path = filedialog.asksaveasfilename(
                
                                        initialdir=self.current_directory,
                                        defaultextension = dext, 
                                        #filetypes= filetypes #[("PNG", ".png"),("JPG",".jpg")] 
                                        ) 
            
            #print(dext, " worked")
            #print(self.selected_file)
            self.current_directory = "\\".join(save_path.split('/')[:-1]) + "\\"
            self.parameter_arbiter.apply_changes(save_path)
            #self.last_folder = self.current_directory
        else:
            messagebox.showerror("showinfo", "Multiple Files Not Implemented")
        
        
            
    def clear_files(self):
        pass
        
            
    def get_directory(self):
        pass
        
    

class GenInfoFrame(ttk.Frame):  
    def __init__(self, parent):
        super().__init__(parent)
        
        
        #General Info
        self.file_name   = None
        self.fps         = None
        self.frame_count = None
        self.duration    = None
        self.width       = None
        self.height      = None
        self.current_frame = None
        self.current_second = None
        self.bitrate     = None
        
        self.title_label= ttk.Label(self, text="General Info")
        
        self.file_name_label= ttk.Label(self, text="File Name:")
        self.file_name_listbox = tk.Listbox(self, 

                                       height=1
                                       
                                       )
        
        self.file_name_scrollbar_x = tk.Scrollbar(self, orient = 'horizontal', command=self.file_name_listbox.xview)
        self.file_name_listbox.config(xscrollcommand=self.file_name_scrollbar_x.set)
        
        self.fps_label= ttk.Label(self, text="FPS:")
        self.duration_label = ttk.Label(self, text="Duration:")
        self.frame_count_label= ttk.Label(self, text="Frame_Count:")
        self.current_frame_label = ttk.Label(self, text="Current Frame:")
        self.current_second_label = ttk.Label(self, text="Current Second:")
        self.width_label= ttk.Label(self, text="Width:")
        self.height_label= ttk.Label(self, text="Height:")
        self.bitrate_label = ttk.Label(self, text="Bitrate:")
        
        #self.title_label.grid(row=0, column=0, sticky="N")
        self.file_name_label.grid(row=0, column=0, sticky="N")
        self.file_name_listbox.grid(row=1, column=0, sticky="NEW")
        self.file_name_scrollbar_x.grid(row=2, column=0, sticky = "EW")
        self.fps_label.grid(row=3, column=0)
        self.duration_label.grid(row=4, column=0, sticky="N")
        self.frame_count_label.grid(row=5, column=0, sticky="N")
        self.current_frame_label.grid(row=6, column=0, sticky="N")
        self.current_second_label.grid(row=7, column=0, sticky="N")
        self.width_label.grid(row=8, column=0, sticky="N")
        self.height_label.grid(row=9, column=0, sticky="N")
        self.bitrate_label.grid(row=10, column=0)
        
        
        
    def set_info(self, **kwargs):
        
        
        if kwargs.get("file_name"):
            self.file_name =  kwargs["file_name"]
        if kwargs.get("fps"):
            self.fps =  kwargs["fps"]
        if kwargs.get("frame_count"):
            self.frame_count =  kwargs["frame_count"]
        if kwargs.get("duration"):
            self.duration =  kwargs["duration"]
        
        
        if kwargs.get("width"):
            self.width  = kwargs["width"]
        if kwargs.get("height"):
            self.height  = kwargs["height"]
        if kwargs.get("current_frame"):
            self.current_frame  = kwargs["current_frame"]
        if kwargs.get("current_second"):
            self.current_second  = kwargs["current_second"]
            
        if kwargs.get("bitrate"):
            self.bitrate = kwargs["bitrate"]
            
        
            
        
        #self.file_name_label.config(text= "File Name:{}".format(self.file_name))
        
        if self.file_name_listbox.size() > 0:
            self.file_name_listbox.delete(0, tk.END)
            
        self.file_name_listbox.insert(0, self.file_name)
        self.fps_label.config(text= "FPS:{}".format(self.fps))
        self.duration_label.config(text= "Duration:{} seconds".format(self.duration))
        self.frame_count_label.config(text= "Frame Count:{}".format(self.frame_count))
        self.current_frame_label.config(text= "Current Frame:{}".format(self.current_frame))
        self.current_second_label.config(text= "Current Second:{:.3f}".format(self.current_second))
        self.width_label.config(text= "Width:{} pixels".format(str(self.width)))
        self.height_label.config(text= "Height:{} pixels".format(str(self.height)))
        self.bitrate_label.config(text= "Bitrate:{} bps".format(str(round(self.bitrate))))
        
           
            
class BarProgress(ttk.Frame):  
    def __init__(self, parent):
        super().__init__(parent)

            
        self.complete_progress_label = ttk.Label(self, text = "Progress ")
        self.complete_progress_bar = ttk.Progressbar(self, orient= "horizontal",  mode="determinate",length=400)
        self.complete_progress_status_label = ttk.Label(self, text = "Idle")
            
        self.logger = self.MyBarLogger(self.complete_progress_bar, self.complete_progress_status_label, self)
        
        self.complete_progress_label.grid(row=10, column=0, sticky="EW")
        self.complete_progress_bar.grid(row=10, column=1, sticky="EW")
        self.complete_progress_status_label.grid(row=10, column=9, sticky="EW")
            
    class MyBarLogger(ProgressBarLogger):
        #https://stackoverflow.com/questions/69423410/moviepy-getting-progress-bar-values
    
        def __init__(self, tk_progressbar, status_label ,parent_window):
            super().__init__()
            self.last_message = ''
            self.previous_percentage = 0

            self.tk_progress = tk_progressbar
            self.root_window = parent_window
            self.status = status_label

        def callback(self, **changes):
            # Every time the logger message is updated, this function is called with
            # the `changes` dictionary of the form `parameter: new value`.
            for (parameter, value) in changes.items():
                # print('Parameter %s is now %s' % (parameter, value))
                self.last_message = value

        def bars_callback(self, bar, attr, value, old_value=None):
            # Every time the logger progress is updated, this function is called
            if 'Writing video' in self.last_message:
                percentage = (value / self.bars[bar]['total']) * 100
                if percentage > 0 and percentage < 100:
                    if int(percentage) != self.previous_percentage:
                        self.previous_percentage = int(percentage)
                        self.tk_progress["value"] = self.previous_percentage
                        self.status["text"] = "Loading"
                        self.root_window.update_idletasks()



class ParameterSelection(ttk.Frame):
    def __init__(self, parent, completion_bar):
        super().__init__(parent)
        
        self.static_filetypes = ['png', 'jpg', 'jpeg','webp', 'tiff', 'tif', 'webp', 'bmp']
        self.animated_filetypes =  ["mp4", "mov", "webm", "gif", "avi", "mkv"] 
        
        
        self.conversion_widgets = self.setup_conversion_widgets()
        
        self.audio_widgets = self.setup_audio_widgets()
    
        self.resize_widgets = self.setup_resize_widgets()
        
        self.cut_widgets = self.setup_cut_widgets()
        
        self.crop_widgets = self.setup_crop_widgets()
        
        self.extraction_widgets = self.setup_extractor_widgets()
        
        self.bitrate_widgets = self.setup_bitrate_widgets()
        
        self.convert_to_checkbutton.config(command=self.set_widget_states)
        self.audio_checkbutton.config(command=self.set_widget_states)
        self.resize_checkbutton.config(command=self.set_widget_states)
        self.cut_checkbutton.config(command=self.set_widget_states)
        self.crop_checkbutton.config(command=self.set_widget_states)
        self.ext_checkbutton.config(command=self.set_widget_states)
        self.bitrate_checkbutton.config(command=self.set_widget_states)
        
        #Conversion
        #Placement
        self.convert_to_label.grid(row = 0, column = 0, sticky="WE")
        self.convert_to_checkbutton.grid(row = 1, column=0, sticky="N")
        self.convert_to_combobox.grid(row = 2, column= 0, sticky="N")
        
        
        #Resize
        #Placement
        self.resize_label.grid(row = 0, column = 1, sticky="WE")
        self.resize_checkbutton.grid(row = 1, column = 1, sticky="N")
        self.resize_spinbox.grid(row = 2, column = 1, sticky="N")
        
        
        #Audio
        #Placement
        self.audio_label.grid(row = 3, column = 0, sticky="WE")
        self.audio_checkbutton.grid(row = 4, column = 0, sticky="N")
        self.volume_scale.grid(row = 5, column = 0, sticky="EW", columnspan=2)
        self.volume_label.grid(row = 6, column = 0, sticky="NEW", columnspan=2)

        
        #Cut
        #Placement
        self.cut_label.grid(row = 7, column = 0, sticky="WE")
        self.cut_checkbutton.grid(row = 8, column = 0, sticky="N")
        self.start_cut_label.grid(row = 9, column = 0, sticky="N")
        self.end_cut_label.grid(row = 10, column = 0, sticky="N")
        self.cut_start_spinbox.grid(row = 9, column = 1, sticky="N")
        self.cut_end_spinbox.grid(row = 10, column = 1, sticky="N")
        
        
        #Crop
        #Placement
        self.crop_label.grid(row = 11, column = 0, sticky="WE")
        self.crop_checkbutton.grid(row = 12, column = 0, sticky="N")
        self.crop_canvas_xy1_coords.grid(row = 13, column = 0, sticky="N")
        self.crop_canvas_xy2_coords.grid(row = 14, column = 0, sticky="N")
        self.crop_image_xy1_coords.grid(row = 13, column = 1, sticky="N")
        self.crop_image_xy2_coords.grid(row = 14, column = 1, sticky="N")
        
        
        #Extraction
        self.ext_label.grid(row = 15, column = 0, sticky="N")
        self.ext_checkbutton.grid(row = 16, column = 0, sticky="N")
        self.ext_frame_label.grid(row = 17, column = 0, sticky="N")
        self.ext_combobox.grid(row = 18, column = 0, sticky="N")
        
        #Bitrate
        self.bitrate_label.grid(row = 19, column = 0, sticky="N")
        self.bitrate_checkbutton.grid(row = 20, column = 0, sticky="N")
        self.final_bitrate_label.grid(row = 21, column = 0, sticky="N")
        self.final_bitrate_spinbox.grid(row = 22, column = 0, sticky="N")
        
        
        
        
        self.selected_file_path = ""
        self.selected_file = ""
        self.current_ext = ""
        
        self.has_file = True
        self.set_widget_states()
        self.has_file = False
        
        
        

        
        
        self.completion_bar = completion_bar
                
    def get_extension(self):
        if self.ext_checkbool.get():
        
         
            return "." + self.ext_combobox.get()  
          
            
        elif self.convert_to_checkbool.get():

            
            if self.convert_to_combobox.get() == "No Change":
 
                return "." + self.current_ext
            else:

                return "." + self.convert_to_combobox.get()
        else:

            if self.selected_file:

                return "." + self.current_ext
            else:

                return "."
               
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
        
    def set_file(self, sel_file, full_file):
        
        self.selected_file = sel_file
        self.selected_file_path = full_file
        self.current_ext = full_file.split(".")[-1]
        
        if self.current_ext not in self.static_filetypes:
            self.convert_to_combobox["values"] = self.convert_to_options[self.current_ext]
        else:
            self.convert_to_combobox["values"] = (  "No Change",
                                                    "mp4",
                                                    "mov",                 
                                                    "webm",
                                                    "mkv",
                                                    "avi",
                                                    "gif"
                                              )
        self.completion_bar.complete_progress_bar['value'] = 0
        self.has_file = True
        
    def set_widget_states(self):
        if self.has_file:
            
            
            if not self.ext_checkbool.get() and self.current_ext not in self.static_filetypes:
                if self.convert_to_checkbool.get():
                    #self.convert_to_checkbutton.config(text = "Enable")
                    for widget in self.conversion_widgets:
                        self.show_widget(widget)
                elif not self.convert_to_checkbool.get():
                
                    #self.convert_to_checkbutton.config(text = "Disabled")
                    for widget in  self.conversion_widgets:
                        self.hide_widget(widget)
            else:
                self.convert_to_checkbool.set(False)
                    
                    
            if not self.ext_checkbool.get() and self.current_ext != 'gif' and self.current_ext not in self.static_filetypes:
                if self.audio_checkbool.get():
                    #self.convert_to_checkbutton.config(text = "Enable")
                    for widget in self.audio_widgets:
                        self.show_widget(widget)
                elif not self.audio_checkbool.get():
                    self.volume_scale.set(100)
                    #self.convert_to_checkbutton.config(text = "Disabled")
                    for widget in self.audio_widgets:
                        self.hide_widget(widget)
            else:
                self.audio_checkbool.set(False)
                    
                    
            
            if self.resize_checkbool.get():
                #self.convert_to_checkbutton.config(text = "Enable")
                for widget in self.resize_widgets:
                    self.show_widget(widget)
            elif not self.resize_checkbool.get():   
                #self.convert_to_checkbutton.config(text = "Disabled")
                for widget in self.resize_widgets:
                    self.hide_widget(widget)
                    
                    
            if not self.ext_checkbool.get() and self.current_ext not in self.static_filetypes:
                if self.cut_checkbool.get():
                    #self.convert_to_checkbutton.config(text = "Enable")
                    for widget in self.cut_widgets:
                        self.show_widget(widget)
                elif not self.cut_checkbool.get():
                
                    #self.convert_to_checkbutton.config(text = "Disabled")
                    for widget in self.cut_widgets:
                        self.hide_widget(widget)
            else:
                self.cut_checkbool.set(False)
                    
                    
                    
            if self.crop_checkbool.get():
                #self.convert_to_checkbutton.config(text = "Enable")
                for widget in self.crop_widgets:
                    self.show_widget(widget)
            elif not self.crop_checkbool.get():
                
                #self.convert_to_checkbutton.config(text = "Disabled")
                for widget in self.crop_widgets:
                    self.hide_widget(widget)
                    
                    
            if self.ext_checkbool.get():
                self.convert_to_checkbool.set(False)
                self.audio_checkbool.set(False)
                self.cut_checkbool.set(False)

                
                for widget in  self.conversion_widgets:
                    self.hide_widget(widget)
                
                
                for widget in self.audio_widgets:
                    self.hide_widget(widget)
                    

                for widget in self.cut_widgets:
                    self.hide_widget(widget)
                    

                
                for widget in self.extraction_widgets:
                    self.show_widget(widget)
                    
            elif not self.ext_checkbool.get():
                #self.convert_to_checkbutton.config(text = "Disabled")
                for widget in self.extraction_widgets:
                    self.hide_widget(widget)
                    
                    
                    
            if not self.ext_checkbool.get() and self.current_ext != 'gif' and self.current_ext not in self.static_filetypes:
                if self.bitrate_checkbool.get():
                    #self.convert_to_checkbutton.config(text = "Enable")
                    for widget in self.bitrate_widgets:
                        self.show_widget(widget)
                elif not self.bitrate_checkbool.get():
                    #self.convert_to_checkbutton.config(text = "Disabled")
                    for widget in self.bitrate_widgets:
                        self.hide_widget(widget)
            else:
                self.bitrate_checkbool.set(False)
                
                    
        else:
            self.convert_to_checkbool.set(False)
            self.audio_checkbool.set(False)
            self.resize_checkbool.set(False)
            self.cut_checkbool.set(False)
            self.crop_checkbool.set(False)
            self.ext_checkbool.set(False)
            self.bitrate_checkbool.set(False)
   
            for widget in  self.conversion_widgets:
                self.hide_widget(widget)
                
                
                
    
            for widget in self.audio_widgets:
                self.hide_widget(widget)
                
                

            for widget in self.resize_widgets:
                self.hide_widget(widget)
                
                

            for widget in self.cut_widgets:
                self.hide_widget(widget)
                
                

            for widget in self.crop_widgets:
                self.hide_widget(widget)  
                
            for widget in self.extraction_widgets:
                    self.hide_widget(widget)
    
    def setup_conversion_widgets(self):
        
        
        #Parameters
        self.convert_to_combobox = ttk.Combobox(self, width = 15,  textvariable = tk.StringVar()) 
        self.convert_to_combobox["values"] = (  "No Change",
                                                "mp4",
                                                "mov",                 
                                                "webm",
                                                "mkv",
                                                "avi",
                                                "gif"
                                              )
        
        self.convert_to_options = {

            'gif':(
                    "No Change",
                    "mp4",
                    "avi",
                    "mkv",
                    "mov",
                    "webm"
                   ),
            
            
            "mp4": (
                    "No Change",
                    "avi",
                    "mkv",
                    "mov",
                    "webm",
                    "gif"
                    ),
            
            "mov": (
                    "No Change",
                    "mp4",
                    "mkv",
                    "avi",
                    "webm",
                    "gif"
                    ),
   
            
            "webm": (
                    "No Change",
                    "mp4",
                    "mov",
                    "avi",
                    "mkv",
                    "gif"
                    ),
            
            "mkv":(
                    "No Change",
                    "mp4",
                    "gif",
                    "avi",
                    "mov",
                    "webm"

                    ),
            
            "avi":(
                    "No Change",
                    "mp4",
                    "gif",
                    "mkv",
                    "mov",
                    "webm"

                    )
            
            
            
                                        }
    
        
        #Enablement Bools
        self.convert_to_label= ttk.Label(self, text="Convert")
        
        self.convert_to_checkbool = tk.BooleanVar()
        self.convert_to_checkbool.set(False)
        
        self.convert_to_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.convert_to_checkbool,
                                                text= "Enabled"

                                                ) 
        
        
        
        
        
        self.convert_to_combobox.current(0)
        
        return [ self.convert_to_combobox ]
                      
    def setup_audio_widgets(self):
        #Parameters
        
        
        #self.mute_checkbool = tk.BooleanVar()
        #self.mute_checkbool.set(False)
        
        #self.mute_checkbutton = ttk.Checkbutton(self,   
        #                                        variable=self.mute_checkbool,
        #                                        text= "Mute"
        #                                        ) 
        self.volume_var = tk.IntVar()
        
        self.volume_label = ttk.Label(self, text = "Volume Percentage: 100")
        
        self.volume_scale = ttk.Scale(self,
                                      variable = self.volume_var,
                                      from_ = 0,
                                      to = 200,
                                      orient = "horizontal",
                                      command = self.set_volume_label
                                      )
        
        self.volume_scale.set(100)
     
        
        #Enablement Bools
        self.audio_label = ttk.Label(self, text="Audio")
        
        self.audio_checkbool = tk.BooleanVar()
        self.audio_checkbool.set(False)
        
        self.audio_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.audio_checkbool,
                                                text= "Enabled"

                                                ) 
        
        
        
        
        
        
    
        
        return [ self.volume_label, self.volume_scale ]
      
    def setup_resize_widgets(self):
        #Parameters
        self.resize_spinbox= ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 500,
                                        width = 10
                                        
                                        )

        
        #Enablement Bools
        
        self.resize_label = ttk.Label(self, text="Resize")
        
        self.resize_checkbool = tk.BooleanVar()
        self.resize_checkbool.set(False)
        
        self.resize_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.resize_checkbool,
                                                text= "Enabled"
                                     
                                                ) 
        
        
        
        self.resize_spinbox.set(100)
       
        
        return [ self.resize_spinbox ]
    
    def setup_cut_widgets(self):
        #Parameters
        
  
        
        
        self.start_cut_label = ttk.Label(self, text = "Start Seconds:")
        self.end_cut_label = ttk.Label(self, text = "End Seconds:")
        

        
        
        self.cut_start_spinbox = ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 300000,
                                        #textvariable=tk.DoubleVar(value=0.00),
                                        increment= 0.01
                                        
                                        ) 
        self.cut_end_spinbox = ttk.Spinbox(self, 
                                        from_ = 0,
                                        to = 300000,
                                        #textvariable=tk.DoubleVar(value=0.00),
                                        increment= 0.01
                                    
                                        ) 
       
        self.cut_end_spinbox.set(0)
        self.cut_start_spinbox.set(0)
        
        
        
        
        
        
        
        #Enablement Bools
        self.cut_label = ttk.Label(self, text = "Cut")
 
        
        self.cut_checkbool = tk.BooleanVar()
        self.cut_checkbool.set(False)
        
        self.cut_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.cut_checkbool,
                                                text= "Enabled"
                                     
                                                ) 
        
        
        
 
 
        
        return [ self.cut_start_spinbox , self.cut_end_spinbox, self.start_cut_label, self.end_cut_label]
             
    def setup_crop_widgets(self):
        #Parameters
        
        self.crop_canvas_xy1_coords = ttk.Label(self, text = "Canvas X1: 0, Canvas Y1: 0")
        self.crop_canvas_xy2_coords  = ttk.Label(self, text = "Canvas X2: 0, Canvas Y2: 0")
        self.crop_image_xy1_coords = ttk.Label(self, text = "Image X1: 0, Image Y1: 0")
        self.crop_image_xy2_coords  = ttk.Label(self, text = "Image X1: 0, Image Y2: 0")
        

        
        
        
        #Enablement Bools
        self.crop_label = ttk.Label(self, text = "Crop")
 
        
        self.crop_checkbool = tk.BooleanVar()
        self.crop_checkbool.set(False)
        
        self.crop_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.crop_checkbool,
                                                text= "Enabled"
                                     
                                                ) 
        self.crop_cx1 = 0
        self.crop_cy1 = 0
        self.crop_cx2 = 0
        self.crop_cy2 = 0
        self.crop_ix1 = 0
        self.crop_iy1 = 0
        self.crop_ix2 = 0
        self.crop_iy2 = 0
        
        return [ self.crop_canvas_xy1_coords, self.crop_canvas_xy2_coords, self.crop_image_xy1_coords, self.crop_image_xy2_coords ]
    
    def setup_extractor_widgets(self):
        #Parameters
        
        self.ext_frame_label = ttk.Label(self, text = "Selected_Frame: 0")
        self.ext_combobox = ttk.Combobox(self, width = 15,  textvariable = tk.StringVar()) 

        self.ext_combobox["values"] = ( "jpg",
                                        "jpeg",
                                        "png",
                                        "bmp",
                                        "tiff",
                                        "tif",
                                        "webp",
                                        "gif"      
                                        )
        self.ext_frame = 0
        self.ext_combobox.current(0)
        
        
        
        #Enablement Bools
        self.ext_label = ttk.Label(self, text = "Extract Image")
 
        
        self.ext_checkbool = tk.BooleanVar()
        self.ext_checkbool.set(False)
        
        self.ext_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.ext_checkbool,
                                                text= "Enabled"
                                     
                                                ) 

        return [ self.ext_frame_label, self.ext_combobox ]
    
    def setup_bitrate_widgets(self):
        #Parameters
        
        
        self.final_bitrate_label = ttk.Label(self, text = "Bits per Second: 0")
        
        

        
        
        self.final_bitrate_spinbox = ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 1800000000,
                                        #textvariable=tk.DoubleVar(value=0.00),
                                        increment=1
                                        
                                        ) 
        
       
  
        self.og_bitrate = 0
        
        self.final_bitrate_spinbox.set(0)
        
        
        
        
        
        
        
        #Enablement Bools
        self.bitrate_label = ttk.Label(self, text = "Bitrate bps")
 
        
        self.bitrate_checkbool = tk.BooleanVar()
        self.bitrate_checkbool.set(False)
        
        self.bitrate_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.bitrate_checkbool,
                                                text= "Enabled"

                                                ) 
        
        
        
 
 
        
        return [ self.final_bitrate_label, self.final_bitrate_spinbox ]
    
    def update_final_bitrate(self, bitrate):
        bitrate = round(bitrate)
        self.og_bitrate = bitrate
        self.final_bitrate_label.config(text = "Bits per Second: {}".format(bitrate))
        self.final_bitrate_spinbox.set(bitrate)
    
    def update_current_ext_frame_label(self, current_frame):
        self.ext_frame = current_frame
        self.ext_frame_label.config(text=f"Selected_Frame: {self.ext_frame}")
    
    def update_crop_widget_labels(self, **kwargs):
        '''
            canvas_x1 = rx,
            canvas_y1 = ry,
            canvas_x2 = rx + rw,
            canvas_y2 = ry + rh,
            image_x1 = ix,
            image_y1 = iy,
            image_x2 = iw,
            image_y2 = ih
        '''
        

        if kwargs.get("canvas_x1"):
            self.crop_cx1 =  round(kwargs["canvas_x1"])
        if kwargs.get("canvas_y1"):
            self.crop_cy1 =  round(kwargs["canvas_y1"])
        if kwargs.get("canvas_x2"):
            self.crop_cx2 =  round(kwargs["canvas_x2"])
        if kwargs.get("canvas_y2"):
            self.crop_cy2 =  round(kwargs["canvas_y2"])
        
        
        
        if kwargs.get("image_x1"):
            self.crop_ix1  =  round(kwargs["image_x1"])
        if kwargs.get("image_y1"):
            self.crop_iy1  =  round(kwargs["image_y1"])
        if kwargs.get("image_x2"):
            self.crop_ix2  =  round(kwargs["image_x2"])
        if kwargs.get("image_y2"):
            self.crop_iy2  =  round(kwargs["image_y2"])
            
            
        
        
        if self.crop_cx1 == -1:
            self.crop_canvas_xy1_coords.config(text = "Canvas X1: 0, Canvas Y1: 0")
            self.crop_canvas_xy2_coords.config(text = "Canvas X2: 0, Canvas Y2: 0")
            self.crop_image_xy1_coords.config(text = "Image X1: 0, Image Y1: 0")
            self.crop_image_xy2_coords.config(text = "Image X1: 0, Image Y2: 0")
        
        else:
            self.crop_canvas_xy1_coords.config(text = f"Canvas X1: {self.crop_cx1}, Canvas Y1: {self.crop_cy1}")
            self.crop_canvas_xy2_coords.config(text = f"Canvas X2: {self.crop_cx2}, Canvas Y2: {self.crop_cy2}")
            self.crop_image_xy1_coords.config(text = f"Image X1: {self.crop_ix1}, Image Y1: {self.crop_iy1}")
            self.crop_image_xy2_coords.config(text = f"Image X2: {self.crop_ix2}, Image Y2: {self.crop_iy2}")
        
        #print(kwargs)
    
    def set_volume_label(self, *args):
        self.volume_label.config( text = f"Volume Percentage: {self.volume_var.get()}")
              
    def apply_changes(self, save_path):
        
        
        if self.selected_file:
            
            if  self.current_ext in self.animated_filetypes:
                self.edit_animated_media(save_path)
            elif self.current_ext in self.static_filetypes:
                #messagebox.showerror("showinfo", "Gif Stuff not Implemented yet")
                self.edit_static_media(save_path)
               
    def gif_image_maker(self, **kwargs):

        
        was_converted = False
        was_cut = False
        was_tuned = False
        was_resized = False
        was_cropped = False
        was_extracted = False
        was_bytten =  False
        
        codec_dict = {}
        cdc = ''
        
        current_ext = ''
        save_path = ''
        selected_file = ''
        start_seconds = 0.0
        end_seconds =  0.0
        conversion_value = ''
        resize_value = 0
        extraction_frame = 0
        byte_value = 0
        
        
        media = None
        
        
        
        
        
        if kwargs.get("was_converted"):
            was_converted =  kwargs["was_converted"]
        if kwargs.get("was_cut"):
            was_cut =  kwargs["was_cut"]
        if kwargs.get("was_tuned"):
            was_tuned =  kwargs["was_tuned"]
        if kwargs.get("was_resized"):
            was_resized =  kwargs["was_resized"]
        if kwargs.get("was_cropped"):
            was_cropped =  kwargs["was_cropped"]
        if kwargs.get("was_extracted"):
            was_extracted =  kwargs["was_extracted"]
        if kwargs.get("was_bytten"):
            was_bytten =  kwargs["was_bytten"]
            
            
        if kwargs.get("codec_dict"):
            codec_dict =  kwargs["codec_dict"]
        if kwargs.get("cdc"):
            cdc =  kwargs["cdc"]
            
        if kwargs.get("current_ext"):
            current_ext =  kwargs["current_ext"]
        if kwargs.get("save_path"):
            save_path =  kwargs["save_path"]
        if kwargs.get("selected_file"):
            selected_file =  kwargs["selected_file"]
        if kwargs.get("start_seconds"):
            start_seconds =  kwargs["start_seconds"]
        if kwargs.get("end_seconds"):
            end_seconds =  kwargs["end_seconds"]
        if kwargs.get("conversion_value"):
            conversion_value =  kwargs["conversion_value"]
        if kwargs.get("resize_value"):
            resize_value =  kwargs["resize_value"]
        if kwargs.get("extraction_frame"):
            extraction_frame =  kwargs["extraction_frame"]
        if kwargs.get("byte_value"):
            byte_value =  kwargs["byte_value"]
        
            
        if kwargs.get("media"):
            media =  kwargs["media"]
        

        
        
        
        
        if current_ext in self.animated_filetypes:
            #https://gist.github.com/laygond/d62df2f2757671dea78af25a061bf234#file-writevideofromimages-py-L25
            #https://theailearner.com/2021/05/29/creating-gif-from-video-using-opencv-and-imageio/
            #https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
            cap = VideoCapture(selected_file)
            # Get General Info
            fps         = cap.get(CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            frame_count = int(cap.get(CAP_PROP_FRAME_COUNT))
        
            duration    = int(frame_count/fps)
            width       = int(cap.get(CAP_PROP_FRAME_WIDTH))  # float
            height      = int(cap.get(CAP_PROP_FRAME_HEIGHT)) # float
            
            image_list = []
            
            
            '''
            '''
            #Using OpenCV's stuff
            #print("OPENCV LOOP")

            if not was_extracted:
                #making a gif from a video or keeping a gif the same
                media.close()
                start_frame = 0
                end_frame = frame_count
                if was_cut:
                    start_frame = start_seconds * fps
                    end_frame = end_seconds * fps
                
                
                frame_current = 0
                cap.set(CAP_PROP_POS_FRAMES, frame_current)
                
                while True:
                    is_reading, frame = cap.read()
                    if not is_reading:
                        break
                    
                    if frame_current > end_frame:
                        break
                    
                    
                    if frame_current >= start_frame and frame_current <= end_frame:
                        frame_rgb =  cvtColor(frame, COLOR_BGR2RGB)
                        if was_cropped:
                            
                            frame_rgb = frame_rgb[self.crop_iy1:self.crop_iy2, self.crop_ix1:self.crop_ix2]
                        
                        if was_resized:
                            rw = int(width * (resize_value/100))
                            rh = int(height * (resize_value/100))
                            frame_rgb = resize(frame_rgb, (rw, rh ))
                        
                        frame_rgb = Image.fromarray(frame_rgb)
                        image_list.append(frame_rgb)
                    
                        self.completion_bar.complete_progress_bar['value'] = int((frame_current/(end_frame - start_frame)) * 100)
                        self.update_idletasks()
                        
                    
                    
                    frame_current += 1
                    
                    
                
                    
                    

                
                milliseconds = (fps**-1) * 1000

                
                cap.release()
                self.completion_bar.complete_progress_status_label["text"] = "Saving"
                #self.complete_progress_status_label["text"] = "Saving"
                
                
                #if PIL's Image.fromarray isn't used
                #imageio.mimsave(save_path, image_list, duration = milliseconds)
                #if PIL's Image.fromarray is used
                image_list[0].save(save_path, format = "GIF", save_all=True, append_images=image_list[1:],  duration = milliseconds, loop=0)
                self.completion_bar.complete_progress_status_label["text"] = "Finished"
                #self.complete_progress_status_label["text"] = "Finished"
                
                #video.write_gif(save_path, progress_bar = True)
            else:
                #converting a frame of a video or gif to an image
                
                #why this, when there's three alternate, instanteous, methods under it
                #when trying to get frames from longer videos, greater than 10 minutes, it often fetched the wrong frame
    
                frame_current = 0
                end_frame = frame_count
                while True:
                    is_reading, frame = cap.read()
                    if not is_reading:
                        break
                    
                    if frame_current > end_frame:
                        break
                    
                    
                    if frame_current == extraction_frame:
                        frame_rgb =  cvtColor(frame, COLOR_BGR2RGB)
                        if was_cropped:
                            #x1=self.crop_ix1 , y1=self.crop_iy1 , x2=self.crop_ix2 , y2=self.crop_iy2
                            frame_rgb = frame_rgb[self.crop_iy1:self.crop_iy2, self.crop_ix1:self.crop_ix2]
                        
                        if was_resized:
                            rw = int(width * (resize_value/100))
                            rh = int(height * (resize_value/100))
                            frame_rgb = resize(frame_rgb, (rw, rh ))
                        
                        #Using Pillow's image methods
                        frame_rgb = Image.fromarray(frame_rgb)
                        #below only works on pngs
                        #frame_rgb = frame_rgb.quantize(method=Image.MEDIANCUT)
                        self.completion_bar.complete_progress_status_label["text"] = "Saving"
                        frame_rgb.save(save_path)
                        self.completion_bar.complete_progress_status_label["text"] = "Finished"
                        print("finished")
                        break
                    
                    self.completion_bar.complete_progress_bar['value'] = int((frame_current/extraction_frame) * 100)
                    self.update_idletasks()
                        
                    
                    
                    frame_current += 1
                '''
                
                cap.set(CAP_PROP_POS_FRAMES, extraction_frame)
                is_reading, frame = cap.read()
                frame_rgb =  cvtColor(frame, COLOR_BGR2RGB)
                if was_cropped:
                    #x1=self.crop_ix1 , y1=self.crop_iy1 , x2=self.crop_ix2 , y2=self.crop_iy2
                    frame_rgb = frame_rgb[self.crop_iy1:self.crop_iy2, self.crop_ix1:self.crop_ix2]
                
                if was_resized:
                    rw = int(width * (resize_value/100))
                    rh = int(height * (resize_value/100))
                    frame_rgb = resize(frame_rgb, (rw, rh ))
                
                #Using Pillow's image methods
                frame_rgb = Image.fromarray(frame_rgb)
                #below only works on pngs
                #frame_rgb = frame_rgb.quantize(method=Image.MEDIANCUT)
                frame_rgb.save(save_path)
                '''
                #OpenCV stuff
                #cv2.imwrite(save_path, frame_rgb)
                
                #MoviePy Stuff
                #frame = media.get_frame(extraction_frame * fps)
                #frame = Image.fromarray(frame)
                #frame.save(save_path)
                #media.save_frame(save_path, t = extraction_frame * fps)
                
                #print("done")
                media.close()
                cap.release()
        elif current_ext in self.static_filetypes:
            #https://stackoverflow.com/questions/60048149/how-to-convert-png-to-jpg-in-python
            #https://www.geeksforgeeks.org/reading-image-opencv-using-python/
            frame_rgb  = imread(selected_file)
            height, width, _ = frame_rgb.shape
            #This doesn't work with transparent images
            #frame_rgb  = cv2.imread(selected_file, cv2.IMREAD_COLOR)
            #This for PIL to OPENCV conversion
            #frame_rgb =  cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if was_cropped:
                #x1=self.crop_ix1 , y1=self.crop_iy1 , x2=self.crop_ix2 , y2=self.crop_iy2
                frame_rgb = frame_rgb[self.crop_iy1:self.crop_iy2, self.crop_ix1:self.crop_ix2]
            
            if was_resized:
                rw = int(width * (resize_value/100))
                rh = int(height * (resize_value/100))
                frame_rgb = resize(frame_rgb, (rw, rh ))
            
            #Using Pillow's image methods
            #frame_rgb = Image.fromarray(frame_rgb)
            #below only works on pngs
            #frame_rgb = frame_rgb.quantize(method=Image.MEDIANCUT)
            #frame_rgb.save(save_path)
            
            #OpenCV stuff
            if self.ext_combobox.get() in ["jpg", "jpeg"]:
                imwrite(save_path, frame_rgb, [int(IMWRITE_JPEG_QUALITY), 100])
            else:
                imwrite(save_path, frame_rgb)
                
    def video_maker(self,  **kwargs):
        was_converted = False
        was_cut = False
        was_tuned = False
        was_resized = False
        was_cropped = False
        was_extracted = False
        was_bytten =  False
        
        codec_dict = {}
        cdc = ''
        
        current_ext = ''
        save_path = ''
        selected_file = ''
        start_seconds = 0.0
        end_seconds =  0.0
        conversion_value = ''
        resize_value = 0
        extraction_frame = 0
        byte_value = 0
        
        
        media = None
        
        
        
        
        
        if kwargs.get("was_converted"):
            was_converted =  kwargs["was_converted"]
        if kwargs.get("was_cut"):
            was_cut =  kwargs["was_cut"]
        if kwargs.get("was_tuned"):
            was_tuned =  kwargs["was_tuned"]
        if kwargs.get("was_resized"):
            was_resized =  kwargs["was_resized"]
        if kwargs.get("was_cropped"):
            was_cropped =  kwargs["was_cropped"]
        if kwargs.get("was_bytten"):
            was_bytten =  kwargs["was_bytten"]
            
        if kwargs.get("codec_dict"):
            codec_dict =  kwargs["codec_dict"]
        if kwargs.get("cdc"):
            cdc =  kwargs["cdc"]
            
        if kwargs.get("current_ext"):
            current_ext =  kwargs["current_ext"]
        if kwargs.get("save_path"):
            save_path =  kwargs["save_path"]
        if kwargs.get("selected_file"):
            selected_file =  kwargs["selected_file"]
        if kwargs.get("start_seconds"):
            start_seconds =  kwargs["start_seconds"]
        if kwargs.get("end_seconds"):
            end_seconds =  kwargs["end_seconds"]
        if kwargs.get("conversion_value"):
            conversion_value =  kwargs["conversion_value"]
        if kwargs.get("resize_value"):
            resize_value =  kwargs["resize_value"]
        if kwargs.get("extraction_frame"):
            extraction_frame =  kwargs["extraction_frame"]
        if kwargs.get("byte_value"):
            byte_value =  kwargs["byte_value"]
            
        if kwargs.get("media"):
            media =  kwargs["media"]
        
        cap = VideoCapture(selected_file)
        # Get General Info
        fps         = cap.get(CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(CAP_PROP_FRAME_COUNT))
        duration    = int(frame_count/fps)
        
        
        width       = int(cap.get(CAP_PROP_FRAME_WIDTH))  # float
        height      = int(cap.get(CAP_PROP_FRAME_HEIGHT)) # float
        
        og_width = width
        og_height = height
        
        
        
        cap.release()
        brate = 0

       
        '''
        if was_cut:
            byte_size = path.getsize(selected_file)
            frame_count = (end_seconds * fps) - (start_seconds * fps)
            duration = (frame_count / fps)
            brate = (byte_size * 8) / duration
        '''
        byte_size = path.getsize(selected_file) #width * height * 24
        if not was_bytten:
           
            if was_cropped or was_resized or was_cut:
                
                
                if was_cropped:
                    width = self.crop_ix2 - self.crop_ix1
                    height = self.crop_iy2 - self.crop_iy1
                
                resize_percent = resize_value/100
                
                if was_resized:
                    width = int(width * resize_percent)
                    height = int(height * resize_percent)
                    
                
                
                
            
                if was_cut:
                    frame_count = (end_seconds * fps) - (start_seconds * fps)
                    duration = (frame_count / fps)
                    
                    brate = (byte_size * 8) / duration
                    if og_width != width or og_height != height:
                        brate = brate * (width * height)/(og_width * og_height)
                else:
                    brate = (byte_size * 8) / duration
                    if og_width != width or og_height != height:
                        brate = brate * (width * height)/(og_width * og_height)
                    
            else:
                brate = (byte_size * 8) / duration
        else:
            brate = byte_value
        
            
        
        
            
        
        #print(brate)
        
        self.completion_bar.complete_progress_status_label["text"] = "Saving"
        media.write_videofile(save_path, 
                            codec = cdc, 
                            logger = self.completion_bar.logger, 
                            bitrate = str(brate)
        )
        self.completion_bar.complete_progress_status_label["text"] = "Finished"

    def edit_animated_media(self, save_path):
        
        was_converted = False
        was_cut = False
        was_tuned = False
        was_resized = False
        was_cropped = False
        was_extracted = False
        was_bytten = False

        codec_dict = {
                    
                    'mp4':'libx264',
                    'webm':'libvpx',
                    "mov":'libx264',
                    "avi":'libx264',
                    "mkv":'libx264',
                      
                      }
        cdc = ""
        
        current_ext = self.current_ext
        save_path = path_correction(save_path)
        selected_file = path_correction(self.selected_file_path)
        
        start_seconds = float(self.cut_start_spinbox.get()) 
        end_seconds =  float(self.cut_end_spinbox.get()) 
        conversion_value = self.convert_to_combobox.get()
        resize_value = int(self.resize_spinbox.get())
        volume_change = self.volume_scale.get()
        extraction_ext = self.ext_combobox.get()
        extraction_frame = self.ext_frame
        byte_value = int(self.final_bitrate_spinbox.get())
        
        #print()
        #print(save_path)
        #print(self.selected_file_path)
        
 
        
        

        video = VideoFileClip(selected_file)
        #AUDIO
        if not self.ext_checkbool.get():
            if current_ext != "gif":
                if self.audio_checkbool.get():
                    #was_tuned = not self.mute_checkbool.get() 
                
                    if volume_change == 100:
                        pass
                    elif volume_change == 0:
                        video = video.set_audio(None)
                        was_tuned = True
                    else:
                        print("vol changed")
                        video = afx.volumex(video, volume_change/100)
                        was_tuned = True
                elif not self.audio_checkbool.get():
                    pass
        #CUT
        if not self.ext_checkbool.get():
            if self.cut_checkbool.get():
                
                if start_seconds >= end_seconds or start_seconds < 0 or end_seconds < 0 or start_seconds > video.end or end_seconds > video.end:
                    pass
                else:
                    was_cut = True
                    video = video.subclip(start_seconds, end_seconds)
            elif not self.cut_checkbool.get():
                pass
            
        #CROP 
        if self.crop_checkbool.get():
            video = vfx.crop(video,  x1=self.crop_ix1 , y1=self.crop_iy1 , x2=self.crop_ix2 , y2=self.crop_iy2)
            was_cropped = True
        elif not self.crop_checkbool.get():
            pass
        
        #RESIZE
        if self.resize_checkbool.get():
            if resize_value == 100:
                pass
            else:
                was_resized = True
                video = video.resize(resize_value/100)
                
        elif not self.resize_checkbool.get():
            pass
        
        #CONVERSION
        if not self.ext_checkbool.get():
            if self.convert_to_checkbool.get():
                #"No Change", "mp4","ogv","webm","gif",   
                if conversion_value == "No Change" or conversion_value == current_ext:
                    if current_ext != "gif":
                        cdc = codec_dict[current_ext]
                        save_path = save_path #+ "." + current_ext
                    else:
                        save_path = save_path #+ "." + current_ext
                else:
                    if conversion_value != "gif":
                        cdc = codec_dict[conversion_value]
                        save_path = save_path #+ "." + conversion_value
                    else:
                        save_path = save_path #+ ".gif" 
                    was_converted = True
            elif not self.convert_to_checkbool.get():
                if current_ext != "gif":
                    cdc = codec_dict[current_ext]
        #BITRATE DECIDER
        if not self.ext_checkbool.get():
            if self.bitrate_checkbool.get():
                #if self.final_bitrate_spinbox.get() not in self.final_bitrate_label:
                byte_value = self.final_bitrate_spinbox.get()
                was_bytten = True
    
        #FRAME EXTRACTION
        if self.ext_checkbool.get():
            was_extracted = True
            #print("yep was extarcted")
            
        
                
                
        #Applying Changes
        if not was_converted and not was_cut and not was_tuned and not was_resized and not was_cropped and not was_extracted and not was_bytten and not was_extracted:
            messagebox.showerror("showinfo", "Make some type of change")
        else:
            if not was_extracted:
                #print("not extracting frame")
                if current_ext != 'gif':
                    if conversion_value == "gif":
                        self.gif_image_maker(
                            was_converted = was_converted,
                            was_cut = was_cut,
                            was_tuned = was_tuned,
                            was_resized = was_resized,
                            was_cropped = was_cropped,
                            was_extracted = was_extracted,
                            was_bytten = was_bytten,
                            
                            codec_dict = codec_dict,
                            cdc = cdc,
                            
                            current_ext = current_ext,
                            save_path = save_path,
                            selected_file = selected_file,
                            start_seconds = start_seconds,
                            end_seconds =  end_seconds,
                            conversion_value = conversion_value,
                            resize_value = resize_value,
                            extraction_ext = extraction_ext,
                            extraction_frame = extraction_frame,
                            
                            media = video
                        )
                        
                        
                        
                        
                        
                    else:
                        #generic video edit
                        self.video_maker(
                            was_converted = was_converted,
                            was_cut = was_cut,
                            was_tuned = was_tuned,
                            was_resized = was_resized,
                            was_cropped = was_cropped,
                            was_extracted = was_extracted,
                            was_bytten = was_bytten,
                            
                            codec_dict = codec_dict,
                            cdc = cdc,
                            
                            current_ext = current_ext,
                            save_path = save_path,
                            selected_file = selected_file,
                            start_seconds = start_seconds,
                            end_seconds =  end_seconds,
                            conversion_value = conversion_value,
                            resize_value = resize_value,
                            extraction_ext = extraction_ext,
                            extraction_frame = extraction_frame,
                            byte_value = byte_value,
                            
                            media = video
                        )
                        
                elif current_ext == 'gif':
                    if was_converted:
                        #gif to video
                        self.video_maker(
                            was_converted = was_converted,
                            was_cut = was_cut,
                            was_tuned = was_tuned,
                            was_resized = was_resized,
                            was_cropped = was_cropped,
                            was_extracted = was_extracted,
                            was_bytten = was_bytten,
                            
                            codec_dict = codec_dict,
                            cdc = cdc,
                            
                            current_ext = current_ext,
                            save_path = save_path,
                            selected_file = selected_file,
                            start_seconds = start_seconds,
                            end_seconds =  end_seconds,
                            conversion_value = conversion_value,
                            resize_value = resize_value,
                            extraction_ext = extraction_ext,
                            extraction_frame = extraction_frame,
                            byte_value = byte_value,
                            
                            media = video
                        )
                        
                    else:
                        #converting a gif to a gif
                        self.gif_image_maker(
                            was_converted = was_converted,
                            was_cut = was_cut,
                            was_tuned = was_tuned,
                            was_resized = was_resized,
                            was_cropped = was_cropped,
                            was_extracted = was_extracted,
                            was_bytten = was_bytten,
                            
                            codec_dict = codec_dict,
                            cdc = cdc,
                            
                            current_ext = current_ext,
                            save_path = save_path,
                            selected_file = selected_file,
                            start_seconds = start_seconds,
                            end_seconds =  end_seconds,
                            conversion_value = conversion_value,
                            resize_value = resize_value,
                            extraction_ext = extraction_ext,
                            extraction_frame = extraction_frame,
                            media = video
                        )
            else:
                #print("extracting frame")
                self.gif_image_maker(
                        was_converted = was_converted,
                        was_cut = was_cut,
                        was_tuned = was_tuned,
                        was_resized = was_resized,
                        was_cropped = was_cropped,
                        was_extracted = was_extracted,
                        
                        codec_dict = codec_dict,
                        cdc = cdc,
                        
                        current_ext = current_ext,
                        save_path = save_path,
                        selected_file = selected_file,
                        start_seconds = start_seconds,
                        end_seconds =  end_seconds,
                        conversion_value = conversion_value,
                        resize_value = resize_value,
                        extraction_ext = extraction_ext,
                        extraction_frame = extraction_frame,
                        media = video
                    )
    
    def edit_static_media(self, save_path):
        was_converted = False
        was_cut = False
        was_tuned = False
        was_resized = False
        was_cropped = False
        was_extracted = False
        
        codec_dict = {'mp4':'libx264','ogv':'libtheora','webm':'libvpx', "mov":'libx264'}
        cdc = ""
        
        current_ext = self.current_ext
        save_path = path_correction(save_path)
        selected_file = path_correction(self.selected_file_path)
        
        start_seconds = float(self.cut_start_spinbox.get()) 
        end_seconds =  float(self.cut_end_spinbox.get()) 
        conversion_value = self.convert_to_combobox.get()
        resize_value = int(self.resize_spinbox.get())
        volume_change = self.volume_scale.get()
        extraction_ext = self.ext_combobox.get()
        extraction_frame = self.ext_frame
        byte_value = int(self.final_bitrate_spinbox.get())
        
        #CROP 
        if self.crop_checkbool.get():
            was_cropped = True
        elif not self.crop_checkbool.get():
            pass
        
        #RESIZE
        if self.resize_checkbool.get():
            if resize_value == 100:
                pass
            else:
                was_resized = True
                
                
        elif not self.resize_checkbool.get():
            pass
        
        #FRAME EXTRACTION
        if self.ext_checkbool.get():
            was_extracted = True
            print("yep was extarcted")
        
        
        if not was_resized and not was_cropped and not was_extracted:
            messagebox.showerror("showinfo", "Make some type of change")
        else:
            #if not was_extracted:
                #print("not extracting frame")
   
            self.gif_image_maker(
                was_converted = was_converted,
                was_cut = was_cut,
                was_tuned = was_tuned,
                was_resized = was_resized,
                was_cropped = was_cropped,
                was_extracted = was_extracted,
                
                codec_dict = codec_dict,
                cdc = cdc,
                
                current_ext = current_ext,
                save_path = save_path,
                selected_file = selected_file,
                start_seconds = start_seconds,
                end_seconds =  end_seconds,
                conversion_value = conversion_value,
                resize_value = resize_value,
                extraction_ext = extraction_ext,
                extraction_frame = extraction_frame,
                
            )
                    
            

class MediaFrameNav(ttk.Frame):
    #https://techvidvan.com/tutorials/python-image-viewer/
    #https://www.geeksforgeeks.org/convert-opencv-image-to-pil-image-in-python/
    #https://stackoverflow.com/questions/41656176/tkinter-canvas-zoom-move-pan/48137257#48137257
    #https://note.nkmk.me/en/python-opencv-pillow-image-size/
    ##https://gist.github.com/laygond/d62df2f2757671dea78af25a061bf234#file-writevideofromimages-py-L25
    #https://theailearner.com/2021/05/29/creating-gif-from-video-using-opencv-and-imageio/
    #https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
    #https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse
    #https://stackoverflow.com/questions/32289175/list-of-all-tkinter-events
    
    def __init__(self, parent, canvas_width: int, canvas_height: int, **kwargs):
        super().__init__(parent)

        self.static_filetypes = ['png', 'jpg', 'jpeg','webp', 'tiff', 'tif', 'webp', 'bmp']
        self.animated_filetypes =  ["mp4", "mov", "webm", "gif", "avi", "mkv"] 

        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=3)
        #self.rowconfigure(0, weight=1)

        self.bck_btn = ttk.Button(self, text='Back',command=self.Back)
        
        self.nxt_btn = ttk.Button(self, text='Next',command=self.Next)
        
        
        
        
        #canvas crop
        #self.pil_image = None   # Image data to be displayed

        self.zoom_cycle = 0
        
        
        self.og_image_scale = 0
        self.current_frame = 0
        self.frame_seconds = 0
        

        self.media = None
        self.current_img = None
        self.rect = None
        
        self.rect_x = None
        self.rect_y = None
        self.rect_w = None
        self.rect_h = None
        
        #General Info
        self.file_name   = None
        self.fps         = None
        self.frame_count = None
        self.duration    = None
        self.width       = None
        self.height      = None
        
    
        
        self.image_ratio = 0
        
        self.interval_spinbox_label = ttk.Label(self, text = "Frame Step")
        self.interval_spinbox= ttk.Spinbox(self, 
                                        from_ = 1, 
                                        to = 10,
                                        width = 10
                                        )
        self.interval_spinbox.set(1)
        
        self.total_frame_label = ttk.Label(self, text = f"Total Frames: 0")
        
        self.current_frame_label = ttk.Label(self, text = f"Current Frame: 0")
        
        
        #self.general_info_label = ttk.Label(self, text = f"Current Frame: 0")
        
        
        #self.scale_label = tk.Label(self, text = "scale:")
        #self.scale_label.pack()
        
        #self.position_mouse_label = tk.Label(self, text = "Canvas MX:0 Canvas MY:0")
        #self.image_pos_mouse_label = tk.Label(self, text = "Image MX:0 Image MY:0")
        #self.image_scale_ratio_label = tk.Label(self, text = "Scale X:0 Scale Y:0")
        #self.image_scale_ratio_label2 = tk.Label(self, text = "Scale X:0 Scale Y:0")
        
        #self.label_rx = ttk.Label(self, text="rect x")
        #self.label_ry = ttk.Label(self, text="rect y")
        #self.label_rw = ttk.Label(self, text="rect w")
        #self.label_rh = ttk.Label(self, text="rect h")
        
        self.current_ext = ""
        
        
        self.path_label =  tk.Label(self, text = "FilePath: ")
        
        self.path_listbox = tk.Listbox(self, 

                                       height=1,
                                       width=82
                                       )
        
        self.path_scrollbar_x = tk.Scrollbar(self, orient = 'horizontal', command=self.path_listbox.xview)
        self.path_listbox.config(xscrollcommand=self.path_scrollbar_x.set)
        
        
        
        #self.file_info = tk.Label(self, text = "General: ")
        
       
        
        
        
        # Canvas
        self.canvas = tk.Canvas(self, background="black", width = canvas_width,height = canvas_height)
        #self.canvas = tk.Canvas(self, background="black")
        
 
        
        
        
        
        
        
    
        # Controls
        self.canvas.bind("<ButtonPress-3>", self.on_button_clear)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        
        self.canvas.bind("<ButtonPress-1>", self.mouse_down_left)                   # MouseDown
        #self.canvas.bind("<B1-Motion>", self.mouse_move_left)                  # MouseDrag
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left)    # MouseDoubleClick
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)                     # MouseWheel
        
        
        #self.canvas.bind("<Button-1>", self.get_canvas_mouse_pos)
        
        self.arb_params = None 
        if kwargs.get("param_arbs"):
            self.arb_params = kwargs["param_arbs"]
            
            
        self.gen_info = None 
        if kwargs.get("info_gen"):
            self.gen_info = kwargs["info_gen"]
        
        #Placement
        
        
        '''
        self.nxt_btn.grid(row=0, column=0)
        self.bck_btn.grid(row=0, column=2)
        self.canvas.grid(row=4, column=1)
        self.current_frame_label.grid(row=3, column=2)
        self.interval_spinbox.grid(row=1, column=2)
        
        self.position_mouse_label.grid(row=0, column=1)
        self.image_pos_mouse_label.grid(row=1, column=1)
        self.image_scale_ratio_label.grid(row=2, column=1)
        self.image_scale_ratio_label2.grid(row=3, column=1)
        self.label_rx.grid(row = 5, column = 1)
        self.label_ry.grid(row = 6, column = 1)
        self.label_rw.grid(row = 7, column = 1)
        self.label_rh.grid(row = 9, column = 1)
        self.total_frame_label.grid(row=2, column=2)
        '''
        
        
        
        arrangement = [
            
            [self.bck_btn, self.path_label   , self.nxt_btn                ],
            [None        , self.path_listbox , self.interval_spinbox_label ],
            [None        , self.path_scrollbar_x, self.interval_spinbox    ],
            [None        , self.canvas       , None                        ],
            [None        , None              , None                        ],
            [None        , None              , None                        ],
            [None        , None              , None                        ],
            [None        , None              , None                        ]
                            
            
            
            
            
        ]
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):
                #self.grid_columnconfigure(ind_x, minsize=20)
                #self.grid_rowconfigure(ind_y, minsize=20)
                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                 
                    arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "EW")
        
    def set_path_listbox(self, filepath):
        if self.path_listbox.size() > 0:
            self.path_listbox.delete(0, tk.END)
        self.path_listbox.insert(0, filepath)
        
    def set_frame(self, file_path):
        if not file_path:
            return
        
        
        
        
        self.current_ext = file_path.split(".")[-1]
        self.file_name = "\\".join(file_path.split('/')[-1:])
        print("File Current EXT: {}".format(self.current_ext))
        if self.current_ext in self.animated_filetypes:
            #if self.media != None:
            #    self.media.release()
            
            self.media =  VideoCapture(file_path)
            self.fps         = self.media.get(CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            self.frame_count = int(self.media.get(CAP_PROP_FRAME_COUNT))
            self.duration    = int(self.frame_count/self.fps)
            self.width       = int(self.media.get(CAP_PROP_FRAME_WIDTH))  # float
            self.height      = int(self.media.get(CAP_PROP_FRAME_HEIGHT)) # float
            
            
            self.current_frame = 0
            

            
            file_size = path.getsize(file_path)
            
            
            brate = 0
            if self.current_ext == "gif":
                brate = 1
            else:
                brate = (file_size * 8) / (self.frame_count / self.fps)
            
            
            if self.gen_info != None:
                self.gen_info.set_info(
                    
                    file_name = self.file_name,
                    fps = self.fps,
                    frame_count = self.frame_count,
                    duration = self.duration,
                    width = self.width,
                    height = self.height,
                    current_frame = self.current_frame,
                    current_second = 1,
                    bitrate = brate
                    
                    
                    
                    
                )
                
            if self.arb_params != None:
                self.arb_params.update_current_ext_frame_label(self.current_frame)
                self.arb_params.update_final_bitrate(brate)
            
            #print("GIF FPS:{}".format(self.fps))
            
            
            self.media.set(CAP_PROP_POS_FRAMES, self.current_frame)
            
            #img is a frame of the video
            ret, img = self.media.read()
            #conversion from CV2 Image Data a into a Pillow Image        
            self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
            
            
            #self.img_label = ttk.Label(self, image = self.current_img)
            #self.img_label.pack()
            self.interval_spinbox.config(from_ = 1, to = int(self.frame_count/3))
            
    
            #self.interval_spinbox.set(1)
            
            
            
            
            self.total_frame_label.config(text = f"Total Frames: {self.frame_count}")
            #print("Gif Width:{} Gif Height:{}".format(self.current_img.width, self.current_img.height))
            #can be image width or height
            #original image width before resize
            self.og_image_scale = self.width
            
            #self.canvas.config(width=self.current_img.width, height=self.current_img.height)
            
            #self.nu_image_scale_w, self.nu_image_scale_h = self.og_image_scale_w, self.og_image_scale_h
            # Set the affine transformation matrix to display the entire image.
            self.zoom_fit(self.current_img.width, self.current_img.height)
            # To display the image
            self.draw_image(self.current_img)
        elif self.current_ext in self.static_filetypes:
            #if self.media != None:
            #    self.media.release()
                
            self.media =  imread(file_path)
            self.fps         = 0      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            self.frame_count = 1
            self.duration    = 0
            self.width, self.height, _ = self.media.shape       
            
            
            self.current_frame = 0
            

            
            file_size = path.getsize(file_path)
            
            #print(vid_size)
            #brate = int((vid_size/((video.duration/60) * .0075)) * 1000000 * 0.9)
            brate = 1
            
            
            if self.gen_info != None:
                self.gen_info.set_info(
                    
                    file_name = self.file_name,
                    fps = self.fps,
                    frame_count = self.frame_count,
                    duration = self.duration,
                    width = self.width,
                    height = self.height,
                    current_frame = self.current_frame,
                    current_second = 1,
                    bitrate = brate
                    
                    
                    
                    
                )
                
            if self.arb_params != None:
                self.arb_params.update_current_ext_frame_label(self.current_frame)
            
            #print("GIF FPS:{}".format(self.fps))
            
            
            #self.media.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            
            #img is a frame of the video
            #ret, img = self.media.read()
            #conversion from CV2 Image Data a into a Pillow Image        
            self.current_img = Image.fromarray(cvtColor(self.media, COLOR_BGR2RGB))
            
            
            #self.img_label = ttk.Label(self, image = self.current_img)
            #self.img_label.pack()
            self.interval_spinbox.config(from_ = 0, to = 1)
            
    
            #self.interval_spinbox.set(1)
            
            
            
            
            self.total_frame_label.config(text = f"Total Frames: {self.frame_count}")
            #print("Gif Width:{} Gif Height:{}".format(self.current_img.width, self.current_img.height))
            #can be image width or height
            #original image width before resize
            self.og_image_scale = self.width
            
            #self.canvas.config(width=self.current_img.width, height=self.current_img.height)
            
            #self.nu_image_scale_w, self.nu_image_scale_h = self.og_image_scale_w, self.og_image_scale_h
            # Set the affine transformation matrix to display the entire image.
            self.zoom_fit(self.current_img.width, self.current_img.height)
            # To display the image
            self.draw_image(self.current_img)
        
    def get_frame(self):
        return self.current_frame
        
    def Next(self):

        
        if self.current_ext in self.animated_filetypes:
        
            if self.current_img == None:
                return
            
            self.canvas.delete("image")
            #global i
            #i = i + 1
            #try:
            self.current_frame += int(self.interval_spinbox.get())
            if self.current_frame > self.frame_count - 1:
                self.current_frame = self.current_frame%self.frame_count
            
            self.media.set(CAP_PROP_POS_FRAMES, self.current_frame)
            
            #img is a frame of the video
            ret, img = self.media.read()
            #conversion from CV2 Image Data a into a Pillow Image        
            self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
            
            #self.img_label.config(image=self.current_img)
            self.current_frame_label.config(text = f"Current Frame: {self.current_frame}")
            
            if self.gen_info != None:
                if self.current_frame != 0:
                    self.gen_info.set_info(
                        current_frame = self.current_frame,
                        current_second = (self.fps**-1) * self.current_frame
                    )
                else:
                     self.gen_info.set_info(
                        current_frame = self.current_frame,
                        current_second = 0
                    )
                     
            if self.arb_params != None:
                self.arb_params.update_current_ext_frame_label(self.current_frame)
            

            self.zoom_fit(self.current_img.width, self.current_img.height)
            self.update()
        elif self.current_ext in self.static_filetypes:
            pass

        
            
    def Back(self):

        
        if self.current_ext in self.animated_filetypes:
            if self.current_img == None:
                return
            self.canvas.delete("image")
            
            self.current_frame -= int(self.interval_spinbox.get())
            
            if self.current_frame < 0:
                self.current_frame = abs(self.frame_count + self.current_frame) 
                
            self.media.set(CAP_PROP_POS_FRAMES, self.current_frame)
            
            #img is a frame of the video
            ret, img = self.media.read()
            #conversion from CV2 Image Data a into a Pillow Image        
            self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
            
            
            
            #self.img_label.config(image=self.current_img)
            self.current_frame_label.config(text = f"Current Frame: {self.current_frame}")
            
            if self.gen_info != None:
                if self.current_frame != 0:
                    self.gen_info.set_info(
                        current_frame = self.current_frame,
                        current_second = (self.fps**-1) * self.current_frame
                    )
                else:
                     self.gen_info.set_info(
                        current_frame = self.current_frame,
                        current_second = 0
                    )
                     
            if self.arb_params != None:
                self.arb_params.update_current_ext_frame_label(self.current_frame)
            
            
            self.zoom_fit(self.current_img.width, self.current_img.height)
            self.update()
        elif self.current_ext in self.static_filetypes:
            pass

        

    
    
    
    
    # -------------------------------------------------------------------------------
    # Mouse events
    # -------------------------------------------------------------------------------
    def on_button_clear(self, event):
        if self.arb_params != None:
                self.arb_params.update_crop_widget_labels(
                    canvas_x1 = -1,
                    canvas_y1 = -1,
                    canvas_x2 = -1,
                    canvas_y2 = -1,
                    image_x1 = -1,
                    image_y1 = -1,
                    image_x2 = -1,
                    image_y2 = -1
                )
        self.canvas.delete("rect")
        
    def mouse_down_left(self, event):
        
        self.__old_event = event
        
        
        
        self.get_canvas_mouse_pos(event)
        
    def get_canvas_mouse_pos(self, event):
        if self.current_img == None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        #self.position_mouse_label.config(text= f"Canvas MX: {x} Canvas MY: {y}")
        
        
        
        
        xny = self.to_image_point(x, y)
        if len(xny) != 0:
            x = xny[0]
            y = xny[1]
            
            #self.rect_x, self.rect_y, self.rect_w, self.rect_h = 0, 0, 0, 0
            
            self.rect_x = self.canvas.canvasx(event.x)
            self.rect_y = self.canvas.canvasx(event.y)
            
            #self.image_pos_mouse_label.config(text = f"Image MX:{x} Image MY:{y}")
            
            
            
            self.canvas.delete("rect")
            # create rectangle if not yet exist
            if not self.rect:
                #pass
                self.rect = self.canvas.create_rectangle(self.rect_x, self.rect_y, 1, 1, outline='black', tags=("rect"))
         
    def on_move_press(self, event):
        if self.current_img == None:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        
        

        '''
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9*w:
            self.canvas.xview_scroll(1, 'units') 
        elif event.x < 0.1*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.canvas.yview_scroll(1, 'units') 
        elif event.y < 0.1*h:
            self.canvas.yview_scroll(-1, 'units')

        '''
        # expand rectangle as you drag the mouse
        # expand rectangle as you drag the mouse
        
        rw = curX - self.rect_x
        rh = curY - self.rect_y
        rx = self.rect_x
        ry = self.rect_y
        
        if rw < 0:
            rx = abs(rx + rw)
            rw = abs(rw)
        if rh < 0:
            ry = abs(ry + rh)
            rh = abs(rh)
        
            
        
        image_xy = self.to_image_point(rx, ry)
        image_wh = self.to_image_point(rw, rh)
        
        #frame_rgb[self.crop_iy1:abs(self.crop_iy2 - self.crop_iy1), self.crop_ix1:abs(self.crop_ix2 - self.crop_ix1)]
        

        if len(image_xy) > 0 and len(image_wh) > 0:
            ix = image_xy[0]
            iy = image_xy[1]   
            
            iw = image_wh[0]
            ih = image_wh[1]
            
            #self.label_rx.config(text= "canvas rect x: {:.2f}".format(rx) + " image rect x: {:.2f}".format(ix))
            #self.label_ry.config(text= "canvas rect y: {:.2f}".format(ry) + " image rect y: {:.2f}".format(iy))
            #self.label_rw.config(text= "canvas rect w: {:.2f}".format(rx + rw) + " image rect w: {:.2f}".format(iw))
            #self.label_rh.config(text= "canvas rect h: {:.2f}".format(ry + rh) + " image rect h: {:.2f}".format(ih))
            

            self.canvas.delete("rect")
            
            self.rect = self.canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline='black', tags=("rect"))
        
        
           
            self.canvas.tag_raise("rect", "image")   
            
            if self.arb_params != None:
                self.arb_params.update_crop_widget_labels(
                    canvas_x1 = rx,
                    canvas_y1 = ry,
                    canvas_x2 = rx + rw,
                    canvas_y2 = ry + rh,
                    image_x1 = ix,
                    image_y1 = iy,
                    image_x2 = ix + iw,
                    image_y2 = iy + ih,
                    
                )
                
    def mouse_move_left(self, event):
        if self.current_img == None:
            return
        
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        #self.__old_event = event

    def mouse_double_click_left(self, event):
        if self.current_img == None:
            return
        if self.current_ext != 'gif':
            self.zoom_fit(self.current_img.width, self.current_img.height)
            self.redraw_image() 
        else:
            self.zoom_fit(self.gif.width, self.gif.height)
            self.redraw_image() 
        
    def mouse_wheel(self, event):
        
        
        if self.current_img == None:
            return
        
        
        
        

        if (event.delta < 0):
            if self.zoom_cycle <= 0:
                return
            # Rotate upwards and shrink
            self.scale_at(0.8, event.x, event.y)
            self.zoom_cycle -= 1
        else:
            if self.zoom_cycle >= 9:
                return
            #  Rotate downwards and enlarge
            self.scale_at(1.25, event.x, event.y)
            self.zoom_cycle += 1
    
        self.redraw_image() # Refresh
        
    # -------------------------------------------------------------------------------
    # Affine Transformation for Image Display
    # -------------------------------------------------------------------------------

    def reset_transform(self):
        self.mat_affine = eye(3) # 3x3の単位行列

    def translate(self, offset_x, offset_y,zoom = False):
        mat = eye(3) # 3x3 identity matrix
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)
        # Get the current canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Get the current scale
        scale = self.mat_affine[0, 0]
        
        im_bounds_w = 0 
        im_bounds_h = 0 
        
        
        im_bounds_w = self.current_img.width
        im_bounds_h = self.current_img.height

        max_y = scale * im_bounds_h #3072
        max_x = scale * im_bounds_w #4096
        
        self.mat_affine = dot(mat, self.mat_affine)

        if not zoom:
            if abs(self.mat_affine[0,2]) > abs(max_x-canvas_width):
                self.mat_affine[0,2] = -(max_x-canvas_width)
            if abs(self.mat_affine[1,2]) > abs(max_y-canvas_height):
                self.mat_affine[1,2] = -(max_y-canvas_height)

        if self.mat_affine[0, 2] > 0.0:
            self.mat_affine[0, 2] = 0.0
        if self.mat_affine[1,2] > 0.0:
            self.mat_affine[1,2]  = 0.0

    def scale(self, scale:float):
        mat = eye(3) # 3x3 identity matrix

        mat[0, 0] = scale
        mat[1, 1] = scale
        
        
        self.mat_affine = dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        #self.scale_label.config(text=f"scale: {scale}")
        # Translate to the origin
        self.translate(-cx, -cy, True)
        # Scale
        self.scale(scale)
        # Restore
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):

        # Update canvas object and get size
        self.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # Initialization of affine transformation
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0
        if (canvas_width * image_height) > (image_width * canvas_height):
            # The widget is horizontally elongated (resizing the image vertically)
            scale = canvas_height / image_height
            # Align the remaining space to the center by offsetting horizontally
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # The widget is vertically elongated (resizing the image horizontally)
            scale = canvas_width / image_width
            # Align the remaining space to the center by offsetting vertically
            offsety = (canvas_height - image_height * scale) / 2
            
            
            
        #self.image_ratio = self.og_image_scale / (self.og_image_scale * scale)
        #self.image_scale_ratio_label.config(text = f"Resized Image ratio to Original Image: {scale}")
        #self.image_scale_ratio_label2.config(text = "Original Image ratio to Resized Image: {}".format(self.image_ratio))
    
        
        # Scale
        self.scale(scale)
        # Align the remaining space to the center
        self.translate(offsetx, offsety)
        self.zoom_cycle = 0
        self.redraw_image()

    def to_image_point(self, x, y):
        #Convert coordinates from the canvas to the image
        if self.current_img == None:
            return []
        # Convert coordinates from the image to the canvas by taking the inverse of the transformation matrix.
        mat_inv = linalg.inv(self.mat_affine)
        image_point = dot(mat_inv, (x, y, 1.))

        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.current_img.width or image_point[1] > self.current_img.height:
            return []


        return image_point

    # -------------------------------------------------------------------------------
    # Drawing 
    # -------------------------------------------------------------------------------

    def draw_image(self, pil_image):
        
        self.update()
        self.canvas.delete("image")
        #self.canvas.delete("rect")
        
        if pil_image == None:
            return


        self.current_img = pil_image


        # Canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate the affine transformation matrix from canvas to image data
        # (Calculate the inverse of the display affine transformation matrix)
        mat_inv = linalg.inv(self.mat_affine)

        # Convert the numpy array to a tuple for affine transformation
        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
        )

        # Apply affine transformation to the PIL image data
        dst = self.current_img.transform(
            (canvas_width, canvas_height),  # Output size
            Image.AFFINE,   # Affine transformation
            affine_inv,     # Affine transformation matrix (conversion matrix from output to input)
            Image.NEAREST   # Interpolation method, nearest neighbor
        )

        
        im = ImageTk.PhotoImage(image=dst)
        
        

        # Draw the image
        item = self.canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=im,        # Display image data
            tags = ("image")
            
        )
        self.image = im
        self.canvas.tag_raise("rect", "image")
        
    def redraw_image(self):
        #Redraw the image
        #if self.current_ext != "gif":
        if self.current_img == None:
            return
        self.draw_image(self.current_img)
        #else:
        #    if self.gif == None:
        #        return
        #    self.draw_image(self.gif)
        
        
    



if __name__ == "__main__":
    app = Application()
    #app.geometry("800x600")
    app.resizable()
    app.mainloop()
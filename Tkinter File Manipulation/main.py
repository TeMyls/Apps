import os
#from PIL import Image
from moviepy.editor import VideoFileClip,concatenate_videoclips,AudioFileClip,vfx,CompositeAudioClip
#import math
#import numpy as np
#from numpy import asarray
from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration
from proglog import ProgressBarLogger
#import cv2
import tkinter as tk
from tkinter import ttk, filedialog

#import potrace



class MyBarLogger(ProgressBarLogger):
    def __init__(self):
        super().__init__()
        self.last_message = ''
        self.previous_percentage = 0    
    
    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        for (parameter, value) in changes.items():
            # print ('Parameter %s is now %s' % (parameter, value))
            self.last_message = value
    
    def bars_callback(self, bar, attr, value,old_value=None):
        # Every time the logger progress is updated, this function is called        
        if 'Writing video' in self.last_message:
            percentage = (value / self.bars[bar]['total']) * 100
            if percentage > 0 and percentage < 100:
                if int(percentage) != self.previous_percentage:
                    self.previous_percentage = int(percentage)
                    print(self.previous_percentage)
                    


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Edit App")

        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=3)
        #self.rowconfigure(0, weight=1)

        frame = PathForm(self)
        frame.grid(row=0, column=0, sticky="NW")
        
        


        
class PathForm(ttk.Frame):
    
    
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        #self.columnconfigure(1, weight=1, uniform="a")
        #self.rowconfigure(1, weight=1, uniform="a")
     
        
        
        codec_dict = {'mp4':'libx264','ogv':'libtheora','webm':'libvpx'}
        

        #open save button
        self.selected_file_open_button = tk.Button(self, text="Open File(s)", command=self.open_files)
    
        
        self.selected_file_label = ttk.Label(self, text="Selected File(s)")
        

        self.selected_file_scrollbar_y = ttk.Scrollbar(self, orient='vertical')
        self.selected_file_scrollbar_x = ttk.Scrollbar(self, orient='horizontal')
        
        self.selected_file_listbox = tk.Listbox(self, 
                                                yscrollcommand = self.selected_file_scrollbar_y.set,
                                                xscrollcommand = self.selected_file_scrollbar_x.set,
                                                selectmode="multiple", 
                                                exportselection=False
                                                )
        
        self.selected_file_scrollbar_x.config(command=self.selected_file_listbox.xview)
        self.selected_file_scrollbar_y.config(command=self.selected_file_listbox.yview)
        self.selected_file_clear_button = tk.Button(self, text="Clear Files", command=self.clear_files)
        #Batch or By File
        
        #Conversion Button
        self.convert_to_label= ttk.Label(self, text="Convert To")
        
        self.convert_to_combobox = ttk.Combobox(self, width = 15,  textvariable = tk.StringVar()) 
        
        self.convert_to_combobox["values"] = (  "No Change",
                                                "mp4",
                                                "ogv",
                                                "webm",
                                                "gif",
                                              )
       
        #Mute
        self.audio_label = ttk.Label(self, text="Audio")
        self.muted_label = ttk.Label(self, text="muted")
        self.mute_checkbutton = ttk.Checkbutton(self,   
                                                onvalue = 0,
                                                offvalue = 1
                                                
                                                ) 
        
        #Resize
        self.resize_label = ttk.Label(self, text = "Resize")
        self.resize_spinbox= ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 500,
                                        width = 10
                                        
                                        )
        
        self.resize_spinbox.set("100")
        
        
        #Cut
        self.cut_label = ttk.Label(self, text = "Cut")
        self.start_cut_label = ttk.Label(self, text = "Start Time:")
        self.end_cut_label = ttk.Label(self, text = "End Time:")
        
        self.cut_start_spinbox = ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 100
                                        ) 
        self.cut_end_spinbox = ttk.Spinbox(self, 
                                        from_ = 0,
                                        to = 100
                                        ) 
                         
  
        
        
        #Save
        self.save_path_label = ttk.Label(self, text="Save Path")
        self.save_name_label = ttk.Label(self, text="File Name")
        
        self.save_name_entry = ttk.Entry(self)
        self.save_path_scrollbar_x = ttk.Scrollbar(self, orient='horizontal')
        self.save_path_listbox = tk.Listbox(self,
                                              xscrollcommand = self.save_path_scrollbar_x.set
                                            )
        
        self.save_path_scrollbar_x.config(command=self.save_path_listbox.xview)
        self.save_path_button = tk.Button(self, text="Select Folder", command=self.get_directory)
        self.save_true = tk.Button(self, text="Save", command=self.save_files)
        
        
        
        
        
        #Combine
        self.combine_label = ttk.Label(self, text="Combine Videos")
        self.combine_scrollbar_x = ttk.Scrollbar(self, orient='horizontal')
        self.combine_scrollbar_y = ttk.Scrollbar(self, orient='vertical')
        self.combine_listbox = tk.Listbox(self,
                                              xscrollcommand = self.save_path_scrollbar_x.set,
                                              yscrollcommand = self.combine_scrollbar_y.set,
                                              selectmode="multiple", 
                                              exportselection=0
                                            )
        
        
        self.combine_scrollbar_x.config(command=self.combine_listbox.xview)
        self.combine_scrollbar_y.config(command=self.combine_listbox.yview)
        
        self.combine_listbox.bind("<<ListboxSelect>>", lambda _: self.get_selected_videos(self.combine_listbox))
        
        #Crop
        #self.crop_label = ttk.Label(self, text="Crop Video")
        #self.crop_video_img_canavs = tk.Canvas(self)
        
        
        
        
        #Selection Type
        self.type_selection_label = ttk.Label(self, text = "Selection Type")
        self.type_selection_svar = tk.StringVar()
        self.type_selection_svar.set("Single")
        
        self.type_selection_radiobutton1 = ttk.Radiobutton(self, text="Single", 
                                                           variable=self.type_selection_svar,
                                                           value = "Single",
                                                           command=self.get_type_sel)
        self.type_selection_radiobutton2 = ttk.Radiobutton(self, text="Multiple", 
                                                           variable=self.type_selection_svar,
                                                           value = "Multiple",
                                                           command=self.get_type_sel)
        
        
  
        
        self.multiple_selection_widgets = [
            self.combine_label,
            self.combine_listbox,
            self.combine_scrollbar_x,
            self.combine_scrollbar_y
        ]
        
        
        
        self.static_widgets = [
            self.selected_file_label,
            self.selected_file_listbox,
            self.selected_file_scrollbar_x,
            self.selected_file_scrollbar_y,
            self.selected_file_open_button,
            self.selected_file_clear_button,
            
            self.type_selection_label,
            self.type_selection_radiobutton1,
            self.type_selection_radiobutton2,
            
            self.save_path_label,
            self.save_path_listbox,
            self.save_path_scrollbar_x,
            self.save_path_button,
            self.save_name_label,
            self.save_name_entry,
            self.save_true
            
        ]
        
        
        #grid positions

        
        arrangement = [
            [self.selected_file_label      , None                          , self.convert_to_label   , self.combine_label     , None                     , self.resize_label    , self.save_path_label        ],
            [self.selected_file_listbox    , self.selected_file_scrollbar_y, self.convert_to_combobox, self.combine_listbox   , self.combine_scrollbar_y ,  self.resize_spinbox , self.save_path_listbox      ],
            [self.selected_file_scrollbar_x, None                          , None                    ,self.combine_scrollbar_x, None                     , None                 , self.save_path_scrollbar_x  ],
            [self.selected_file_open_button, None                          , None                    , None                   , None                     , None                 , self.save_path_button       ],
            [self.selected_file_clear_button,None                          , None                    , self.cut_label         , self.audio_label         , None                 , self.save_name_label        ],                     
            [self.type_selection_label     , None                          ,  self.start_cut_label   , self.cut_start_spinbox , self.mute_checkbutton    , self.muted_label     , self.save_name_entry        ],    
            [self.type_selection_radiobutton1, None                        ,  self.end_cut_label     , self.cut_end_spinbox   , None                     , None                 , self.save_true              ],  
            [self.type_selection_radiobutton2, None                        , None                    , None                   , None                     , None                 , None                      ], 
            [None                          , None                          , None                    , None                   , None                     , None                 , None                        ]                       
            
            
        ]
        
        
        for ind_y in range(len(arrangement)):
            for ind_x in range(len(arrangement[ind_y])):
                #self.grid_columnconfigure(ind_x, minsize=20)
                #self.grid_rowconfigure(ind_y, minsize=20)
                if arrangement[ind_y][ind_x] == None:
                    pass
                else:
                    if isinstance(arrangement[ind_y][ind_x], tk.Label):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "E")
                    elif isinstance(arrangement[ind_y][ind_x], tk.Scrollbar):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NEWS")
                    elif isinstance(arrangement[ind_y][ind_x], tk.Spinbox):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "N", columnspan = 1)
                    elif isinstance(arrangement[ind_y][ind_x], tk.Button):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NWES", columnspan = 1)
                    else:
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NW")
                
                
        self.get_type_sel()            
        test = "C:/Users/Tlmyl/Downloads/Downloads/Scripts/Simple Scripts"
        blank = "/"
        self.last_folder = test
        self.logger = MyBarLogger()

        
        
    def get_type_sel(self):
        type_sel = self.type_selection_svar.get()
        #for ind_y in range(len(arrangement)):
            #for ind_x in range(2, len(arrangement[ind_y]) - 1):
        for widget in self.winfo_children():
            print("Yes")
          
            #and  widget in self.static_widgets
            if type_sel == "Single":
                if widget in self.multiple_selection_widgets:
                    widget.grid_remove()
                else:
                    widget.grid()
            elif type_sel == "Multiple":
                if widget in self.multiple_selection_widgets:
                    widget.grid()
                else:
                    if widget not in self.static_widgets:
                        widget.grid_remove()
                    
                    
                
                    
                    
        
        
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
        
        
    def open_files(self):
        filetypes = [
                    ("All files", "*.*"),
                    ("mp4 files", "*.mp4"), 
                    ("webm files", "*.webm"),
                    ("ogv files", "*.ogv"),
                    ("gif files", "*.gif"),
                    ("jpg files", ".jpg .jpeg"),
                    ("png files", "*.png")
                    
                    ]
        
        file_path_list = filedialog.askopenfilenames(
            title='Open files',
            initialdir=self.last_folder,
            filetypes=filetypes)
        
        if file_path_list:
            #text = "\n".join(file_path_list)
            for ind in range(len(file_path_list)):
               raw_file = file_path_list[ind]
               edited_file = raw_file.split('/')[-1]
               
               
            self.selected_file_listbox.insert(0, *file_path_list)
            
        
            temp = file_path_list[0].split('/')
            self.last_folder = "/".join(temp[:len(temp) - 1]) + "/"
            
            self.process_file(file_path_list)
            
    def clear_files(self):
        if self.selected_file_listbox.size() > 0:
            self.selected_file_listbox.delete(0, tk.END)
        
            
    def get_directory(self):
        current_directory = filedialog.askdirectory(
            initialdir = self.last_folder
        )
        file_name = os.path.join(self.last_folder, self.save_name_entry.get())       
        self.save_path_listbox.insert(tk.END, self.last_folder)
        
        print(self.last_folder)
        print(file_name)      
        
    def save_files(self):
        file_paths = self.selected_file_listbox.curselection()
        video = VideoFileClip()

    def get_selected_videos(self, lb):
       # Get selected values from the Listbox widget
        selected_videopaths = [lb.get(idx) for idx in lb.curselection()]
        for i in selected_videopaths:
            print(i)
        

    def process_file(self, file_path_list):
        # Implement your file processing logic here
        # For demonstration, let's just display the contents of the selected file
        try:
            pass
            #with open(file_path, 'r') as file:
            #file_contents = file.read()
            #self.file_text.delete('1.0', tk.END)
            #self.file_text.insert(tk.END, file_path_list[0])
        except Exception as e:
            self.selected_file_label.config(text=f"Error: {str(e)}")
            
   
        

    def add_to_list(self, _event=None):
        text = self.entry.get()
        if text:
            self.text_list.insert(tk.END, text)
            self.entry.delete(0, tk.END)

    def clear_list(self):
        self.text_list.delete(0, tk.END)







if __name__ == "__main__":
    app = Application()
    app.geometry("800x600")
    app.mainloop()
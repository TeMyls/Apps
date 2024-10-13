import os
import sys

#from PIL import Image
from moviepy.editor import VideoFileClip,concatenate_videoclips,AudioFileClip,vfx,CompositeAudioClip
import math
#from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration
from proglog import ProgressBarLogger
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import imageio





                    


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
                                                selectmode="single", 
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
        
        self.convert_to_combobox.current(0)
       
        #Mute
        self.audio_label = ttk.Label(self, text="Audio")
        self.muted_label = ttk.Label(self, text="Muted")
        self.mute_checkbool = tk.BooleanVar()
        self.mute_checkbool.set(False)
        self.mute_checkbutton = ttk.Checkbutton(self,   
                                                variable=self.mute_checkbool,
                                                command=self.is_muted
                                                ) 
        #self.mute_checkbutton
        
        
        #Resize
        self.resize_label = ttk.Label(self, text = "Resize %")
        self.resize_spinbox= ttk.Spinbox(self, 
                                        from_ = 0, 
                                        to = 500,
                                        width = 10
                                        
                                        )
        
        self.resize_spinbox.set(100)
        
        
        #Cut
        self.cut_label = ttk.Label(self, text = "Cut")
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
        #self.save_true["state"] = "disabled"
        
        
        
        
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
        
        #Progress Bar
        self.complete_progress_label = ttk.Label(self, text = "Progress ")
        
        self.complete_progress_bar = ttk.Progressbar(self, orient="vertical",  mode="determinate")
        
        self.complete_progress_status_label = ttk.Label(self, text = "Idle")
        
  
        
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
            
            self.complete_progress_label,
            self.complete_progress_bar,
            
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
           
            [self.selected_file_label      , None                          , self.convert_to_label   , self.combine_label     , None                     , self.resize_label    , self.save_path_label        , self.complete_progress_label],
            [self.selected_file_listbox    , self.selected_file_scrollbar_y, self.convert_to_combobox, self.combine_listbox   , self.combine_scrollbar_y ,  self.resize_spinbox , self.save_path_listbox      , self.complete_progress_bar  ],
            [self.selected_file_scrollbar_x, None                          , None                    ,self.combine_scrollbar_x, None                     , None                 , self.save_path_scrollbar_x  , None                        ],
            [self.selected_file_open_button, None                          , None                    , None                   , None                     , None                 , self.save_path_button       , None                        ],
            [self.selected_file_clear_button,None                          , None                    , self.cut_label         , self.audio_label         , None                 , self.save_name_label        , self.complete_progress_status_label],                   
            [self.type_selection_label     , None                          ,  self.start_cut_label   , self.cut_start_spinbox , self.muted_label         , self.mute_checkbutton, self.save_name_entry        , None                        ], 
            [self.type_selection_radiobutton1, None                        ,  self.end_cut_label     , self.cut_end_spinbox   , None                     , None                 , self.save_true              , None                        ], 
            [self.type_selection_radiobutton2, None                        , None                    , None                   , None                     , None                 , None                        , None                        ],
            [None                          , None                          , None                    , None                   , None                     , None                 , None                        , None                        ]           
            
            
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
                    elif isinstance(arrangement[ind_y][ind_x], ttk.Progressbar):
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NWES", rowspan = 3)
                    else:
                        arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NW")
                
                
        self.get_type_sel()            
        
        blank = "/"
        
  
        
        self.current_directory = ""
        self.last_folder = blank
        self.logger = self.MyBarLogger(self.complete_progress_bar, self.complete_progress_status_label, self)

        
        
    def get_type_sel(self):
        type_sel = self.type_selection_svar.get()
        #for ind_y in range(len(arrangement)):
            #for ind_x in range(2, len(arrangement[ind_y]) - 1):
        for widget in self.winfo_children():
            #print("Yes")
          
            #and  widget in self.static_widgets
            if type_sel == "Single":
                self.selected_file_listbox["selectmode"] = "single"
                self.selected_file_listbox.select_clear(0, tk.END)
                if widget in self.multiple_selection_widgets:
                    self.hide_widget(widget)
                else:
                    self.show_widget(widget)
                    
            elif type_sel == "Multiple":
                self.selected_file_listbox["selectmode"] = "multiple"
                self.selected_file_listbox.select_clear(0, tk.END)
                if widget in self.multiple_selection_widgets:
                    self.show_widget(widget)
                else:
                    if widget not in self.static_widgets:
                        self.hide_widget(widget)
                    
                    
                  
        
    def hide_widget(self, widget):
        widget.grid_remove()
        
    def show_widget(self, widget):
        widget.grid()
        
        
    def open_files(self):
        filetypes = [
                    #("All files", "*.*"),
                    ("mp4 files", "*.mp4"), 
                    ("webm files", "*.webm"),
                    ("ogv files", "*.ogv"),
                    ("gif files", "*.gif")
                    #("jpg files", ".jpg .jpeg"),
                    #("png files", "*.png")
                    
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
            
            
            
    def clear_files(self):
        if self.selected_file_listbox.size() > 0:
            self.selected_file_listbox.delete(0, tk.END)
        
            
    def get_directory(self):
        self.current_directory = filedialog.askdirectory(
            initialdir = self.last_folder
        )
        
        #self.last_folder = self.current_directory
        self.save_path_listbox.delete(0,tk.END)
        self.save_path_listbox.insert(tk.END, self.current_directory)
        
    def path_correction(self, path):
        foward_slash = "/"
        back_slash = "\\"
        path = path.replace(foward_slash, back_slash)

        return path
    
    
          
        
    def save_files(self):
        
        #self.save_path_listbox.insert(tk.END, self.last_folder)
        was_changed = False
        was_cut = False
        was_muted = False
        was_resized = False
        
        file_path_s = ""
        video = ""
        video_list = []
        s_logger = self.logger
        cdc = ""
        codec_dict = {'mp4':'libx264','ogv':'libtheora','webm':'libvpx'}
        self.current_directory = self.path_correction(self.current_directory)
        save_file = self.save_name_entry.get()
        if save_file == "":
            save_file = "file"
        save_path = os.path.join(self.current_directory,save_file)
        conversion_value = ""
        try:
            
            
            
            
            sel_len = len(self.selected_file_listbox.curselection())
            filp_len = self.save_path_listbox.size()
            if  self.selected_file_listbox["selectmode"] == "single" and sel_len > 0 and filp_len > 0:
                file_path_s = self.path_correction(self.selected_file_listbox.get(self.selected_file_listbox.curselection()[0])) 
                

                current_ext = file_path_s.split(".")[-1]

                was_muted = self.mute_checkbool.get() == False
                
                video = VideoFileClip(
                    file_path_s,
                    audio = was_muted
                    
                )
                
                
                
                
                start_seconds = float(self.cut_start_spinbox.get()) 
                end_seconds =  float(self.cut_end_spinbox.get()) 
                
                
                if start_seconds >= end_seconds or start_seconds < 0 or end_seconds < 0 or start_seconds > video.end or end_seconds > video.end:
                    pass
                else:
                    was_cut = True
                    video = video.subclip(start_seconds, end_seconds)
                    
                resize_value = int(self.resize_spinbox.get())
                if resize_value == 100:
                    pass
                else:
                    was_resized = True
                    video = video.resize(resize_value/100)
                    
                    
                #"No Change", "mp4","ogv","webm","gif",   
                conversion_value = self.convert_to_combobox.get()
                
                
                if conversion_value == "No Change" or conversion_value == current_ext:
                    if current_ext != "gif":
                        cdc = codec_dict[current_ext]
                        save_path = save_path + "." + current_ext
                    else:
                        save_path = save_path + "." + current_ext
                else:
                    if conversion_value != "gif":
                        cdc = codec_dict[conversion_value]
                        save_path = save_path + "." + conversion_value
                    else:
                        save_path = save_path + ".gif" 
                    was_changed = True
                    
                    
                print("yep")
                print(self.current_directory,'\n',save_path, "\n", file_path_s,"\n", cdc, "\n", conversion_value)
                print(f"Muted {was_muted} \nCut: {was_cut} \n Resized:{was_resized} \nCoverted {was_changed}")    
                    
                    
                
                if not was_changed and not was_cut and not was_muted and not was_resized:
                    messagebox.showerror("showinfo", "Make some type of change")
                else:
                    print("\nStarting")
                    if conversion_value == "gif" and current_ext in codec_dict and was_changed:
                        #Using OpenCV's stuff
                        video.close()
                        
                        self.complete_progress_status_label["text"] =  "Loading"
                        
                        #https://gist.github.com/laygond/d62df2f2757671dea78af25a061bf234#file-writevideofromimages-py-L25
                        #https://theailearner.com/2021/05/29/creating-gif-from-video-using-opencv-and-imageio/
                        
                        cap = cv2.VideoCapture(file_path_s)
                        # Get General Info
                        fps         = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                        duration    = int(frame_count/fps)
                        width       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float
                        height      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # float
                        
                        image_list = []
                        
                        
                        
                        

                        print("OPENCV LOOP")
                        start_time = 0
                        end_time = frame_count
                        if was_cut:
                            start_time = start_seconds * fps
                            end_time = end_seconds * fps
                        
                        
                        i = 0
                        
                        while True:
                            is_reading, frame = cap.read()
                            if not is_reading:
                                break
                            
                            
                            if i >= start_time and i <= end_time:
                                frame_rgb =  cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                
                                if was_resized:
                                    rw = int(width * (resize_value/100))
                                    rh = int(height * (resize_value/100))
                                    frame_rgb = cv2.resize(frame_rgb, (rw, rh ))
                                    
                                image_list.append(frame_rgb)
                                self.complete_progress_bar['value'] = int((i/(end_time - start_time)) * 100)
                                
                            
                            
                            i += 1
                            
                            self.update_idletasks()
                        
                            
                            

                        
                        milliseconds = (1/fps) * 1000
                                
                        print(fps, "\n", milliseconds)
                        
                        self.complete_progress_status_label["text"] = "Saving"
                        
                        imageio.mimsave(save_path, image_list, duration = milliseconds)
                        self.complete_progress_status_label["text"] = "Finished"
                        cap.release()
                        #video.write_gif(save_path, progress_bar = True)
                      
                    else:
                        #Using MoviePy's VideoFileClip
                        vid_size = os.path.getsize(file_path_s)/1000000000
                       
                        #print(vid_size)
                        brate = int((vid_size/((video.duration/60) * .0075)) * 1000000 * 0.9)
                        #print(brate)
                        
                        video.write_videofile(save_path, 
                                            codec = cdc, 
                                            logger = s_logger, 
                                            bitrate = str(brate)
                        )
                                                          
                                                          
                                                          
                        self.complete_progress_status_label["text"] = "Finished"
                        
                    
            elif self.selected_file_listbox["selectmode"] == "multiple"  and sel_len > 0 and filp_len > 0:
                file_path_s = [self.path_correction(self.selected_file_listbox.get(self.selected_file_listbox.curselection()[ind])) for ind in self.selected_file_listbox.curselection()]
            
                #multiple selection
                for path in file_path_s:
                    print(path)
            else:
                if sel_len == 0:
                    messagebox.showerror("showinfo", "Make sure the filepath is selected. It should be highlighted blue if clicked on.")
                elif filp_len == 0:
                    
                
                    messagebox.showerror("showinfo", "Make sure the save directory is selected.")
            
            
           
           
            #    pass
            #file_contents = file.read()
            #self.file_text.delete('1.0', tk.END)
            #self.file_text.insert(tk.END, file_path_list[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(self.current_directory,'\n',save_path, "\n", file_path_s,"\n", cdc, "\n", conversion_value)
            messagebox.showerror("Error", "File Path Invalid")
            self.selected_file_label.config(text=f"Error: {str(e)}")
            
        

    def get_selected_videos(self, lb):
       # Get selected values from the Listbox widget
        selected_videopaths = [lb.get(idx) for idx in lb.curselection()]
        for i in selected_videopaths:
            print(i)
        
    def is_muted(self):
        print("Muted", self.mute_checkbool.get() == False)
            
   
        

    def add_to_list(self, _event=None):
        text = self.entry.get()
        if text:
            self.text_list.insert(tk.END, text)
            self.entry.delete(0, tk.END)

    def clear_list(self):
        self.text_list.delete(0, tk.END)
        
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
            
                
                       
                       







if __name__ == "__main__":
    app = Application()
    app.geometry("800x600")
    app.mainloop()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from Tool_tip import *
from WidgetUtils import *
from Scrollable_Frame import *
import csv


class PaletteManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        #The main drawing canvas
        #self.drawing_canvas = None
        #Data
        #dictionary arranged in filename: list of colors
        self.palette_name_hex_list_dict = {"Current Colors":[]}
        #keeps track of the dynamically generated checkboxes
            #main checkboxes
        self.og_check_dict = {}
            #pop up checkboxes
        self.wn_check_dict = {}
            
        #the color that will be sent ot the main drawing canvas- a hexidecimal color
        self.og_selected_color = '#000000'
        self.wn_selected_color = '#000000' 

        self.og_selected_idx = -1
        self.wn_selected_idx = -1

        self.sub_wn = None
    
        

        self.og_checkbox_sf = ScrollableFrame(self,
                                             True,
                                             True,
                                             True,
                                             9
                                            )
        self.sf_w = 250
        self.sf_h = 150
        self.og_checkbox_sf.canvas.config(width=self.sf_w, height=self.sf_h, bg="SystemButtonFace")


        #Widgets
        self.palette_label = ttk.Label(self, text="Palette", anchor="center")
        self.palette_options = ["Current Colors"]
        
        self.middle_frame = tk.Frame(self)

        self.selected_palette_sv = tk.StringVar(value=self.palette_options[0])
        
        self.current_palette_cb = ttk.Combobox(self.middle_frame, 
                                                values=self.palette_options, 
                                                textvariable=self.selected_palette_sv,
                                                background="SystemButtonFace" 
                                                

                                                )

        
        #https://www.iconfinder.com/
        #self.current_palette_cb["values"] = list(range(0, 100))
        self.current_palette_cb.bind("<<ComboboxSelected>>", self._regenerate_checks)

        
        #https://stackoverflow.com/questions/22200003/tkinter-button-not-showing-image
        self.import_palette_img = tk.PhotoImage(file="icons\\add_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.import_palette_btn = tk.Button(self.middle_frame, 
                                        #text=" + ", 
                                        command= lambda:self._manage_palette("Create Palette", False), #lambda:self._import_palette(self.og_checkbox_sf.scrollable_frame, self.selected_palette_sv.get(), self.og_check_dict),#
                                        image=self.import_palette_img, 
                                        
                                        )
        CreateToolTip(self.import_palette_btn, "Create a new palette")
        
        self.edit_palette_img = tk.PhotoImage(file="icons\\edit_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.edit_palette_btn = tk.Button(self.middle_frame, 
                                        #text="+?", 
                                        command=lambda:self._manage_palette("Edit Palette", True), 
                                        image=self.edit_palette_img,
                                        
                                        )
        CreateToolTip(self.edit_palette_btn, "Manage Palette")
        
        
        

        self.palette_label.pack(side="top", anchor="s", fill="x")

        self.middle_frame.pack(side="top", anchor="s", fill="x")

        self.edit_palette_btn.pack(side="left", anchor="s", fill="x")
        self.current_palette_cb.pack(side="left", anchor="s", fill="both", expand=True)
        self.import_palette_btn.pack(side="left", anchor="s", fill="x")

        
        
        

        self.og_checkbox_sf.pack(side="bottom", anchor="s", fill="both", expand=True)
        #self.canvas.config(width=self.sf_w, height=self.sf_h)
        #self.canvas.pack(side="top", fill="both", expand=True)
        self.current_directory = os.getcwd()
        self._import_palette_data()

    

    def _import_palette_data(self):
        # checking to see if "palette.csv exist if not, it creates it"
        palette_exists = False
        for file in os.listdir(self.current_directory):
            if file == "palette.csv":
                palette_exists = True
                break
            else:
                continue

        # creating the palette if it doesn't exist
        if not palette_exists:
            with open("palette.csv", mode='w') as csv_file:
                pass


        with open("palette.csv", mode='r') as csv_file:
            
            csv_reader = csv.DictReader(csv_file)

            #print(csv_reader)
            #print(dict(csv_reader[0])["arcade-standard-29-32x.png"])
            print("importing palette")
            #for row in csv_reader:
            #    print(row)

                #if self.palette_name_hex_list_dict.get(ro)
            
            for row in csv_reader:
                #print(row) #, row["arcade-standard-29-32x.png"])
                for key in row:
                    if self.palette_name_hex_list_dict.get(key):
                        if row[key] != "NA" and row[key].startswith("#") and len(row[key]) == 7:
                            
                            self.palette_name_hex_list_dict[key].append(row[key])
                    else:
                        self.palette_name_hex_list_dict[key] = []
                        if row[key] != "NA" and row[key].startswith("#") and len(row[key]) == 7:
                            self.palette_name_hex_list_dict[key].append(row[key])
                #if self.palette_name_hex_list_dict.get(row):


            # updating check
            self.palette_options = list(self.palette_name_hex_list_dict.keys())
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette_sv.set(self.palette_options[-1])

            palette_name = self.selected_palette_sv.get()

            hex_codes = self.palette_name_hex_list_dict[palette_name] #self._get_check_dict_hex_codes(self.wn_check_dict)
       
            self._create_checkboxes(self.og_checkbox_sf, self.selected_palette_sv.get(), self.og_check_dict, self.selected_palette_sv.get(), hex_codes)
         
            
        

    def _export_palette_data(self):
        with open("palette.csv", mode='w') as csv_file:
            #https://realpython.com/python-csv/
            #https://dev.to/devasservice/guide-to-pythons-csv-module-32ie
            #fieldnames = ["Edges, Vertices, Gridlines"] #list(map(str, self.edges.keys())) #['emp_name', 'dept', 'birth_month']
            #writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            fieldnames = list(self.palette_name_hex_list_dict.keys())
            #writer.writeheader()
            
            #writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
            #writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

            # The number of keys in edges should be the same as the amount of V3D, or vertex objects, 

            #fieldnames = ["Edges", "Vertices", "Gridlines"]
            row_max = max([len(self.palette_name_hex_list_dict[key]) for key in self.palette_name_hex_list_dict]) #max(map(len, self.edges.values()))
            col_max = len(fieldnames)

            ls_csv = [["NA" for col in range(col_max)] for row in range(row_max + 1)]
            #for row in ls_csv:
            #    print(row)

            for row in range(row_max):
                for col in range(col_max):
                
                    if row < 1:
                        ls_csv[row][col] = fieldnames[col]
                    
                    else:
                        if row < len(self.palette_name_hex_list_dict[fieldnames[col]]):
                            ls_csv[row][col] = self.palette_name_hex_list_dict[fieldnames[col]][row]
                        
                        
                    
            print("exporting palette")
            for row in ls_csv:
                print(row)
            
            writer = csv.writer(csv_file)#, delimiter="\t")

            # Write data to the file
            writer.writerows(ls_csv)

    def _is_wn_open(self, window):
        #https://stackoverflow.com/questions/76940339/is-there-a-way-to-check-if-a-window-is-open-in-tkinter
        # window has been created an exists, so don't create again.
        return window is not None and window.winfo_exists()
       
    def _setup_sub_wn_widgets(self, _is_editing = False):
        
        self.wn_left_frame = tk.Frame(self.sub_wn)
        self.wn_right_frame = tk.Frame(self.sub_wn)

        self.wn_top_left_frame = tk.Frame(self.wn_left_frame)
        self.wn_bottom_left_frame = tk.Frame(self.wn_left_frame)

        self.wn_top_right_frame = tk.Frame(self.wn_right_frame)
        self.wn_middle_right_frame = tk.Frame(self.wn_right_frame)
        self.wn_bottom_right_frame = tk.Frame(self.wn_right_frame)

        self.wn_bottom_right_left_frame = tk.Frame(self.wn_bottom_right_frame)
        self.wn_bottom_right_right_frame = tk.Frame(self.wn_bottom_right_frame)

        self.wn_bottom_right_left_top_frame = tk.Frame(self.wn_bottom_right_left_frame)
        self.wn_bottom_right_left_middle_frame = tk.Frame(self.wn_bottom_right_left_frame)
        self.wn_bottom_right_left_bottom_frame = tk.Frame(self.wn_bottom_right_left_frame)

    

    
        self.wn_hex_lbl = tk.Label(self.wn_middle_right_frame, text=self.rgb_to_hex(0, 0, 0))
        #Canvas the indicates the color of the sliders
        self.wn_color_canvas = tk.Canvas(
                                self.wn_middle_right_frame, 
                                width=200, height=200, 
                                background=self.rgb_to_hex(0, 0, 0)
                                )
        
        self.wn_red_iv = tk.IntVar()
        self.wn_red_lbl = tk.Label(self.wn_bottom_right_left_top_frame, text="R", anchor="e")
        self.wn_red_scl = ttk.Scale(
            self.wn_bottom_right_left_top_frame,
            variable=self.wn_red_iv,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=self.wn_color_canvas.winfo_width()
         
        )
        
        self.wn_green_iv = tk.IntVar()
        self.wn_green_lbl = tk.Label(self.wn_bottom_right_left_middle_frame, text="G", anchor="e")
        self.wn_green_scl = ttk.Scale(
            self.wn_bottom_right_left_middle_frame,
            variable=self.wn_green_iv,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=self.wn_color_canvas.winfo_width()
        )
        
        self.wn_blue_iv = tk.IntVar()
        self.wn_blue_lbl = tk.Label(self.wn_bottom_right_left_bottom_frame, text="B", anchor="e")
        self.wn_blue_scl = ttk.Scale(
            self.wn_bottom_right_left_bottom_frame,
            variable=self.wn_blue_iv,
            from_ = 0,
            to = 255,
            orient = "horizontal",
            length=self.wn_color_canvas.winfo_width()
        )

        
        

        

        

        
        self.wn_checkbox_sf = ScrollableFrame(
                                        self.wn_bottom_left_frame,
                                        True,
                                        True,
                                        True,
                                        9
                                        )
        self.wn_checkbox_sf.canvas.config(width=self.sf_w, height=self.sf_h, bg="SystemButtonFace")

        self.wn_palette_lbl = tk.Label(self.wn_top_left_frame, text="Name")
        self.wn_palette_sv = tk.StringVar()
        self.wn_palette_ent = tk.Entry(self.wn_top_left_frame, textvariable=self.wn_palette_sv)


        
        self.wn_clear_btn = tk.Button(self.wn_bottom_right_right_frame, 
                                   text="Deselect Color", 
                                   command=self._deselect_color,
                                   #variable=self.wn_clear_bv
                                   
                                   )

        self.wn_add_btn = tk.Button(self.wn_bottom_right_right_frame, 
                                   text="Add Color", 
                                   command=self._add_color
                                   )
        
        
        
        self.wn_remove_btn = tk.Button(self.wn_bottom_right_right_frame, 
                                   text="Remove Color", 
                                   command=self._remove_color
                                   )
   
        
        self.wn_option_btn = None
        self.wn_edit_btn = None
        if _is_editing:

            self.wn_palette_ent.insert(tk.END, self.selected_palette_sv.get())
            self.wn_palette_ent.config(state="disabled")
            
            self.wn_option_btn = tk.Button(self.wn_top_right_frame, 
                                   text="Delete Palette", 
                                   command=lambda:self._delete_palette()
                                   )
            
            self.wn_edit_btn = tk.Button(self.wn_top_right_frame, 
                                   text="Edit Palette", 
                                   command=lambda:self._edit_palette(self.wn_checkbox_sf, self.selected_palette_sv.get(), self.wn_check_dict)
                                   )
            
            
        else:
            self.wn_palette_ent.config(state="normal")
            self.wn_palette_ent.insert(tk.END, "New Palette Name")
            self.wn_option_btn = tk.Button(self.wn_top_right_frame, 
                                   text="Import Palette", 
                                   command=lambda:self._import_palette(self.wn_checkbox_sf, self.wn_palette_sv.get(), self.wn_check_dict)
                                   )
            '''
            wn_edit_btn = tk.Button(self.sub_wn, 
                                   text="Update Palette", 
                                   command=lambda:self.edit_palette(wn_checkbox_sf.canvas, wn_checkbox_sf.scrollable_frame, self.current_palette_cb , self.wn_check_dict)
                                   )
            '''

            
            
        self.wn_cancel_btn = tk.Button(self.wn_bottom_right_right_frame, 
                                   text="Cancel", 
                                   command=self.sub_wn.destroy)
        
        self.wn_save_btn = tk.Button(self.wn_bottom_right_right_frame, 
                                 text="Save", 
                                 command=lambda:self._save_palette()
                                 )
            
        
        #changing the selected rbg slide color based on the selected checkbutton color

        #self.sub_wn.bind("<ButtonPress-1>", lambda _ :self._set_rgb_sliders())
        
        # Changing the canvas color based on the rgb sliderss
        change_canvas_color = lambda _:self._set_color_configs()
        
        self.wn_red_scl.config(command=change_canvas_color)
        self.wn_blue_scl.config(command=change_canvas_color)
        self.wn_green_scl.config(command=change_canvas_color)
        
        
       
        
        

        
        
        '''
        # Original Gridded Arrangement: before the layout frames existed and everying was a child of sub_wn
        #   rather than an attribute of the main class
        # A widget's pack() method allows a little more freedom than the grid() method
        arrangement = [
            [palette_label , wn_palette_ent    ,wn_option_btn    , wn_edit_btn],
            [None          , wn_checkbox_sf   ,wn_color_canvas      , None        ],
            [None          , None             , wn_hex_lbl        , None        ],
            [None          ,wn_red_lbl         ,wn_red_scl        ,None,wn_add_btn],
            [None          ,wn_green_lbl       ,wn_green_scl      ,None,wn_remove_btn],
            [None          ,wn_blue_lbl        ,wn_blue_scl       ,None,wn_cancel_btn],
            [None          ,None              , None             ,None  , save_palette]
        ]

        arrange_widgets(arrangement)
        '''

        '''
        # pack arrangement
        wn_left_frame              wn_right_frame
        _________________________________________________
        |wn_top_left_frame      |wn_top_right_frame      |
        |                       |                        |
        |_______________________|________________________| 
        |wn_bottom_right_frame  |wn_middle_right_frame   |
        |                       |                        |
        |                       |                        |
        |                       |                        |
        |                       |________________________|
        |                       |wn_bottom_right_frame   |
        |                       |            |           |
        |                       |wn          |wn         |
        |                       |bottom      |bottom     |
        |                       |right       |right      |
        |                       |left        |right      |
        |                       |frame       |frame      |
        |_______________________|____________|___________|
        '''

        # General Layout
        self.wn_left_frame.pack(side="left", anchor="s", fill="both", expand=True)
        self.wn_right_frame.pack(side="left", anchor="s", fill="both", expand=True)

        # Palette Name, Label and Scrollable Frame
        self.wn_top_left_frame.pack(side="top")#, anchor="n", fill="x", expand=True)
        self.wn_bottom_left_frame.pack(side="top", anchor="n", fill="both", expand=True)

        # Import Button, Color Canvas, Sliders, Options
        self.wn_top_right_frame.pack(side="top", anchor="n", fill="both", expand=True)
        self.wn_middle_right_frame.pack(side="top", anchor="center", fill="both", expand=True)
        self.wn_bottom_right_frame.pack(side="top", anchor="s", fill="both", expand=True)


        self.wn_bottom_right_left_frame.pack(side="left", anchor="w", fill="both", expand=True)
        self.wn_bottom_right_right_frame.pack(side="left", anchor="e")

        # Sliders and Slider Labels
        self.wn_bottom_right_left_top_frame.pack(side="top", anchor="s", fill="both", expand=True)
        self.wn_bottom_right_left_middle_frame.pack(side="top", anchor="s", fill="both", expand=True)
        self.wn_bottom_right_left_bottom_frame.pack(side="top", anchor="s", fill="both", expand=True)

        # The widgets

        # wn_top_left_frame
        self.wn_palette_lbl.pack(side="left", anchor="n", fill="x")
        self.wn_palette_ent.pack(side="left", anchor="n", fill="x", expand=True)
        # wn_bottom_left_frame
        self.wn_checkbox_sf.pack(side="top", anchor="n",fill="both", expand=True)
        
        # wn_top_right_frame
        self.wn_option_btn.pack(side="left", anchor="n", fill="x", expand=True)
        if _is_editing:
            print("edit packed")
            self.wn_edit_btn.pack(side="left", anchor="n", fill="x", expand=True)
            '''
            self._create_checkboxes(
                                    self.wn_checkbox_sf, 
                                    self.selected_palette_sv.get(), 
                                    self.og_check_dict,
                                    self.selected_palette_sv.get(),
                                    self._get_check_dict_hex_codes(self.og_check_dict)
                                    )
            '''

        # wn_middle_right_frame
        self.wn_color_canvas.pack(side="top")
        self.wn_hex_lbl.pack(side="top")
        

        # wn_bottom_right_frame

        # wn_bottom_right_right_frame
        self.wn_clear_btn.pack(side="top", anchor="w", fill="x", expand=True)
        self.wn_add_btn.pack(side="top", anchor="w", fill="x", expand=True)
        self.wn_remove_btn.pack(side="top", anchor="w", fill="x", expand=True)
        self.wn_cancel_btn.pack(side="top", anchor="w", fill="x", expand=True)
        self.wn_save_btn.pack(side="top", anchor="w", fill="x", expand=True)
        # wn_bottom_left_frame

        # wn_bottom_right_left_top_frame
        self.wn_red_lbl.pack(side="left", anchor="w")
        self.wn_red_scl.pack(side="left", anchor="w", fill="x", expand=True)
        # wn_bottom_right_left_middle_frame
        self.wn_green_lbl.pack(side="left", anchor="w")
        self.wn_green_scl.pack(side="left", anchor="w", fill="x", expand=True)
        # wn_bottom_right_left_bottom_frame
        self.wn_blue_lbl.pack(side="left", anchor="w")
        self.wn_blue_scl.pack(side="left", anchor="w", fill="x", expand=True)

    def _manage_palette(self, title = "Window", _is_editing = False):
        if self._is_wn_open(self.sub_wn):
            return
        
        
        #self.disable_multiple_widgets(self.arrangement)

        self.sub_wn = Toplevel()

        self._setup_sub_wn_widgets(_is_editing)

        self.sub_wn.resizable(False, False)
        #above tkinter windows
        self.sub_wn.lift()

        
        #above all windows
        #self.sub_wn.attributes('-topmost', 1)
        #self.sub_wn.attributes('-topmost', 0)

        #self.sub_wn.geometry("200x150")
        self.sub_wn.title(title)
        self.sub_wn.mainloop()
        #print("mainloop")
        #self.enable_multiple_widgets(self.arrangement)

    #https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    #https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa

    
    def invert_color(self, color: str):
        rgb = self.hex_to_rgb(color)
            
        rgb[0] = 255 - rgb[0]
        rgb[1] = 255 - rgb[1]
        rgb[2] = 255 - rgb[2]
        

        r, g, b = rgb
        _hex = self.rgb_to_hex(r, g, b)
        return _hex

    def rgb_to_hex(self, r,g,b):
        hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)

        return hexcode
    
    def hex_to_rgb(self, hexcode, alpha = False):
        hexcode = hexcode[1:]
        rgb = [int(hexcode[i:i+2], 16) for i in (0, 2, 4)]
        if alpha:
            rgb.append(255)
            return rgb 

        return rgb 
        
    def _color_unselect(self, check_dict):
        for key in check_dict:
            
            #print(data)
            
            data = check_dict[key]
            var_bln = data[0]
            chk_btn = data[1]
            is_chkd = data[2]

            data[0].set(value=False)
            data[1].config(background = "SystemButtonFace")
            data[2] = False

    def _color_select(self, check_dict):
        #selects a color tp return to the main drawing canvas
        #so the check mark of a selected color is always visible
        changed_cb = None
        changed_bool = None
        changed_key = ''


        
        for key in check_dict:
            
            #print(data)
            
            data = check_dict[key]
            var_bln = data[0]
            chk_btn = data[1]
            is_chkd = data[2]

            if var_bln.get() and not is_chkd:
                changed_cb = chk_btn
                changed_key = key
                
                data[2] = True
                changed_bool = data[2]
                data[1].config(background = "Green")
                #print('turned on ', key)
                break
            else:
                data[2] = False
                #print('turned off ', key)
            

        for key in check_dict:
           if key != changed_key:
               data = check_dict[key]
               data[0].set(False)
               data[2] = False
               data[1].config(background = "SystemButtonFace")

        
            
        print(changed_key)
        
        if self._is_wn_open(self.sub_wn):
            if check_dict == self.wn_check_dict:
                self.wn_selected_color = changed_key
                self.wn_color_canvas.config(bg = self.wn_selected_color)
                self.wn_hex_lbl.config(text = self.wn_selected_color)


                self._set_rgb_sliders()
        else:
            if check_dict == self.og_check_dict:
                self.og_selected_color = changed_key
        
        print(f"Selected Color: {self.og_selected_color} Window Color: {self.wn_selected_color}")

    def _regenerate_checks(self, *args):
        #called by the palette combobox every time a different palette is selected
        if self.selected_palette_sv.get() == "Current Colors":
            #scans colors of the main drawing canvas
            if len(self.palette_name_hex_list_dict) > 1:
                disable_widget(self.import_palette_btn)
                disable_widget(self.edit_palette_btn)


        elif self.palette_name_hex_list_dict.get(self.selected_palette_sv.get()):
            if len(self.palette_name_hex_list_dict) > 1:
                enable_widget(self.import_palette_btn)
                enable_widget(self.edit_palette_btn)
            
            hex_codes = self.palette_name_hex_list_dict[self.selected_palette_sv.get()] #self._get_check_dict_hex_codes(self.og_check_dict)
            self._create_checkboxes(
                                    self.og_checkbox_sf, 
                                    self.selected_palette_sv.get(), 
                                    self.og_check_dict, 
                                    self.selected_palette_sv.get(), 
                                    hex_codes
                                )
            #self.clear_checkboxes(self.og_checkbox_sf.canvas, self.og_checkbox_sf.scrollable_frame, self.og_check_dict)
            #self.create_checkboxes(self.og_checkbox_sf.scrollable_frame, self.current_palette_cb.get(), self.og_check_dict)
            #self._create_checkboxes(self.og_checkbox_sf.scrollable_frame, self.selected_palette_sv.get(), self.og_check_dict)

    def _read_colors_from_image(self):
        # gets all of the colors from an image as hexcolors
        # always includes black hexcolor #000000
        # colors are stored in a dictionary with key:value pairs such as filename:[hexcolor1, hwxcolor2, etc]
        # this dictionary is used to build out the check_dict
        # this is stored in 

        filetypes = [
            
                    ("png files", "*.png"),
                    ("jpg files", ".jpg .jpeg")

                    ]
        
        file_path = filedialog.askopenfilename(
                                                title="Open Text File", 
                                                filetypes=filetypes
                                            )
        if file_path:
            
            #https://stackoverflow.com/questions/56722800/how-to-get-set-of-colours-in-an-image-using-python-pil
            #https://shegocodes.medium.com/extracting-all-colors-in-images-with-python-2e36eb8a67d2
            img = Image.open(file_path)
            colors = []
            # getting the file name
            file_name = file_path.split("/")[-1]
            if file_name == "Current Colors":
                return
            #scan colors of the main drawing canvas
            
            #colors = img.convert('RGB').getcolors() #maxcolors=256
            colors = img.quantize().getpalette()
            hex_codes = []
            print(colors)
            temp = []
            #if filename not in self.palette_name_hex_list_dict:
            prev_color = []
            
            current_color = [colors[0], colors[1], colors[2]]
            #if self.palette_name_hex_list_dict.get(filename):
            #    self.palette_name_hex_list_dict[filename].clear()
            #self.palette_name_hex_list_dict[filename] = []

            for i in range(0, len(colors), 3):
                prev_color = current_color

                hex_color = self.rgb_to_hex(colors[i], colors[i + 1], colors[i + 2])
                #if hex_color not in self.palette_name_hex_list_dict[filename]:
                #   self.palette_name_hex_list_dict[filename].append(hex_color)
                if hex_color not in hex_codes:
                    hex_codes.append(hex_color)
                if i >= 3:
                    temp.append(prev_color)
                    current_color = [colors[i], colors[i + 1], colors[i + 2]]
                    if current_color == prev_color:
                        #could cut off black (0,0,0) from colors that end with cmyk
                        #self.palette_name_hex_list_dict[filename].pop()
                        break
            
            return file_name, hex_codes #self.palette_name_hex_list_dict[filename]

        return "", ""     
    
    def _deselect_color(self):
        if not self._is_wn_open(self.sub_wn):
            return
        
        self.wn_selected_color = ""
        self._color_unselect(self.wn_check_dict)

    def _add_color(self): 
        #adds color checkbuttons to a canvas 
        if not self._is_wn_open(self.sub_wn):
            return
        
        #if palette_name != "Current Colors":
            
        hex_color = self.rgb_to_hex(self.wn_red_iv.get(), self.wn_green_iv.get(), self.wn_blue_iv.get())
        
        if self.wn_check_dict.get(hex_color):
            data = self.wn_check_dict.pop(hex_color)
            var_bln = data[0]
            chk_btn = data[1]
            booln = data[2]

            #destroying and recreating check box
        

            idx = self.wn_checkbox_sf.widget_list.index(chk_btn)

            inv_hex_color = self.invert_color(hex_color)
            nu_chk = tk.Checkbutton(
                            self.wn_checkbox_sf.scrollable_frame, 
                            #text=txt, 
                            variable=var_bln,
                            command= lambda:self._color_select(self.wn_check_dict),
                            onvalue=True,
                            offvalue=False,
                            selectcolor= hex_color,
                            background = "Green",
                            foreground =inv_hex_color
                            )
            
            self.wn_checkbox_sf.remove_widget(idx)
            self.wn_checkbox_sf.add_widget(nu_chk, idx)
            self.wn_checkbox_sf.update_grid_frame()

            self.wn_check_dict[hex_color] = [var_bln, nu_chk, False]

            #
        else:
            var_bln = tk.BooleanVar()
            chk_btn = tk.Checkbutton(self.wn_checkbox_sf.scrollable_frame, 
                                #text=txt, 
                                variable=var_bln,
                                command= lambda:self._color_select(self.wn_check_dict),
                                onvalue=True,
                                offvalue=False,
                                selectcolor= hex_color,
                                
                                )
            
            self.wn_checkbox_sf.add_widget(
                chk_btn,
                len(self.wn_checkbox_sf.widget_list)
            )

            self.wn_check_dict[hex_color] = [var_bln, chk_btn, False]
            self.wn_checkbox_sf.update_grid_frame()

    def _remove_color(self): 
        #removes color checkbuttons from a canvas 
        #if palette_name != "Current Colors":
        if not self._is_wn_open(self.sub_wn):
            return
        
        if not self.wn_selected_color:
            return
            
        if self.wn_check_dict.get(self.wn_selected_color):
            data = self.wn_check_dict[self.wn_selected_color]
            var_bln = data[0]
            chk_btn = data[1]
            
            self.wn_checkbox_sf.remove_widget(
               self.wn_checkbox_sf.widget_list.index(chk_btn)
            )

            self.wn_check_dict.pop(self.wn_selected_color)
            self.wn_checkbox_sf.update_grid_frame()

            '''
            if isinstance(chk_btn, tk.Checkbutton):
                var_bln.set(False)
                chk_btn.destroy()
            check_dict.pop(self.wn_selected_color)
            '''

            

                        

            #self.clear_checkboxes(canvas, scrl_frame, check_dict)
            #self.create_checkboxes(scrl_frame, palette_name, check_dict)
            #self._create_checkboxes(scrl_frame, palette_name, check_dict)

    def _get_check_dict_hex_codes(self, check_dict: dict[str, list[str]]):
        hex_codes = []
        for key in check_dict:
            data = check_dict[key]
            var_bln = data[0]
            chk_btn = data[1]
            is_chkd = data[2]

            hex_codes.append(chk_btn.cget("selectcolor"))
        return hex_codes

    def _delete_palette(self):
        if not self._is_wn_open(self.sub_wn):
            return

        palette_name = self.wn_palette_sv.get()
        if self.palette_name_hex_list_dict.get(palette_name) and palette_name != "Current Colors":
            self.palette_name_hex_list_dict.pop(palette_name)
            

            self.palette_options.remove(palette_name)
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette_sv.set(self.palette_options[-1])
            hex_codes = self.palette_name_hex_list_dict[self.selected_palette_sv.get()]#self._get_check_dict_hex_codes(self.wn_check_dict)
            #delete_warning = True
            #The Original Window
            #self.clear_checkboxes(self.og_checkbox_sf.canvas, self.og_checkbox_sf.scrollable_frame, self.og_check_dict)
            #self._create_checkboxes(self.og_checkbox_sf.scrollable_frame, self.selected_palette_sv.get(), self.og_check_dict,self.selected_palette_sv.get(),hex_codes)
            self._create_checkboxes(self.og_checkbox_sf, self.selected_palette_sv.get(), self.og_check_dict,self.selected_palette_sv.get(),hex_codes)
            #Exporting CSV file to be read when widget is initialized
            self._export_palette_data()
            self.sub_wn.destroy()

    def _save_palette(self):
        #self.update_listbox(self.selected_palette_sv.get())

        if not self._is_wn_open(self.sub_wn):
            return
        
        palette_name = self.wn_palette_sv.get()
        if palette_name not in self.palette_options:
            self.palette_options.append(palette_name)
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette_sv.set(self.palette_options[-1])


        hex_codes = self._get_check_dict_hex_codes(self.wn_check_dict)
        # updating the listbox
        self.palette_name_hex_list_dict[palette_name] = hex_codes

        self._create_checkboxes(self.wn_checkbox_sf, self.wn_palette_sv.get(), self.wn_check_dict, self.wn_palette_sv.get(), hex_codes)
        self._create_checkboxes(self.og_checkbox_sf, self.wn_palette_sv.get(), self.og_check_dict, self.wn_palette_sv.get(), hex_codes)

        #Exporting CSV file to be read when widget is initialized
        self._export_palette_data()
        
         
    def _import_palette(self, scrl_frame: ScrollableFrame, palette_name: str, check_dict: dict[str, list[str]]):
        
        #self._read_colors_from_image()
        
        #The Pop-Up Window
        # self.clear_checkboxes(scrl_frame, check_dict)
        # self.create_checkboxes(scrl_frame, entry.get(), check_dict)
        #self._create_checkboxes(scrl_frame, palette_name, check_dict)

        


        file_name, hex_codes = self._read_colors_from_image()
        if not file_name and not hex_codes:
            return
        
        if self._is_wn_open(self.sub_wn):
            # if importing 
            self.wn_palette_sv.set(file_name)

        self._create_checkboxes(scrl_frame, palette_name, check_dict, file_name, hex_codes)


        #The Original Window
        #self.clear_checkboxes(self.og_checkbox_sf.canvas, self.og_checkbox_sf.scrollable_frame, self.og_check_dict)
        #self.create_checkboxes(self.og_checkbox_sf.scrollable_frame, entry.get(), self.og_check_dict)

        #Raising up about base window
        
        self.sub_wn.lift()
         
    def _edit_palette(self, scrl_frame: ScrollableFrame, palette_name: str, check_dict: dict[str, list[str]]):
        #The Pop-Up Window
        #self.clear_checkboxes(canvas, scrl_frame, check_dict)
        #self.create_checkboxes(scrl_frame, cb.get(), check_dict)


        hex_codes = self._get_check_dict_hex_codes(self.og_check_dict)
        self._create_checkboxes(scrl_frame, palette_name, check_dict, palette_name, hex_codes)
        #The Original Window
        #self.clear_checkboxes(self.og_checkbox_sf.canvas, self.og_checkbox_sf.scrollable_frame, self.og_check_dict)
        #self.create_checkboxes(self.og_checkbox_sf.scrollable_frame, entry.get(), self.og_check_dict)



    def _create_checkboxes(self, scrl_frame: ScrollableFrame, palette_name: str, check_dict: dict[str, list[str]], file_name: str, hex_codes:list[str]):
        
        

        # clearing the checkdict
        if check_dict:
            for key in check_dict:
                data = check_dict[key]
                var_bln = data[0]
                chk_btn = data[1]
                if isinstance(chk_btn, tk.Checkbutton):
                    var_bln.set(False)
                    chk_btn.destroy()
        check_dict.clear()

        # clearing the scrollable frame
        scrl_frame.widget_list.clear()
        while scrl_frame.widget_list:
            scrl_frame.remove_widget(len(scrl_frame.widget_list) - 1)
        
        for idx in range(len(hex_codes)):
            #print(idx)
            hex_color = hex_codes[idx]
            #print(f"Hexcode: {hex_color}")
            color = self.hex_to_rgb(hex_color)
            
            inv_hex_color = self.invert_color(hex_color)
            #print(f"Color RGB: {color}, Hexcode: {hex_color}")
            
            var_bln = tk.BooleanVar(value=False)
            chk_btn = tk.Checkbutton(
                                scrl_frame.scrollable_frame, 
                                #text=hex_color, 
                                variable = var_bln,
                                command = lambda: self._color_select(check_dict),
                                foreground= inv_hex_color,
                                onvalue = True,
                                offvalue = False,
                                selectcolor = hex_color,
                                )
            CreateToolTip(chk_btn, hex_color)

            # how the checkbuttons work
            # foreground is the actually checkmark color of the checkbutton
            # background is the color of the area surrounding the indiviudual check button
            # selectcolor is the color of the checkbox surrounding the check itslef

            scrl_frame.add_widget(
                    chk_btn,
                    len(scrl_frame.widget_list)
                )
            
            #recreating the checkdict
            check_dict[hex_color] = [var_bln, chk_btn, False]

        scrl_frame.update_grid_frame()

        
        

   
    
    def update_listbox(self, palette_name):
        if palette_name not in self.palette_options:
            self.palette_options.append(palette_name)
            self.current_palette_cb['values'] = self.palette_options
            self.selected_palette_sv.set(self.palette_options[-1])

    

    def _set_rgb_sliders(self):#, c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label):
        #sets the rgb sliders to match the selected color

        if not self._is_wn_open(self.sub_wn):
            return
        
        if not self.wn_selected_color:
            return
            
        if not self.wn_check_dict.get(self.wn_selected_color):
            return

        #if self.palette_name_hex_list_dict.get(palette_name):
        #if self.wn_selected_color in self.palette_name_hex_list_dict[palette_name]:
        self.update_idletasks()
        # changing the rgb sliders based on selected checkbutton
        data = self.wn_check_dict[self.wn_selected_color]
        var_bln = data[0]
        chk_btn = data[1]
        idx = self.wn_checkbox_sf.widget_list.index(chk_btn) #self.palette_name_hex_list_dict[palette_name].index(self.wn_selected_color)
        
        #hex_color = self.rgb_to_hex(r,g,b)

        rgb = self.hex_to_rgb(self.wn_selected_color)

        self.wn_red_iv.set(rgb[0])
        self.wn_green_iv.set(rgb[1])
        self.wn_blue_iv.set(rgb[2])
        
        self.wn_red_lbl.config(text="R:{}".format(rgb[0]))
        self.wn_green_lbl.config(text="G:{}".format(rgb[1]))
        self.wn_blue_lbl.config(text="B:{}".format(rgb[2]))
        
        #updates all checkboxes, unfeasible for large color palette editing
        #self.clear_checkboxes(o_canvas, scrl_frame, check_dict)
        #self.create_checkboxes(o_canvas, scrl_frame, check_dict)

    def _set_color_configs(self):#, c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label, scrl_frame, check_dict):
        # self.set_rgb_sliders(c_canvas, r, g, b, label, palette_name, r_label, g_label, b_label)
        # allows the color canvas color to be changed 
        # and the selected color buttons to be as well
        # using ethe rgb color sliders

        if not self._is_wn_open(self.sub_wn):
            return

            
        #changing to new hex
        hex_color = self.rgb_to_hex(self.wn_red_iv.get(), self.wn_green_iv.get(), self.wn_blue_iv.get())
        self.wn_color_canvas.config(bg=hex_color)
        self.wn_hex_lbl.config(text=hex_color)
        
        
        self.wn_red_lbl.config(text="R:{}".format(self.wn_red_iv.get()))
        self.wn_green_lbl.config(text="G:{}".format(self.wn_green_iv.get()))
        self.wn_blue_lbl.config(text="B:{}".format(self.wn_blue_iv.get()))

        if self.wn_check_dict.get(self.wn_selected_color):
            #print("runsa")
            
            data = self.wn_check_dict.pop(self.wn_selected_color)
            var_bln = data[0]
            chk_btn = data[1]
            booln = data[2]

            #destroying and recreating check box
            c_grid_info = chk_btn.grid_info() #config(selectcolor=hex_color)
            c_row = c_grid_info['row']
            c_col = c_grid_info['column']
            #chk_btn.destroy()

            idx = self.wn_checkbox_sf.widget_list.index(chk_btn)

            inv_hex_color = self.invert_color(hex_color)
            nu_chk = tk.Checkbutton(
                            self.wn_checkbox_sf.scrollable_frame, 
                            #text=txt, 
                            variable=var_bln,
                            command= lambda:self._color_select(self.wn_check_dict),
                            onvalue=True,
                            offvalue=False,
                            selectcolor= hex_color,
                            background = "Green",
                            foreground =inv_hex_color
                            )
            
            self.wn_checkbox_sf.remove_widget(idx)
            self.wn_checkbox_sf.add_widget(nu_chk, idx)
            self.wn_checkbox_sf.update_grid_frame()

            self.wn_check_dict[hex_color] = [var_bln, nu_chk, False]
        

            
            self.wn_selected_color = hex_color

    def get_selected_color(self):
        return self.og_selected_color

    def set_selected_color(self, color: str):
        if not color.startswith("#"):
            return
        self.og_selected_color = color
        

    def set_current_colors(self, hex_codes: set[str]):
        self.palette_name_hex_list_dict["Current Colors"].clear()
        self.palette_name_hex_list_dict["Current Colors"] = list(hex_codes)
        palette_name = self.selected_palette_sv.get()
        

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        
        #Ts = Palette_Frame(self)#PaletteFrame(self, True, True, )
        Ts = PaletteManager(self)
        Ts.pack(side="top", fill="both", expand=True)
        
        
    
        

               

if __name__ == "__main__":



    app = App()
    
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    app.title("Palette Manager")
    #app.resizable()
    app.mainloop()

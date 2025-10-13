import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk, ImageSequence, ImageOps
from MatrixMath import *
from collisions import *
from Frame__Image import *
#from FrameImage import *
from Tool_tip import *
import numpy as np
from numpy import radians as to_radians
import math
import time

def angle_to(x1, y1, x2, y2):
    #in radians
    return math.atan2(y2 - y1, x2 - x1)

def distance_to(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    s = dx * dx + dy * dy
    return math.sqrt(s)

def in_bounds(x, y, w, h):
    return 0 <= x < w and 0 <= y < h

def degrees_to_radians(deg):
    return to_radians(deg) #(deg * math.pi)/180



def path_correction(file_path):
    foward_slash = "/"
    back_slash = "\\"
    file_path = file_path.replace(foward_slash, back_slash)

    return file_path

def hide_widget(widget):
    widget.grid_remove()
        
def show_widget(widget):
    widget.grid()

def hide_pack_widget(widget):
    widget.pack_forget()

def show_pack_widget(widget):
    widget.pack()

def disable_widget(widget):
    widget.config(state="disabled")

def enable_widget(widget):
    widget.config(state="normal")

def delete_widget(widget):
    widget.destroy()

def arrange_widgets(arrangement, branch = "NEWS"):
    for ind_y in range(len(arrangement)):
        for ind_x in range(len(arrangement[ind_y])):

            if arrangement[ind_y][ind_x] == None:
                pass
            else:
                arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = branch)





    

class Animator(ttk.Frame):
    def __init__(self, parent, c_width, c_height, p_width, p_height):
        super().__init__(parent)
        #the color selection palette


        self.pixel_canvas_width = p_width
        self.pixel_canvas_height = p_height
        self.canvas_width = c_width
        self.canvas_height = c_height
        #the reason this has an underscore is to 
        self.canvas_color = "#808080"
        self.bg_color = "#FFFFFF"
        self.pixels_to_paste = []
        self.colors_to_paste = []
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #The main canvas
        self.main_frame = tk.Frame(self) 
        self.canvas = tk.Canvas(self.main_frame, 
                                width=c_width,
                                height=c_height, 
                                bg=self.canvas_color) 
        self.canvas_s_barv = tk.Scrollbar(self.main_frame, orient='vertical')
        self.canvas_s_barh = tk.Scrollbar(self.main_frame, orient='horizontal')

        self.canvas_s_barv.config(command=self.canvas.yview)
        self.canvas_s_barh.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.canvas_s_barv.set)
        self.canvas.config(xscrollcommand=self.canvas_s_barh.set)
        self.canvas.config(scrollregion=(0,0,c_width,c_height))



        self.color = "#000000"
        

        self.frame_idx = 0
        self.key_frame_collection = []
        self.current_key_frame = self.get_key_frame(self.frame_idx)
        
        
        



        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        self.options_frame = tk.Frame(self)

        self.onion_iv = tk.BooleanVar(value=False)
        self.onion_next = 3
        self.onion_prev = 3
        self.onion_prev_lbl = ttk.Label(self.options_frame, text="Onion Prev")
        self.onion_next_lbl = ttk.Label(self.options_frame, text="Onion Next")
        self.onion_prev_sb = ttk.Spinbox(self.options_frame, from_ = 0, to = 3, increment=1, width=10, command=self.render_canvas)
        self.onion_next_sb = ttk.Spinbox(self.options_frame, from_ = 0, to = 3, increment=1, width=10, command=self.render_canvas)
        self.onion_prev_sb.set(1)
        self.onion_next_sb.set(1)
        self.onion_cb = ttk.Checkbutton(self.options_frame, text="Onion Skin", variable=self.onion_iv, command=self.render_canvas)
        self.onion_image = None

        self.brush_lbl = ttk.Label(self.options_frame, text="Brush Size")
        self.brush_sb = ttk.Spinbox(self.options_frame, from_ = 1, to = 10, increment=0.5, width=10, command=self.render_canvas)
        self.brush_sb.set(1)

        self.debug_btn = ttk.Button(self.options_frame, text="Debug", command=self.debug)
        self.clear_btn = ttk.Button(self.options_frame, text="Clear Frame", command=self.clear_frame)
        self.wipeout_btn = ttk.Button(self.options_frame, text="Clear All", command=self.clear_frames)
        self.save_btn = ttk.Button(self.options_frame, text="Save Frame", command=self.save_frame)
        self.gif_btn = ttk.Button(self.options_frame, text="Save Gif", command=self.save_gif)
        self.color_btn = ttk.Button(self.options_frame, text="Color", command=self.choose_color)
        self.canvas_color_btn = ttk.Button(self.options_frame, text="Canvas Color", command=self.change_canvas_color)
        self.resize_btn = ttk.Button(self.options_frame, text="Resize", command=self.on_pixel_image_resize)
        self.open_btn = ttk.Button(self.options_frame, text="Import", command=self.open_file)

        self.bg_color_iv = tk.BooleanVar(value=False)
        self.bg_color_cb = ttk.Checkbutton(self.options_frame, text="Save Color", variable=self.bg_color_iv, command=self.render_canvas)
        self.bg_color_btn = tk.Button(self.options_frame, text="BG Color", command=self.change_bg_color, bg=self.bg_color, fg=self.current_key_frame.invert_color(self.bg_color))

        self.scale_lbl = ttk.Label(self.options_frame, text="Scale:0")
        self.dim_lbl = ttk.Label(self.options_frame, text=f"[{p_width}x{p_height}]")

        #self.nav_frame = ttk.Frame(self)
        self.cpy_btn =  ttk.Button(self.options_frame, 
                                   text="Clone Frame", 
                                   command=self.duplicate_key_frame
                                   )
        self.next_btn = ttk.Button(self.options_frame,
                                   text="Next Frame",
                                   command=self.next_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.prev_btn = ttk.Button(self.options_frame,
                                   text="Prev Frame", 
                                   command=self.prev_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.delete_btn = ttk.Button(self.options_frame,
                                   text="Delete Frame",
                                   command=self.delete_key_frame,
                                   #width=c_width/16
                                   #state="disabled"
                                   )
        self.add_btn = ttk.Button(self.options_frame, 
                                   text="Add Frame", 
                                   command=self.add_key_frame, 
                                   #width=c_width/16
                                   
                                   #state="disabled"
                                   )
      
        

        
        options_arrangement = [
            [self.brush_lbl, self.brush_sb],
            [self.color_btn, self.canvas_color_btn],
            [self.clear_btn, self.wipeout_btn],
            [self.prev_btn,  self.next_btn],
            [self.delete_btn, self.add_btn],
            [self.debug_btn, self.cpy_btn],
            [self.save_btn, self.gif_btn ],
            [self.resize_btn, self.open_btn],
            [self.bg_color_cb, self.bg_color_btn],
            [self.onion_cb, None],
            [self.onion_prev_lbl, self.onion_prev_sb],
            [self.onion_next_lbl, self.onion_next_sb],
            [self.scale_lbl, self.dim_lbl]
            


         
           
        ]




        

        
        
        
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        #https://blog.teclado.com/tkinter-scrollable-frames/
        #the widget below the only widget that has to be gridded in arrangement
        self.timeline_frame = tk.Frame(self)

        self.timeline_cell_size = 100
        self.timeline_canvas = tk.Canvas(self.timeline_frame, width=self.timeline_cell_size, height=c_height) #about the width of a listbox with no specificied width and heoght
        self.timeline_sb_y = ttk.Scrollbar(self.timeline_frame, orient='vertical', command=self.timeline_canvas.yview)
        self.timeline_scroll_frame = tk.Frame(self.timeline_canvas)
        
        
        #below keeps track for the dynamic checkboxes generated
        #will be the edges and whether they're connected tp other edges,
        # a dictionary of dictionarys and bools 
        self.timeline_widget_list = []
        #collection of th shown checkbox, deleted and regenerated frequently
        self.timeline_img_list = []
        
        
        self.timeline_scroll_frame.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(
                scrollregion=self.timeline_canvas.bbox("all")
            )
        )
        
        self.timeline_canvas.create_window((0, 0), window=self.timeline_scroll_frame, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=self.timeline_sb_y.set)

        #self.edge_scrollbar_y.config(command=self.self.edge_canvas.yview)
        #self.timeline_canvas.pack(fill="y", expand=True) #.grid(row=0, column=0)
        #self.timeline_sb_y.pack(fill="y", expand=True)  #.grid(row=0, column=1, sticky="NS")
        
        self.timeline_canvas.pack(side="left", fill="y", expand=True)
        self.timeline_sb_y.pack(side="left", fill="y", expand=True)
        '''
        #Test
        #comment out the "adding the first frame" part of the script
        options = ["Option " + str(i) for i in range(1,50)]
        
        #https://cs111.wellesley.edu/archive/cs111_fall14/public_html/labs/lab12/tkintercolor.html
        #AI generated: since I didn't feel like  
        colors = {
            "AliceBlue": "#F0F8FF",
            "AntiqueWhite": "#FAEBD7",
            "Aqua": "#00FFFF",
            "Aquamarine": "#7FFFD4",
            "Azure": "#F0FFFF",
            "Beige": "#F5F5DC",
            "Bisque": "#FFE4C4",
            "Black": "#000000",
            "BlanchedAlmond": "#FFEBCD",
            "Blue": "#0000FF",
            "BlueViolet": "#8A2BE2",
            "Brown": "#A52A2A",
            "BurlyWood": "#DEB887",
            "CadetBlue": "#5F9EA0",
            "Chartreuse": "#7FFF00",
            "Chocolate": "#D2691E",
            "Coral": "#FF7F50",
            "CornflowerBlue": "#6495ED",
            "Cornsilk": "#FFF8DC",
            "Crimson": "#DC143C",
            "Cyan": "#00FFFF",
            "DarkBlue": "#00008B",
            "DarkCyan": "#008B8B",
            "DarkGoldenRod": "#B8860B",
            "DarkGray": "#A9A9A9",
            "DarkGreen": "#006400",
            "DarkKhaki": "#BDB76B",
            "DarkMagenta": "#8B008B",
            "DarkOliveGreen": "#556B2F",
            "DarkOrange": "#FF8C00",
            "DarkOrchid": "#9932CC",
            "DarkRed": "#8B0000",
            "DarkSalmon": "#E9967A",
            "DarkSeaGreen": "#8FBC8F",
            "DarkSlateBlue": "#483D8B",
            "DarkSlateGray": "#2F4F4F",
            "DarkTurquoise": "#00CED1",
            "DarkViolet": "#9400D3",
            "DeepPink": "#FF1493",
            "DeepSkyBlue": "#00BFFF",
            "DimGray": "#696969",
            "DodgerBlue": "#1E90FF",
            "FireBrick": "#B22222",
            "FloralWhite": "#FFFAF0",
            "ForestGreen": "#228B22",
            "Fuchsia": "#FF00FF",
            "Gainsboro": "#DCDCDC",
            "GhostWhite": "#F8F8FF",
            "Gold": "#FFD700",
            "GoldenRod": "#DAA520"
        }


        i = 0
        ckeys = list(colors.keys())
        for option in options:
            var = tk.BooleanVar()
            #chk = tk.Checkbutton(self.timeline_scroll_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
            chk = tk.Canvas(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.timeline_cell_size, bg=random.choice(ckeys)).grid(row=i, column=1)
            
            i += 1
        '''
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #Preview Canvas
        self.preview_frame = tk.Frame(self)
        self.preview_canvas = tk.Canvas(self.preview_frame, width=self.timeline_cell_size * 2, height=self.timeline_cell_size * 2, bg=self.canvas_color)
        self.fps_iv = tk.IntVar(value=1)
        self.fps_lbl = tk.Label(self.preview_frame, text="FPS")
        self.fps_scl = tk.Scale(self.preview_frame, from_=1, to=24, variable=self.fps_iv,orient="horizontal", command=None, state="active")
        self.play_img = tk.PhotoImage(file="icons\\play_arrow_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(6, 6)
        self.playing = True
        self.play_btn = tk.Button(self.preview_frame, text="Play", image=self.play_img, command=self.play_preview) 
        self.preview_idx = 0
        self.preview_id = ""
        self.preview_img_list = []
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #Drawing Button Type
        self.btn_frame = tk.Frame(self)
        
        self.pen_img = tk.PhotoImage(file="icons\\edit_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.pen_bn = tk.Button(self.btn_frame, 
                                 text="Draw", 
                                 image=self.pen_img,
                                 ) 
        CreateToolTip(self.pen_bn, "Pen Tool")
        
        self.fill_img = tk.PhotoImage(file="icons\\format_color_fill_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.fill_bn = tk.Button(self.btn_frame, 
                                 text="Bucket", 
                                 image=self.fill_img
                                 ) 
        CreateToolTip(self.fill_bn, "Bucket Tool")
        
        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_bn = tk.Button(self.btn_frame, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_bn, "Eraser Tool")
        

        
        self.rect_img = tk.PhotoImage(file="icons\\rectangle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_bn = tk.Button(self.btn_frame,  
                                 text="Rectangle", 
                                 image=self.rect_img
                                 ) 
        CreateToolTip(self.rect_bn, "Rectangle Tool")
        
        self.circ_img = tk.PhotoImage(file="icons\\circle_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.circ_bn = tk.Button(self.btn_frame, 
                                 text="Circle", 
                                 image=self.circ_img
                                 ) 
        CreateToolTip(self.circ_bn, "Circle Tool")
        
        self.move_img = tk.PhotoImage(file="icons\\back_hand_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.move_bn = tk.Button(self.btn_frame, 
                                 text="Move", 
                                 image=self.move_img
                                 ) 
        CreateToolTip(self.move_bn, "Move Tool")
        
        self.lasso_sel_img = tk.PhotoImage(file="icons\\lasso_select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.lasso_sel_bn = tk.Button(self.btn_frame, 
                                 text="Lasso", 
                                 image=self.lasso_sel_img
                                 ) 
        CreateToolTip(self.lasso_sel_bn, "Lasso Selection\n\tLMB: Selects\n\tRMB: To Move\n\tDelete: Delete Selection")
        
        self.rect_sel_img = tk.PhotoImage(file="icons\\select_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.rect_sel_bn = tk.Button(self.btn_frame, 
                                 text="Select", 
                                 image=self.rect_sel_img
                                 ) 
        CreateToolTip(self.rect_sel_bn, "Rectangle Selection\n\tLMB: Selects\n\tRMB: To Move\n\tDelete: Delete Selection")
        
        self.line_img = tk.PhotoImage(file="icons\\border_color_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.line_bn = tk.Button(self.btn_frame, 
                                 text="Stroke", 
                                 image=self.line_img 
                                 ) 
        CreateToolTip(self.line_bn, "Stroke Tool")
        
        self.picker_img = tk.PhotoImage(file="icons\\colorize_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.picker_bn = tk.Button(self.btn_frame,  
                                 text="Picker", 
                                 image=self.picker_img
                                 ) 
        CreateToolTip(self.picker_bn, "Color Picker")

        self.shear_h_img = tk.PhotoImage(file="icons\\arrow_range_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shear_h_bn = tk.Button(self.btn_frame,  
                                 text="H-Shear", 
                                 image=self.shear_h_img
                                 ) 
        CreateToolTip(self.shear_h_bn, "Shear Horizontal \n(Mousewheel)")

        self.shear_v_img = tk.PhotoImage(file="icons\height_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shear_v_bn = tk.Button(self.btn_frame,  
                                 text="V-Shear", 
                                 image=self.shear_v_img
                                 ) 
        CreateToolTip(self.shear_v_bn, "Shear Vertical \n(Mousewheel)")

        self.rotate_img = tk.PhotoImage(file="icons\\rotate_left_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rotate_bn = tk.Button(self.btn_frame,  
                                 text="Rotate", 
                                 image=self.rotate_img
                                 ) 
        CreateToolTip(self.rotate_bn, "Rotate \n(Mousewheel)")

        

        

        self.wand_img = tk.PhotoImage(file="icons\\wand_stars_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.wand_bn = tk.Button(self.btn_frame,  
                                 text="Wand", 
                                 image=self.wand_img,
                                 ) 
        CreateToolTip(self.wand_bn, "Color Selection\n\tLMB: Selects\n\tRMB: To Move\n\tDelete: Delete Selection")

        self.shift_img = tk.PhotoImage(file="icons\\mobile_theft_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shift_bn = tk.Button(self.btn_frame,  
                                 text="Shift", 
                                 image=self.shift_img,
                                 ) 
        CreateToolTip(self.shift_bn, "Move Image")

        #self.palette_img = tk.PhotoImage(file="icons\\blank.png")
        self.palette_canvas = tk.Canvas(self.btn_frame,  
                                 #text="Draw", 
                                 #image=self.palette_img,
                                 state="disabled",
                                 bg = self.color,
                                 width=32,
                                 height=32,
                                 relief="sunken"
                                 
                                 ) 
        #CreateToolTip(self.palette_canvas, "Current Color")
        #CreateToolTip(self.palette_canvas, "Selected Color")
        
        self.pen_bn.config(command=lambda:self.select_mode(self.pen_bn))
        self.erase_bn.config(command=lambda:self.select_mode(self.erase_bn))
        self.rect_bn.config(command=lambda:self.select_mode(self.rect_bn))
        self.rect_sel_bn.config(command=lambda:self.select_mode(self.rect_sel_bn))
        self.picker_bn.config(command=lambda:self.select_mode(self.picker_bn))
        self.line_bn.config(command=lambda:self.select_mode(self.line_bn))
        self.move_bn.config(command=lambda:self.select_mode(self.move_bn))
        self.circ_bn.config(command=lambda:self.select_mode(self.circ_bn))
        self.lasso_sel_bn.config(command=lambda:self.select_mode(self.lasso_sel_bn))
        self.fill_bn.config(command=lambda:self.select_mode(self.fill_bn))
        self.shear_h_bn.config(command=lambda:self.select_mode(self.shear_h_bn))
        self.shear_v_bn.config(command=lambda:self.select_mode(self.shear_v_bn))
        self.rotate_bn.config(command=lambda:self.select_mode(self.rotate_bn))
        self.wand_bn.config(command=lambda:self.select_mode(self.wand_bn))
        self.shift_bn.config(command=lambda:self.select_mode(self.shift_bn))


        self.drawing_widgets = [
            self.pen_bn     , self.line_bn,
            self.erase_bn   , self.move_bn,
            self.rect_bn    , self.circ_bn,
            self.rect_sel_bn, self.lasso_sel_bn,
            self.picker_bn  ,  self.fill_bn,
            self.shear_h_bn, self.shear_v_bn,
            self.rotate_bn, self.wand_bn,
            self.shift_bn
        ]

        btn_arrangement = [

            [self.pen_bn     , self.line_bn],
            [self.erase_bn   , self.move_bn],
            [self.rect_bn    , self.circ_bn],
            [self.rect_sel_bn, self.lasso_sel_bn],
            [self.picker_bn  ,  self.fill_bn],
            [self.wand_bn, self.rotate_bn],
            [self.shear_h_bn, self.shear_v_bn],
            
            [self.palette_canvas, self.shift_bn]
        ]

        

        #states
        self.mode = "Draw"
        self.direction = ""
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #grid, pack, and place
        arrange_widgets(options_arrangement)
        arrange_widgets(btn_arrangement)
        self.sub_wn = None
        
        

       
        
        
        self.btn_frame.pack(side="left", fill="y")
        self.timeline_frame.pack(side="left", fill="y")
        self.main_frame.pack(side="left", fill="both", expand=True)
        self.preview_frame.pack(side="top", fill="both", anchor="center")
        self.options_frame.pack(side="top", fill="both", anchor="center")
        
        #Preview frame widgets
        self.preview_canvas.pack(side="top", anchor="center")
        self.play_btn.pack(side="left", anchor="center")
        self.fps_lbl.pack(side="left", anchor="center")
        self.fps_scl.pack(side="left", fill="x", expand=True)
        
        
        #main frame's widgets: I used pack to have them expand
        #main widget parts: the order they were backed in matters
        #the other frame's widgets were gridded with grid
        #self.scaling_scl.pack(side="bottom", fill="x")
        
        self.canvas_s_barh.pack(side="bottom", fill="x")
        #packing the rotation scale under the canvas horizontal scrollwheel, packed and unpacked based on 
        #whether the anchor/rotation button is selected
        
        self.canvas.pack(side="left", fill="both", anchor= "center",expand=True)
        self.canvas_s_barv.pack(side="left", fill="y")
        #self.rotation_scl.pack(side="bottom", fill="y")
        #self.rotation_lbl.pack(side="bottom", fill="y", expand=True)
        

        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        
        
        
        
        self.select_mode(self.pen_bn)

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_lmb_release)

        self.canvas.bind("<ButtonPress-3>", self.on_canvas_rmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        self.canvas.bind("<ButtonRelease-3>", self.on_canvas_rmb_release)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel_scroll)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.undo_stack = []
        self.redo_queue = []
        

        
        #thr following attributes are for the four borders, anything else is temporary
        self.top_left = Vertex(
            -1,
            -1,
        )

        self.bottom_left = Vertex(
            
            -1,
            -1,
        )

        self.bottom_right = Vertex(
            -1,
            -1,
        )

        

        self.top_right = Vertex(
            -1,
            -1,
        )
        
        self.borders = []
        
        self.borders = self.set_borders(c_width, c_height, p_width, p_height)
        
        self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale = self.set_scaling(self.canvas)
        self.pixel_scale_og = self.pixel_scale

        #scaling the initial image
        self.pivot_matrix = np.eye(3, dtype=np.float64)
        self.matrix_pivot = np.eye(3, dtype=np.float64)

        #rendering the canvas
        self.current_key_frame.render_image(self.canvas, self.borders)

        #adding the first frame to the timeline
        #self.update_animation_timeline()
        self.update_key_frame(self.frame_idx)
        self.render_borders()
        
        print("Scales Max, Current, Min: ", self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale)
    
        #Turns playing false to true and true to false
        #self.play_preview()



        self.current_directory = os.getcwd()
        #self.selected_file = ""
       
    def set_scaling(self, canvas):
        min_scale, scale, max_scale = -1, -1, -1
        border_x = self.borders[0]
        border_y = self.borders[1]
        border_width = self.borders[4] - self.borders[0]
        border_height = self.borders[5] - self.borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width
        self.scale_lbl.config(text=f"Scale: {true_pixel_width:.2f}")
        self.dim_lbl.config(text=f"[{self.pixel_canvas_width}x{self.pixel_canvas_height}]")
        min_scale = .6
        max_scale = 75 #min(self.canvas_width, self.canvas_height)
        self.max_pixel_scale, self.pixel_scale, self.min_pixel_scale = max_scale, scale, min_scale
        return max_scale, scale, min_scale

    
        
    #border focused methods

    def set_borders(self,canvas_width, canvas_height, pixel_width, pixel_height):
        #these exists so pixels are always square
        c_dimension = max(canvas_width, canvas_height)
        diagonal =  math.sqrt(pixel_width ** 2 + pixel_height ** 2) #distance_to(0, 0, pixel_width, pixel_height) 
        ratio_x = (pixel_width/diagonal) 
        ratio_y = (pixel_height/diagonal)
        #the rest of the area iis space for rotations

        
        #top left
        x0 = canvas_width  * (1 - ratio_x)/2
        y0 = canvas_height * (1 - ratio_y)/2
        #bottom left
        x1 = x0 
        y1 = y0 + c_dimension * ratio_y
        #bottom right
        x2 = x0 + c_dimension * ratio_x
        y2 = y0 + c_dimension * ratio_y
        #top right
        x3 = x0 + c_dimension * ratio_x
        y3 = y0 

        #

 

        self.top_left.set_coords(
            x0,
            y0,
        )

        self.bottom_left.set_coords(
            
            x1,
            y1,
        )

        self.bottom_right.set_coords(
            x2,
            y2,
        )

        

        self.top_right.set_coords(
            x3,
            y3,
        )


        
        
        self.pixel_vertices = []
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]

    def get_borders(self):
        return [
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        ]

    def get_borders_center(self):
        return line_line_intersection(
            self.top_left.get_X(),     self.top_left.get_Y(),
            self.bottom_right.get_X(), self.bottom_right.get_Y(),
            self.top_right.get_X(),    self.top_right.get_Y(),
            self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        )
    
    def render_borders(self, fill = ''):
        #self.canvas.delete("shapes")
        self.borders = self.get_borders()
        self.canvas.create_polygon(self.borders,
                                    fill = fill,
                                    outline='blue',
                                    #tags=("shapes")
                                    )
        
    

    def transform_borders(self, translation_matrix, transform_matrix, matrix_translation):
        
        self.top_left.transform(translation_matrix, transform_matrix, matrix_translation)
        self.top_right.transform(translation_matrix, transform_matrix, matrix_translation)
        self.bottom_left.transform(translation_matrix, transform_matrix, matrix_translation)
        self.bottom_right.transform(translation_matrix, transform_matrix, matrix_translation)

       
    #button focused methods

    def select_mode(self, clicked_widget):
        
        for widget in self.drawing_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
                
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")

        

    def select_direction(self, clicked_widget, widget_array):
        
        for widget in widget_array:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="yellow")
                self.direction = widget.cget("text").strip().upper()

    def on_canvas_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        self.canvas_height = event.height
        self.canvas_width = event.width
       

        canvas_center = line_line_intersection(0, 0, self.canvas_width, self.canvas_height, 0, self.canvas_height, self.canvas_width, 0)
        frame_center = self.get_borders_center()

        cx, cy = -1, -1 #self.canvas_width/2, self.canvas_height/2
        fx, fy = -1, -1
        
        if frame_center:
            fx = frame_center[0]
            fy = frame_center[1]

        if canvas_center:
            cx = canvas_center[0]
            cy = canvas_center[1]

        if frame_center and canvas_center:
            self.canvas.delete("all")
            transform_matrix = np.eye(3)
            self.transform_borders(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
            self.borders = self.get_borders()
            self.render_canvas()


    def wn_open(self, window):
        #https://stackoverflow.com/questions/76940339/is-there-a-way-to-check-if-a-window-is-open-in-tkinter
        # window has been created an exists, so don't create again.
        return window is not None and window.winfo_exists()

    def resize_all_frames(self, width: str, height: str, pivot):

        #resizes the pixel grid for every frame
        #is negative
        if width.startswith("-"):
            return
        
        if height.startswith("-"):
            return
        
        #is the exact same
        if self.pixel_canvas_width == int(width) and self.pixel_canvas_height == int(height):
            return
        
        if int(width) == 0 or int(height) == 0:
            return

        if not width.isnumeric():
            return
        
        

        if not height.isnumeric():
            return
         
        #canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        

        #self.render_borders()
        for i in range(len(self.key_frame_collection)):
            key_frame = self.key_frame_collection[i]
            key_frame.alter_image_dimensions(pivot, int(width), int(height), self.canvas, self.borders)
            key_frame.pixel_canvas_width = int(width)
            key_frame.pixel_canvas_height = int(height)
            #key_frame.scale_image()
            key_frame.scale_image(self.canvas, self.borders)
            self.update_key_frame(i)
            
            #key_frame.update_borders(pivot)
        
        

        self.sub_wn.destroy()
        
        
        
        self.pixel_canvas_width, self.pixel_canvas_height = int(width), int(height)
        self.set_scaling(self.canvas)
        self.borders = self.set_borders(self.canvas_width, self.canvas_height, self.pixel_canvas_width, self.pixel_canvas_height)
        self.dim_lbl.config(text=f"[{self.pixel_canvas_width}x{self.pixel_canvas_height}]")
        self.highlight_current_frame()
        self.render_canvas()

        
    def on_pixel_image_resize(self):

        #resizes pixel grid in every frame: connected to the resize button
        if self.wn_open(self.sub_wn):
            return

        
        #Pop up Window
        self.sub_wn = Toplevel()
        self.sub_wn.resizable(False, False)

        
        apply_resize_btn = tk.Button(self.sub_wn, text="Resize")
        width_frame = tk.Frame(self.sub_wn)
        height_frame = tk.Frame(self.sub_wn)
        sub_frame_1 = tk.Frame(self.sub_wn)
        sub_frame_2 = tk.Frame(self.sub_wn)
        sub_frame_3 = tk.Frame(self.sub_wn)

        NE_btn = tk.Button(sub_frame_1, text="NE")
        N_btn  = tk.Button(sub_frame_1, text="N ")
        NW_btn = tk.Button(sub_frame_1, text="NW")
        E_btn = tk.Button(sub_frame_2, text="E ")
        C_btn = tk.Button(sub_frame_2, text="C ")
        W_btn = tk.Button(sub_frame_2, text="W ")
        SE_btn = tk.Button(sub_frame_3, text="SE")
        S_btn = tk.Button(sub_frame_3, text="S ")
        SW_btn = tk.Button(sub_frame_3, text="SW")

        anchor_widgets = [
            NE_btn, N_btn, NW_btn,
            E_btn, C_btn, W_btn,
            SE_btn, S_btn, SW_btn,
        ]

        NE_btn.config(command=lambda:self.select_direction(NE_btn, anchor_widgets))
        N_btn.config(command=lambda:self.select_direction(N_btn, anchor_widgets))
        NW_btn.config(command=lambda:self.select_direction(NW_btn, anchor_widgets))
        E_btn.config(command=lambda:self.select_direction(E_btn, anchor_widgets))
        C_btn.config(command=lambda:self.select_direction(C_btn, anchor_widgets))
        W_btn.config(command=lambda:self.select_direction(W_btn, anchor_widgets))
        SE_btn.config(command=lambda:self.select_direction(SE_btn, anchor_widgets))
        S_btn.config(command=lambda:self.select_direction(S_btn, anchor_widgets))
        SW_btn.config(command=lambda:self.select_direction(SW_btn, anchor_widgets))

        self.select_direction(C_btn, anchor_widgets)

        width_lbl = tk.Label(width_frame, text="Width")
        width_px_lbl = tk.Label(width_frame, text="px")
        width_entry = tk.Entry(width_frame)

        w = self.pixel_canvas_width #self.current_key_frame.pixel_canvas_width
        width_entry.insert(tk.END, str(w))

        height_lbl = tk.Label(height_frame, text="Height")
        height_px_lbl = tk.Label(height_frame, text="px")
        height_entry = tk.Entry(height_frame)

        h = self.pixel_canvas_height #self.current_key_frame.pixel_canvas_height
        height_entry.insert(tk.END, str(h))

        apply_resize_btn.config(command=lambda:self.resize_all_frames(width_entry.get(), height_entry.get(), self.direction))

        '''
        direction_arrangement = [
            [NE_btn, N_btn, NW_btn],
            [E_btn, C_btn, W_btn],
            [SE_btn, S_btn, SW_btn],
        ]
        

        arrange_widgets(direction_arrangement)
        '''

        NW_btn.pack(fill="both", anchor="nw", side="left", expand=True)
        N_btn.pack(fill="both", anchor="n", side="left", expand=True)
        NE_btn.pack(fill="both", anchor="ne", side="left", expand=True)

        W_btn.pack(fill="both", anchor="w",side="left", expand=True)
        C_btn.pack(fill="both", anchor="center",side="left", expand=True)
        E_btn.pack(fill="both", anchor="e",side="left", expand=True)
        
        
        SW_btn.pack(fill="both", anchor="sw",side="left", expand=True)
        S_btn.pack(fill="both", anchor="s",side="left", expand=True)
        SE_btn.pack(fill="both", anchor="se",side="left", expand=True)
        

        width_lbl.pack(fill="both",side="left", expand=True)
        width_entry.pack(fill="both", side="left", expand=True)
        width_px_lbl.pack(fill="both",side="left", expand=True)

        height_lbl.pack(fill="both",side="left", expand=True)
        height_entry.pack(fill="both", side="left", expand=True)
        height_px_lbl.pack(fill="both",side="left", expand=True)

        #main frames
        width_frame.pack(side="top", fill="both", expand=True)
        height_frame.pack(side="top", fill="both", expand=True)
        sub_frame_1.pack(side="top", fill="both", expand=True)
        sub_frame_2.pack(side="top", fill="both", expand=True)
        sub_frame_3.pack(side="top", fill="both", expand=True)
        apply_resize_btn.pack(side="top", fill="both", expand=True)



        #above tkinter windows
        self.sub_wn.lift()
        self.sub_wn.title("Resize") 
        #app.geometry("800x600")
        self.sub_wn.geometry("250x300")
        self.sub_wn.mainloop()

        
        self.render_canvas()
        #self.render_onion_skin()

        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.update_key_frame(self.frame_idx)
        #self.update_animation_timeline()


    
    #Shortcuts 


    def paste_pixels(self, *args):
        for i in range(len(self.pixels_to_paste)):
            pixel = self.pixels_to_paste[i]
            color = self.colors_to_paste[i]
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                inverted_color = tuple( 
                    self.current_key_frame.hex_to_rgb(
                        self.current_key_frame.invert_color(
                            self.current_key_frame.rgb_to_hex(color[0], color[1], color[2])
                        ),
                        True
                    )
                )
                self.current_key_frame.pixel_image.putpixel((pixel[0], pixel[1]), color)
                #self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = color
                #self.current_key_frame.draw_pixel(self.canvas, current_coord, color, color, current_coord, self.borders)
                #self.canvas.delete(current_coord)


        self.render_canvas()
        #draw_pixel(self, canvas, key_coord, fill, outline, tag, borders):
        
        self.update_key_frame(self.frame_idx)

    def copy_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
        
        self.pixels_to_paste = [pixel for pixel in temp_pixels]
        self.colors_to_paste = [color for color in temp_colors]
        
        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()

        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        #self.render_canvas()

        self.update_key_frame(self.frame_idx)

    def cut_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
        
        for pixel in temp_pixels:
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                #self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = None
                self.current_key_frame.pixel_image.putpixel((pixel[0], pixel[1]), self.current_key_frame.blank)
                #if self.current_key_frame.pixel_coords.get(current_coord):
                #    del self.current_key_frame.pixel_coords[current_coord]
                #self.canvas.delete(current_coord)
        
        self.pixels_to_paste = [pixel for pixel in temp_pixels]
        self.colors_to_paste = [color for color in temp_colors]

        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()
        
        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        self.render_canvas()

        self.update_key_frame(self.frame_idx)

    def delete_pixels(self, *args):
        temp_pixels = self.current_key_frame.get_temp_pixels()
        temp_colors = self.current_key_frame.get_temp_colors()
    
        for pixel in temp_pixels:
            if in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                current_coord = self.current_key_frame.coord_to_str(pixel[0], pixel[1])
                #self.current_key_frame.pixel_grid[pixel[1]][pixel[0]] = None
                self.current_key_frame.pixel_image.putpixel((pixel[0], pixel[1]), self.current_key_frame.blank)
                #if self.current_key_frame.pixel_coords.get(current_coord):
                #    del self.current_key_frame.pixel_coords[current_coord]
                #self.canvas.delete(current_coord)

        self.current_key_frame.temp_colors.clear()
        self.current_key_frame.temp_pixels.clear()
        

        #self.render_onion_skin()
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        #self.render_borders()
        self.render_canvas()

        self.update_key_frame(self.frame_idx)
        
    #Canvas Interaction

    def on_mousewheel_scroll(self, event):

       
        #applies transformations to the canvas or to pixels
        #connect to the mousewheel
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        transform_matrix = np.eye(3, dtype=np.float64)
        
        if self.mode == "H-Shear":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(shear_matrix2D(sign, 0)) #np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            #self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
            self.update_key_frame(self.frame_idx)
            
        elif self.mode == "V-Shear":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(shear_matrix2D(0 , sign)) #np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            self.update_key_frame(self.frame_idx)
            
        elif self.mode == "Rotate":
            #rotating pixels
            sign = (abs(event.delta)//event.delta)
            angle_inc = 20
            #print(sign, degrees_to_radians(angle_inc))
            transform_matrix = np.array(rotation_matrix2D(sign * degrees_to_radians(angle_inc)))
            cx, cy = x, y #self.get_borders_center()
            cx, cy = self.current_key_frame.canvas_to_pixel(self.canvas, cx, cy, self.borders)
            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            self.current_key_frame.transform_pixels(self.matrix_pivot, transform_matrix,  self.pivot_matrix, self.canvas, self.borders)
            self.render_canvas()
            self.update_key_frame(self.frame_idx)
           
            
        else:
        
            #resizing pixels
        
        
        
            scaling_change = 1 + (abs(event.delta)//event.delta)/5
            prev_scale = self.pixel_scale

            self.pixel_scale = self.pixel_scale * scaling_change
            self.scale_lbl.config(text=f"Scale: {self.pixel_scale:.2f}")
            self.dim_lbl.config(text=f"[{self.pixel_canvas_width}x{self.pixel_canvas_height}]")
            #self.scaling_scl.set(self.pixel_scale)
            #print(self.max_pixel_scale, self.min_pixel_scale, prev_scale, self.pixel_scale, scaling_change)

            if self.pixel_scale < self.min_pixel_scale:
                self.pixel_scale = prev_scale
            if self.pixel_scale >= self.max_pixel_scale:
                self.pixel_scale = prev_scale

            if prev_scale != self.pixel_scale:
                
                transform_matrix = np.array(scale_matrix2D(scaling_change, scaling_change))
            else:
                scaling_change = 1
            
            #start = time.time()

            #cx, cy = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            cx, cy = x, y

            self.pivot_matrix[0, 2] = cx
            self.pivot_matrix[1, 2] = cy

            self.matrix_pivot[0, 2] = -cx
            self.matrix_pivot[1, 2] = -cy

            #print(self.current_key_frame.get_borders())
            
            self.transform_borders(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
            self.borders = self.get_borders()
            ltx, lty, rtx, rty, rbx, rby, lbx, lby = self.get_borders()
            #self.render_onion_skin()
            self.canvas.config(scrollregion=(ltx, lty, rbx, rby))

            #for key_frame in self.key_frame_collection:
                #key_frame.pixel_scale = self.pixel_scale
                #key_frame.transform_vertices(self.matrix_pivot, transform_matrix,  self.pivot_matrix)
                #key_frame.scale_image(self.canvas, self.borders)
            #self.current_key_frame.scale_image(self.canvas, self.borders)
            self.render_canvas()
            #self.current_key_frame.render_image(self.canvas, self.borders)
            #self.render_borders()
            #self.current_key_frame.resize_canvas(self.canvas, cx, cy, scaling_change, scaling_change)
            #self.current_key_frame.render_grid(self.canvas, self.borders)

    def render_canvas(self):

        
        self.canvas.delete("all")
        if self.bg_color_iv.get():
            #render borders is first used as a potential background
            self.render_borders(self.bg_color)
            self.preview_canvas.config(bg=self.bg_color)
        else:
            self.preview_canvas.config(bg=self.canvas_color)
            
        self.render_onion_skin()
        self.current_key_frame.render_image(self.canvas, self.borders)
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        self.render_borders()

    def render_onion_skin(self):
  
        if self.onion_iv.get():
            #print("yeap")
            '''
            def rgb_to_hex(self, r,g,b):
                hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)
                return hexcode
            '''
            #self.canvas.delete("onion")
            border_x = self.borders[0]
            border_y = self.borders[1]

            border_width = self.borders[4] - self.borders[0]
            border_height = self.borders[5] - self.borders[1]

            im_width, im_height = self.current_key_frame.pixel_image.size  
            
            true_pixel_width = border_width/im_width
            true_pixel_height = border_height/im_height

            mxp_dim = max(im_width, im_height)
            mxb_dim = max(border_width, border_height)

            scale_dim = mxb_dim/mxp_dim


            img = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.current_key_frame.blank)
            for i in range(self.frame_idx - int(self.onion_prev_sb.get()), self.frame_idx + int(self.onion_next_sb.get()) + 1):
                #if current_frame < len(self.key_frame_collection):
                key_frame = None
                
                
                
                #key_frame = self.key_frame_collection[current_frame]
                #using current_key_frame's 
                #for y in range(self.pixel_canvas_height):
                #    for x in range(self.pixel_canvas_width):
                #print(i)
                if i < self.frame_idx:
                    #previous frame in onion skin
                    if i > -1:
                        key_frame = self.key_frame_collection[i]
                        #coord_key = key_frame.coord_to_str(x, y)
                        prev_img = key_frame.get_pil_image().copy()
                        prev_img_data = []
                        for color in prev_img.getdata():
                            if color[-1] == 0:
                                prev_img_data.append(color)
                            else:
                                prev_img_data.append(
                                                        (
                                                            255, 
                                                            color[1], 
                                                            color[2], 
                                                            int(255 - (175 * ((self.frame_idx - i)/self.onion_prev)))
                                                        )
                                                    )
                        prev_img = Image.new(img.mode, img.size)
                        prev_img.putdata(prev_img_data)
                        #splitting image into color bands
                        #red_img, green_img, blue_img, alpha = prev_img.split()

                        #red_img.putalpha(int(200 * ((self.frame_idx - i)/self.onion_prev)))
                        #prev_img.putalpha(int(200 * ((self.frame_idx - i)/self.onion_prev)))

                        img = Image.alpha_composite(img, prev_img)
                        #img.paste(prev_img, (0,0))

                        
                if i > self.frame_idx:
                    #next frame in onion skin
                 
                    if i < len(self.key_frame_collection):
                        key_frame = self.key_frame_collection[i]
                        next_img = key_frame.get_pil_image().copy()
                        next_img_data = []
                        for color in next_img.getdata():
                            if color[-1] == 0:
                                next_img_data.append(color)
                            else:
                                next_img_data.append(
                                                        (
                                                            color[0], 
                                                            color[1], 
                                                            255, 
                                                            int(255 - (175 * ((i - self.frame_idx)/self.onion_next)))
                                                        )
                                                    )
                        next_img = Image.new(img.mode, img.size)
                        next_img.putdata(next_img_data)
                        #splitting image into color bands
                        #red_img, green_img, blue_img, alpha  = next_img.split()
                        #green_img.putalpha(int(200 * ((i - self.frame_idx)/self.onion_next)))
                        #next_img.putalpha(int(200 * ((i - self.frame_idx)/self.onion_next)))

                        img = Image.alpha_composite(img, next_img)
                        #img.paste(next_img, (0,0))
                        

            self.onion_image =  ImageTk.PhotoImage(
                                    img.resize(
                                        (round(scale_dim * im_width), round(scale_dim * im_height))
                                        , Image.Resampling.NEAREST
                                                            )
                                                )
            
            # Draw the image
            self.canvas.create_image(
                border_x, border_y,     # Image display position (top-left coordinate)
                anchor='nw',            # Anchor, top-left is the origin
                image=self.onion_image,     # Display image data
                #tags = ("image")
                
            )

    def on_canvas_lmb_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return
        
        #self.render_onion_skin()
        
        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        if self.mode == "Draw":
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_click(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()), True)
        elif self.mode == "Erase":
            #print("press")
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_click(x, y, self.canvas, self.canvas_color, self.borders, float(self.brush_sb.get()), False)
        elif self.mode == "Stroke":
            self.current_key_frame.start_stroke(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()))
        elif self.mode == "Move":
            #self.canvas.delete("all")
            self.current_key_frame.move_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Picker":
            self.color = self.current_key_frame.pick_color(x, y, self.canvas, self.borders)
            self.palette_canvas.config(bg=self.color)
        elif self.mode == "Rectangle" or self.mode == "Circle" or self.mode == "Select":
            self.current_key_frame.shape_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Lasso":
            self.current_key_frame.lasso_click(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Bucket":
            self.current_key_frame.bucket_fill(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Wand":
            self.current_key_frame.wand_click(x, y, self.canvas, self.color, self.borders)

    def on_canvas_lmb_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return


        if self.mode == "R-Shear":
            return
        
        if self.mode == "L-Shear":
            return

        if self.mode == "Rotate":
            return

        if self.mode == "Draw":
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_press(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()), True)
        elif self.mode == "Erase":
            #print("press")
            #print(self.current_key_frame.pixel_scale)
            self.current_key_frame.brush_press(x, y, self.canvas, self.canvas_color, self.borders, float(self.brush_sb.get()), False)
        elif self.mode == "Stroke":
            self.current_key_frame.start_stroke(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()))
        elif self.mode == "Move":
            #this was to test the difference between this file and PixAnimate3.py's speed
            #start = time.time()
            self.current_key_frame.move_press(x, y, self.canvas, self.color, self.borders)
            #print(f"Transform Time {time.time() - start}")
        elif self.mode == "Picker":
            self.color = self.current_key_frame.pick_color(x, y, self.canvas, self.borders)
            self.palette_canvas.config(bg=self.color)
        elif self.mode == "Rectangle":
            self.current_key_frame.rectangle_press(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()))
        elif self.mode == "Circle":
            self.current_key_frame.circle_press(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()))
        elif self.mode == "Lasso":
            #print("L")
            self.current_key_frame.lasso_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Select":
            self.current_key_frame.select_press(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Bucket" or self.mode == "Wand":
            pass
        elif self.mode == "Shift":
            # the borders array
            # [
                # self.top_left.get_X(),     self.top_left.get_Y(),
                # self.top_right.get_X(),    self.top_right.get_Y(),
                # self.bottom_right.get_X(), self.bottom_right.get_Y(),
                # self.bottom_left.get_X(),  self.bottom_left.get_Y()  
            # ]
            self.borders = self.current_key_frame.translate_borders(x, y, self.canvas, self.color, self.borders)
            self.top_left.set_coords(self.borders[0], self.borders[1])
            self.top_right.set_coords(self.borders[2], self.borders[3])
            self.bottom_right.set_coords(self.borders[4], self.borders[5])
            self.bottom_left.set_coords(self.borders[6], self.borders[7])
            self.canvas.delete("all")
            self.render_canvas()
        
        self.render_borders()

    def on_canvas_lmb_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        if self.mode == "Draw" or self.mode == "Erase" or self.mode == "Shift" or self.mode == "Bucket" or self.mode == "Wand":
            self.current_key_frame.last_pixel.clear()
        elif self.mode == "Stroke":
            self.current_key_frame.end_stroke(x, y, self.canvas, self.color, self.borders, float(self.brush_sb.get()))
        elif self.mode == "Move":
            self.current_key_frame.move_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Rectangle" or self.mode == "Circle":
            self.current_key_frame.shape_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Lasso":
            #print("L")
            self.current_key_frame.lasso_release(x, y, self.canvas, self.color, self.borders)
        elif self.mode == "Select":
            self.current_key_frame.select_release(x, y, self.canvas, self.color, self.borders)

  
        #self.current_key_frame.render_image(self.canvas, self.borders)

        if self.mode !="Lasso" and self.mode != "Select":
            #this is so temp pixels and temp colors don't get cleared before being used
            self.render_canvas()
            self.update_key_frame(self.frame_idx)
        self.render_borders()
        
    def on_canvas_rmb_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return
        
        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        if self.mode == "Select" or self.mode == "Lasso" or self.mode == "Wand":
            self.current_key_frame.select_move_click(x, y, self.canvas, self.color, self.borders)

    def on_canvas_rmb_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        if self.mode == "Select" or self.mode == "Lasso" or self.mode == "Wand":
            #self.current_key_frame.scale_image(self.canvas, self.borders)
            self.current_key_frame.move_press(x, y, self.canvas, "", self.borders)
        self.render_borders()

    def on_canvas_rmb_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.wn_open(self.sub_wn):
            return
        
        
        #self.render_onion_skin()

        if self.mode == "H-Shear":
            return
        
        if self.mode == "V-Shear":
            return
        
        if self.mode == "Rotate":
            return

        if self.mode == "Select" or self.mode == "Lasso" or self.mode == "Wand":
            self.current_key_frame.select_move_release(x, y, self.canvas, self.color, self.borders)
        #self.update_animation_timeline()
        self.render_canvas()
        self.update_key_frame(self.frame_idx)
        #reason render canvas is commented is because doing so removes the negative colors of
        #both lasso and select
        #self.current_key_frame.render_grid(self.canvas)
        self.render_borders()
      
    def fps_to_ms(self, fps):
        return 1000/fps

    #saving and importing files

    def load_frames(self, image: Image, mode='RGBA'):
        #https://stackoverflow.com/questions/74731252/fastest-way-to-load-an-animated-gif-in-python-into-a-numpy-array
        return [
            np.array(frame.convert(mode))
            for frame in ImageSequence.Iterator(image)
        ]
    
    def open_file(self):


        filetypes = [

                        ("png files", "*.png"),
                        ("gif files", "*.gif"),
    
                    ]
        

        selected_file = filedialog.askopenfilename(
            title='Open files',
            initialdir=self.current_directory,
            filetypes=filetypes
            )
        
        if selected_file:
            self.current_directory = "\\".join(selected_file.split('/')[:-1]) + "\\"
            blank = [255, 255, 255, 0]
            

            self.timeline_img_list.clear()
            for widget in self.timeline_widget_list:
                delete_widget(widget)

            self.timeline_widget_list.clear()
            self.preview_img_list.clear()
            self.key_frame_collection.clear()

            self.canvas.delete("all")
            #self.timeline_canvas.delete("all")
            self.preview_canvas.delete("all")

            #self.timeline_canvas.create_window((0, 0), window=self.timeline_scroll_frame, anchor="nw")
            #self.timeline_canvas.configure(yscrollcommand=self.timeline_sb_y.set)
            
            self.canvas.config(state="disabled")
            if selected_file.split(".")[-1].lower() == "gif":
                #print(selected_file)
                img = [] #Image.open(selected_file)
                
                total_frames = 0
                rgba_grids = []
                selected_file = path_correction(selected_file)
                
                with Image.open(selected_file) as img:
                    rgba_frames = self.load_frames(img)
          
                    total_frames = img.n_frames
                    self.pixel_canvas_width, self.pixel_canvas_height = img.size 
                    self.set_scaling(self.canvas)
                    self.borders = self.set_borders(self.canvas_width, self.canvas_height, self.pixel_canvas_width, self.pixel_canvas_height)
                
                    for i in range(total_frames):
                        #print(i)
                        #img.seek(i)
                        #can't just convert a frame of a gif as an RGBA numpy array
                        #rgba_array = self.load_frames(img) #np.array(img).tolist() 
                        #print(rgba_frames[i])
                        new_frame = ImageFrame( 
                                    self.pixel_canvas_width,
                                    self.pixel_canvas_height, 
                                    self.canvas_width,
                                    self.canvas_height 
                                )
                        #if it's a clear pixel put None in the 2D array, otherwise a hexcode
                        #evil 2d list comprehension, downright devious
                        
                        new_frame.pixel_image = Image.fromarray(rgba_frames[i], mode="RGBA")
        
                        
                        '''
                        new_frame.pixel_grid = [
                                                    [
                                                        #col is an RGBA array like [255, 255, 255, 0] if the last is 0 that means Alpha, transparency is 0
                                                        new_frame.rgb_to_hex(col[0], col[1], col[2]) if col[-1] != 0 else None for col in row
                                                    ] for row in rgba_frames[i]
                                                ]
                        #debug
                        for y in range(len(rgba_frames[i])):
                            for x in range(len(rgba_frames[i][y])):
                                col = rgba_frames[i][y][x]
                                #col is an RGBA array like [255, 255, 255, 0] if the last is 0 that means Alpha, transparency is 0
                                if i == 0:
                                    print(col, len(col))
                                if col[-1] != 0:
                                    
                                    
                                    new_frame.pixel_grid[y][x] = new_frame.rgb_to_hex(col[0], col[1], col[2])
                                else:
                                    new_frame.pixel_grid[y][x] = None 
                        '''   
                                    
                                    
                        
                                    
                        #new_frame.pixel_coords = new_frame.grid_to_coords(self.borders)
                        self.key_frame_collection.append(new_frame)
                        #img.save(target_folder + f'/frame_{i:03d}.png')`
                
                
            else:
                #print(selected_file)
                img = Image.open(selected_file)
                self.pixel_canvas_width, self.pixel_canvas_height = img.size 
                #rgba_array = np.array(img).tolist() 
                #self.temp_pixels = [ [col, row] for row in range(len(self.pixel_grid)) for col in range(len(self.pixel_grid[0])) if self.pixel_grid[row][col] ]
                #print(rgba_array)
                new_frame = ImageFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
                
                self.set_scaling(self.canvas)
                self.borders = self.set_borders(self.canvas_width, self.canvas_height, self.pixel_canvas_width, self.pixel_canvas_height)
                #if it's a clear pixel put None in the 2D array, otherwise a hexcode
                #evil 2d list comprehension, downright devious
                '''
                new_frame.pixel_grid = [
                                            [
                                                #col is an RGBA array like [255, 255, 255, 0] if the last is 0 that means Alpha, transparency is 0
                                                new_frame.rgb_to_hex(col[0], col[1], col[2]) if col[-1] != 0  else None for col in row
                                            ] for row in rgba_array 
                                        ]
                new_frame.pixel_coords = new_frame.grid_to_coords(self.borders)
                '''
                new_frame.pixel_image = img
                self.key_frame_collection.append(new_frame)
                
            self.frame_idx = 0
            self.current_key_frame = self.get_key_frame(self.frame_idx)
            self.render_canvas()
            self.highlight_current_frame()
            self.update_animation_timeline()
            self.canvas.config(state="normal")

    def save_gif(self):

        filetypes = [
                    #("All files", "*.*"),
                    ("gif files", "*.gif"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = self.current_directory, #os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        
        #https://stackoverflow.com/questions/60948028/python-pillow-transparent-gif-isnt-working
        if save_path:
            key_frame_images = []
            if self.bg_color_iv.get():

                rgba = tuple(self.current_key_frame.hex_to_rgb(self.bg_color, True))
                for key_frame in self.key_frame_collection:

                    blank_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), rgba)
                    #blank_image.paste(key_frame.get_pil_image(), (0, 0))
                    blank_image = Image.alpha_composite(blank_image, key_frame.get_pil_image())
                    key_frame_images.append(blank_image)
                key_frame_images[0].save(
                                            save_path, 
                                            format = "GIF", 
                                            save_all=True, 
                                            append_images=key_frame_images[1:],  
                                            duration = self.fps_to_ms(self.fps_scl.get()), 
                                            loop=0, 
                                            disposal=2
                                            
                                        )

                
                
            else:

                key_frame_images = [key_frame.get_pil_image() for key_frame in self.key_frame_collection]
                key_frame_images[0].save(
                                            save_path, 
                                            format = "GIF", 
                                            save_all=True, 
                                            append_images=key_frame_images[1:],  
                                            duration = self.fps_to_ms(self.fps_scl.get()), 
                                            loop=0, 
                                            disposal=2
                                        )

    def save_frame(self):

        #saves an individual frame
        filetypes = [
                    #("All files", "*.*"),
                    ("png files", "*.png"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = self.current_directory, #os.getcwd(),
                                    defaultextension = ".png",
                                    filetypes= filetypes                   
                                    ) 
        if save_path:
            print(save_path)
            if self.bg_color_iv.get():
                rgba = tuple(self.current_key_frame.hex_to_rgb(self.bg_color, True))
                blank_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), rgba)
                blank_image = Image.alpha_composite(blank_image, self.current_key_frame.get_pil_image())
                #blank_image.paste(, (0, 0))
                blank_image.save(save_path)
                
            else:
                self.current_key_frame.get_pil_image().save(save_path)
         
    def clear_frame(self):

        self.current_key_frame.pixel_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.current_key_frame.blank)
        #self.canvas.delete('all')

        self.current_key_frame.pixel_vertices.clear()
        self.current_key_frame.last_pixel = []
        self.current_key_frame.stroke_pixels = []
        self.current_key_frame.temp_pixels = []
        self.current_key_frame.temp_colors = []
        self.current_key_frame.first_pixel = []
        #self.current_key_frame.render_image(self.canvas, self.borders)

        self.update_key_frame(self.frame_idx)
        self.render_canvas()
        self.render_borders()
        #self.update_animation_timeline()

    def clear_frames(self):

        for i in range(len(self.key_frame_collection)):
            key_frame = self.key_frame_collection[i]
            key_frame.pixel_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), key_frame.blank)
            self.update_key_frame(i)
        
            key_frame.pixel_vertices.clear()
            key_frame.last_pixel = []
            key_frame.stroke_pixels = []
            key_frame.temp_pixels = []
            key_frame.temp_colors = []
            key_frame.first_pixel = []

        #self.canvas.delete('all')
        #self.current_key_frame.render_grid(self.canvas, self.borders)
        self.render_canvas()
        self.render_borders()
        #self.update_animation_timeline()

    def debug(self):
       
        print("yep")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        print("Unique Vertices\n")
        #print(f"Length:{len(self.current_key_frame.pixel_vertices)}")

        '''
        for key in self.current_key_frame.pixel_coords:
                        
            vertices = self.current_key_frame.pixel_coords[key]
            
            if vertices:

                print(f"Top Left: {vertices[0]}\nTop Right: {vertices[1]}\nBottom Right: {vertices[2]}\nBottom Left: {vertices[3]}\n")
        '''
        #print("Pixel Coords Len", len(self.current_key_frame.pixel_coords))
        print(f"Sizes:\n Images {len(self.timeline_img_list)} Preview {len(self.preview_img_list)} Timeline: {len(self.timeline_widget_list)}")

        #self.current_key_frame.display_2d([[col for col in self]])
        pixel_grid =  self.current_key_frame.pil_image_to_grid()
        self.current_key_frame.display_2d(pixel_grid)
        #self.current_key_frame.display_2d(self.current_key_frame.pil_image_to_array2D())
        #self.current_key_frame.display_2d(self.current_key_frame.pil_image_to_numpy_array2D())
      
    def choose_color(self):
        print("pixel grid")
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        print(color_code)
        if color_code[1]:
            print(len(color_code[1]))
            self.color = color_code[1]
            self.palette_canvas.config(bg=self.color)

    def change_canvas_color(self):

        #print("pixel grid")
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        #print(self.pixel_coords)
      
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        #print(color_code)
        if color_code[1]:
            #color_code index 1 is a hex code, index 0 is an rgb tuble
            #this is so erasing works
            self.canvas_color = color_code[1] 
            self.canvas.config(bg=self.canvas_color)
            
        self.render_canvas()

    def change_bg_color(self):
        #bg color saved
        #print("pixel grid")
        # variable to store hexadecimal code of selected_color
        color_code = colorchooser.askcolor(title ="Choose selected_color") 
        #print(color_code)
        if color_code[1]:
            #color_code index 1 is a hex code, index 0 is an rgb tuble
            #this is so erasing works
            self.bg_color = color_code[1] 
            self.bg_color_btn.config(bg=self.bg_color, fg=self.current_key_frame.invert_color(self.bg_color))
            

        
        self.render_canvas()
            
    def get_canvas_colors(self):
        set_of_colors = {col for row in self.current_key_frame.pixel_grid for col in row if col != None}
        return set_of_colors

    #Preview Controling Widgets
    def update_preview_canvas(self):

        if self.preview_idx > len(self.preview_img_list) - 1:
            self.preview_idx = 0

        #print(type(self.preview_img_list[self.preview_idx]), type(self.timeline_img_list[self.preview_idx]))
        self.preview_canvas.delete("all")
        
        
        self.preview_canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=self.preview_img_list[self.preview_idx],      # Display image data
            tags = ("image")
        )

        
        self.preview_idx += 1
        self.preview_id = self.after(int(self.fps_to_ms(self.fps_scl.get())),lambda:self.update_preview_canvas())

    def play_preview(self):
        #so you can only chang the fps when the playing is false
        
        #https://stackoverflow.com/questions/66361332/creating-a-timer-with-tkinter
        if self.playing == True:
            #print("fps scale on")
            self.play_btn.config(bg="SystemButtonFace")
            self.fps_scl.config(state="normal", bg="SystemButtonFace")
            self.playing = False
            self.update()
            if self.preview_id:
                self.preview_id = self.after_cancel(self.preview_id)
        else:
            #print("fps scale off")
            self.play_btn.config(bg="yellow")
            self.fps_scl.config(state="disabled", bg="gray")
            
            self.playing = True
            #forcing the buttons to update
            self.update()
            #makes the preview_canvas continually update
            self.preview_id = self.after(int(self.fps_to_ms(self.fps_scl.get())),lambda:self.update_preview_canvas())
            #print(f"FPS to Millisecond {self.fps_to_ms(self.fps_scl.get())}")
    
    ##Timeline controlling widgets
    
    def get_key_frame(self, idx):
        if not self.key_frame_collection:
            new_frame = ImageFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height,
                            )
            self.key_frame_collection.append(new_frame)
            #allows the key_frame to delete selected pixels
            #self.bind("<Delete>", lambda:new_frame.select_delete(self, self.canvas))
            
            return self.key_frame_collection[idx]
        else:
            return self.key_frame_collection[idx]
            
    def next_key_frame(self, *args):

        #self.canvas.delete("all")
        self.frame_idx += 1
        if self.frame_idx == len(self.key_frame_collection):
            self.frame_idx = len(self.key_frame_collection) - 1
        
        self.current_key_frame = self.get_key_frame(self.frame_idx)

        self.render_canvas()
        self.highlight_current_frame()

    def prev_key_frame(self, *args):

        #self.canvas.delete("all")
        self.frame_idx -= 1
        if self.frame_idx < 0:
            self.frame_idx = 0

        self.current_key_frame = self.get_key_frame(self.frame_idx)

        self.render_canvas()
        self.highlight_current_frame()

    def highlight_current_frame(self):

        for i in range(len(self.timeline_widget_list)):
            widget = self.timeline_widget_list[i]
    
            if i == self.frame_idx:
                
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="Azure3")

    def duplicate_key_frame(self):

        #new_len = len(self.key_frame_collection)
        new_frame = ImageFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
        
        

        new_frame.pixel_image = self.current_key_frame.pixel_image.copy()

        
        if len(self.key_frame_collection) - 1 == self.frame_idx:
        

            self.key_frame_collection.append(new_frame)
            self.update_animation_timeline()
            #clones the image to the timeline
            self.timeline_widget_list[self.frame_idx + 1].config(image=self.timeline_img_list[self.frame_idx])
        else:
            self.key_frame_collection.insert(self.frame_idx + 1, new_frame)
            self.update_animation_timeline()
            #clones the image to the timeline
            self.timeline_widget_list[self.frame_idx + 1].config(image=self.timeline_img_list[self.frame_idx])
        

        self.render_canvas()

    def add_key_frame(self):
     
        new_frame = ImageFrame( 
                                self.pixel_canvas_width,
                                self.pixel_canvas_height, 
                                self.canvas_width,
                                self.canvas_height 
                            )
        
        
  
        new_frame.pixel_scale = self.pixel_scale
        

        
        if len(self.key_frame_collection) - 1 == self.frame_idx:
        

            self.key_frame_collection.append(new_frame)
        else:
            self.key_frame_collection.insert(self.frame_idx + 1, new_frame)
        
 
        self.update_animation_timeline()
    
    def delete_key_frame(self, *args):
        
        if len(self.key_frame_collection) > 1:
            
            if self.frame_idx >= len(self.key_frame_collection) - 1:

                self.key_frame_collection.pop(self.frame_idx)
                self.timeline_img_list.pop(self.frame_idx)
                self.preview_img_list.pop(self.frame_idx)
                delete_widget(self.timeline_widget_list.pop(self.frame_idx))
                self.frame_idx = len(self.key_frame_collection) - 1

                
            else:
                
                self.key_frame_collection.pop(self.frame_idx)
                self.timeline_img_list.pop(self.frame_idx)
                self.preview_img_list.pop(self.frame_idx)
                delete_widget(self.timeline_widget_list.pop(self.frame_idx))
                
 
            
            
            
            self.current_key_frame = self.get_key_frame(self.frame_idx)
            self.render_canvas()

            self.update_animation_timeline()
            
    def select_key_frame(self, string_idx : str):
        
        print("selected",string_idx)
        self.canvas.delete("all")
        self.frame_idx = int(string_idx)

        
      

        self.current_key_frame = self.get_key_frame(self.frame_idx)
        self.render_canvas()
        #self.current_key_frame.borders = self.key_frame_collection[0].borders
        if self.timeline_widget_list:
           
            self.highlight_current_frame()
            
    def update_key_frame(self, idx):
        '''
        item = self.canvas.create_image(
            0, 0,           # Image display position (top-left coordinate)
            anchor='nw',    # Anchor, top-left is the origin
            image=im,        # Display image data
            tags = ("image")
            
        )
        '''
        key_frame = self.get_key_frame(idx) #self.key_frame_collection[idx]
            
        #https://note.nkmk.me/en/python-pillow-paste/
        #self.current_key_frame.display_2d(self.current_key_frame.pixel_grid)
        display_img = None


        img = key_frame.get_pil_image()
        im_width, im_height = img.size  
        canvas_size = self.timeline_cell_size
        mx_dim = max(im_width, im_height)
        mn_dim = min(im_width, im_height)
        scale_dim = canvas_size/mx_dim

        #button/canvas background image, will have the scaled image pasted on top of it
        blank_image = Image.new("RGBA", (canvas_size, canvas_size), "#000000")

        ratio_x = im_width/mx_dim - 1
        ratio_y = im_height/mx_dim - 1

        ix = 0
        iy = 0
        if ratio_x != 0:
            ix = round((abs(ratio_x) * canvas_size)/2)

        if ratio_y != 0:
            iy = round((abs(ratio_y) * canvas_size)/2)

        #Timeline display image
        #scaling the image for the button/canvas size 
        #LANCZOS looks better on larger pixel grids while Nearest Looks better on smaller pixel grids
        #3000 is the area of 50 * 60 pixels
        if self.pixel_canvas_height * self.pixel_canvas_width > 3000:
            scaled_img = img.resize((round(scale_dim * im_width), round(scale_dim * im_height)),  Image.Resampling.LANCZOS)
            blank_image.paste(scaled_img, (ix, iy))
        else:
            scaled_img = img.resize((round(scale_dim * im_width), round(scale_dim * im_height)),  Image.Resampling.NEAREST)
            blank_image.paste(scaled_img, (ix, iy))
        #print(scaled_img.size)
        display_img = ImageTk.PhotoImage(blank_image)

        #Preview display image
        #10000 is the area of 100 * 100 pixels
        preview_img = None
        if self.pixel_canvas_height * self.pixel_canvas_width > 10000:
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.LANCZOS))
        else:
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))



        #initialization
        if len(self.timeline_img_list) <= idx:
            #print("a")
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))
            self.preview_img_list.append(preview_img)
            self.timeline_img_list.append(display_img)
        else:
            #print("b")
            preview_img = ImageTk.PhotoImage(img.resize((round(2 * scale_dim * im_width), round(2 * scale_dim * im_height)),  Image.Resampling.NEAREST))
            self.preview_img_list[idx] = preview_img
            self.timeline_img_list[idx] = display_img
            
        #initialization
        if len(self.timeline_widget_list) <= idx:
            #print("c")
            #the reason timeline_img_list is used is because without a container keeping track of an image, widget, or whatever, it will be garbage collected and not show up
            w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        bg="Azure3",
                        text = str(idx),
                        command=lambda:self.select_key_frame(str(idx))
                        )

            w.grid(row=idx, column=0)
            self.timeline_widget_list.append(w)
            #w.config(command=self.select_key_frame(w.cget("text")))
            
        else:
            #print("d")
            delete_widget(self.timeline_widget_list[idx])
            w = None
            if idx == self.frame_idx:
                w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        bg="SystemButtonFace",
                        text = str(idx),
                        command=lambda:self.select_key_frame(str(idx))
                        )
            else:
                w = tk.Button(
                        self.timeline_scroll_frame, 
                        image=self.timeline_img_list[idx],
                        text = str(idx),
                        bg="Azure3",
                        command=lambda:self.select_key_frame(str(idx))
                        )
            #self.timeline_widget_list[idx] = w
            #w.config(command=self.select_key_frame(w.cget("text")))
        
        
        

            
            self.timeline_widget_list[idx] = w
            self.timeline_widget_list[idx].grid(row=idx, column=0)



    
    
    
        

        #chk = tk.Canvas(self.timeline_scroll_frame, width=self.timeline_cell_size, height=self.anim_canvas_height, bg="gray").grid(row=self.current_key_frame, column=1)
        #self.update()
        #self.update_idletasks()

    def update_animation_timeline(self):
        #matches the 
        
        
        for i in range(len(self.key_frame_collection)):
            self.update_key_frame(i)
            widget = self.timeline_widget_list[i]
        
            if i == self.frame_idx:
                
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="Azure3")
            
                    
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #frame.bind('<Left>', leftKey)
        #frame.bind('<Right>', rightKey)
        "<Left>"
        "<Right>"
        "<Control-z>"
        "<Control-y>"
        #self.bind("<Down>", self.t2d_poly.undo)
        #self.bind("<Up>", self.t2d_poly.redo)
        
        IKs = Animator(self, 500, 500, 32, 32)
        IKs.pack(side="top", fill="both", expand=True)
        
        self.bind("<Up>", IKs.prev_key_frame)
        self.bind("<Down>", IKs.next_key_frame)
        self.bind("<Delete>", IKs.delete_pixels)
        self.bind("<Control-c>", IKs.copy_pixels)
        self.bind("<Control-v>", IKs.paste_pixels)
        self.bind("<Control-x>", IKs.cut_pixels)
        self.bind("<Control-d>", IKs.delete_key_frame)
        
        self.bind("<Control-s>", lambda a:print("Quick Save not implemented"))
        self.bind("<Control-z>", lambda a:print("Undo not implemented"))
        self.bind("<Control-y>", lambda a:print("Redo not implemented"))
        

    


if __name__ == "__main__":
    # problems
    # duplicate works but doesn't update the timeline FIXED
    # pixels that don't exist in the grid not being moved or deleted when selected FIXED
    # resize grid sometimes not working FIXED
    # Need to add animation preview FIXED
    # onion skin spinboxes on prev and next FIXED
    # palette import from pixelplacer3.py
    # impor images and gifs FIXED
    # Xaolin's Woo's antialiasing
    # different brush sizes DONE
    # rotation and anchoring FIXED
    # 9  23 25
    # see if it's possible replace the draw_pixel method in Frame_image render_image and Image.getpixel((x,y)) and Image.putpixel((x,y)) SUCCESS
        # draw_pixel is essential as placeholder pixels, until the image is really updated
        # so perhaps each FrameImage can have three images, in addition to canvas_image, the Tkinter PhotoImage, and pixel_image, the Pil Image
            # This would likely be a temporary image that temp_pixels can be pasted to and displayed over the real image
        # 9 28 25 as of now, when moving pixels a temporary image and canvas image is used and discarded when appropiate
    # fix render order for bucket and wand FIXED
    # drag borders DONE
    # swap frames, both with button and timeline
    # make the timeline more effient, only update frames after.
    # pixel size label DONE
    # fix resizing? DONE


    app = App()
    
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    app.title("Tk Toon")
    app.resizable()
    app.mainloop()
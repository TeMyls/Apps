import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk, ImageSequence, ImageOps
from MatrixMath import *
from collisions import *
from WidgetUtils import *
from Vertex3D import *
from Vertex2D import *
#from Frame__Image import *
#from FrameImage import *
from Tool_tip import *
import numpy as np
from numpy import radians as to_radians
import math
import time
import csv

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

def degrees_to_radians(deg):
    return to_radians(deg) #(deg * math.pi)/180

def clamp(x, lower, upper):
  if x < lower:
    return lower
  elif x > upper:
    return upper
  else:
    return x

def lerp(a, b, amount):
  return a + (b - a) * clamp(amount, 0, 1)

  

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
        #self.current_key_frame = self.get_key_frame(self.frame_idx)
        self.last_pixel = []
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #3D DATA
        #A List of vertices
        #Example
        #x1, y1, z1, x2, y2, z2, x3, etc 
        self.vertices = []
        #An Dictionary/Adjacency List of edges
        #The keys are the x indexes of vertices 
        #The values are a list of vertex connections
        #Example
        #{0: [], 6: [1, 2, 0, 3], 3: [0, 2], 1: [2, 0], 5: [0, 3, 4], 4: [1, 2]}
        self.edges = {}
        # A List of lists of vertices forming faces from their egdes
        # uses in the same x indexes vertices as above
        #Formed from a Depth First Search Graph Cycle Detecton Algorithm on the edges
        #or Triangles from the Vertex and it's edge
        #Example
        #[[0, 2, 3], [1, 4, 5], [0, 2, 7], [0, 3, 6], [1, 4, 8], [1, 5, 9], etc]
        self.faces = []
        
        
        
        #camera planes 
        self.near = 1
        self.far = -1
        self.scale = 1
        
        #orthographic screen coordinates
        self.top = 1
        self.left = -1
        self.right = 1
        self.bottom = -1

        
        
        #depth cirle size
        
        self.z_min = 1
        self.z_max = 20
        self.z_size = (self.far + self.near)/2
        
        
        #actual z value
        self.zed = round((self.z_size/(self.z_max - self.z_min)) * (self.far - self.near))
        
        

        #MATRICES
        

        a = 2/(self.right - self.left)
        b = 2/(self.top - self.bottom) 
        c = -2/(self.far - self.near)
        d = -1 * (self.far + self.near)/(self.far - self.near)
        e = -1 * (self.top + self.bottom)/(self.top - self.bottom)
        f = -1 * (self.right + self.left)/(self.right - self.left)
        #OpenGL Orthographic Matrix
        self.ortho_perspective_matrix = np.array([
                    [a, 0, 0, f], #x
                    [0, b, 0, e], #y
                    [0, 0, c, d], #z 
                    [0, 0, 0, 1] 
        ])
        
        
        
        #screen coordinates perspective
        self.fov = 110
        self.fov_radians = (self.fov * math.pi)/180
        self.aspect_ratio = self.canvas_width/self.canvas_height
        
        
        self.top = math.tan(self.fov_radians/2) * self.near
        self.left = -self.top * self.aspect_ratio
        self.right = self.top * self.aspect_ratio
        self.bottom = -self.top
        
        
        
        a = (2*self.near)/(self.right - self.left) #1/(self.aspect_ratio*math.tan(self.fov_radians/2))
        b = (2*self.near)/(self.top - self.bottom) #1/math.tan(self.fov_radians/2)
        c = -1 * ( self.far + self.near)/(self.far - self.near)
        d = -1 * ( 2 * self.far * self.near)/(self.far - self.near)
        e = (self.top + self.bottom)/(self.top - self.bottom)
        f = (self.right + self.left)/(self.right - self.left)
        
        
        #OpenGL perspective matrix
        self.true_perspective_matrix = np.array([
                    [a, 0, e, 0], #x
                    [0, b, f, 0], #y
                    [0, 0, c, d], #z 
                    [0, 0,-1, 0] 
        ])
        
        #Handled by switch matrix states
        self.current_matrix = self.true_perspective_matrix #self.ortho_perspective_matrix



        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        '''
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

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #Drawing Button Type

        self.btn_frame = tk.Frame(self)

        self.place_img = tk.PhotoImage(file="icons\\add_circle_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.place_btn = tk.Button(self.btn_frame, 
                                 text="Place", 
                                 image=self.place_img,
                                 ) 
        CreateToolTip(self.place_btn, "RMB:Preview Vertex\nLMB:Place Vertex\nScroll:Set Depth")

        self.pan_img = tk.PhotoImage(file="icons\\drag_pan_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.pan_btn = tk.Button(self.btn_frame, 
                                 text="Pan", 
                                 image=self.pan_img
                                 ) 
        CreateToolTip(self.pan_btn, "RMB:Pan\nLMB:Rotate\nScroll:Move")

        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_btn = tk.Button(self.btn_frame, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_btn, "Eraser Vertex")

        self.select_img = tk.PhotoImage(file="icons\link_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.select_btn = tk.Button(self.btn_frame, 
                                 text="Select", 
                                 image=self.select_img
                                 ) 
        CreateToolTip(self.select_btn, "Select Vertex")

        self.connect_img = tk.PhotoImage(file="icons\\add_link_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.connect_btn = tk.Button(self.btn_frame, 
                                 text="Connect", 
                                 image=self.connect_img
                                 ) 
        CreateToolTip(self.connect_btn, "Add Edge")


        self.break_img = tk.PhotoImage(file="icons\\link_off_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.break_btn = tk.Button(self.btn_frame, 
                                 text="Break", 
                                 image=self.break_img
                                 ) 
        CreateToolTip(self.break_btn, "Break Edge")




        self.target_img = tk.PhotoImage(file="icons\\point_scan_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.target_btn = tk.Button(self.btn_frame, 
                                 text="Target", 
                                 image=self.target_img
                                 ) 
        CreateToolTip(self.target_btn, "Target Point")

        self.rotate_img = tk.PhotoImage(file="icons\\rotate_right_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rotate_btn = tk.Button(self.btn_frame, 
                                 text="Rotate", 
                                 image=self.rotate_img
                                 ) 
        CreateToolTip(self.rotate_btn, "Rotate Vertex\nLMB:X rotation\nRMB:Y Rotation\nScroll:Z rotation")

        self.mirror_img = tk.PhotoImage(file="icons\\flip_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.mirror_btn = tk.Button(self.btn_frame, 
                                 text="Mirror", 
                                 image=self.mirror_img
                                 ) 
        CreateToolTip(self.mirror_btn, "Mirror")



        self.drawing_widgets = [
            self.place_btn, self.pan_btn,
            self.select_btn, self.connect_btn,
            self.break_btn, self.target_btn,
            self.erase_btn, self.rotate_btn
            
        ]

        self.mode ="Draw"

        self.place_btn.config(command=lambda:self.select_mode(self.place_btn))
        self.pan_btn.config(command=lambda:self.select_mode(self.pan_btn))
        self.select_btn.config(command=lambda:self.select_mode(self.select_btn))
        self.connect_btn.config(command=lambda:self.select_mode(self.connect_btn))
        self.break_btn.config(command=lambda:self.select_mode(self.break_btn))
        self.target_btn.config(command=lambda:self.select_mode(self.target_btn))
        self.rotate_btn.config(command=lambda:self.select_mode(self.rotate_btn))
        self.erase_btn.config(command=lambda:self.select_mode(self.erase_btn))
        self.mirror_btn.config(command=lambda:self.select_mode(self.mirror_btn))

        btn_arrangement = [

            [self.place_btn, self.pan_btn],
            [self.select_btn, self.connect_btn],
            [self.break_btn, self.target_btn ],
            [self.erase_btn, self.rotate_btn],
            [self.mirror_btn]
 
        ]

        

        #states
        self.mode = "Draw"
     
        
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        self.options_frame = tk.Frame(self)
        
        

        self.screen_xy = VTX2D(self.canvas_width/2, self.canvas_height/2) #[self.canvas_width/2, self.canvas_height/2]
        self.screen_xy_label = ttk.Label(self.options_frame, text = "Screen \nX:{} \nY: {}".format(self.screen_xy.get_X(), self.screen_xy.get_Y()))

        self.world_xyz = VTX3D(0.0, 0.0, self.zed) #[0.0, 0.0, self.zed]
        self.world_xyz_label = ttk.Label(self.options_frame, text = "World \nX:{} \nY:{} \nZ:{}".format(self.world_xyz.get_X(), self.world_xyz.get_Y(), round(self.world_xyz.get_Z(),3)))

        '''
        #camera planes 
        self.near = 1
        self.far = -1
        self.scale = 1
        
        #orthographic screen coordinates
        self.top = 1
        self.left = -1
        self.right = 1
        self.bottom = -1
        '''
        self.camera_label = ttk.Label(self.options_frame, text = "Camera \nNear:{:.02f} \nFar:{:.02f} \nTop:{:.02f} \nLeft:{:.02f} \nRight:{:.02f} \nBottom:{:.02f}".format(
            self.near, self.far, self.top, self.left, self.right, self.bottom
            )
        )

        self.data_btn = ttk.Button(self.options_frame, text="Print Data", command=self.display_data)

        self.seek_btn = ttk.Button(self.options_frame, 
                                  text="DFS",
                                  command=self.traverse
                                )
        
        self.imp_btn = ttk.Button(self.options_frame, text="Import CSV", command=self.import_data)
        self.exp_btn = ttk.Button(self.options_frame, text="Export CSV", command=self.export_data)
        
        self.arrows_iv = tk.BooleanVar(value=False)
        self.arrows_cb = tk.Checkbutton(self.options_frame, 
                                 text="Arrows", 
                                 variable=self.arrows_iv,
                                 command=self.has_arrows
                                 ) 
        
        self.loop_iv = tk.BooleanVar(value=False)
        self.loop_cb = tk.Checkbutton(self.options_frame, 
                                 text="Loop Edges", 
                                 variable=self.loop_iv,
                                 command=self.is_looping
                                 )
        
        self.idx_iv = tk.BooleanVar(value=False)
        self.idx_cb = tk.Checkbutton(self.options_frame, 
                                 text="Indexes", 
                                 variable=self.idx_iv,
                                 command=self.has_indexes
                                 ) 
        
        self.vtx_iv = tk.BooleanVar(value=True)
        self.vtx_cb = tk.Checkbutton(self.options_frame, 
                                 text="Vertices", 
                                 variable=self.vtx_iv,
                                 command=self.has_vertices
                                 ) 

        self.edge_iv = tk.BooleanVar(value=True)
        self.edge_cb = tk.Checkbutton(self.options_frame, 
                                 text="Edge", 
                                 variable=self.edge_iv,
                                 command=self.has_vertices
                                 ) 
        
        self.rot_iv = tk.BooleanVar(value=False)
        self.rot_cb = tk.Checkbutton(self.options_frame, 
                                 text="Angle", 
                                 variable=self.rot_iv,
                                 command=self.has_angles
                                 ) 
        
        self.xyz_iv = tk.BooleanVar(value=False)
        self.xyz_cb = tk.Checkbutton(self.options_frame, 
                                 text="XYZ", 
                                 variable=self.xyz_iv,
                                 command=self.has_position
                                 )

        self.grid_vis_iv = tk.BooleanVar(value=True)
        self.grid_vis_cb = tk.Checkbutton(self.options_frame, 
                                 text="Grid", 
                                 variable=self.grid_vis_iv,
                                 command=self.has_position
                                )

        self.grid_xyz_iv = tk.BooleanVar(value=True)
        self.grid_xyz_cb = tk.Checkbutton(self.options_frame, 
                                 text="Grid XYZ", 
                                 variable=self.grid_xyz_iv,
                                 command=self.has_position
                                 )
        
        self.z_edge_iv = tk.BooleanVar(value=False)
        self.z_edge_cb = tk.Checkbutton(self.options_frame, 
                                 text="Z Edges", 
                                 variable=self.z_edge_iv,
                                 command=self.has_position
                                 )
        
        

        options_arrangement = [

            [self.screen_xy_label, self.world_xyz_label],
            [self.data_btn, self.seek_btn],
            [self.imp_btn, self.exp_btn],
            [self.arrows_cb, self.idx_cb],
            [self.vtx_cb, self.rot_cb],
            [self.xyz_cb, self.grid_vis_cb],
            [self.grid_xyz_cb, self.edge_cb],
            [self.loop_cb, self.z_edge_cb]
            


        ]
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        #grid, pack, and place
        arrange_widgets(options_arrangement, "W")
        arrange_widgets(btn_arrangement)

        self.sub_wn = None
        
        
        self.selected_vtx = 0
        self.target_vtx = 0
       
        
        
        self.btn_frame.pack(side="left", fill="y")
        #self.timeline_frame.pack(side="left", fill="y")
        self.main_frame.pack(side="left", fill="both", expand=True)
        #self.preview_frame.pack(side="top", fill="both", anchor="center")
        self.options_frame.pack(side="top", fill="both", anchor="center")
        
        #Preview frame widgets
        #self.preview_canvas.pack(side="top", anchor="center")
        #self.play_btn.pack(side="left", anchor="center")
        #self.fps_lbl.pack(side="left", anchor="center")
        #self.fps_scl.pack(side="left", fill="x", expand=True)
        
        
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
        
        
        
        
        
        self.select_mode(self.place_btn)

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<B1-Motion>",  self.on_canvas_lmb_press) #self.z_pos)
        self.canvas.bind("<ButtonRelease-1>",  self.on_canvas_lmb_release)

        
        self.canvas.bind("<ButtonPress-3>",  self.on_canvas_rmb_click) #self.place_vertex)
        self.canvas.bind("<B3-Motion>",  self.on_canvas_rmb_press)
        self.canvas.bind("<ButtonRelease-3>",  self.on_canvas_rmb_release)
        

        self.canvas.bind("<MouseWheel>",  self.on_mousewheel_scroll)#self.set_depth)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.undo_stack = []
        self.redo_queue = []
        

        
        #thr following attributes are for the four borders, anything else is temporary
        '''
        self.top_left = VTX2D(
            -1,
            -1,
        )

        self.bottom_left = VTX2D(
            
            -1,
            -1,
        )

        self.bottom_right = VTX2D(
            -1,
            -1,
        )

        

        self.top_right = VTX2D(
            -1,
            -1,
        )
        
        self.borders = []
        '''
        #self.borders = self.set_borders(c_width, c_height, p_width, p_height)
        
        #self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale = self.set_scaling(self.canvas)
        #self.pixel_scale_og = self.pixel_scale

        #scaling the initial image
        self.pivot_matrix = np.eye(3, dtype=np.float64)
        self.matrix_pivot = np.eye(3, dtype=np.float64)

        #rendering the canvas
        #self.current_key_frame.render_image(self.canvas, self.borders)

        #adding the first frame to the timeline
        #self.update_animation_timeline()
        #self.update_key_frame(self.frame_idx)
        #self.render_borders()
        
        #print("Scales Max, Current, Min: ", self.max_pixel_scale, self.pixel_scale,  self.min_pixel_scale)
    
        #Turns playing false to true and true to false
        #self.play_preview()

        self.down_shift = False
        self.reset_grid_states()
        self.current_directory = os.getcwd()
        self.update_viewport()
        #self.selected_file = ""

    def select_mode(self, clicked_widget):
        
        for widget in self.drawing_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
                
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")

    # Canvas Methods

    def on_canvas_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        print(f"Canvas resized to: {event.width}x{event.height}")
        c_min = min(event.height, event.width)
        self.canvas_height = c_min
        self.canvas_width = c_min
        self.last_pixel.clear()

        canvas_center = line_line_intersection(0, 0, self.canvas_width, self.canvas_height, 0, self.canvas_height, self.canvas_width, 0)

        
        self.update_viewport()

    def on_canvas_lmb_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)


        #self.render_onion_skin()
        
        if self.mode == "Place":
            return
        
        elif self.mode == "Pan":
            #print("eh")
            #self.last_pixel.clear()
            self.pan_camera(event, "LMB_Click")
        
        self.update_viewport()
        #self.render_projected_vertices()

    def on_canvas_lmb_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.mode == "Place":
            #self.z_pos(event)
            self.place_vertex(event, "LMB_Press")
        
        elif self.mode == "Pan":
            #self.shift_camera(event)
            self.pan_camera(event, "LMB_Press")

        elif self.mode == "Erase":
            self.remove_vertex(event)

        elif self.mode == "Connect":
            self.connect_vertex(event)
            
        elif self.mode == "Select":
            self.select_vertex(event)
            
        elif self.mode == "Break":
            self.break_vertex(event)
            
        elif self.mode == "Target":
            #self.target_vertex(event)
            #self.FABRIK()
            pass
        elif self.mode == "Mirror":
            pass
        elif self.mode == "Rotate":
            self.rotate_vertex(event, "X")
           

        #if self.vertices:
        #    self.highlight_vertex(self.selected_vtx)
        
        self.update_viewport()
        #self.render_projected_vertices()

    def on_canvas_lmb_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.mode == "Place":
            return
        
        elif self.mode == "Pan":
            #print("eh")
            self.pan_camera(event, "LMB_Release")
            #self.last_pixel.clear()

        self.update_viewport()
        #self.render_projected_vertices()
        
    def on_canvas_rmb_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.mode == "Place":
            self.place_vertex(event, "RMB_Click")
        
        elif self.mode == "Pan":
            #print("eh")
            self.pan_camera(event, "RMB_Click")
            #self.last_pixel.clear()

        self.update_viewport()
        #self.render_projected_vertices()

    def on_canvas_rmb_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.mode == "Place":
            pass
        
        elif self.mode == "Pan":
            self.pan_camera(event, "RMB_Press")
            #self.rotate_camera(event)
        elif self.mode == "Rotate":
            self.rotate_vertex(event, "Y")

        self.update_viewport()
        #self.render_projected_vertices()

    def on_canvas_rmb_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.mode == "Place":
            return
        
        elif self.mode == "Pan":
            #print("eh")
            self.pan_camera(event, "RMB_Release")
            #self.last_pixel.clear()

        self.update_viewport()
        #self.render_projected_vertices()
    
    def on_mousewheel_scroll(self, event):
        if self.mode == "Place":
            #self.set_depth(event)
            self.place_vertex(event, "Scroll")
        
        elif self.mode == "Pan":
            #self.rescale(event)
            self.pan_camera(event, "Scroll")
            
        elif self.mode == "Rotate":
            self.rotate_vertex(event, "Z")

        self.update_viewport()
    #COORDINATE SPACE TRANSFORMATIONS

    def update_matrix(self):
        '''
        #camera planes 
        self.near = 1
        self.far = -1
        self.scale = 1
        
        #orthographic screen coordinates
        self.top = 1
        self.left = -1
        self.right = 1
        self.bottom = -1

        
        #x y z
        self.camera_position = [0.0, 0.0, -self.far/2]
        '''
        
        #actual z value
        #self.zed = round((self.z_size/(self.z_max - self.z_min)) * (self.far - self.near))
        
        

        #MATRICES
        

        a = 2/(self.right - self.left)
        b = 2/(self.top - self.bottom) 
        c = -2/(self.far - self.near)
        d = -1 * (self.far + self.near)/(self.far - self.near)
        e = -1 * (self.top + self.bottom)/(self.top - self.bottom)
        f = -1 * (self.right + self.left)/(self.right - self.left)
        #OpenGL Orthographic Matrix
        
        
        
        
        #screen coordinates perspective
        self.fov = 110
        self.fov_radians = (self.fov * math.pi)/180
        self.aspect_ratio = self.canvas_width/self.canvas_height
        
        
        self.top = math.tan(self.fov_radians/2) * self.near
        self.left = -self.top * self.aspect_ratio
        self.right = self.top * self.aspect_ratio
        self.bottom = -self.top
        
        
        
        a = (2*self.near)/(self.right - self.left) #1/(self.aspect_ratio*math.tan(self.fov_radians/2))
        b = (2*self.near)/(self.top - self.bottom) #1/math.tan(self.fov_radians/2)
        c = -1 * ( self.far + self.near)/(self.far - self.near)
        d = -1 * ( 2 * self.far * self.near)/(self.far - self.near)
        e = (self.top + self.bottom)/(self.top - self.bottom)
        f = (self.right + self.left)/(self.right - self.left)
        
        
        #OpenGL perspective matrix
        self.true_perspective_matrix = np.array([
                    [a, 0, f, 0], #x
                    [0, b, e, 0], #y
                    [0, 0, c, d], #z 
                    [0, 0,-1, 0] 
        ])
        
        #Handled by switch matrix states
        #self.current_matrix = self.ortho_perspective_matrix
    
    def world_to_screen(self, xyz_coords: VTX3D):
        #this is the function that projects 3d points from the world to the screen
        #xyz_coords = set_matrix3D(x, y, z)\
        #gx, gy, gz = xyz_coords.get_X(), xyz_coords.get_Y(), xyz_coords.get_Z()
        projected_points = self.current_matrix @ xyz_coords.vertex
        gx, gy, gz = projected_points[0, 0], projected_points[1, 0], projected_points[2, 0]
        
        return ((gx + 1)/2) * self.canvas_width,  ((-gy + 1)/2) * self.canvas_height #((gy + 1)/2) * self.canvas_height #
    
    def screen_to_world(self, xy_coords: VTX2D):
        #for mouse to world detection, based of the OpenGL 2d clip space
        #https://webglfundamentals.org/webgl/lessons/webgl-fundamentals.html
        #y 1 would be top center -1 bottom center
        #x 1 would be right center -1 left center
        #the center of the screen would be the orgin 0, 0
        x, y = xy_coords.get_X(), xy_coords.get_Y()
        return  round((x/self.canvas_width)  * 2 - 1, 6),  round((y/self.canvas_height) * -2 + 1, 6), self.zed #round((y/self.canvas_height) * 2 - 1, 6), self.zed #
    
    # Utils

    def DDA(self, x0, y0, x1, y1):
        #Digital Differential Analyzer
        
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx),abs(dy))
        
        coordinates = []
        if steps != 0:
            x_inc = dx/steps
            y_inc = dy/steps
            
            x = x0
            y = y0
            
            
            
            for i in range(int(steps)):
                x += x_inc
                y += y_inc
                floored_coords = [math.floor(x), math.floor(y)]
                if floored_coords not in coordinates:
                    coordinates.append(floored_coords)
                    
            
        return coordinates

    def DDA_raycast(self, x0, y0, radians, limit):
        x_inc = math.cos(radians)
        y_inc = math.sin(radians)

        _x = x0
        _y = y0

        d = distance_to(x0, y0, _x, _y)
        while d < limit:
            _x += x_inc
            _y += y_inc
            d = distance_to(x0, y0, _x, _y)

        return _x, _y

    # Mouse Methods

    


    def reset_last_pixel(self):
        #print("eh")
        self.last_pixel.clear()

    

    def pan_camera(self, event, action):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        z =  event.delta
        _x, _y, _z = self.screen_to_world(VTX2D(x, y))
        if action == "LMB_Click":
            self.last_pixel.clear()
        elif action == "RMB_Click":
            self.last_pixel.clear()
        elif action == "LMB_Press":
            if self.last_pixel:
                damper = 200
                
                dx, dy = (_x - self.last_pixel[0]), (_y - self.last_pixel[1])
                dxy = (dy + dx)/2
                #self.near = 1
                #self.far = -1
                
                

                #orthographic screen coordinates

                tm = np.array(translation_matrix3D(-self.world_xyz.get_X(), -self.world_xyz.get_Y(), -self.world_xyz.get_Z()))
                xm = np.array(translation_matrix3D(dx, 0, 0))
                ym = np.array(translation_matrix3D(0, dy, 0))
                mt = np.array(translation_matrix3D(self.world_xyz.get_X(), self.world_xyz.get_Y(), self.world_xyz.get_Z()))
                tran_tot = xm @ ym 
                #self.near += dxy
                #self.far += dxy

                for i in range(len(self.vertices)):
                    self.vertices[i].transform(tm, tran_tot, mt)
                
                #self.near += dxy
                #self.far += dxy

                
                #if self.current_matrix == self.ortho_perspective_matrix:
                self.apply_grid_transformation(self.grid_lines, tm, tran_tot, mt)
                #self.apply_grid_transformation(self.grid_lines_x, tm, tran_tot, mt)
                #self.apply_grid_transformation(self.grid_lines_z, tm, tran_tot, mt)
            
                '''
                else:
                    a = (2*self.near)/(self.right - self.left) #1/(self.aspect_ratio*math.tan(self.fov_radians/2))
                    b = (2*self.near)/(self.top - self.bottom) #1/math.tan(self.fov_radians/2)
                    c = -1 * ( self.far + self.near)/(self.far - self.near)
                    d = -1 * ( 2 * self.far * self.near)/(self.far - self.near)
                    e = (self.top + self.bottom)/(self.top - self.bottom)
                    f = (self.right + self.left)/(self.right - self.left)

                    self.true_perspective_matrix = np.array([
                        [a, 0, f, 0], #x
                        [0, b, e, 0], #y
                        [0, 0, c, d], #z 
                        [0, 0,-1, 0] 
                    ])
                '''
                #self.camera_label.config(text = "Camera \nNear:{:.02f} \nFar:{:.02f} \nTop:{:.02f} \nLeft:{:.02f} \nRight:{:.02f} \nBottom:{:.02f}".format(
                #    self.near, self.far, self.top, self.left, self.right, self.bottom
                #    )
                #)

            self.last_pixel.clear()
            if not self.last_pixel:
                self.last_pixel = [_x, _y]
        elif action == "RMB_Press":
            # Rotates Camera Around the World Screens

            if self.last_pixel:
                '''
                #camera planes 
                self.near = 1
                self.far = -1
                self.scale = 1
                
                #orthographic screen coordinates
                self.top = 1
                self.left = -1
                self.right = 1
                self.bottom = -1
                '''
                damper = 200
                sign_x = -1 if _x < 0 else 1
                sign_y = -1 if _y < 0 else 1
                dx, dy = (_x - self.last_pixel[0])/(self.right - self.left) * 360, (_y - self.last_pixel[1])/(self.top - self.bottom) * 360
                dxy = (dy + dx)/2
                #self.near = 1
                #self.far = -1
                #print(f"{dx:.2f} {dy:.2f} {(_x - self.last_pixel[0])} {(_y - self.last_pixel[1])}")
                
                #orthographic screen coordinates

                
                tm = np.array(translation_matrix3D(-self.world_xyz.get_X(), -self.world_xyz.get_Y(), -self.world_xyz.get_Z()))
                xm = np.array(x_rotation_matrix3D(degrees_to_radians(dy)))
                ym = np.array(y_rotation_matrix3D(degrees_to_radians(-dx)))
                zm = np.array(z_rotation_matrix3D(degrees_to_radians(dxy)))
                mt = np.array(translation_matrix3D(self.world_xyz.get_X(), self.world_xyz.get_Y(), self.world_xyz.get_Z()))
        
        
                tot_rot = xm @ ym #@ zm
                #self.near += dxy
                #self.far += dxy
                for i in range(len(self.vertices)):
                    
                    self.vertices[i].transform(tm, tot_rot, mt)
                
                self.apply_grid_transformation(self.grid_lines, tm, tot_rot, mt)
                #self.apply_grid_transformation(self.grid_lines_x, tm, tot_rot, mt)
                #self.apply_grid_transformation(self.grid_lines_z, tm, tot_rot, mt)
                #if self.current_matrix == self.ortho_perspective_matrix:

                
    
            
                
            self.last_pixel.clear()
            if not self.last_pixel:
                self.last_pixel = [_x, _y]
        elif action == "LMB_Release":
            self.last_pixel.clear()
        elif action == "RMB_Release":
            self.last_pixel.clear()
        elif action == "Scroll":
            # Resizing the scene

            scale = abs(event.delta/(event.delta + 1))
            self.z_max = self.z_max * scale

            tm = np.array(translation_matrix3D(-self.world_xyz.get_X(), -self.world_xyz.get_Y(), -self.world_xyz.get_Z()))
            xm = np.array(scale_matrix3D(scale, scale, scale))
            mt = np.array(translation_matrix3D(self.world_xyz.get_X(), self.world_xyz.get_Y(), self.world_xyz.get_Z()))
            tran_tot = xm 
            #self.near += dxy
            #self.far += dxy

            for i in range(len(self.vertices)):
                self.vertices[i].transform(tm, tran_tot, mt)
                
            #self.near += dxy
            #self.far += dxy

            
            #if self.current_matrix == self.ortho_perspective_matrix:
            self.apply_grid_transformation(self.grid_lines, tm, tran_tot, mt)
            #self.apply_grid_transformation(self.grid_lines_x, tm, tran_tot, mt)
            #self.apply_grid_transformation(self.grid_lines_z, tm, tran_tot, mt)

    def place_vertex(self, event, action):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        z =  event.delta
        _x, _y, _z = self.screen_to_world(VTX2D(x, y))
        if action == "LMB_Click":
            pass
        elif action == "RMB_Click":
            # Placing a Vertex
            # Updating Edges

            wx, wy, wz = self.world_xyz.get_X(), self.world_xyz.get_Y(), self.world_xyz.get_Z()
            
            vertex = VTX3D(wx, wy, wz)
            self.vertices.append(vertex)
            #self.vertices.append(wx)
            #self.vertices.append(wy)
            #self.vertices.append(wz)
            
            deci = 2
            rwx, rwy, rwz = round(wx, deci), round(wy, deci), round(wz, deci)
            
            #total_verts = (len(self.vertices)//3) - 1
            
            #self.vertex_listbox.insert(tk.END, "V{}-x:{}:y:{}:z:{}".format(total_verts, rwx, rwy, rwz))
            if len(self.vertices) > 0:
                
                x, y = self.world_to_screen(vertex)
                
                #Vertex Styles
                idx = len(self.vertices) - 1
                oval_size = self.z_oval(wz)
                self.canvas.create_oval(
                                x - oval_size, 
                                y - oval_size, 
                                x + oval_size, 
                                y + oval_size, 
                                fill = "blue",
                                tags=("vertex")
                                )
                
                self.edges[idx] = []
                #self.edges[total_verts] = []
                #self.update_edge_checkbuttons()
                
                
                print("New Vertex x:{}:y:{}:z:{}".format(rwx, rwy, rwz))
                #print(self.vertices)

        elif action == "LMB_Press":
            #Updateing the Screen and World Positions
            #  screen coords
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            

            self.screen_xy.set_coords(x, y)
            _x, _y, _z = self.screen_to_world(self.screen_xy)
            self.world_xyz.set_coords(_x, _y, _z)

            oval_size = 3
            self.canvas.delete("s-coords")
            self.canvas.create_oval(
                            x - oval_size, 
                            y - oval_size,
                            x + oval_size,
                            y + oval_size,
                            fill = "yellow",
                            tags=("s-coords")
                            )
            
            # world coords
            x, y = self.world_to_screen(self.world_xyz)
            
            oval_size = self.z_oval(self.zed)
            #print(oval_size)
            self.canvas.delete("w-coords")
            self.canvas.create_oval(
                            x - oval_size, 
                            y - oval_size,
                            x + oval_size,
                            y + oval_size,
                            fill = "green",
                            tags=("w-coords")
                            )
            

            
        elif action == "RMB_Press":
            pass
        elif action == "LMB_Release":
            pass
        elif action == "RMB_Release":
            pass
        elif action == "Scroll":
            # Setting the Depth
            #mousewheel
            z_inc =  z/3600
            #print(z_inc)
            '''
            if z_inc < 0:
                if self.z_size > self.z_min:
                    self.z_size = self.z_size + z_inc
                else:
                    self.z_size = self.z_min
                    
            if z_inc > 0:
                if self.z_size < self.z_max:
                    self.z_size = self.z_size + z_inc
                else:
                    self.z_size = self.z_max
            '''  
            self.zed += z_inc #= 1 + (self.z_size/(self.z_max - self.z_min)) * (self.far - self.near) + 0.22
            
            self.world_xyz.set_coords(self.world_xyz.get_X(), self.world_xyz.get_Y(), self.zed)
             
            x, y = self.screen_xy.get_X(), self.screen_xy.get_Y()
            oval_size = 3
            self.canvas.delete("s-coords") 
            self.canvas.create_oval(
                            x - oval_size, 
                            y - oval_size,
                            x + oval_size,
                            y + oval_size,
                            fill = "yellow",
                            tags=("s-coords")
                            )
            
            x, y = self.world_to_screen(self.world_xyz)
            oval_size = self.z_oval(self.zed)
            
            self.canvas.delete("w-coords")
            self.canvas.create_oval(
                            x - oval_size, 
                            y - oval_size,
                            x + oval_size,
                            y + oval_size,
                            fill = "green",
                            tags=("w-coords")
                            )
        deci = 2
        rwx, rwy, rwz = round(self.world_xyz.get_X(), deci), round(self.world_xyz.get_Y(), deci), round(self.world_xyz.get_Z(), deci)
        sx, sy = round(self.screen_xy.get_X(), deci), round(self.screen_xy.get_Y(), deci)
        self.world_xyz_label.config(text = "World \nX:{} \nY:{} \nZ:{}".format(rwx, rwy, rwz))
        self.screen_xy_label.config(text = "Screen \nX:{} \nY:{}".format(sx, sy))
        '''
        if action == "LMB_Click":
            pass
        elif action == "RMB_Click":
            pass
        elif action == "LMB_Press":
            pass
        elif action == "RMB_Press":
            pass
        elif action == "LMB_Release":
            pass
        elif action == "RMB_Release":
            pass
        elif action == "Scroll":
            pass
        '''

    def rotate_vertex(self, event, action):
        if not self.loop_iv.get():
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            z =  event.delta/36
            _x, _y, _z = self.screen_to_world(VTX2D(x, y))
            #"Rotate Vertex\nLMB:X rotation\nRMB:Y Rotation\nScroll:Z rotation"
            if self.last_pixel and len(self.edges[self.selected_vtx]) > 0:
                dx = (_x - self.last_pixel[0])/(self.right - self.left) * 360
                dy = (_y - self.last_pixel[1])/(self.top - self.bottom) * 360
                dz = z 
                
                
                tot_rot = np.eye(4)
                #prev_angle = self.vertices[self.selected_vtx].angle
                #self.vertices[self.selected_vtx].angle = self.rotation_scl.get()
                #angle_change = degrees_to_radians(prev_angle - self.vertices[self.selected_vtx].angle)

                '''
                vx,vy = self.vertices[self.selected_vtx].get_coords()
                transform_matrix = np.array(rotation_matrix2D(angle_change))
                
                anchor_matrix = np.array(translation_matrix2D(-vx, -vy))
                matrix_anchor = np.array(translation_matrix2D(vx, vy))
                childern = self.dfs(self.edges, self.selected_vtx)[1:]
                '''
                anchor_matrix = np.array(translation_matrix3D(-self.vertices[self.selected_vtx].get_X(), -self.vertices[self.selected_vtx].get_Y(), -self.vertices[self.selected_vtx].get_Z()))
                matrix_anchor = np.array(translation_matrix3D(self.vertices[self.selected_vtx].get_X(), self.vertices[self.selected_vtx].get_Y(), self.vertices[self.selected_vtx].get_Z()))
                childern = self.dfs(self.edges, self.selected_vtx)[1:]
                #tm = np.array(translation_matrix3D(-self.world_xyz.get_X(), -self.world_xyz.get_Y(), -self.world_xyz.get_Z()))
                #xm = np.array(x_rotation_matrix3D(degrees_to_radians(dy)))
                #ym = np.array(y_rotation_matrix3D(degrees_to_radians(-dx)))
                #zm = np.array(z_rotation_matrix3D(degrees_to_radians(dxy)))
                #mt = np.array(translation_matrix3D(self.world_xyz.get_X(), self.world_xyz.get_Y(), self.world_xyz.get_Z()))
        
                if action == "X":
                    #prev_angle = self.vertices[self.selected_vtx].x_angle
                    #dx = (_x - self.last_pixel[0])/(self.right - self.left) * 360
                    #print(dy)
                    transform_matrix =  np.array(x_rotation_matrix3D(degrees_to_radians(dy)))
                    #self.vertices[self.selected_vtx].x_angle = self.rotation_scl.get()
                elif action == "Y":
                    #dy = (_y - self.last_pixel[1])/(self.top - self.bottom) * 360
                    #print(-dx)
                    transform_matrix = np.array(y_rotation_matrix3D(degrees_to_radians(-dx)))
                    #prev_angle = self.vertices[self.selected_vtx].y_angle
                    
                elif action == "Z":
                    #print(dz)
                    transform_matrix = np.array(z_rotation_matrix3D(degrees_to_radians(dz)))

                #print(transform_matrix)
                for vtx in childern:
                    self.vertices[vtx].transform(anchor_matrix, transform_matrix, matrix_anchor)

            self.last_pixel.clear()
            if not self.last_pixel:
                self.last_pixel = [_x, _y]

    def remove_vertex(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        #_x, _y, _z = self.screen_to_world(VTX2D(x, y))
        radius = 5

        if self.vertices:
            idx = self.is_vertex_colliding(x, y, radius)
            
            '''
            for i in range(len(self.vertices)):
                #if point_circle(x, y, self.vertices[i].get_X(), self.vertices[i].get_Y(), self.radius * 2):
                vx, vy, vz = self.vertices[i].get_X(), self.vertices[i].get_Y(), self.vertices[i].get_Z()
                oval_size = self.z_oval(vz)
                vx, vy = self.world_to_screen(self.vertices[i])
                if circle_circle(x, y, radius, vx, vy, oval_size):
                    idx = i
                    break
            '''
            if idx > -1:
                #print(idx)
                self.canvas.delete("vertex")
                self.vertices.pop(idx)
                #----------------------------------------------------------------------------------------------------
                
                #updating the edges list
                #self.edges is an adjcency list
                
                #print("remove vert")
                #getting rid of the deleted vertex in the dictionary
                self.edges.pop(idx)

                dict_new = {}

            
                for key in self.edges:
                    #getting rid of the deleted vertex in the vertex's array
                    if idx in self.edges[key]:
                        self.edges[key].remove(idx)
                        #self.edge_options[key].pop(v_ind)

                    #reorganizing the dictionary with updated indexes to reflect deletion
                    for i in range(len(self.edges[key])):
                        if self.edges[key][i] > idx:
                            self.edges[key][i] = self.edges[key][i] - 1


                    #filling the replacement dictionary
                
                    if key > idx:
                        #print('ye')
                        new_key = key - 1
                        dict_new[new_key] = self.edges[key]
                    else:
                        #print('ne')
                        dict_new[key] = self.edges[key]

                self.edges = dict_new
                #----------------------------------------------------------------------------------------------------

                
                if self.selected_vtx >= idx:
                    if idx != 0:
                        self.selected_vtx = idx - 1
                    else:
                        self.selected_vtx = 0

                if len(self.vertices) < 1:
                    self.target_vtx = -1

                self.render_projected_vertices()
                #self.render_vertices()
                #self.render_edges()
                #self.distances = self.edge_distance()
                
                
                

                
                #self.update_edge_checkbuttons()

        self.render_brush(x, y, radius, 1, "red", "erasing", "")

    def select_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)



        #self.canvas.delete("selected")
        #self.canvas.delete("erasing")
        
        radius = 5


        if len(self.vertices) > 0:
            idx = self.is_vertex_colliding(x, y, radius)
            '''
            for i in range(len(self.vertices)):
                
                vx, vy, vz = self.vertices[i].get_X(), self.vertices[i].get_Y(), self.vertices[i].get_Z()
                oval_size = self.z_oval(vz)
                vx, vy = self.world_to_screen(self.vertices[i])
                if circle_circle(x, y, radius, vx, vy, oval_size):
                    idx = i
                  
                    break
            '''

            if idx != -1:
                self.selected_vtx = idx

                self.highlight_vertex(idx)
                #print(f"selected: {self.selected_vtx}")

        #self.render_brush(x, y, radius, 1, "red", "erasing")
        self.render_brush(x, y, radius, 1.5, "red", "erasing", "")

        #if self.vertices:
        #    self.rotation_iv.set(self.vertices[self.selected_vtx].angle)
            
    def connect_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        radius = 3
        
        if len(self.vertices) > 1:
           
            idx = self.is_vertex_colliding(x, y, radius)
            '''
            for i in range(len(self.vertices)):
                if i != self.selected_vtx:
                    vx, vy, vz = self.vertices[i].get_X(), self.vertices[i].get_Y(), self.vertices[i].get_Z()
                    oval_size = self.z_oval(vz)
                    vx, vy = self.world_to_screen(self.vertices[i])
                    if circle_circle(x, y, radius, vx, vy, oval_size):
                        idx = i
                        
                        break
            '''
            #print(f"selected: {self.selected_vtx} Parent Type:{type(list(self.edges.keys())[0])} idx: {idx}")
            
                #self.selected_vtx = idx
            
      
            if idx > -1 and self.selected_vtx > -1:

                if idx != self.selected_vtx:
                    #print("HEARS")
                    if idx not in self.edges[self.selected_vtx]:
                        self.edges[self.selected_vtx].append(idx)
                        if not self.loop_iv.get():
                            #self.edges[idx].append(self.selected_vtx)
                            cycle_count = len(self.get_cycles(self.edges))
                            #print(cycle_count)
                            if cycle_count > 0:
                                #print("cycle prevented")
                                self.edges[self.selected_vtx].remove(idx)
                                #self.edges[idx].remove(self.selected_vtx)
                    
                self.selected_vtx = idx       
                if idx != -1:
                        
                        self.highlight_vertex(idx)

                        
        #self.render_vertices()  
        #self.render_edges()
        self.render_brush(x, y, radius, 0.7, "green", "connected", "")
        #self.render_brush(x, y, radius, 1, "red", "erasing")

    def break_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        radius = 4
        
        
        if len(self.vertices) > 1:
            #print('yep')
            idxs = {}
            #oval_size = self.z_oval(z1)
            for key_1 in self.edges:
                for key_2 in self.edges[key_1]:
                    x1, y1, z1 = self.vertices[key_1].get_X(), self.vertices[key_1].get_Y(), self.vertices[key_1].get_Z()
                    
                    x1, y1 = self.world_to_screen(self.vertices[key_1])

                    x2, y2, z2 = self.vertices[key_2].get_X(), self.vertices[key_2].get_Y(), self.vertices[key_2].get_Z()
                    x2, y2 = self.world_to_screen(self.vertices[key_2])
                    
                    if line_circle(x1, y1, x2, y2, x, y, radius):
                    
                        if idxs.get(key_1):
                            idxs[key_1].append(key_2)
                        else:
                            idxs[key_1] = [key_2]
                               
            #print(idxs)                 
            for key_1 in idxs:
                for key_2 in idxs[key_1]:
                    self.edges[key_1].remove(key_2)

                        

                        
        #self.render_vertices()  
        #self.render_edges()
        self.render_brush(x, y, radius, 1.5, "red", "breaking", "")

    def target_vertex(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        #self.target.set_coords(x, y)
        self.render_brush(x, y, 0.5, "gray", "target", "")
        radius = 3
        if len(self.vertices) > 1:
            idx = self.is_vertex_colliding(x, y, radius)
            '''
            for i in range(len(self.vertices)):
                
                ox, oy = self.vertices[i].get_coords()
                if circle_circle(x, y, self.radius, ox, oy, self.radius):
                    #if the index in self.vertices has no childern as represented by []
                    if not self.edges[i] and self.selected_vtx != idx:
                        idx = i
                  
                        break
            '''

            if idx != -1:
                self.target_vtx = idx

                #self.highlight_vertex(idx)
                #print(f"selected: {self.selected_vtx}")
                ox, oy = self.vertices[idx].get_coords()
                self.render_brush(ox, oy, radius, 1.5, "gray", "target_sel", "")

    def is_vertex_colliding(self, x, y, radius) -> int:
        idx = -1
        for i in range(len(self.vertices)):
            if i != self.selected_vtx:
                vx, vy, vz = self.vertices[i].get_X(), self.vertices[i].get_Y(), self.vertices[i].get_Z()
                oval_size = self.z_oval(vz)
                vx, vy = self.world_to_screen(self.vertices[i])
                if circle_circle(x, y, radius, vx, vy, oval_size):
                    idx = i
                    return idx
        return idx
    
    def z_oval(self, z):
        return clamp((1 - (z - 1)/(self.far - self.near)) * self.z_max, self.z_min, self.z_max)

    def display_data(self):
        print("Vertices")
        for vertex in self.vertices:
            print(f"Vertex: {vertex}")
        print("Edges")
        for key in self.edges:
            # Parent Type:{type(key)}
            print(f"Parent: {key} Childern: {self.edges[key]}")
        print("Distances")
        #for key in self.distances:
            # Parent Type:{type(key)}
            
            #print(f"Vertex: {key} Distances: {self.distances[key]}")
        
        print(f"Selected: {self.selected_vtx}")
        print(f"Target: {self.target_vtx}")
        print("Last Pixel ", self.last_pixel)
        #print("X Grid")
        #print("| |".join([str(vtx) for vtx in self.grid_lines_x]))
        #print("Z Grid")
        #print("| |".join([str(vtx) for vtx in self.grid_lines_z]))

    def z_sort(self):
        pass

    def render_projected_vertices(self):
        self.canvas.delete("vertex")
        if self.vertices:
            mult = 2
            
            #self.canvas.delete("all")
            #self.vertex_listbox.delete(0, tk.END)
            deci = 2
            z_verts = {self.vertices[i].get_Z():i for i in range(len(self.vertices))}
            #sorting 
            #https://stackoverflow.com/questions/9001509/how-do-i-sort-a-dictionary-by-key
            #https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
            #sort by value
            #z_verts = {k: v for k, v in sorted(z_verts.items(), key=lambda item: item[0])}
            #sort by key
            z_verts = dict(sorted(z_verts.items()))
            z_ordered = list(z_verts.values())
            #print(list(map(str, z_verts.keys())))
            #print(z_ordered)
            #print([str(vert) for vert in self.vertices])



            #for i in range(len(self.vertices)):
            for i in z_ordered:
   
                
                vertex = self.vertices[i]
                
                x, y, z = vertex.get_X(), vertex.get_Y(), vertex.get_Z()
                
                
                
                #self.vertex_listbox.delete(vert_ind)
                #self.vertex_listbox.insert(vert_ind, "V{}-x:{}:y:{}:z:{}".format(vert_ind, rx, ry, rz))
                if y < self.top:
                    x, y = self.world_to_screen(vertex)
                    
                    oval_size = self.z_oval(z)
                    cx1 = x - oval_size
                    cy1 = y - oval_size 
                    cx2 = cx1 + oval_size * 2
                    cy2 = cy1 + oval_size * 2
                    rotation = 90

                    if self.vtx_iv.get():

                        self.canvas.create_oval(
                                                cx1, cy1, 
                                                cx2, cy2,
                                                tags = ("vertex"),
                                                fill = "blue"
                                                )
                        
                    if self.idx_iv.get():
                        idx = str(i)
                        self.canvas.create_text(

                                            x + oval_size * mult * math.cos(degrees_to_radians(rotation)), 
                                            y + oval_size * mult * math.sin(degrees_to_radians(rotation)), 
                                            text = idx,
                                            tags = ("vertex"),
                                            fill = "orange"
                                            
                                            )
                        rotation += 90
                        
                    if self.xyz_iv.get():
                        #print(abs(rotation % 90))
                        mult = 4
                        if abs(rotation % 180) > 0: 
                            self.canvas.create_text(

                                                x + oval_size * mult * math.cos(degrees_to_radians(rotation)), 
                                                y + oval_size * mult * math.sin(degrees_to_radians(rotation)), 
                                                text = f"X:{vertex.get_X():.2f}Y:{vertex.get_Y():.2f}Z:{vertex.get_Z():.2f}",
                                                tags = ("vertex"),
                                                fill="yellow"
                                                
                                                )
                            
                            
                        else:
                            self.canvas.create_text(

                                                x + oval_size * mult * math.cos(degrees_to_radians(rotation)), 
                                                y + oval_size * mult * math.sin(degrees_to_radians(rotation)), 
                                                text = f"X:{vertex.get_X():.2f}\nY:{vertex.get_Y():.2f}\nZ:{vertex.get_Z():.2f}",
                                                tags = ("vertex"),
                                                fill="yellow"
                                                
                                                )
                            
                        rotation += 90
                        
    def render_edges(self):
        self.canvas.delete("edgelines")
        if self.edges:
            for key in self.edges:
                for value in self.edges[key]:
                    #print("yep")
                    ax, ay, az = self.vertices[key].get_X(), self.vertices[key].get_Y(), self.vertices[key].get_Z()
                    bx, by = self.vertices[value].get_X(), self.vertices[value].get_Y()

                    ax, ay = self.world_to_screen(self.vertices[key])
                    bx, by = self.world_to_screen(self.vertices[value])
                    if self.edge_iv.get():
                        self.canvas.create_line(
                                ax, ay,
                                bx, by,
                                tags=("edgelines"),
                                fill="black"
                            )
                    
                    if ax != bx and ax != by: 
                        if self.arrows_iv.get():
                            angle = angle_to(ax, ay, bx, by)
                            radius = self.z_oval(az) if self.vtx_iv.get() else 1
                            arrow_size = 7 * (((self.near - self.far) + az)/(self.near - self.far))
                            a1 = 150
                            a2 = a1 + 60
                            
                            vx1 = bx + math.cos(angle) * -radius
                            vy1 = by + math.sin(angle) * -radius
                            vx2 = vx1 + math.cos(angle - degrees_to_radians(a1)) * arrow_size
                            vy2 = vy1 + math.sin(angle - degrees_to_radians(a1)) * arrow_size
                            vx3 = vx1 + math.cos(angle - degrees_to_radians(a2)) * arrow_size
                            vy3 = vy1 + math.sin(angle - degrees_to_radians(a2)) * arrow_size
                            triangle = [
                                    vx1, vy1,
                                    vx2, vy2,
                                    vx3, vy3
                                ]
                            
                            self.canvas.create_polygon(
                                triangle,
                                tags = ("edgelines"),
                            )
                        if self.z_edge_iv.get():
                            angle = angle_to(ax, ay, bx, by)
                            radius = self.z_oval(az) if self.vtx_iv.get() else 1
                            arrow_size = 7 * (((self.near - self.far) + az)/(self.near - self.far))
                            a1 = 150
                            a2 = a1 + 60
                            
                            vx1 = bx + math.cos(angle) * -radius
                            vy1 = by + math.sin(angle) * -radius
                            vx2 = vx1 + math.cos(angle - degrees_to_radians(a1)) * arrow_size
                            vy2 = vy1 + math.sin(angle - degrees_to_radians(a1)) * arrow_size
                            vx3 = vx1 + math.cos(angle - degrees_to_radians(a2)) * arrow_size
                            vy3 = vy1 + math.sin(angle - degrees_to_radians(a2)) * arrow_size
                            vx4 = ax + math.cos(angle) * radius
                            vy4 = ay + math.sin(angle) * radius
                            triangle = [
                                    vx4, vy4,
                                    vx2, vy2,
                                    vx3, vy3
                                ]
                            
                            self.canvas.create_polygon(
                                triangle,
                                tags = ("edgelines"),
                            )
                    
            #if len(cycles).split
            
    def render_brush(self, x, y, radius, r_mult, color, tag, fill):
        self.canvas.delete(tag)
        cx1 = x - radius * r_mult
        cy1 =  y - radius * r_mult
        cx2 = cx1 + radius * r_mult * 2
        cy2 = cy1 + radius * r_mult * 2
        
        self.canvas.create_oval(
                            cx1, cy1, 
                            cx2, cy2, 
                            outline=color,
                            tags=(tag),
                            fill=fill
                            )       

    def render_grid_lines(self, grid_lines: list[VTX3D], one_sign = 1):
        #Grid Lines
        #if self.grid_lines_boolvar.get():
        #print("yep")
        #self.canvas.delete("gridlines")
        #print(len(grid_lines))
        if grid_lines:
            if self.grid_vis_iv.get():
                start_point = None
                end_point = None
                for i in range(len(grid_lines)):
                    #print("ye")


                    if start_point != None and end_point == None:
                        #x y z
                        end_point = grid_lines[i]
                        
                    
                    if start_point == None:
                        #x y z
                        start_point = grid_lines[i]
                        
                    if start_point != None and end_point != None:
                        sx, sy, sz = start_point.get_X(), start_point.get_Y(), start_point.get_Z()
                        ex, ey, ez = end_point.get_X(), end_point.get_Y(), end_point.get_Z()

                        
                        #if sy < self.top and ey < self.top:
                        sx, sy = self.world_to_screen(start_point)
                        ex, ey = self.world_to_screen(end_point)

                        

                        self.canvas.create_line(
                                            sx, sy, ex, ey,
                                            tags=("gridlines"),
                                            width=3
                                            #tuple(dash_size - pixel_spacing)
                                            #dash=(dash_size, 1)
                        )

                        start_point = None
                        end_point = None
                
                
            else:
                self.canvas.delete("gridlines")

            if self.grid_xyz_iv.get():
                deci = 2
                color = "red"
                min_font_size = 8
                font_mult = 5
                #first four last four
                for i in [0, 1, 2, 3, -1, -2, -3, -4]:

                    vx, vy, vz = grid_lines[i].get_X(), grid_lines[i].get_Y(), grid_lines[i].get_Z()
                    _vx, _vy = self.world_to_screen(grid_lines[i])
                    self.canvas.create_text(
                                        _vx, 
                                        _vy,
                                        text="x:{}\ny:{}\nz:{}".format(round(vx, deci), round(vy, deci), round(vz, deci)),
                                        fill=color,
                                        font = ("Arial", round((1 - (vz - 1)/(self.far - self.near)) * font_mult) + min_font_size),
                                        tags=("gridlines"))
            
                
            else:
                if not self.grid_vis_iv.get():
                    self.canvas.delete("gridlines")
        
    def apply_grid_transformation(self, line_grid: list[VTX3D], translation_matrix, transform_matrix, matrix_translation):
        #if self.grid_lines_boolvar.get():
        #if self.grid_rotation_boolvar.get():
        for vtx in line_grid:   
            vtx.transform(translation_matrix, transform_matrix, matrix_translation)
        
    def update_viewport(self):
        
        #Grid Display
        #self.canvas.delete("gridlinelabels")
        self.canvas.delete("gridlines")
        #self.render_grid_lines(self.grid_lines_z)
        #self.render_grid_lines(self.grid_lines_x)
        self.render_grid_lines(self.grid_lines)

        #Vertex Display
        
        self.render_projected_vertices()
        self.render_edges()
        #self.draw_edge_lines()

    def reset_grid_states(self):
        #X AXIS SPANNING Z PLANE
        divides = 10
        mult = 1
        offset_x = -0.5
        offset_y = 0.0
        offset_z = 0.0
        #The total amount of space occupied by clip space on the x y and z plane 
        total_space = abs(self.far - self.near) * mult
        spacing = total_space/divides 
        #spacing multipliers
        sxm, szm, exm, ezm = 1, 1, 1, 1

        #self.grid_lines = []
        
        #ugliest list comprehension
        self.grid_lines = [
            
            
            [
                #z spanning, points are xyz pairs of lines 
                #world space
                #start x, y,z end x, y, z
                VTX3D(
                    offset_x + round(i * spacing, 2), 
                    offset_y, 
                    offset_z + self.near * mult
                    ),

                VTX3D(
                    offset_x + round(i * spacing, 2), 
                    offset_y, 
                    offset_z + self.far * mult
                    ),
                #x spanning, points are xyz pairs of lines 
                #world space
                #start x, y,z end x, y, z
                VTX3D(
                    offset_x + self.near * mult, 
                    0.0, 
                    offset_z + round(i * spacing, 2),
                    ),

                VTX3D(
                    offset_x + self.far * mult, 
                    0.0,  
                    offset_z + round(i * spacing, 2)
                    )
             
            ] for i in range(divides + 1)
        ]
        


        print("X Lines")
        print("| |".join([str(vtx) for pair in self.grid_lines for vtx in pair]))
        
        #flattening the 2d array
        self.grid_lines = [
            xyz for coord in self.grid_lines for xyz in coord
        ]
        print()
        print("| |".join([str(vtx) for vtx in self.grid_lines]))
        '''
        #X AXIS SPANNING Z PLANE
        divides = 10
        mult = 1
        #The total amount of space occupied by clip space on the x y and z plane 
        total_space = abs(self.far - self.near) * mult
        spacing = total_space/divides 
        #spacing multipliers
        sxm, szm, exm, ezm = 1, 1, 1, 1
        
        #ugliest list comprehension
        self.grid_lines_x = [
            #x spanning, points are xyz pairs of lines 
            #world space
            #start x, y,z end x, y, z
            [

                VTX3D(
                    round(x * spacing  * mult + -1, 2), 
                    0.0, 
                    self.near * mult
                    ),

                VTX3D(
                    round(x * spacing  * mult + -1, 2), 
                    0.0, 
                    self.far * mult
                    )

            ] for x in range(divides + 1)
        ]
        
        print("X Lines")
        print("| |".join([str(vtx) for pair in self.grid_lines_x for vtx in pair]))
        
        #flattening the 2d array
        self.grid_lines_x = [
            xyz for coord in self.grid_lines_x for xyz in coord
        ]
        print()
        print("| |".join([str(vtx) for vtx in self.grid_lines_x]))
        
        
        #Z AXIS SPANNING X PLANE
        sxm, szm, exm, ezm = 1, 1, 1, 1
        self.grid_lines_z = [
            #z spanning, points are xyz pairs of lines 
            #world space
            #start x, y,z end x, y, z
            [

            VTX3D(
                self.near * mult, 
                0.0, 
                round(z * spacing * mult + -1, 2),
                ),

            VTX3D(
                self.far * mult, 
                0.0, 
                round(z * spacing * mult + -1, 2)
                )

            ] for z in range(divides + 1)
        ]
        
        #print(self.grid_lines_z)
        print("Z Lines")
        print("| |".join([str(vtx) for pair in self.grid_lines_z for vtx in pair]))
        #flattening the 2d array
        self.grid_lines_z = [
            xyz for coord in self.grid_lines_z for xyz in coord
        ]

        print()
        print("| |".join([str(vtx) for vtx in self.grid_lines_z]))

        #self.grid_lines_x = []
        #self.grid_lines_z = []
        #print(self.grid_lines_z)
        #print()
        #print(self.canvas_height, self.canvas_width)
        
        #self.update_viewport()
        '''
    
    
    def has_arrows(self):
        #print(self.arrows_iv.get())
        #self.render_vertices()  
        #self.render_edges()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def has_indexes(self):
        #self.render_vertices()  
        #self.render_edges()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def has_angles(self):
        #self.render_vertices()  
        #self.render_edges()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def has_vertices(self):
        #self.render_vertices()  
        #self.render_edges()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def has_position(self):
        #self.render_vertices()  
        #self.render_edges()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def is_looping(self):
        for edge in self.edges:
            self.edges[edge].clear()
        self.update_viewport()
        self.highlight_vertex(self.selected_vtx)

    def export_data(self):
        filetypes = [
                    #("All files", "*.*"),
                    ("csv files", "*.csv"),
                    ]
        

        save_path = filedialog.asksaveasfilename(
                                    initialdir = self.current_directory, #os.getcwd(),
                                    defaultextension = ".csv",
                                    filetypes= filetypes                   
                                    ) 
        
        #https://stackoverflow.com/questions/60948028/python-pillow-transparent-gif-isnt-working
        if save_path:
            with open(save_path, mode='w') as csv_file:
                #https://realpython.com/python-csv/
                #https://dev.to/devasservice/guide-to-pythons-csv-module-32ie
                fieldnames = ["Edges, Vertices, Gridlines"] #list(map(str, self.edges.keys())) #['emp_name', 'dept', 'birth_month']
                #writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                #writer.writeheader()
                
                #writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
                #writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})

                # The number of keys in edges should be the same as the amount of V3D, or vertex objects, 

                fieldnames = ["Edges", "Vertices", "Gridlines"]
                row_max = max(len(self.grid_lines), len(self.vertices))  #max(map(len, self.edges.values()))
                col_max = len(fieldnames)

                ls_csv = [["NA" for col in range(col_max)] for row in range(row_max)]
                for row in ls_csv:
                    print(row)
                
                for col in range(col_max):
                    for row in range(row_max):
                        if row < 1:
                            ls_csv[row][col] = fieldnames[col]
                        
                        else:
                            if fieldnames[col] == fieldnames[0]:

                                if row <= len(self.edges):
                                    if self.edges[row - 1]:
                                        ls_csv[row][col] = " "
                                        for ele in self.edges[row - 1]:
                                            ls_csv[row][col] += str(ele) + " "
                                    else:
                                        ls_csv[row][col] = " "


                            elif fieldnames[col] == fieldnames[1]:
                                
                                if row <= len(self.vertices):
                                    ls_csv[row][col] = str(self.vertices[row - 1])

                            elif fieldnames[col] == fieldnames[2]:
                                
                                if row <= len(self.grid_lines):
                                    ls_csv[row][col] = str(self.grid_lines[row - 1])
                         
                        
                       
                for row in ls_csv:
                    print(row)
                
                writer = csv.writer(csv_file)#, delimiter="\t")

                # Write data to the file
                writer.writerows(ls_csv)
                
                '''
                for i in range(row_max):
                    row_dict = {}
                    for key, value in self.edges.items():
                        if i == len(value):
                            row_dict.update({str(key):"NA"})
                        else:
                            print(value, i)
                            if value:
                                row_dict.update({str(key):str(value[i])})
                            else:
                                row_dict.update({str(key):"NA"})
                    writer.writerow(row_dict)
                '''





    def import_data(self):
        filetypes = [

                        ("csv files", "*.csv"),
                        #("gif files", "*.gif"),
    
                    ]
        

        selected_file = filedialog.askopenfilename(
            title='Open files',
            initialdir=self.current_directory,
            filetypes=filetypes
            )
        
        if selected_file:
       

            with open(selected_file, mode='r') as csv_file:
                fieldnames = ["Edges", "Vertices", "Gridlines"]
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                #print(csv_reader)
                #for row in csv_reader:
                    #print(row)
                
                # print(list(map(int, csv_reader[0]["Edges"].split())))
                self.vertices.clear()
                self.grid_lines.clear()
                self.edges.clear()


                i = 0
                for row in csv_reader:
                    if row.get("Edges"):
                        
                        if row["Edges"][0] != "NA":
                            edge_array = row["Edges"].split(" ")
                            if len(edge_array) > 1:
                                # print([int(ele) for ele in row["Edges"].split(" ") if ele != "" and ele != "NA"])
                        
                                self.edges[i] = [int(ele) for ele in row["Edges"].split(" ") if ele != "" and ele != "NA"]
                            

                    if row.get("Vertices"):
                        if row["Vertices"][0] != "NA":
                            vertex_array = row["Vertices"].split(" ")
                            if len(vertex_array) > 1:
                                
                                vx = float(vertex_array[1])
                                vy = float(vertex_array[3])
                                vz = float(vertex_array[5])
                                self.vertices.append(VTX3D(vx, vy, vz))
                                #print(vertex_array)
                                #print(vx, vy, vz)
                    
                    if row.get("Gridlines"):
                        if row["Gridlines"][0] != "NA":
                            grid_array = row["Gridlines"].split(" ")
                            if len(grid_array) > 1:
                                
                                vx = float(grid_array[1])
                                vy = float(grid_array[3])
                                vz = float(grid_array[5])
                                self.grid_lines.append(VTX3D(vx, vy, vz))
                                #print(vertex_array)
                                #print(vx, vy, vz)
                    
                    i += 1
                
                self.selected_vtx = 0
                self.update_viewport()
                self.highlight_vertex(self.selected_vtx)
                '''
                self.edges.clear()
                i = 0
                for row in len(csv_reader):
                    if row.get("Edges"):
                        if row["Edges"]:

                            if self.edges.get(i):
                                self.edges[i].append()
                            else:
                                self.edges[i] = []
                    i += 1
                '''

                '''
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
                    line_count += 1
                print(f'Processed {line_count} lines.')
                '''


    #############################################

    def get_cycles(self, graph):
        #cycles = [[node]+path  for node in graph for path in dfs(graph, node, node)]
        #cycles = list({"-".join((str(ele) for ele in sorted([node]+path[:-1])))  for node in graph for path in self.dfs(graph, node, node) if len([node]+path) > 3})
        cycles = list(
                        {
                            "-".join( (str(ele) for ele in sorted([node]+path[:-1])))  for node in graph for path in self.dfs_cycle(graph, node, node) if len([node]+path) > 3
                        }
                    )

        #print(cycles, len(cycles))
        #print(graph)
        return cycles

    def highlight_vertex(self, ind):
        if self.vertices:
            self.canvas.delete("halo")
            ox, oy, oz = self.vertices[ind].get_X(), self.vertices[ind].get_Y(), self.vertices[ind].get_Z()
            
            oval_size = self.z_oval(oz)
            ox, oy, = self.world_to_screen(self.vertices[ind])
            self.render_brush(ox, oy, oval_size, 1.5, "cyan", "halo", "")



    def bfs(self, graph, node):
        visited = [node]
        queue = [node]
        while queue:
            #print(stack)
            item = queue.pop(0)
            if graph.get(item):
                for thing in graph[item]:
                    if thing not in visited:
                        queue.append(thing)
                        visited.append(thing)

        #print("Visited\n", visited)
        return visited[1:]

    def dfs_cycle(self, graph, start, end):
        fringe = [(start, [])]
        while fringe:
            state, path = fringe.pop()
            if path and state == end:
                yield path
                continue
            for next_state in graph[state]:
                if next_state in path:
                    continue
                fringe.append((next_state, path+[next_state]))

    def dfs(self, graph, node):
        visited = [node]
        stack = [node]
        while stack:
            #print(stack)
            item = stack.pop()
            if graph.get(item):
                for thing in graph[item]:
                    if thing not in visited:
                        stack.append(thing)
                        visited.append(thing)

        #print("Visited\n", visited)
        return visited
        
    

    def traverse(self):
            print("selected vertex\n", self.selected_vtx)
            print("visited dfs\n",self.dfs(self.edges, self.selected_vtx))
            print("visited bfs\n",self.bfs(self.edges, self.selected_vtx))

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
        
        IKs = Animator(self, 500, 500, 32, 32)
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
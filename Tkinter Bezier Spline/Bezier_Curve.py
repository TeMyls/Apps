import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
from numpy import array, uint8,  dot, float64, eye
from numpy import radians as to_radians
import math
from WidgetUtils import *
from Tool_tip import *
from Vertex2D import *
import time

def degrees_to_radians(deg):
    return to_radians(deg) #(deg * math.pi)/180

def angle_to( x1, y1, x2, y2):
        #in radians
        return math.atan2(y2 - y1, x2 - x1)


def distance_to(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    s = dx * dx + dy * dy
    return math.sqrt(s)

def clamp(x, a, b):
  return min(max(x, a), b)



def lerp(a, b, amount):
  return a + (b - a) * clamp(amount, 0, 1)

def bfs(graph, node):
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

def dfs(graph, node):
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

def dfs_path_between(graph, start, end):
    stack = [(start, [start])]
    visited = set()

    while stack:
        node, path = stack.pop()
        if node == end:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in reversed(graph.get(node, [])):  # reverse for consistent DFS order
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return []
    
def dfs_visited(graph, node, visited):
    #the purpose is to return the childern of the brnach of a tree
    stack = [node]
    visited_new = []
    while stack:
        #print(stack)
        item = stack.pop()
        if graph.get(item):
            for thing in graph[item]:
                if thing not in visited:
                    stack.append(thing)
                    visited_new.append(thing)

    #print("Visited\n", visited)
    return visited_new

def dfs_cycle(graph, start, end):
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
            
def get_cycles(graph):
    #cycles = [[node]+path  for node in graph for path in dfs(graph, node, node)]
    #cycles = list({"-".join((str(ele) for ele in sorted([node]+path[:-1])))  for node in graph for path in dfs(graph, node, node) if len([node]+path) > 3})
    cycles = list(
                    {
                        "-".join( (str(ele) for ele in sorted([node]+path[:-1])))  for node in graph for path in dfs_cycle(graph, node, node) if len([node]+path) > 3
                    }
                )

    #print(cycles, len(cycles))
    #print(graph)
    return cycles

def r_bez(point_ls: list[float], points: int, point: int) -> list[float]:
	# the way bezier curves work is by linear interpolating(lerp)
		# the value from one coordinate to another, getting a percentage between the two
		# these points are lerp-ed until the path of a single line is deduced
	# 4 X-Y coordinate pairs have 3 lines between them
	# when a value is connected inbetween these 3 lines sequentially you get 2 lines, then 1 line fron where each point on the found
	# this recurcise and iterative versions do exactly that, once the amount of points is reduced to 4 numbers, 2 X-Y pairs, a line
			# the curve's coordinate at that percentage is found
			
	ln = len(point_ls)
	#print(point_ls)
	if ln == 4:
		x1 = point_ls[0]
		y1 = point_ls[1]
		
		x2 = point_ls[2]
		y2 = point_ls[3]
	
		#print(x1, y1, x2, y2)
		
		x = lerp(x1, x2, point/points)
		y = lerp(y1, y2, point/points)
			
		return [x , y]
				
    
	if ln < 6:
		return []
    
   
	ls_point = []
	for i in range(3, ln, 2):
		
		x1 = point_ls[i - 3]
		y1 = point_ls[i - 2]
		
		x2 = point_ls[i - 1]
		y2 = point_ls[i]
	
		#print(x1, y1, x2, y2)
		ls_point.append(
			lerp(x1, x2, point/points)
			)
		ls_point.append(
			lerp(y1, y2, point/points)
			)

	return r_bez(ls_point, points, point)
	
def i_bez(point_ls: list[float], points: int, point: int) -> list[float]:
	
	ln = len(point_ls)
	
	if ln < 6:
		return []
	
	ls_point = [coord for coord in point_ls]
	while len(ls_point) != 4:
		ln = len(ls_point)
		i = 3 
		while i < ln:
		#for i in range(3, ln, 2):
		
			x1 = ls_point[i - 3]
			y1 = ls_point[i - 2]
			
			x2 = ls_point[i - 1]
			y2 = ls_point[i]
		
			#print(x1, y1, x2, y2)
			ls_point.append(
				lerp(x1, x2, point/points)
				)
			ls_point.append(
				lerp(y1, y2, point/points)
				)
			i += 2
			
		ls_point = ls_point[ln:ln + i]
		#print(len(ls_point))
		#if len(ls_point) == 4:
			#return ls_point
	x1 = ls_point[0]
	y1 = ls_point[1]
	
	x2 = ls_point[2]
	y2 = ls_point[3]

	#print(x1, y1, x2, y2)
	
	x = lerp(x1, x2, point/points)
	y = lerp(y1, y2, point/points)
	return [x , y]

class Joint():
    def __init__(self, x , y, name):
        self.vtx = VTX2D(x, y)
        self.angle = 180
        self.name = name

    def __str__(self):
        return f"Joint: {self.name} " + str(self.vtx) + f" Angle:{self.angle}"
    
    def get_coords(self):
        return self.vtx.get_X(), self.vtx.get_Y()
    
    def set_coords(self, x, y):
        self.vtx.set_coords(x, y)

    def transform(self, translation_matrix, transform_matrix, matrix_translation):
        self.vtx.transform(translation_matrix, transform_matrix, matrix_translation)
    


class Kinematics(ttk.Frame):
    def __init__(self, parent, c_width, c_height):
        super().__init__(parent)
        #A List of vertices
        #Example
        #a container for the joint class etc 
        self.vertices = []
        
        #An Dictionary/Adjacency List of edges
        #The keys are the x indexes of vertices 
        #The values are a list of vertex connections
        #Edges is a directed graph
        #Example
        """
        Parent: 0 Childern: [3, 1, 2]
        Parent: 1 Childern: [4]
        Parent: 2 Childern: [5]
        Parent: 3 Childern: [7]
        Parent: 4 Childern: []
        Parent: 5 Childern: [6]
        Parent: 6 Childern: []
        Parent: 7 Childern: []
        """
        #if it were an undirected graph
        """
        Parent: 0 Childern: [3, 1, 2]
        Parent: 1 Childern: [4, 0]
        Parent: 2 Childern: [5, 0]
        Parent: 3 Childern: [7, 0]
        Parent: 4 Childern: [1]
        Parent: 5 Childern: [6, 2]
        Parent: 6 Childern: [5]
        Parent: 7 Childern: [3]
        """
        self.edges = {}
        self.distances = {}
        #self.line = []

        #------------------------------------------------------------------------------------------------
        self.root_vtx = 0

        self.radius = 5
        self.selected_idx = 0
        self.target = VTX2D(-1, -1)
        self.target_idx = -1
        self.anchored_vtx = 0
        self.last_pixel = []
        #------------------------------------------------------------------------------------------------


        
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        self.canvas_width = c_width #self.canvas.winfo_width()
        self.canvas_height = c_height #self.canvas.winfo_height()
        #self.canvas.grid(row = 0, column = 0, sticky = "N")
        #------------------------------------------------------------------------------------------------
        self.bottom_frame = ttk.Frame(self)
        self.line_lbl =  ttk.Label(self.bottom_frame, text = "Line Divisions", anchor="center")
        self.line_iv = tk.IntVar(value=3)
        self.line_scl = ttk.Scale(
            self.bottom_frame,
            variable = self.line_iv,
            from_= 1,
            to = 30,
            orient = "horizontal",
            length=c_width,
            command = self.line_resolution
        )


       
        self.line_lbl.pack(side="bottom", anchor="center", expand=True)
        self.line_scl.pack(side="bottom", anchor="center", expand=True)
        self.line_lbl.config(text=f"Line Divisions: {self.line_iv.get()}")
        '''
        btn_arrangement = [

            [self.line_scl],
            [self.line_lbl]
            
        ]
        arrange_widgets(btn_arrangement, "NEWS")
        '''
        #------------------------------------------------------------------------------------------------
        self.data_frame = ttk.Frame(self)

        self.data_btn = tk.Button(self.data_frame, 
                                  text="Data",
                                  command=self.display_data)
        


        
        self.idx_iv = tk.BooleanVar(value=True)
        self.idx_cb = tk.Checkbutton(self.data_frame, 
                                 text="Indexes", 
                                 variable=self.idx_iv,
                                 command=self.update_canvas
                                 ) 
        
        self.vtx_iv = tk.BooleanVar(value=True)
        self.vtx_cb = tk.Checkbutton(self.data_frame, 
                                 text="Vertices", 
                                 variable=self.vtx_iv,
                                 command=self.update_canvas
                                 ) 

        self.bezier_iv = tk.BooleanVar(value=True)
        self.bezier_cb = tk.Checkbutton(self.data_frame, 
                                 text="Bezier", 
                                 variable=self.bezier_iv,
                                 command=self.update_canvas,
                                 onvalue=True,
                                 offvalue=False
                                 ) 
        
        self.spline_cb = tk.Checkbutton(self.data_frame, 
                                 text="Spline", 
                                 variable=self.bezier_iv,
                                 command=self.update_canvas,
                                 onvalue=False,
                                 offvalue=False
                                 ) 
        
        '''
        btn_arrangement = [

            [self.arrows_cb],
            [self.idx_cb],
            [self.vtx_cb],
            [self.data_btn],
            [self.exp_btn],
            


        ]

        arrange_widgets(btn_arrangement, "N")
        '''
        #self.arrows_cb.pack(side="top", fill="x", expand=True, anchor="center")
        self.idx_cb.pack(side="top", fill="x", expand=True, anchor="center")
        self.vtx_cb.pack(side="top", fill="x", expand=True, anchor="center")
        self.bezier_cb.pack(side="top", fill="x", expand=True, anchor="center")
        self.spline_cb.pack(side="top", fill="x", expand=True, anchor="center")
        self.data_btn.pack(side="top", fill="x", expand=True, anchor="center")




        #------------------------------------------------------------------------------------------------
        self.btn_frame = ttk.Frame(self)

        


        #Button Type

        
        self.place_img = tk.PhotoImage(file="icons\\add_circle_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.place_btn = tk.Button(self.btn_frame, 
                                 text="Draw", 
                                 image=self.place_img,
                                 ) 
        CreateToolTip(self.place_btn, "Place Vertex")

        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_btn = tk.Button(self.btn_frame, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_btn, "Eraser Vertex")







        self.replace_img = tk.PhotoImage(file="icons\\touch_double_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.replace_btn = tk.Button(self.btn_frame, 
                                 text="Move", 
                                 image=self.replace_img
                                 ) 
        CreateToolTip(self.replace_btn, "Move Vertex")

        self.shift_img = tk.PhotoImage(file="icons\\drag_pan_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.shift_btn = tk.Button(self.btn_frame, 
                                 text="Shift", 
                                 image=self.shift_img
                                 ) 
        CreateToolTip(self.shift_btn, "Shift Vertices")


        self.drawing_widgets = [
            self.place_btn, self.erase_btn,
            self.replace_btn, self.shift_btn
            
        ]

        self.mode ="Draw"

        self.place_btn.config(command=lambda:self.select_mode(self.place_btn))
        self.erase_btn.config(command=lambda:self.select_mode(self.erase_btn))
        self.replace_btn.config(command=lambda:self.select_mode(self.replace_btn))
        self.shift_btn.config(command=lambda:self.select_mode(self.shift_btn))
        
        btn_arrangement = [

            [self.place_btn, self.replace_btn],
            [self.shift_btn, self.erase_btn  ]
 
        ]

        arrange_widgets(btn_arrangement, "N")

        #------------------------------------------------------------------------------------------------

        '''
        arrangement = [
            [None           , None                   , None                 , None            ],
            [self.btn_frame ,self.canvas             , self.data_frame      , None            ],
            [None           ,self.line_scl       , None                 , None            ],
            [None           ,self.line_lbl       , None                 , None            ],
            [None           , None                   , None                 , None            ]

        ]



        arrange_widgets(arrangement)
        '''
        self.bottom_frame.pack(side="bottom", fill="x", anchor="center")
        self.btn_frame.pack(side="left", anchor="ne")
        self.canvas.pack(side="left", fill="both", expand=True, anchor="center")
        self.data_frame.pack(side="left", anchor="nw")

        
        

        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_lmb_release)
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_lmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        # treeview
        # self.vertex_tv.tag_bind('tree_print', "<ButtonPress-1>", self.treeview_click_bind)
        # self.vertex_tv.tag_bind('tree_print', "<<TreeviewSelect>>", self.treeview_click_bind)
        # self.vertex_tv.tag_bind('tree_print', "<<TreeviewOpen>>", self.treeview_click_bind)
        # self.vertex_tv.tag_bind('tree_print', "<<TreeClose>>", self.treeview_click_bind)
        
        self.select_mode(self.place_btn)

    def on_canvas_resize(self, event):
   
        # Updates every canvas resize due to the window dimensions changing
        # Update canvas dimensions or redraw elements based on event.width and event.height

        #print(f"Canvas resized to: {event.width}x{event.height}")
        self.canvas_height = event.height
        self.canvas_width = event.width
        self.line_scl.config(length=self.canvas_width + 128)
       
    def traverse(self):
        print("selected vertex\n", self.selected_idx)
        print("visited dfs\n",dfs(self.edges, self.selected_idx))
        print("visited bfs\n",bfs(self.edges, self.selected_idx))
        
    

    def on_canvas_lmb_click(self, event):
        if self.mode == "Draw":
            self.place_vertex(event)
        elif self.mode == "Erase":
            self.remove_vertex(event)

        elif self.mode == "Shift":
            self.shift_vertices(event)
        elif self.mode == "Move":
            self.move_vertex(event)
   
        if self.vertices:
            self.highlight_vertex(self.selected_idx)

    def on_canvas_lmb_press(self, event):
        if self.mode == "Draw":
            pass
            #self.place_vertex(event)
        elif self.mode == "Erase":
            self.remove_vertex(event)
   
        elif self.mode == "Shift":
            self.shift_vertices(event)
        elif self.mode == "Move":
            self.move_vertex(event)
        
           

        if self.vertices:
            self.highlight_vertex(self.selected_idx)
            #self.update_treeview(self.edges, self.selected_idx)
        
    def on_canvas_lmb_release(self, event):
        if self.mode == "Shift" or self.mode == "Move":
            self.last_pixel.clear()
            

    def on_canvas_rmb_click(self, event):
        pass

    def on_canvas_rmb_press(self, event):
        pass

    def on_canvas_rmb_release(self, event):
        pass

    def select_mode(self, clicked_widget):
        
        for widget in self.drawing_widgets:
            if widget != clicked_widget:
                widget.config(bg="SystemButtonFace")
            else:
                widget.config(bg="yellow")
                self.mode = widget.cget("text")
    
    #Button Start---------------------------------------------------------------------------------------------------

    def display_data(self):
        print("Vertices")
        for vertex in self.vertices:
            print(f"Vertex: {vertex}")
    
    def place_vertex(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        v = Joint(x, y, str(len(self.vertices)))
        self.vertices.append(v)
        #self.edges[len(self.vertices) - 1] = []

        self.render_vertices()
        self.render_curve()
        #self.render_edges()
        #self.distances = self.edge_distance()
        #self.update_edge_checkbuttons()

    def remove_vertex(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)


        

        if len(self.vertices) > 0:
            idx = self.is_vertex_colliding(x, y, self.radius, 1, 1)
            
            if idx > -1:
                #print(idx)
                self.vertices.pop(idx)

                if self.selected_idx >= idx:
                    if idx != 0:
                        self.selected_idx = idx - 1
                    else:
                        self.selected_idx = 0

                if len(self.vertices) < 1:
                    self.target_idx = -1


                self.render_vertices()
                self.render_curve()
                #self.render_edges()
                #self.distances = self.edge_distance()
                
                #self.canvas.delete(str(idx))
                

                
                #self.update_edge_checkbuttons()

        self.render_brush(x, y, 1, "red", "erasing")
    
    def move_vertex(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.vertices and self.last_pixel:
            if self.last_pixel != [x, y]:
                dx, dy = x - self.last_pixel[0], y - self.last_pixel[1] 
                #vx, vy = self.vertices[self.selected_idx].get_coords()
                idx = self.is_vertex_colliding(x, y, self.radius, 2, 1)
                if idx != -1: 
                    vx, vy = self.vertices[idx].get_coords()
                    self.vertices[idx].set_coords(
                        vx + dx,
                        vy + dy
                    )
                self.render_vertices() 
                self.render_curve() 
                #self.render_edges()
                self.render_brush(x, y, 2, "purple", "connected")

        self.last_pixel.clear()
        if len(self.last_pixel) == 0:
            self.last_pixel = [x, y]

    def shift_vertices(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.vertices and self.last_pixel:
            if self.last_pixel != [x, y]:
                for vertex in self.vertices:
                    
                    dx, dy = x - self.last_pixel[0], y - self.last_pixel[1] 
                    vx, vy = vertex.get_coords()
                    vertex.set_coords(
                        vx + dx,
                        vy + dy
                    )
                self.render_vertices()  
                self.render_curve()
                #self.render_edges()
                #self.render_brush(x, y, 1, "cyan", "connected")

        self.last_pixel.clear()
        if len(self.last_pixel) == 0:
            self.last_pixel = [x, y]

    def highlight_vertex(self, ind):
        ox, oy = self.vertices[ind].get_coords()
        self.render_brush(ox, oy, 1.5, "cyan", "halo")
        
    def render_brush(self, x, y, r_mult, color, tag):
        self.canvas.delete(tag)
        cx1 = x - self.radius * r_mult
        cy1 =  y - self.radius * r_mult
        cx2 = cx1 + self.radius * r_mult * 2
        cy2 = cy1 + self.radius * r_mult * 2
        
        self.canvas.create_oval(
                            cx1, cy1, 
                            cx2, cy2, 
                            outline=color,
                            tags=(tag)
                            )
    
    def is_vertex_colliding(self, x, y, radius, m1 = 1, m2 = 1) -> int:
        idx = -1
        for i in range(len(self.vertices)):
            #if i != self.selected_idx:
            vx, vy = self.vertices[i].get_coords()
            if circle_circle(x, y, radius * m1, vx, vy, radius * m2):
                idx = i
                return idx
        return idx

    #Render Canvas---------------------------------------------------------------------------------------------------
    
    def render_curve(self):
        # Bezier curves have to be more than two vertices/X-Y coordinate points
        if len(self.vertices) > 2:

            control_points = []
            curve_coords = []
            points = self.line_iv.get()
            for i in range(len(self.vertices)):
                vtx = self.vertices[i]
                vx, vy  = vtx.get_coords()
                control_points.append(vx)
                control_points.append(vy)

            if self.bezier_iv.get():
                # Bezier Curve 
                # Every point has influence on the entire line
                # the x_bez function 
                for i in range(points + 1):
                    curve_xy = i_bez(control_points, points, i)

                    curve_coords.append(curve_xy[0])
                    curve_coords.append(curve_xy[1])

                self.canvas.create_line(curve_coords)
        
            else:
                # Spline
                # Splitting the points into smaller quadratic Bezier curves, each which only have 8 X-Y, or 4 control points
                    # Every other point is on the line itself and the curve is controlled by the two points preceding it
                    # control is more localized 
                #print(points)
                control_matrix = []
                
                if len(control_points) > 7:

                    #print(control_points)
                    #print(control_matrix)
                    # 8 points is 4 X-Y points
                    inc = 8
                    dec = 0
                    for i in range(0, len(control_points) + 1, inc):
                        if i + inc - dec < len(control_points):
                            start = i - dec
                            stop = i + inc - dec
                            ele = control_points[ start:stop ]
                            dec += 2
                            control_matrix.append(ele)
                            #print(ele, start, stop, "yep")

                        

                            #curve_coords.clear()
                            for j in range(points + 1):
                                curve_xy = i_bez(ele, points, j)
                            
                                curve_coords.append(curve_xy[0])
                                curve_coords.append(curve_xy[1])
                    self.canvas.create_line(curve_coords)

                   
                        
                    
                
            
            
   

    def render_vertices(self):
        self.canvas.delete("all")
        for i in range(len(self.vertices)):
            vtx = self.vertices[i]
            vx, vy  = vtx.get_coords()
            cx1 = vx - self.radius
            cy1 =  vy - self.radius
            cx2 = cx1 + self.radius * 2
            cy2 = cy1 + self.radius * 2
            vtx.name = str(i)
            if self.vtx_iv.get():
                self.canvas.create_oval(cx1, cy1, 
                                        cx2, cy2,
                                        tags=vtx.name)
            if self.idx_iv.get():
                if self.bezier_iv.get():
                    self.canvas.create_text(cx1 - self.radius, cy1 + self.radius,
                                    text=vtx.name)
                else:
                    if i % 3 == 0:
                        self.canvas.create_text(cx1 - self.radius, cy1 + self.radius,
                                        text=str(i//3))
                    else:
                        self.canvas.create_text(cx1 - self.radius, cy1 - self.radius,
                                        text=f"|{str(i//3)}|{str(i%3)}|")


    def line_resolution(self, *args):
        if self.vertices:

            self.line_lbl.config(text=f"Line Divisions: {self.line_iv.get()}")
            self.render_vertices()  
            self.render_curve()
            #self.render_edges()
            self.highlight_vertex(self.selected_idx)

            #self.update_treeview(self.edges, self.selected_idx)
        #self.apply_stack_transformations(transform_matrix, False, True, False, False, False)

    def update_canvas(self):
        self.render_vertices()  
        self.render_curve()
        #self.render_edges()
        self.highlight_vertex(self.selected_idx)

 

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        IKs = Kinematics(self, 500, 500)
        IKs.pack(fill="both", expand=True, anchor="center")

    


if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    app.title("Bezier Curve")
    #app.resizable()
    app.mainloop()
        
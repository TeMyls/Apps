import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
from numpy import array, uint8,  dot, float64, eye
from numpy import radians as to_radians
import math

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

def disable_widget(widget):
    widget.config(state="disabled")

def enable_widget(widget):
    widget.config(state="normal")

def delete_widget(widget):
    widget.destroy()

def arrange_widgets(arrangement):
    for ind_y in range(len(arrangement)):
        for ind_x in range(len(arrangement[ind_y])):

            if arrangement[ind_y][ind_x] == None:
                pass
            else:
                arrangement[ind_y][ind_x].grid(row = ind_y, column = ind_x, sticky = "NEWS")
#https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip():

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class Vertex():
    def __init__(self, x , y):
        self.v = array(
            set_matrix2D(x, y),  dtype=float64
        )


    def get_X(self):
        return self.v[0, 0]

    def get_Y(self):
        return self.v[1, 0]

    def __str__(self):
        return "X {} Y {}".format(self.get_X(), self.get_Y())
    
    def set_coords(self, x, y):
        self.v[0, 0] = x
        self.v[1, 0] = y
        self.v[2, 0] = 1

    def transform(self, translation_matrix, transform_matrix, matrix_translation):
        
        '''
        XnY = np.linalg.multi_dot(
                            [
                            self.v,
                            translation_matrix, #moves to origin
                            transform_matrix, #applies transform
                            matrix_translation, #moves back to original position
                            
                            ] 
        )
        
        '''
        '''
        XnY = translation_matrix @ self.v #moves to origin
        #print(XnY, '\n')
        XnY = transform_matrix @ XnY #applies transform
        #print(XnY, '\n')
        XnY = matrix_translation @ XnY #moves back to original position
        '''
        '''
        XnY = dot(translation_matrix, self.v) #moves to origin
        #print(XnY, '\n')
        XnY = dot(transform_matrix, XnY) #applies transform
        #print(XnY, '\n')
        XnY = dot(matrix_translation, XnY) #moves back to original position
        '''
        XnY = dot(matrix_translation, dot(transform_matrix, dot(translation_matrix, self.v)))
        #print('nump')
        #print(XnY)
        self.set_coords(XnY[0 ,0], XnY[1, 0])

class Joint():
    def __init__(self, x , y, name):
        self.vtx = Vertex(x, y)
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
        

        #------------------------------------------------------------------------------------------------
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        self.canvas_width = c_width #self.canvas.winfo_width()
        self.canvas_height = c_height #self.canvas.winfo_height()
        self.canvas.grid(row = 0, column = 0, sticky = "N")



        self.root_vtx = 0

        self.radius = 5
        self.selected_vtx = 0
        self.target = Vertex(-1, -1)
        self.target_vtx = -1
        self.anchored_vtx = 0


        '''
        self.vtx_lbl = ttk.Label(self, text="Vertices", anchor="center")
        self.vtx_sb_y = ttk.Scrollbar(self, orient='vertical')
        self.vtx_sb_x = ttk.Scrollbar(self, orient='horizontal')
        self.vtx_lb = tk.Listbox(self, 
                                        yscrollcommand = self.vtx_sb_y.set,
                                        xscrollcommand = self.vtx_sb_x.set,
                                        selectmode="single", 
                                        exportselection=False,
                                        width=40
                                        )
        

        
        self.vtx_sb_y.config(command=self.vtx_lb.yview)
        self.vtx_sb_x.config(command=self.vtx_lb.xview)

        self.vtx_tv = ttk.Treeview(self)

        '''

        self.rotation_lbl =  ttk.Label(self, text = "Rotation", anchor="center")
        self.rotation_iv = tk.IntVar(value=180)
        self.rotation_scl = ttk.Scale(
            self,
            variable = self.rotation_iv,
            from_= 0,
            to = 360,
            orient = "horizontal",
            length=c_width,
            command = self.rotate_relative
        )

        self.data_frame = ttk.Frame(self)

        self.data_btn = tk.Button(self.data_frame, 
                                  text="Data",
                                  command=self.display_data)
        
        self.exp_btn = tk.Button(self.data_frame, 
                                  text="DFS",
                                  command=self.traverse)
        
        self.arrows_iv = tk.BooleanVar(value=True)
        self.arrows_cb = tk.Checkbutton(self.data_frame, 
                                 text="Arrows", 
                                 variable=self.arrows_iv,
                                 command=self.has_arrows
                                 ) 
        
        self.idx_iv = tk.BooleanVar(value=True)
        self.idx_cb = tk.Checkbutton(self.data_frame, 
                                 text="Indexes", 
                                 variable=self.idx_iv,
                                 command=self.has_indexes
                                 ) 
        
        self.vtx_iv = tk.BooleanVar(value=True)
        self.vtx_cb = tk.Checkbutton(self.data_frame, 
                                 text="Vertices", 
                                 variable=self.vtx_iv,
                                 command=self.has_vertices
                                 ) 

        self.btn_frame = ttk.Frame(self)

        btn_arrangement = [

            [self.arrows_cb],
            [self.idx_cb],
            [self.vtx_cb],
            [self.data_btn],
            [self.exp_btn]


        ]

        arrange_widgets(btn_arrangement)

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
        
        self.drawing_widgets = [
            self.place_btn, self.erase_btn,
            self.select_btn, self.connect_btn,
            self.break_btn, self.target_btn
            
        ]

        self.mode ="Draw"

        self.place_btn.config(command=lambda:self.select_mode(self.place_btn))
        self.erase_btn.config(command=lambda:self.select_mode(self.erase_btn))
        self.select_btn.config(command=lambda:self.select_mode(self.select_btn))
        self.connect_btn.config(command=lambda:self.select_mode(self.connect_btn))
        self.break_btn.config(command=lambda:self.select_mode(self.break_btn))
        self.target_btn.config(command=lambda:self.select_mode(self.target_btn))
        
        btn_arrangement = [

            [self.place_btn, self.erase_btn],
            [self.select_btn, self.connect_btn],
            [self.break_btn, self.target_btn ],
 
        ]

        arrange_widgets(btn_arrangement)

        

        arrangement = [
            [None           , None                   , None                 , None            ],
            [self.btn_frame ,self.canvas             , self.data_frame      , None            ],
            [None           ,self.rotation_scl       , None                 , None            ],
            [None           ,self.rotation_lbl       , None                 , None            ],
            [None           , None                   , None                 , None            ]

        ]



        arrange_widgets(arrangement)


        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<ButtonRelease-1>", None)
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_lmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        
        
        self.select_mode(self.place_btn)
    
    def traverse(self):
        print("selected vertex\n", self.selected_vtx)
        print("visited dfs\n",self.dfs(self.edges, self.selected_vtx))
        print("visited bfs\n",self.bfs(self.edges, self.selected_vtx))
        
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
    
    def dfs_path_between(self, graph, start, end):
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
        
    def dfs_visited(self, graph, node, visited):
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

    def on_canvas_lmb_click(self, event):
        if self.mode == "Draw":
            self.place_vertex(event)
        elif self.mode == "Erase":
            self.remove_vertex(event)
        elif self.mode == "Connect":
            self.connect_vertex(event)
            
        elif self.mode == "Select":
            self.select_vertex(event)

        elif self.mode == "Break":
            self.break_vertex(event)
        elif self.mode == "Target":
            self.target_vertex(event)
            self.FABRIK()

        if self.vertices:
            self.highlight_vertex(self.selected_vtx)

    def on_canvas_lmb_press(self, event):
        if self.mode == "Draw":
            pass
            #self.place_vertex(event)
        elif self.mode == "Erase":
            self.remove_vertex(event)

        elif self.mode == "Connect":
            self.connect_vertex(event)
            
        elif self.mode == "Select":
            self.select_vertex(event)
        elif self.mode == "Break":
            self.break_vertex(event)
        elif self.mode == "Break":
            self.break_vertex(event)
        elif self.mode == "Target":
            self.target_vertex(event)
            self.FABRIK()
           

        if self.vertices:
            self.highlight_vertex(self.selected_vtx)
        



    def on_canvas_rmb_click(self, event):
        pass

    def on_canvas_rmb_press(self, event):
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
        print("Edges")
        for key in self.edges:
            # Parent Type:{type(key)}
            print(f"Parent: {key} Childern: {self.edges[key]}")
        print(f"Selected: {self.selected_vtx}")
        print(f"Target: {self.target_vtx}")
        '''
        
        print("Vertices\n", self.vertices)
        print("Edges\n", self.edges)
        print("Edge Options\n", self.edge_options)
        print("Edge Checks\n", self.edge_checklist)
        '''
    



    def place_vertex(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        v = Joint(x, y, str(len(self.vertices)))
        self.vertices.append(v)
        self.edges[len(self.vertices) - 1] = []

        self.render_vertices()
        self.render_edges()
        self.distances = self.edge_distance()
        #self.update_edge_checkbuttons()



    def remove_vertex(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)


        

        if len(self.vertices) > 0:
            idx = -1
            

            for i in range(len(self.vertices)):
                #if point_circle(x, y, self.vertices[i].get_X(), self.vertices[i].get_Y(), self.radius * 2):
                vx, vy = self.vertices[i].get_coords()
                if circle_circle(x, y, self.radius, vx, vy, self.radius):
                    idx = i
                    break
            
            if idx > -1:
                #print(idx)
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


                self.render_vertices()
                self.render_edges()
                self.distances = self.edge_distance()
                
                #self.canvas.delete(str(idx))
                

                
                #self.update_edge_checkbuttons()

        self.render_brush(x, y, 1, "red", "erasing")

        

    def select_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)



        #self.canvas.delete("selected")
        #self.canvas.delete("erasing")
        
        


        if len(self.vertices) > 0:
            idx = -1
            for i in range(len(self.vertices)):
                
                ox, oy = self.vertices[i].get_coords()
                if circle_circle(x, y, self.radius * 1.5, ox, oy, self.radius):
                    idx = i
                  
                    break


            if idx != -1:
                self.selected_vtx = idx

                #self.highlight_vertex(idx)
                #print(f"selected: {self.selected_vtx}")

        self.render_brush(x, y, 1.5, "gold", "selected")

        if self.vertices:
            self.rotation_iv.set(self.vertices[self.selected_vtx].angle)
            
    def connect_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        
        
        if len(self.vertices) > 1:
           
            idx = -1
            for i in range(len(self.vertices)):
                if i != self.selected_vtx:
                    ox, oy = self.vertices[i].get_coords()
                    if circle_circle(x, y, self.radius * 0.7, ox, oy, self.radius):
                        idx = i
                        
                        break

            #print(f"selected: {self.selected_vtx} Parent Type:{type(list(self.edges.keys())[0])} idx: {idx}")
            
                #self.selected_vtx = idx
            
      
            if idx > -1 and self.selected_vtx > -1:

                if idx != self.selected_vtx:
                    #print("HEARS")
                    if idx not in self.edges[self.selected_vtx]:
                        self.edges[self.selected_vtx].append(idx)
                        #self.edges[idx].append(self.selected_vtx)
                        cycle_count = len(self.get_cycles(self.edges))
                        #print(cycle_count)
                        if cycle_count > 0:
                            #print("cycle prevented")
                            self.edges[self.selected_vtx].remove(idx)
                            #self.edges[idx].remove(self.selected_vtx)
                self.selected_vtx = idx       
                  

                        
        self.render_vertices()  
        self.render_edges()
        self.render_brush(x, y, 0.7, "green", "connected")



    def break_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        
        
        
        if len(self.vertices) > 1:
            #print('yep')
            idxs = {}
            for key_1 in self.edges:
                for key_2 in self.edges[key_1]:
                    
                    
                    x1, y1 = self.vertices[key_1].get_coords()
                    x2, y2 = self.vertices[key_2].get_coords()
                    if line_circle(x1, y1, x2, y2, x, y, self.radius * 1.5):
                    
                        if idxs.get(key_1):
                            idxs[key_1].append(key_2)
                        else:
                            idxs[key_1] = [key_2]
                               
            #print(idxs)                 
            for key_1 in idxs:
                for key_2 in idxs[key_1]:
                    self.edges[key_1].remove(key_2)

                        

                        
        self.render_vertices()  
        self.render_edges()
        self.render_brush(x, y, 1.5, "red", "breaking")

    def target_vertex(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.target.set_coords(x, y)
        self.render_brush(x, y, 0.5, "gray", "target")

        if len(self.vertices) > 1:
            idx = -1
            for i in range(len(self.vertices)):
                
                ox, oy = self.vertices[i].get_coords()
                if circle_circle(x, y, self.radius, ox, oy, self.radius):
                    #if the index in self.vertices has no childern as represented by []
                    if not self.edges[i] and self.selected_vtx != idx:
                        idx = i
                  
                        break


            if idx != -1:
                self.target_vtx = idx

                #self.highlight_vertex(idx)
                #print(f"selected: {self.selected_vtx}")
                ox, oy = self.vertices[i].get_coords()
                self.render_brush(ox, oy, 1.5, "gray", "target_sel")


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
    

    #Render Canvas---------------------------------------------------------------------------------------------------
    
    def render_edges(self):

        for key in self.edges:
            for value in self.edges[key]:
                ax, ay = self.vertices[key].get_coords()
                bx, by = self.vertices[value].get_coords()
                
                self.canvas.create_line(
                        ax, ay,
                        bx, by

                    )
                
                if ax != bx and ax != by and self.arrows_iv.get():
                    angle = self.angle_to(ax, ay, bx, by)
                    arrow_size = 10
                    a1 = 150
                    a2 = a1 + 60

                    vx1 = bx + math.cos(angle) * -self.radius
                    vy1 = by + math.sin(angle) * -self.radius
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
                    )
                    
            #if len(cycles).split
            
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
                self.canvas.create_text(cx1 - self.radius, cy1 + self.radius,
                                    text=vtx.name)

    def rotate_relative(self, *args):
        if self.vertices:

            prev_angle = self.vertices[self.selected_vtx].angle
            self.vertices[self.selected_vtx].angle = self.rotation_scl.get()
            angle_change = degrees_to_radians(prev_angle - self.vertices[self.selected_vtx].angle)


            vx,vy = self.vertices[self.selected_vtx].get_coords()
            transform_matrix = array(rotation_matrix2D(angle_change))
            
            anchor_matrix = array(translation_matrix2D(-vx, -vy))
            matrix_anchor = array(translation_matrix2D(vx, vy))
            childern = self.dfs(self.edges, self.selected_vtx)[1:]
            for vtx in childern:
                self.vertices[vtx].transform(anchor_matrix, transform_matrix, matrix_anchor)
            
            self.render_vertices()  
            self.render_edges()
            self.highlight_vertex(self.selected_vtx)
        #self.apply_stack_transformations(transform_matrix, False, True, False, False, False)

    def has_arrows(self):
        #print(self.arrows_iv.get())
        self.render_vertices()  
        self.render_edges()
        self.highlight_vertex(self.selected_vtx)

    def has_indexes(self):
        self.render_vertices()  
        self.render_edges()
        self.highlight_vertex(self.selected_vtx)

    def has_vertices(self):
        self.render_vertices()  
        self.render_edges()
        self.highlight_vertex(self.selected_vtx)


    def edge_distance(self):
        distances = {}
        for key1 in self.edges:
            distances[key1] = [-1] * len(self.edges)
            for key2 in self.edges:
                
                if key1 != key2:
                    vx1, vy1 = self.vertices[key1].get_coords()
                    vx2, vy2 = self.vertices[key2].get_coords()
                    distances[key1][key2] = self.distance_to(vx1, vy1, vx2, vy2)

        return distances

    def vertex_distance(self, vertex_ls):
        distances = []
        for i in range(len(vertex_ls) - 1):
            vx1, vy1 = self.vertices[vertex_ls[i]].get_coords()
            vx2, vy2 = self.vertices[vertex_ls[i + 1]].get_coords()
            distances.append(self.distance_to(vx1, vy1, vx2, vy2))

        #print("Visited\n", visited)
        return distances

    def vertex_positions(self, vertex_ls):
        positions = {}
        for i in range(len(vertex_ls)):
            vx, vy = self.vertices[vertex_ls[i]].get_coords()
            positions.update({vertex_ls[i]:[vx, vy]})
        return positions




    
            
    def reaching(self, v_chain, target_x, target_y, og_positions):
        #getting all the distances in the chain to keep it constant
        

        for i in range(0, len(v_chain) - 1):
         
            vx1, vy1 = self.vertices[v_chain[i]].get_coords()
            vx2, vy2 = self.vertices[v_chain[i + 1]].get_coords()

            dist = self.distances[v_chain[i]][v_chain[i + 1]]
            #moving the end effector towards the target
            if i == 0:
                self.vertices[v_chain[i]].set_coords(target_x, target_y)
                vx1, vy1 = self.vertices[v_chain[i]].get_coords()

            #getting the angle between it and it's parent
            angle = self.angle_to(vx1, vy1, vx2, vy2)

            #moving it's parent to it's original distance at the angle it was originally pointed
            self.vertices[v_chain[i + 1]].set_coords(vx1 + math.cos(angle) * dist, vy1 + math.sin(angle) * dist)

        
            
            #side chains on the chains from base to end
            if len(self.edges[v_chain[i]]) > 1:
                if v_chain[i] != v_chain[0]:
                    chain = [v_chain[i]] + list(set(self.dfs(self.edges, v_chain[i])) - set(v_chain))
                    
                    tx, ty = self.vertices[v_chain[i]].get_coords()

                    self.vertices[v_chain[i]].set_coords(og_positions[v_chain[i]][0], og_positions[v_chain[i]][1])

                    self.reaching(chain, tx, ty,  og_positions)
            

            
     
                              

          



    def rearrange(self, v_chain):
        tx, ty = self.target.get_X(), self.target.get_Y()
        sx1, sy1 = self.vertices[v_chain[0]].get_coords()
        ex, ey = self.vertices[v_chain[-1]].get_coords()
        

        
        #foward reaching
        #towards the target
        
        #print(distances)
        og_positions = self.vertex_positions(list(self.edges.keys()))
        #print(og_positions)
        #print(v_chain)
        
        self.reaching(v_chain, tx, ty, og_positions)

        #backwards reaching
        #towards the parent
        v_chain.reverse()
        self.reaching(v_chain, ex, ey, og_positions)
        
    



            

            

    def FABRIK(self):
        if len(self.vertices) > 1 and self.target_vtx != -1 and self.target_vtx != self.selected_vtx:
            base = self.selected_vtx
            end = self.target_vtx #random.choice([key for key in self.edges if not self.edges[key]])


            '''
                Edges
                Parent: 0 Childern: [1]
                Parent: 1 Childern: [2]
                Parent: 2 Childern: [3]
                Parent: 3 Childern: []
            '''
            




            #list in opposite order to end effector/target
            v_chain = self.dfs_path_between(self.edges, base, end)[::-1]
            #print(v_chain)
            if v_chain:
            
                self.rearrange(v_chain)
                self.render_vertices()  
                self.render_edges()
            
            #print(f"Base {base} End {end}")
            #childern = self.dfs(self.edges, self.selected_vtx)
        
    
    #Vertex Frame ---------------------------------------------------------------------------------------------------






    def angle_to(self, x1, y1, x2, y2):
        #in radians
        return math.atan2(y2 - y1, x2 - x1)

    def DDA(x0, y0, x1, y1, dist):
        #Digital Differential Analyzer
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx),abs(dy))
            
        x_inc = dx/steps
        y_inc = dy/steps
        
        x = x0
        y = y0
        
        coordinates = []
        
        for i in range(int(steps)):
            x += x_inc
            y += y_inc
            floored_coords = [math.floor(x), math.floor(y)]
            if floored_coords not in coordinates:
                coordinates.append(floored_coords)
                
        return coordinates

    def distance_to(self, x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        s = dx * dx + dy * dy
        return math.sqrt(s)

 
                    
            

                





class App(tk.Tk):
    def __init__(self):
        super().__init__()
        IKs = Kinematics(self, 500, 500)
        IKs.grid()

    


if __name__ == "__main__":
    app = App()
    #transparent frame
    #app.config(bg = '#add123')
    #app.wm_attributes('-transparentcolor','#add123')
    #app.geometry("800x600")
    
    #app.resizable()
    app.mainloop()

        

import tkinter as tk
from tkinter import ttk, filedialog, messagebox , colorchooser, PhotoImage, Toplevel
import os
from PIL import Image, ImageTk
from MatrixMath import *
from collisions import *
from numpy import array, uint8,  dot, float64, eye
from numpy import radians as to_radians
import math

def degrees_to_radians(self, deg):
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
        self.angle = 0
        self.name = name

    def __str__(self):
        return f"Joint: {self.name} " + str(self.vtx) + f" Angle:{self.angle}"
    
    def get_coords(self):
        return self.vtx.get_X(), self.vtx.get_Y()
    
    def transform(self, translation_matrix, transform_matrix, matrix_translation, new_angle):
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
        #Example
        #{0: [], 6: [1, 2, 0, 3], 3: [0, 2], 1: [2, 0], 5: [0, 3, 4], 4: [1, 2]}
        self.edges = {}
        
        #below keeps track for the dynamic checkboxes generated
        #will be the edges and whether they're connected tp other edges,
        # a dictionary of dictionarys and bools 
        self.edge_options = {} 
        #collection of th shown checkbox, deleted and regenerated frequently
        self.edge_checklist = []

        #the main frame which everything within the lines will be placed
        self.edge_con_frm = ttk.Frame(self)
        #------------------------------------------------------------------------------------------------
        self.edge_label = ttk.Label(self.edge_con_frm, text="Vertex:? - Edges")
        

        #https://blog.teclado.com/tkinter-scrollable-frames/
        self.edge_mn_frame = ttk.Frame(self.edge_con_frm)
        self.edge_canvas = tk.Canvas(self.edge_mn_frame, width=100, height=c_height - 50) #about the width of a listbox with no specificied width and heoght
        self.edge_scrollbar_y = ttk.Scrollbar(self.edge_mn_frame, orient='vertical', command=self.edge_canvas.yview)
        self.edge_scrl_frame = ttk.Frame(self.edge_canvas)
        
        self.edge_scrl_frame.bind(
            "<Configure>",
            lambda e: self.edge_canvas.configure(
                scrollregion=self.edge_canvas.bbox("all")
            )
        )


        
        self.edge_canvas.create_window((0, 0), window=self.edge_scrl_frame, anchor="nw")
        self.edge_canvas.configure(yscrollcommand=self.edge_scrollbar_y.set)
        #self.edge_scrollbar_y.config(command=self.self.edge_canvas.yview)
        
        self.edge_canvas.grid(row=0, column=0)#pack(side="left", fill="both", expand=True)
        self.edge_scrollbar_y.grid(row=0, column=1, sticky="NS")#pack(side="right", fill="y")

        self.edge_next = tk.Button(self.edge_con_frm,
                                   text="Next Vertex",
                                   command=self.next_vertex,
                                   #state="disabled"
                                   )
        self.edge_prev = tk.Button(self.edge_con_frm, 
                                   text="Prev Vertex", 
                                   command=self.prev_vertex, 
                                   #state="disabled"
                                   )
        
        edge_arrangement = [
            [self.edge_label],
            [self.edge_mn_frame],
            [self.edge_next],
            [self.edge_prev]
        ]

        

        arrange_widgets(edge_arrangement)

        #------------------------------------------------------------------------------------------------
        self.canvas = tk.Canvas(self, width=c_width, height=c_height, bg="white") 
        self.canvas_width = c_width #self.canvas.winfo_width()
        self.canvas_height = c_height #self.canvas.winfo_height()
        self.canvas.grid(row = 0, column = 0, sticky = "N")



        self.root_vtx = 0

        self.radius = 10
        self.selected_vtx = 0



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


        self.rotation_lbl =  ttk.Label(self, text = "Rotation", anchor="center")
        self.rotation_iv = tk.IntVar(value=0)
        self.rotation_scl = ttk.Scale(
            self,
            variable = self.rotation_iv,
            from_= 0,
            to = 360,
            orient = "horizontal",
            length=c_width,
            command = None
        )

        self.data_btn = tk.Button(self, 
                                  text="Data",
                                  command=self.display_data)
        


        self.btn_frame = ttk.Frame(self)

        
        #Button Type

        
        self.pen_img = tk.PhotoImage(file="icons\\add_circle_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.pen_btn = tk.Button(self.btn_frame, 
                                 text="Draw", 
                                 image=self.pen_img,
                                 ) 
        CreateToolTip(self.pen_btn, "Place Vertex")

        self.erase_img = tk.PhotoImage(file="icons\\ink_eraser_32dp_000000_FILL0_wght400_GRAD0_opsz40.png").subsample(4,4)
        self.erase_btn = tk.Button(self.btn_frame, 
                                 text="Erase", 
                                 image=self.erase_img
                                 ) 
        CreateToolTip(self.erase_btn, "Eraser Tool")

        self.rect_sel_img = tk.PhotoImage(file="icons\link_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rect_sel_btn = tk.Button(self.btn_frame, 
                                 text="Select", 
                                 image=self.rect_sel_img
                                 ) 
        CreateToolTip(self.rect_sel_btn, "Select Vertex")

        self.rect_con_img = tk.PhotoImage(file="icons\\add_link_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rect_con_btn = tk.Button(self.btn_frame, 
                                 text="Connect", 
                                 image=self.rect_con_img
                                 ) 
        CreateToolTip(self.rect_con_btn, "Add Edge")


        self.rect_off_img = tk.PhotoImage(file="icons\link_off_128dp_000000_FILL0_wght400_GRAD0_opsz48.png").subsample(4,4)
        self.rect_off_btn = tk.Button(self.btn_frame, 
                                 text="Break", 
                                 image=self.rect_off_img
                                 ) 
        CreateToolTip(self.rect_off_btn, "Erase Edge")
        
        self.drawing_widgets = [
            self.pen_btn, self.erase_btn,
            self.rect_sel_btn, self.rect_con_btn,
            self.rect_off_btn
            
        ]

        self.mode ="Draw"

        self.pen_btn.config(command=lambda:self.select_mode(self.pen_btn))
        self.erase_btn.config(command=lambda:self.select_mode(self.erase_btn))
        self.rect_sel_btn.config(command=lambda:self.select_mode(self.rect_sel_btn))
        self.rect_con_btn.config(command=lambda:self.select_mode(self.rect_con_btn))
        self.rect_off_btn.config(command=lambda:self.select_mode(self.rect_off_btn))

        btn_arrangement = [
            [self.pen_btn, self.erase_btn],
            [self.rect_sel_btn, self.rect_con_btn],
            [self.rect_off_btn, None]
        ]

        arrange_widgets(btn_arrangement)

        _arrangement = [
            [None           , None                   , self.vtx_lbl   , None            ],
            [self.btn_frame ,self.canvas             , self.vtx_lb    , self.vtx_sb_y   ],
            [None           ,self.rotation_scl       , self.vtx_sb_x  , None            ],
            [None           ,self.rotation_lbl       , self.data_btn  , None            ]

        ]

        arrangement = [
            [None           , None                   , None                 , None            ],
            [self.btn_frame ,self.canvas             , self.edge_con_frm    , None            ],
            [None           ,self.rotation_scl       , self.data_btn        , None            ],
            [None           ,self.rotation_lbl       , None                 , None            ],

        ]

        arrange_widgets(arrangement)


        self.canvas.bind("<B1-Motion>", self.on_canvas_lmb_press) 
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_lmb_click)
        self.canvas.bind("<ButtonRelease-1>", None)
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_lmb_click) 
        self.canvas.bind("<B3-Motion>", self.on_canvas_rmb_press) 
        

        self.select_mode(self.pen_btn)
    
    def dfs(self, graph, start, end):
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
                            "-".join( (str(ele) for ele in sorted([node]+path[:-1])))  for node in graph for path in self.dfs(graph, node, node) if len([node]+path) > 3
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
                

    def display_data(self):
        print("Vertices")
        for vertex in self.vertices:
            print(f"Vertex: {vertex}")
        print("Edges")
        for key in self.edges:
            # Parent Type:{type(key)}
            print(f"Parent: {key} Childern: {self.edges[key]}")
        print(f"Selected: {self.selected_vtx}")
        print("Vertices\n", self.vertices)
        print("Edges\n", self.edges)
        print("Edge Options\n", self.edge_options)
        print("Edge Checks\n", self.edge_checklist)
    
    



    def place_vertex(self, event): 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        v = Joint(x, y, str(len(self.vertices)))
        self.vertices.append(v)
        self.edges[len(self.vertices) - 1] = []

        self.render_vertices()
        self.update_edge_checkbuttons()



    def remove_vertex(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.canvas.delete("connected")
        self.canvas.delete("erasing")
        cx1 = x - self.radius
        cy1 = y - self.radius
        cx2 = cx1 + self.radius * 2
        cy2 = cy1 + self.radius * 2
        self.canvas.create_oval(
                                cx1, cy1, 
                                cx2, cy2, 
                                outline="red",
                                tags=("erasing")
                                )

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
                    self.selected_vtx = idx - 1
             
                
                #self.canvas.delete(str(idx))
                

                self.render_vertices()
                self.render_edges()

                

                self.update_edge_checkbuttons()

                


    def select_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)



        #self.canvas.delete("selected")
        self.canvas.delete("erasing")
        self.canvas.delete("connected")
        cx1 = x - self.radius * 1.5
        cy1 =  y - self.radius * 1.5
        cx2 = cx1 + self.radius * 3
        cy2 = cy1 + self.radius * 3

        self.canvas.create_oval(
                            cx1, cy1, 
                            cx2, cy2, 
                            outline="green",
                            tags=("connected")
                            )
        


        if len(self.vertices) > 0:
            idx = -1
            for i in range(len(self.vertices)):
                
                ox, oy = self.vertices[i].get_coords()
                if circle_circle(x, y, self.radius * 1.5, ox, oy, self.radius):
                    idx = i
                    self.canvas.delete("selected")
                    cx1 = ox - self.radius * 1.5
                    cy1 =  oy - self.radius * 1.5
                    cx2 = cx1 + self.radius * 3
                    cy2 = cy1 + self.radius * 3

                    self.canvas.create_oval(
                                        cx1, cy1, 
                                        cx2, cy2, 
                                        outline="cyan",
                                        tags=("selected")
                                )
                    break


            if idx != -1:
                self.selected_vtx = idx
                #print(f"selected: {self.selected_vtx}")
            
    

    def connect_vertex(self, event):

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.canvas.delete("connected")
        cx1 = x - self.radius * 1.5
        cy1 =  y - self.radius * 1.5
        cx2 = cx1 + self.radius * 3
        cy2 = cy1 + self.radius * 3

        self.canvas.create_oval(
                            cx1, cy1, 
                            cx2, cy2, 
                            outline="cyan",
                            tags=("connected")
                            )
        
        if len(self.vertices) > 1:
           
            idx = -1
            for i in range(len(self.vertices)):
                if i != self.selected_vtx:
                    ox, oy = self.vertices[i].get_coords()
                    if circle_circle(x, y, self.radius * 1.5, ox, oy, self.radius):
                        idx = i
                        
                        break

            #print(f"selected: {self.selected_vtx} Parent Type:{type(list(self.edges.keys())[0])} idx: {idx}")
            
                #self.selected_vtx = idx
            
            if idx > -1 and self.selected_vtx > -1:

                if idx != self.selected_vtx:
                    #print("HEARS")
                    if idx not in self.edges[self.selected_vtx]:
                        cycle_count = len(self.get_cycles(self.edges))
                        self.edges[self.selected_vtx].append(idx)
                        self.edges[idx].append(self.selected_vtx)
                        
            self.render_vertices()  
            self.render_edges(idx)
                        
                        #print(self.get_cycles(self.edges))

    
    def render_edges(self):

        for key in self.edges:
            for value in self.edges[key]:
                ax, ay = self.vertices[key].get_coords()
                bx, by = self.vertices[value].get_coords()
                self.canvas.create_line(
                        ax, ay,
                        bx, by
                    )
                    
                    
            #if len(cycles).split
            
    def render_vertices(self):
        self.canvas.delete(str("all"))
        for vertex in self.vertices:
            vx, vy  = vertex.get_coords()
            cx1 = vx - self.radius
            cy1 =  vy - self.radius
            cx2 = cx1 + self.radius * 2
            cy2 = cy1 + self.radius * 2
            self.canvas.create_oval(cx1, cy1, 
                                    cx2, cy2,
                                    tags=vertex.name)
            self.canvas.create_text(cx1 + self.radius, cy1 + self.radius,
                                    text=vertex.name)

    


    def connect_chk_vertices(self):
        if len(self.vertices) > 1:
            #print("yep")
            if len(self.edge_checklist) > 0:
                for ele in self.edge_checklist:
                    var = ele[0]
                    chk = ele[1]
                    parent = ele[2]
                    child = ele[3]
                    
                    booln = var.get()
                    
                    if isinstance(chk, tk.Checkbutton):
                        self.edge_options[parent][child] = booln
                        self.edge_options[child][parent] = booln
                        #print(parent, child)

            
            for parent in self.edge_options:
                for child in self.edge_options[parent]:
                    if self.edge_options[parent][child] == True:
                        
                        #if self.edges.get(child):
                        
                        if child not in self.edges[parent]:
                            self.edges[parent].append(child)
                        if parent not in self.edges[child]:
                            self.edges[child].append(parent)
                     
                    else:
                        #if self.edges.get(parent):
                        if child in self.edges[parent]:
                            self.edges[parent].remove(child)
                            #self.edges[child].remove(parent)
                        if parent in self.edges[child]:
                            self.edges[child].remove(parent) 
        self.render_vertices()       
        self.render_edges()         

    

    def next_vertex(self):
        #self.edge_label = ttk.Label(self, text="Vertex:? - Edges")
        if len(self.vertices) > 1:
            '''
            self.edge_keys_ls = None #self.edges.keys()
            self.edge_options = None #will be the edges and whether they're connected tp other edges, a dictionary of dictionarys and bools 
            
            '''
            self.selected_vtx += 1
            if len(self.edge_keys_ls) - self.selected_vtx == 0:
                self.selected_vtx = 0
            self.edge_label.config(text="Vertex:" + f"{self.selected_vtx} - Edges")

            self.create_edge_checkbuttons()
            
    def prev_vertex(self):
        #self.edge_label = ttk.Label(self, text="Vertex:? - Edges")
        if len(self.vertices) > 1:
            
            self.selected_vtx -= 1
            if self.selected_vtx < 0:
                self.selected_vtx = (len(self.edge_keys_ls) - 1) 
            self.edge_label.config(text="Vertex:" + f"{self.selected_vtx} - Edges")
            
            '''
            #Test
            options = ["Option " + str(i) for i in range(1,50)]
            i = 0
            for option in options:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.edge_scrl_frame, text=option, variable=var, command=None).grid(row=i, column=1)#pack()
                i += 1
            '''
            self.create_edge_checkbuttons()

    def create_edge_checkbuttons(self):
        #dynamically creating checkboxes for edges
        if len(self.edge_checklist) > 0:
            for ele in self.edge_checklist:
                var = ele[0]
                chk = ele[1]
                if isinstance(chk, tk.Checkbutton):
                    var.set(False)
                    delete_widget(chk)
                
        self.edge_checklist.clear()
        
        i = 0
        
        for key in self.edge_options[self.selected_vtx]:
            if key != self.selected_vtx:
                txt = "Vertex:" + str(key)
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self.edge_scrl_frame, 
                                    text=txt, 
                                    variable=var,
                                    command=self.connect_chk_vertices,
                                    onvalue=True,
                                    offvalue=False
                                    
                                    )
                
                var.set(self.edge_options[self.selected_vtx][key])
                
                parent = self.selected_vtx
                child = key
                
                self.edge_checklist.append([var, chk, parent, child])
                chk.grid(row=i, column=1)
                
                i = i + 1

    def update_edge_checkbuttons(self):
        if self.vertices:
            #print("update edges")
            #updating the edge checkbuttons
            if len(self.vertices) == 0:
                self.edge_label.config(text="Vertex:? - Edges")
            
            #self.edge_options = {} 
            #below keeps track for the dynamic checkboxes generated
            #will be the edges and whether they're connected tp other edges, 
            # a dictionary of dictionarys and bools 
            
            self.edge_keys_ls = self.edges.keys()
            self.edge_canvas.delete("all")
            self.edge_canvas.create_window((0, 0), window=self.edge_scrl_frame, anchor="nw")
            self.edge_options.clear()
            self.edge_keys_ls = self.edges.keys()
            
            for key in self.edges:
                #rewriting edges
                self.edge_options[key] = {}
                for ele in self.edge_keys_ls:
                    if key != ele:
                        if ele in self.edges[key]:
                            self.edge_options[key][ele] = True
                        else:
                            self.edge_options[key][ele] = False


            self.edge_label.config(text="Vertex:" + f"{self.selected_vtx} - Edges")

            self.create_edge_checkbuttons()      

    def angle_to(x1, y1, x2, y2):
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

    def get_distance(x1, y1, x2, y2):
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
        
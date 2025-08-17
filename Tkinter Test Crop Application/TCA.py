import tkinter as tk
from tkinter import ttk
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_POS_FRAMES, cvtColor, COLOR_BGR2RGB
from PIL import ImageTk, Image
#import numpy as np  
from numpy import eye, dot, linalg



class TestCropApplication(tk.Tk):
    def __init__(self, cv_width: int, cv_height: int):
        super().__init__()
        self.title("Video Crop Sampl")

        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=3)
        #self.rowconfigure(0, weight=1)

        self.bck_btn = ttk.Button(self, text='Back',command=self.Back)
        
        self.nxt_btn = ttk.Button(self, text='Next',command=self.Next)
        self.nxt_btn.grid(row=0, column=2)
        self.bck_btn.grid(row=0, column=0)
        
        
        
        #canvas crop
        #self.pil_image = None   # Image data to be displayed

        self.zoom_cycle = 0
        
        self.og_image_scale = 0
        
        self.video = None
        self.current_img = None
        self.rect = None
        
        self.rect_x = None
        self.rect_y = None
        self.rect_w = None
        self.rect_h = None
        
        
    
        
        self.image_ratio = 0
        
     
        
        
        self.current_frame_label = ttk.Label(self, text = f"Current Frame: 0")
        self.current_frame_label.grid(row=3, column=2)
        
        #self.scale_label = tk.Label(self, text = "scale:")
        #self.scale_label.pack()
        
        self.position_mouse_label = tk.Label(self, text = "Canvas MX:0 Canvas MY:0")
        self.position_mouse_label.grid(row=0, column=1)
        
        self.image_pos_mouse_label = tk.Label(self, text = "Image MX:0 Image MY:0")
        self.image_pos_mouse_label.grid(row=1, column=1)
        
        self.image_scale_ratio_label = tk.Label(self, text = "Scale X:0 Scale Y:0")
        self.image_scale_ratio_label.grid(row=2, column=1)
        
        self.image_scale_ratio_label2 = tk.Label(self, text = "Scale X:0 Scale Y:0")
        self.image_scale_ratio_label2.grid(row=3, column=1)
        
        
       
        
        
        
        # Canvas
        self.canvas = tk.Canvas(self, background="black", width = cv_width,height = cv_height)
        #self.canvas = tk.Canvas(self, background="black")
        self.canvas.grid(row=4, column=1)
        
        self.label_rx = ttk.Label(self, text="rect x")
        self.label_ry = ttk.Label(self, text="rect y")
        self.label_rw = ttk.Label(self, text="rect w")
        self.label_rh = ttk.Label(self, text="rect h")
        
        self.label_rx.grid(row = 5, column = 1)
        self.label_ry.grid(row = 6, column = 1)
        self.label_rw.grid(row = 7, column = 1)
        self.label_rh.grid(row = 9, column = 1)
        
    
        # Controls
        self.canvas.bind("<ButtonPress-3>", self.on_button_clear)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        
        self.canvas.bind("<ButtonPress-1>", self.mouse_down_left)                   # MouseDown
        #self.canvas.bind("<B1-Motion>", self.mouse_move_left)                  # MouseDrag
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left)    # MouseDoubleClick
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)                     # MouseWheel
        
        
        #self.canvas.bind("<Button-1>", self.get_canvas_mouse_pos)
        
        
    def set_video_frame(self, video_path):
        #To open an frame of a video as file
        if not video_path:
            return
        
        self.video = VideoCapture(video_path)
        
        if not self.video.isOpened():
            return
        
        
        # Get General Info
        self.fps         = self.video.get(CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        self.frame_count = int(self.video.get(CAP_PROP_FRAME_COUNT))
    
        self.duration    = int(self.frame_count/self.fps)
        self.width       = int(self.video.get(CAP_PROP_FRAME_WIDTH))  # float
        self.height      = int(self.video.get(CAP_PROP_FRAME_HEIGHT)) # float
        
        self.current_frame = 0
        self.video.set(CAP_PROP_POS_FRAMES, self.current_frame)
        
        #img is a frame of the video
        ret, img = self.video.read()
        #conversion from CV2 Image Data a into a Pillow Image        
        self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
        
        
        #self.img_label = ttk.Label(self, image = self.current_img)
        #self.img_label.pack()
        
        self.interval_spinbox= ttk.Spinbox(self, 
                                        from_ = 1, 
                                        to = int(self.frame_count/3),
                                        width = 10
                                        
                                        )
        self.interval_spinbox.set(1)
        self.interval_spinbox.grid(row=1, column=2)
        
        self.total_frame_label = ttk.Label(self, text = f"Total Frames: {self.frame_count}")
        self.total_frame_label.grid(row=2, column=2)
        
        
        
        #can be image width or height
        #original image width before resize
        self.og_image_scale = self.width
        
        #self.canvas.config(width=self.current_img.width, height=self.current_img.height)
        
        #self.nu_image_scale_w, self.nu_image_scale_h = self.og_image_scale_w, self.og_image_scale_h
        # Set the affine transformation matrix to display the entire image.
        self.zoom_fit(self.current_img.width, self.current_img.height)
        # To display the image
        self.draw_image(self.current_img)
        
        
    def Next(self):
        if self.current_img == None:
            return
        self.canvas.delete("image")
        #global i
        #i = i + 1
        #try:
        self.current_frame += int(self.interval_spinbox.get())
        if self.current_frame > self.frame_count - 1:
            self.current_frame = self.current_frame%self.frame_count
        
        self.video.set(CAP_PROP_POS_FRAMES, self.current_frame)
        
        #img is a frame of the video
        ret, img = self.video.read()
        #conversion from CV2 Image Data a into a Pillow Image        
        self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
        
        #self.img_label.config(image=self.current_img)
        
        self.current_frame_label.config(text = f"Current Frame: {self.current_frame}")
        #cv2.imshow("video", img)
        #cv2.waitKey(0)
        #except:
            #i = -1
            #Next()
        #self.canvas.delete("all")
        
        self.zoom_fit(self.current_img.width, self.current_img.height)
        self.update()
        
            
    def Back(self):
        if self.current_img == None:
            return
        self.canvas.delete("image")
        
        self.current_frame -= int(self.interval_spinbox.get())
        
        if self.current_frame < 0:
            self.current_frame = abs(self.frame_count - self.frame_count) 
            
        self.video.set(CAP_PROP_POS_FRAMES, self.current_frame)
        
        #img is a frame of the video
        ret, img = self.video.read()
        #conversion from CV2 Image Data a into a Pillow Image        
        self.current_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB))
        
        
        
        #self.img_label.config(image=self.current_img)
        
        self.current_frame_label.config(text = f"Current Frame: {self.current_frame}")
        #cv2.imshow("video", img)
        #cv2.waitKey(0)
        #self.canvas.delete("all")
        
        self.zoom_fit(self.current_img.width, self.current_img.height)
        self.update()
        
 
    
    
    
    
    # -------------------------------------------------------------------------------
    # Mouse events
    # -------------------------------------------------------------------------------
    def on_button_clear(self, event):
        self.canvas.delete("rect")
    
    def mouse_down_left(self, event):
        
        self.__old_event = event
        
        
        
        self.get_canvas_mouse_pos(event)
        
    def get_canvas_mouse_pos(self, event):
        if self.current_img == None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.position_mouse_label.config(text= f"Canvas MX: {x} Canvas MY: {y}")
        
        
        
        
        xny = self.to_image_point(x, y)
        if len(xny) != 0:
            x = xny[0]
            y = xny[1]
            
            #self.rect_x, self.rect_y, self.rect_w, self.rect_h = 0, 0, 0, 0
            
            self.rect_x = self.canvas.canvasx(event.x)
            self.rect_y = self.canvas.canvasx(event.y)
            
            self.image_pos_mouse_label.config(text = f"Image MX:{x} Image MY:{y}")
            
            
            
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
        image_wh = self.to_image_point(rx + rw, ry + rh)
        

        if len(image_xy) > 0 and len(image_wh) > 0:
            ix = image_xy[0]
            iy = image_xy[1]
            iw = abs(ix - image_wh[0])
            ih = abs(iy - image_wh[1])
            
            self.label_rx.config(text= "canvas rect x: {:.2f}".format(rx) + " image rect x: {:.2f}".format(ix))
            self.label_ry.config(text= "canvas rect y: {:.2f}".format(ry) + " image rect y: {:.2f}".format(iy))
            self.label_rw.config(text= "canvas rect w: {:.2f}".format(rx + rw) + " image rect w: {:.2f}".format(iw))
            self.label_rh.config(text= "canvas rect h: {:.2f}".format(ry + rh) + " image rect h: {:.2f}".format(ih))
            

            
            
            self.canvas.delete("rect")
            
            self.rect = self.canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline='black', tags=("rect"))
        
        
           
            self.canvas.tag_raise("rect", "image")   
    
    
                
        

    def mouse_move_left(self, event):
        if self.current_img == None:
            return
        
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        #self.__old_event = event



    def mouse_double_click_left(self, event):
        if self.current_img == None:
            return
        
        self.zoom_fit(self.current_img.width, self.current_img.height)
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
            
            
            
        self.image_ratio = self.og_image_scale / (self.og_image_scale * scale)
        
        
         


        self.image_scale_ratio_label.config(text = f"Resized Image ratio to Original Image: {scale}")
        self.image_scale_ratio_label2.config(text = "Original Image ratio to Resized Image: {}".format(self.image_ratio))
    
        
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
        if self.current_img == None:
            return
        self.draw_image(self.current_img)
        
    
if __name__ == "__main__":
    app = TestCropApplication(500, 500)
    app.set_video_frame("Test\\Homies Home.mp4")
    app.resizable()
    app.mainloop()

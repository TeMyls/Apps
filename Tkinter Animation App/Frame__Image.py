from MatrixMath import *
from collisions import *
import numpy as np
from numpy import radians as to_radians
from PIL import Image, ImageTk, ImageSequence, ImageDraw, ImageOps, ImageChops

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

def mid_point_ellipse(cx, cy, rx, ry):
    # Python3 program for implementing 
    # Mid-Point Ellipse Drawing Algorithm 
    
    x = 0
    y = ry

    # Initial decision parameter of region 1 
    d1 = ((ry * ry) - (rx * rx * ry) + (0.25 * rx * rx))
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y

    points = []

    # For region 1 
    while (dx < dy): 

        # Print points based on 4-way symmetry 
        points.append((x + cx, y + cy))
        points.append((-x + cx, y + cy)) 
        points.append((x + cx, -y + cy ))
        points.append((-x + cx, -y + cy))

        # Checking and updating value of 
        # decision parameter based on algorithm 
        if (d1 < 0): 
            x += 1
            dx = dx + (2 * ry * ry)
            d1 = d1 + dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx = dx + (2 * ry * ry) 
            dy = dy - (2 * rx * rx)
            d1 = d1 + dx - dy + (ry * ry)

    # Decision parameter of region 2 
    d2 = (((ry * ry) * ((x + 0.5) * (x + 0.5))) + ((rx * rx) * ((y - 1) * (y - 1))) - (rx * rx * ry * ry))

    # Plotting points of region 2 
    while (y >= 0):

        # printing points based on 4-way symmetry 
        points.append((x + cx, y + cy))
        points.append((-x + cx, y + cy))
        points.append((x + cx, -y + cy))
        points.append((-x + cx, -y + cy))

        # Checking and updating parameter 
        # value based on algorithm 
        if (d2 > 0):
            y -= 1; 
            dy = dy - (2 * rx * rx); 
            d2 = d2 + (rx * rx) - dy; 
        else:
            y -= 1; 
            x += 1; 
            dx = dx + (2 * ry * ry); 
            dy = dy - (2 * rx * rx); 
            d2 = d2 + dx - dy + (rx * rx); 
    return points

def DDA(x0, y0, x1, y1):
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

def DDA_raycast(x0, y0, radians, limit):
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

class Vertex():
    def __init__(self, x , y):
        self.v = np.array(
            set_matrix2D(x, y),  dtype=np.float64
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
        #multiple ways to transform points
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
        XnY = np.dot(translation_matrix, self.v) #moves to origin
        #print(XnY, '\n')
        XnY = np.dot(transform_matrix, XnY) #applies transform
        #print(XnY, '\n')
        XnY = np.dot(matrix_translation, XnY) #moves back to original position
        '''
        '''
        XnY = np.dot(matrix_translation, np.dot(transform_matrix, np.dot(translation_matrix, self.v)))
        '''
        full_transform = matrix_translation @ transform_matrix @ translation_matrix
        XnY = full_transform @ self.v
        self.set_coords(XnY[0 ,0], XnY[1, 0])
        self.been_transformed = True


class ImageFrame():

    # ImageFrame
        # ImageFrame is a class that acts on upon the Tkinter canvas given to it, displaying an every updating canvas_image, based on an interal pixel_image. B
            # Both of these images are Image Objects provided by the PIL, or Python Image Library

    def __init__(self, pixel_width, pixel_height, canvas_width, canvas_height):
        '''
        0 - KeyFrame is a class that represents a collection of vertices from the very edges of the shape to the edges of individual pixel polygons made of XY vertices
        1 - pixel grid is a 2D array/list of Hex Codes, that represent the pixels in an image, and empty cell/pixel is denoted by None/"#______ instead of a hexcode
        2 - pixel coords is a dictionary of vertex coordinates 
            say for instance a 4x4 grid
            "X-Y" as a string that is a key to a dictionary/hashmap
            Each of these keys would have an array linking to their vertex coordinates 
                [V1, V2, V3, V4] of their polygon 
            'V' is an x, y vertex
            'N' and 'M' are it's respective dimensions 
            For a 4x4 cell grid both M and N would be 4

                        M
    
            V-------V-------V-------V-------V
            | 0-0   | 0-1   | 0-2   | 0-3   | 
            V-------V-------V-------V-------V
            | 1-0   | 1-1   | 1-2   | 1-3   |
       N    V-------V-------V-------V-------V  
            | 2-0   | 2-1   | 2-2   | 2-3   | 
            V-------V-------V-------V-------V
            | 3-0   | 3-1   | 3-2   | 3-3   |
            V-------V-------V-------V-------V

            
            

        3 - pixel vertices is a list of the vertices in an area, the vertices that are values in pixel coords are the same objects  in this list
            The amount of unique vertices are as follows
            4 outside vertices with 2 neighbors
            2(M - 1) + 2(N - 1) vertices with 3 neighbors
            (M - 1 ) * (N - 1) vettices with 4 neighbors

            For a 4x4 grid it's 4 + (2(4 - 1) + 2(4 - 1)) +  ((4 - 1) * (4 - 1)) which equals 25 vertices
            Why? Computationally more efficient. 16 rectangle polygons with 4 vertices each totaling 48 vertices with many sharing the same coordinates doesn't scale well.
            With each vertex being an object, updating them once will change all of them in whatever data structure their in
        '''
        

        #Variou ways to initizial a 2D array
        #very painful bug
        #it's possible to initialize a 2D array like this but all the rows change at once when updating the contents of one
        #print([[None] * pixel_width] * pixel_height)

        '''
        for y in range(self.pixel_canvas_height):
            self.pixel_grid.append([])
            for x in range(self.pixel_canvas_width):
                self.pixel_grid[y].append(None)
        '''

        #self.pixel_grid = [[None for _ in range(pixel_width)] for _ in range(pixel_height)]
        
        #The last tuple is Red(0 - 255), Green(0 - 255), Blue(0 - 255), and Alpha/Transparency(0 - 255)
        #White (225, 255, 255, 255) Transparent (x, x, x, 0)
        self.blank = (0, 0, 0, 0)
        self.pixel_image = Image.new("RGBA", (pixel_width, pixel_height), self.blank)
        self.temp_image = Image.new("RGBA", (pixel_width, pixel_height), self.blank)
        
        #used to be essential, now is just used for debuging
        self.pixel_grid = [["#______"] * pixel_width for _ in range(pixel_height)]#[[None] * pixel_width for _ in range(pixel_height)]

        # deprecated as I realized the draw_pixel function was slower than updating pixel_image and resizing it to the canvas
        self.pixel_coords = {}
        # deprecated when I realized that pixel coords could keep track of vertices perfectly fine
        self.pixel_vertices = []


        self.pixel_canvas_width = pixel_width
        self.pixel_canvas_height = pixel_height
        
        

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.canvas_image = None
        self.temp_canvas_image = None

        
        self.pixel_scale = -1
        

        self.brush_size = 1

        #line stroke drawing vars
        self.is_drawing_line = False

        
        self.stroke_pixels = []
        self.temp_pixels = []
        self.temp_colors = []
        self.first_pixel = []
        self.last_pixel = []
        self.anchor_pixel = []
        self.lasso_polygon = []

        #print(f"{self.canvas_width} {self.canvas_height}")
    
        
        #rectangle vars
        self.rect = None
        self.rect_x = None
        self.rect_y = None
        self.rect_w = None
        self.rect_h = None

    def get_pil_image(self):
        return self.pixel_image
    
    def get_temp_pixels(self):
        return self.temp_pixels
    
    def get_temp_colors(self):
        return self.temp_colors


    #pixel conversion methods

    def pil_image_to_grid(self):
        return [
                    [
                        self.rgb_to_hex(col[0], col[1], col[2]) if col[-1] != 0  else "#______" for col in row
                    ]for row in np.array(self.pixel_image).tolist()
                ]
    
    def grid_to_pil_image(self, grid_pixel):
        return Image.fromarray(
                        np.array(
                                    [
                                        [
                                            self.hex_to_rgb(grid_pixel[row][col], True) if grid_pixel[row][col] != "#______"  else self.blank for col in range(len(grid_pixel[0]))
                                        ]for row in range(len(grid_pixel))
                                    ], 
                                    dtype=np.uint8
                                )
                            )

    def pil_image_to_array2D(self):
        #
        return [
                    [
                        self.pixel_image.getpixel((x, y)) for x in range(self.pixel_canvas_width - 1)
                    ] for y in range(self.pixel_canvas_height - 1)
                ]
    
    def pil_image_to_numpy_array2D(self):
        #print(np.array(self.pixel_image).shape)
        return np.array(self.pixel_image, dtype=np.uint8)
        #return np.array(self.pil_image_to_array2D())
    
    def numpy_array2D_to_pil_image(self, np_array):
        return Image.fromarray(np_array)

    # transform_pixels
        # applies affine transformations to the image 
        # translation_matrix and matrix_translation are the pivot points represented in matrix form
        # transformation_matrix can be a scaling, rotation, shearing, translation, or reflection matrix

    def transform_pixels(self, translation_matrix, transform_matrix, matrix_translation, canvas, borders):
        #grid_pixel = [[  None ] * len(self.pixel_grid[0]) for _ in range(len(self.pixel_grid))]
        canvas.delete("all")
        im_width, im_height = self.pixel_image.size
        new_pixels = []
        new_colors = []
        full_transform = matrix_translation @ transform_matrix @ translation_matrix

        
        if self.temp_pixels:

            
            new_colors = self.temp_colors

            for pxl in self.temp_pixels:
                rgba = self.pixel_image.getpixel((pxl[0], pxl[1]))
                if rgba != self.blank:
                    old_x, old_y = pxl[0], pxl[1]
                    XnY = np.array(
                        set_matrix2D(old_x, old_y),  dtype=np.float64
                    )
                    #if self.pixel_grid[old_y][old_x] != None:
                    
                    XnY = full_transform @ XnY
                    
                    new_x, new_y = round(XnY[0 ,0]), round(XnY[1, 0])
                    if in_bounds(new_x, new_y, len(self.pixel_grid[0]), len(self.pixel_grid)):
                        self.pixel_image.putpixel((old_x, old_y), self.blank)
                        new_pixels.append((new_x, new_y))
                    else:
                        self.pixel_image.putpixel((old_x, old_y), self.blank)

        else:

            for y in range(im_height):
                for x in range(im_width):
                    rgba = self.pixel_image.getpixel((x, y))
                    if rgba != self.blank:
                        old_x, old_y = x, y
                        XnY = np.array(
                            set_matrix2D(old_x, old_y),  dtype=np.float64
                        )

                        XnY = full_transform @ XnY
                        
                        new_x, new_y = round(XnY[0 ,0]), round(XnY[1, 0])
                        if in_bounds(new_x, new_y, len(self.pixel_grid[0]), len(self.pixel_grid)):
                            self.pixel_image.putpixel((old_x, old_y), self.blank)
                            new_pixels.append((new_x, new_y))
                            new_colors.append(rgba)
                        else:
                            self.pixel_image.putpixel((old_x, old_y), self.blank)

        

        for i in range(len(new_pixels)):
            pxl = new_pixels[i]
            color = new_colors[i]
            self.pixel_image.putpixel((pxl[0], pxl[1]), color)
        
        self.temp_pixels = new_pixels
        self.temp_colors = new_colors

    # scale_image
        # scales up the pixel_image (the actually image size) to the canvas_image (the image displayed on the canvas)
        # the canvas image changes based on position, scale,and updates to the pixel_image
    # render_image
        # actually draws the canvas_image to the canvas
    # the borders array
        # [
            # self.top_left.get_X(),     self.top_left.get_Y(),
            # self.top_right.get_X(),    self.top_right.get_Y(),
            # self.bottom_right.get_X(), self.bottom_right.get_Y(),
            # self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        # ]

    def scale_image(self, canvas, borders):
        #canvas.delete("all")
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]

        im_width, im_height = self.pixel_image.size  
        
        true_pixel_width = border_width/im_width
        true_pixel_height = border_height/im_height

        mxp_dim = max(im_width, im_height)
        mxb_dim = max(border_width, border_height)

        scale_dim = mxb_dim/mxp_dim
        
        self.canvas_image =  ImageTk.PhotoImage(
                                    self.pixel_image.resize(
                                        (round(scale_dim * im_width), round(scale_dim * im_height))
                                        , Image.Resampling.NEAREST
                                                            )
                                                )
        
        
        im_width, im_height = self.pixel_image.size 
        #print(im_width, im_height)
        self.pixel_coords.clear()
        #self.pixel_image = display_image

        #self.image = im

    def render_image(self, canvas, borders):
        #canvas.delete("all")
        border_x = borders[0]
        border_y = borders[1]
        self.scale_image(canvas, borders)
        # Draw the image
        canvas.create_image(
            border_x, border_y,         # Image display position (top-left coordinate)
            anchor='nw',                # Anchor, top-left is the origin
            image=self.canvas_image,    # Display image data
            #tags = ("image")
            
        )
        self.pixel_coords.clear()

    def scale_temp_image(self, canvas, borders):
        #canvas.delete("all")
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]

        im_width, im_height = self.temp_image.size  
        
        true_pixel_width = border_width/im_width
        true_pixel_height = border_height/im_height

        mxp_dim = max(im_width, im_height)
        mxb_dim = max(border_width, border_height)

        scale_dim = mxb_dim/mxp_dim
        
        self.temp_canvas_image =  ImageTk.PhotoImage(
                                    self.temp_image.resize(
                                        (round(scale_dim * im_width), round(scale_dim * im_height))
                                        , Image.Resampling.NEAREST
                                                            )
                                                )
        
        
        im_width, im_height = self.temp_image.size  
        #print(im_width, im_height)
        self.pixel_coords.clear()
        #self.pixel_image = display_image

        #self.image = im

    def render_temp_image(self, canvas, borders):
        #canvas.delete("all")
        border_x = borders[0]
        border_y = borders[1]
        self.scale_temp_image(canvas, borders)
        # Draw the image
        canvas.create_image(
            border_x, border_y,         # Image display position (top-left coordinate)
            anchor='nw',                # Anchor, top-left is the origin
            image=self.temp_canvas_image,    # Display image data
            #tags = ("image")
            
        )
        self.pixel_coords.clear()

    # controls the keys from pixel_coords

    def coord_to_str(self, x, y):
        return str(x) + '|' + str(y)
    
    def str_to_coord(self, string):
        if '|' in string:
            x, y = map(int, string.split('|'))
            return x, y
        return 0, 0


    #https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    #https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa

    # rgb_to_hex
        # converts a red, green, and blue colors (0 - 255) in a hexcode
    # hex_to_rgb
        # takes a hexcode and converts it into an red, green, blue (RGB) or red, green, blue, list (RGBA)

    def rgb_to_hex(self, r,g,b):
        hexcode = '#%02x%02x%02x' % (r, g, b) #"#{:02x}{:02x}{:02x}".format(r,g,b)
        return hexcode
    
    def hex_to_rgb(self, hexcode, alpha = False):
        hexcode = hexcode[1:]
        rgb = list(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
        if alpha:
            rgb.append(255)
            return rgb 
        return rgb 
    
    def invert_color(self, color):
        rgb = self.hex_to_rgb(color)
            
        rgb[0] = 255 - rgb[0]
        rgb[1] = 255 - rgb[1]
        rgb[2] = 255 - rgb[2]
        

        r, g, b = rgb
        _hex = self.rgb_to_hex(r, g, b)
        return _hex
    
    # display_1d and display_2d 
        # prints 1 dimensional and 2 dimensional arrays in a readable format
   
    def display_1d(self, arr):
        s = ""
        for i in range(len(arr)):
            
            s = s + str(arr[i]) + " "
            
        print(s)    
    
    def display_2d(self, arr2d):
        s = ""
        for row in range(len(arr2d)):
            for col in range(len(arr2d[row])):
                s = s + str(arr2d[row][col]) + " "
            s = s + '\n'
        print(s)

    # alter_image_dimensions
        # creates a new image based on the new dimensions
        # then pastes the old image inside of it whose location depends on the anchor point

    
    def alter_image_dimensions(self, anchor, new_width, new_height, canvas, borders):
        #https://note.nkmk.me/en/python-pillow-paste/
        

        

        
        #Crop : Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
            #https://note.nkmk.me/en/python-pillow-invert/
            #https://note.nkmk.me/en/python-pillow-concat-images/
            #img_to_paste = self.pixel_image.crop((x1, y1, x2, y2)).convert("RGB")
            #img_to_paste = ImageOps.invert(img_to_paste).convert("RGBA")
        #https://note.nkmk.me/en/python-pillow-image-crop-trimming/

        
        cur_width, cur_height = self.pixel_image.size
        top_left_x = 0
        top_left_y = 0
        bottom_right_x = abs(new_width - cur_width)
        bottom_right_y = abs(new_height - cur_height)


        anchor_xy = {
            "NW": [top_left_x, top_left_y], "N": [bottom_right_x//2, top_left_y], "NE": [bottom_right_x, top_left_y],
            "W":  [top_left_x, bottom_right_y//2], "C": [bottom_right_x//2, bottom_right_y//2],  "E": [bottom_right_x, bottom_right_y//2],
            "SW": [top_left_x, bottom_right_y], "S": [bottom_right_x//2, bottom_right_y], "SE": [bottom_right_x, bottom_right_y]
        }

        #self.temp_image = ImageChops.offset(self.temp_image, dx, dy) #wraps arounf
        
        
        #crop
        #(left, upper, right, lower)
        blank_image = Image.new("RGBA", (new_width, new_height), self.blank)
        blank_used = False
        cropped = False
        vector = anchor_xy[anchor]
        crop_box = []

        print("\nNew")
        if new_width > cur_width:
            
            vector = anchor_xy[anchor]
            #blank_image.paste(self.pixel_image, (vector[0], vector[1]))
            blank_used = True
            #print(blank_image.size)
            #print("bigger width")
        if new_width <= cur_width:
            vector = anchor_xy[anchor]
            crop_box = [vector[0], vector[1], vector[0] + new_width,  vector[1] + cur_height]
            #print(crop_box)
            #self.pixel_image = self.pixel_image.crop((vector[0], vector[1], vector[0] + new_width,  vector[1] + cur_height))
            #blank_image.paste(self.pixel_image, (vector[0], vector[1]))
            cur_width = new_width
            cropped = True
            #print(self.pixel_image.size)
            #print("smaller width")



        if new_height > cur_height:
            
            vector = anchor_xy[anchor]
            
            blank_used = True
            print("bigger height")
        if new_height <= cur_height:
            vector = anchor_xy[anchor]
            crop_box = [vector[0], vector[1], vector[0] + cur_width,  vector[1] + new_height]
            print(crop_box)
            cropped = True
            print()
            #self.pixel_image = self.pixel_image.crop((vector[0], vector[1], vector[0] + cur_width,  vector[1] + new_height))
            #blank_image.paste(self.pixel_image, (vector[0], vector[1]))
            print(self.pixel_image.size)
            print("smaller height")
        
        if blank_used:
            print("true 2")
            if cropped:
                self.pixel_image.crop(box=crop_box)
            blank_image.paste(self.pixel_image, (vector[0], vector[1]))
            
            self.pixel_image = blank_image

        if cropped and not blank_used:
            self.pixel_image = self.pixel_image.crop(box=crop_box)

        
            
        
        
    
    # canvas_to_pixel
        # determines pixel coordinates from the width and height of the border

    def canvas_to_pixel(self, canvas, mouse_x, mouse_y, borders):
        canvas.delete("lines")
        #print("canvas2pixel")

        top_left_x, top_left_y = borders[0], borders[1]
        

        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        
        distance = distance_to(mouse_x, mouse_y, top_left_x, top_left_y) 
        radians =  angle_to(top_left_x, top_left_y, mouse_x, mouse_y) #+ degrees_to_radians(180)
        distance_x = distance_to(top_left_x + math.cos(radians) * distance, top_left_y, top_left_x, top_left_y)
        distance_y = distance_to(top_left_x, top_left_y + math.sin(radians) * distance, top_left_x, top_left_y)
        x_offset = -1 if mouse_x < top_left_x else 1
        y_offset = -1 if mouse_y < top_left_y else 1

        grid_x = math.floor((distance_x/border_width * x_offset) * self.pixel_canvas_width)
        grid_y = math.floor((distance_y/border_height * y_offset) * self.pixel_canvas_height)
        
        if False:
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x + math.cos(radians) * distance, top_left_y + math.sin(radians) * distance,
                    
                    fill = "cyan",
                    tags="lines"
                )
            
            
            
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x, top_left_y + math.sin(radians) * distance,
                    
                    fill = "yellow",
                    tags="lines"
                )
            
            canvas.create_line(
                    top_left_x, top_left_y, 
                    top_left_x + math.cos(radians) * distance, top_left_y,
                    
                    fill = "magenta",
                    tags="lines"
                )
        

        return [grid_x, grid_y]

    # pixel_to_canvas
        # gets the real canvas coordinates of a pixel if it's within pixel_coords


    def pixel_to_canvas(self, pixel_x, pixel_y):
        #print("pixel2canvas")
        key_coord = self.coord_to_str(pixel_x, pixel_y)
        if self.pixel_coords.get(key_coord):
            vertices = self.pixel_coords[key_coord]
            #if vertices:
            #canvas.delete(key)
            #color = self.pixel_grid[y_pixel][x_pixel]

            #pixel polygon vertices not sheet
            top_left_x, top_left_y = vertices[0].get_X(), vertices[0].get_Y()
            top_right_x, top_right_y = vertices[1].get_X(), vertices[1].get_Y()
            bottom_right_x, bottom_right_y = vertices[2].get_X(), vertices[2].get_Y()
            bottom_left_x, bottom_left_y = vertices[3].get_X(), vertices[3].get_Y()

            return [
                top_left_x, top_left_y,
                top_right_x, top_right_y,
                bottom_right_x, bottom_right_y,
                bottom_left_x, bottom_left_y
            ]
        return [
                0, 0,
                0, 0,
                0, 0,
                0, 0,
              
            ]
        
    # recycle_vertices
        # this method ensures that vertices are shared between pixels rather than each being independent
        # that two adjecent pixels will comprise of 6 pixels rather than 8 a better explanation is above

    def recycle_vertices(self, grid_x, grid_y, left_top, right_top, right_bottom, left_bottom):
        #print("recycle")
        #The purpose of this to reuse existing vertices
        #[N,NE,E,SE,S,SW,W,NW]
        #possible directions
        #8 direction
        '''
                        x  y 
                        0,-1
            -1,-1                   1, -1
                V-----V-----V-----V
                |  NW |  N  |  NE | 
                V-----V-----V-----V     
        -1,0    |  W  |  CC |  E  |     1, 0
                V-----V-----V-----V
                |  SW |  S  |  SE | 
                V-----V-----V-----V
            -1,1                    1, 1
                        0, 1
        '''
        #temp = Vertex(-1, -1)
        #The vertices of CC

        top_left  = left_top
        top_right  = right_top
        bottom_right = right_bottom
        bottom_left = left_bottom

        bottom_right_vectors = [
            #x y
            (1, 0), #East
            (1, 1), #South East
            (0,  1) #South
        ]

        bottom_left_vectors = [
            #x y
            (-1, 0), #West
            (-1, 1), #South West
            (0,  1) #South
        ]

        top_left_vectors = [
            #x y
            (0, -1), #North
            (-1,-1), #North West
            (-1, 0) #West
        ]

        top_right_vectors = [
            #x y
            (0, -1), #North
            (1,-1),  #North East
            (1, 0)   #East
        ]

 


        """
            top_left     = vertices[0]
            top_right    = vertices[1]
            bottom_right = vertices[2]
            bottom_left  = vertices[3]
       """
        
      
        '''
                        x  y 
                        0,-1
            -1,-1                   1, -1
                V-----V-----V-----V
                |  NW |  N  |  NE | 
                V-----V-----V-----V     
        -1,0    |  W  |  CC |  E  |     1, 0
                V-----V-----V-----V
                |  SW |  S  |  SE | 
                V-----V-----V-----V
            -1,1                    1, 1
                        0, 1
        '''


        
        for i in range(len(bottom_right_vectors)):
            if in_bounds(grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + bottom_right_vectors[i][0], grid_y + bottom_right_vectors[i][1])
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    
                    if i == 0: #East
                        n_bottom_left  = vertices[3]
                        bottom_right = n_bottom_left
                        
                    elif i == 1: #South East
                        n_top_left = vertices[0]
                        bottom_right = n_top_left
                    elif i == 2: #South
                        n_top_right  = vertices[1]
                        bottom_right = n_top_right

            

            if in_bounds(grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + bottom_left_vectors[i][0], grid_y + bottom_left_vectors[i][1])
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    if i == 0: #West
                        n_bottom_right = vertices[2]
                        bottom_left = n_bottom_right
                    elif i == 1: #South West
                        n_top_right    = vertices[1]
                        bottom_left = n_top_right
                    elif i == 2: #South
                        n_top_left     = vertices[0]
                        bottom_left = n_top_left

                    
            if in_bounds(grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + top_left_vectors[i][0], grid_y + top_left_vectors[i][1])
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]
                    if i == 0: #North
                        n_bottom_left  = vertices[3]
                        top_left = n_bottom_left
                    elif i == 1: #North West
                        n_bottom_right = vertices[2]
                        top_left = n_bottom_right
                    elif i == 2: #West
                        n_top_right    = vertices[1]
                        top_left = n_top_right

                 
                    
            if in_bounds(grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                coord_key = self.coord_to_str(grid_x + top_right_vectors[i][0], grid_y + top_right_vectors[i][1],)
                if self.pixel_coords.get(coord_key):
                    vertices = self.pixel_coords[coord_key]

                    if i == 0: #North
                        n_bottom_right  = vertices[2]
                        top_right = n_bottom_right
                    elif i == 1: #North East
                        n_bottom_left = vertices[3]
                        top_right = n_bottom_left
                    elif i == 2: #East
                        n_top_left     = vertices[0]
                        top_right = n_top_left
  

    
        return top_left, top_right, bottom_right, bottom_left  

    # draw_pixel
        # draws fake pixels whose size is determined from the width and height of the border
        # these pixels usually serve as transitory pixels before the image is updated

    def draw_pixel(self, canvas, key_coord, fill, outline, tag, borders):
   
        grid_x, grid_y = self.str_to_coord(key_coord)
        canvas.delete("lines")

        top_left_x, top_left_y = borders[0], borders[1]

        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width
        
        top_left_x = border_x + border_width  * (grid_x/self.pixel_canvas_width)
        top_left_y = border_y + border_height * (grid_y/self.pixel_canvas_height)

        bottom_right_x = top_left_x + scale
        bottom_right_y = top_left_y + scale

        bottom_left_x = top_left_x
        bottom_left_y = top_left_y + scale

        top_right_x = top_left_x + scale
        top_right_y = top_left_y 

        
        '''top_left, top_right, bottom_right, bottom_left =''' 
        top_left, top_right, bottom_right, bottom_left = self.recycle_vertices(grid_x, grid_y,
            Vertex(top_left_x, top_left_y), Vertex(top_right_x, top_right_y), Vertex(bottom_right_x, bottom_right_y),  Vertex(bottom_left_x, bottom_left_y)
        )
                                                                

        polygon = [
                    top_left.get_X(),     top_left.get_Y(),
                    top_right.get_X(),    top_right.get_Y(),
                    bottom_right.get_X(), bottom_right.get_Y(),
                    bottom_left.get_X(),  bottom_left.get_Y()  
                ]
        


        self.pixel_coords[key_coord] = [top_left, top_right, bottom_right, bottom_left]

        #print(top_left)
        #self.pixel_grid[grid_y][grid_x] = fill
        
        canvas.create_polygon(polygon,
                            fill = fill,
                            outline=outline,
                            tags=(tag)
                            )
            
    # brush_click and brush_press
        # using the approximate pixel positions calculated from the border dimension
        # a pixel coordinate is derived, placed on the image, and then the image is redrawn
        # DDA is used to fill in gaps between pixels

    def brush_click(self, x, y, canvas, color, borders, size, is_drawing):
        self.last_pixel.clear()
        canvas.delete("lasso")
        canvas.delete("lassoline")
        canvas.delete("shape")
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if size == 1:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):

                    if is_drawing:
                        self.pixel_image.putpixel((x_pixel, y_pixel), tuple(self.hex_to_rgb(color, True)))

                    else:
                        self.pixel_image.putpixel((x_pixel, y_pixel), self.blank)
            else:
                #https://note.nkmk.me/en/python-pillow-imagedraw/
                x1 = math.floor(x_pixel - size/2)
                y1 = math.floor(y_pixel - size/2)
                x2 = math.floor(x_pixel + size/2)
                y2 = math.floor(y_pixel + size/2)

                draw = ImageDraw.Draw(self.pixel_image)
                if is_drawing:
                    draw.ellipse((x1, y1, x2, y2), fill=tuple(self.hex_to_rgb(color, True)))

                else:
                    draw.ellipse((x1, y1, x2, y2), fill=self.blank)
            
            self.render_image(canvas, borders)
                
    def brush_press(self, x, y, canvas, color, borders, size, is_drawing):

        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)

            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    if size == 1:
                        if is_drawing:
                            self.pixel_image.putpixel((x_pixel, y_pixel), tuple(self.hex_to_rgb(color, True)))

                        else:
                            self.pixel_image.putpixel((x_pixel, y_pixel), self.blank)

                        if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                            between = DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])

                            for pixel in between:
            
                                if is_drawing:
                                    self.pixel_image.putpixel((pixel[0], pixel[1]), tuple(self.hex_to_rgb(color)))

                                else:
                                    self.pixel_image.putpixel((pixel[0], pixel[1]), self.blank)
                    else:
                        #https://note.nkmk.me/en/python-pillow-imagedraw/
                        x1 = math.floor(x_pixel - size/2)
                        y1 = math.floor(y_pixel - size/2)
                        x2 = math.floor(x_pixel + size/2)
                        y2 = math.floor(y_pixel + size/2)

                        draw = ImageDraw.Draw(self.pixel_image)
                        if is_drawing:
                            draw.ellipse((x1, y1, x2, y2), fill=tuple(self.hex_to_rgb(color, True)))

                        else:
                            draw.ellipse((x1, y1, x2, y2), fill=self.blank)

                        if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                            between = DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])

                            for pixel in between:
                                x1 = math.floor(pixel[0] - size/2)
                                y1 = math.floor(pixel[1] - size/2)
                                x2 = math.floor(pixel[0] + size/2)
                                y2 = math.floor(pixel[1] + size/2)

                                if is_drawing:
                                    draw.ellipse((x1, y1, x2, y2), fill=tuple(self.hex_to_rgb(color, True)))
                         
                                else:
                                    draw.ellipse((x1, y1, x2, y2), fill=self.blank)
               

                    self.render_image(canvas, borders)
                                          
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]
        
    # start_stroke and end_stroke
        # places a first pixel, keeps track of it
        # start_stroke: makes fake pixels to imply a path, until RMB is released
        # end_stroke: actually adds a pixel coordinates to the image, then updates the rendered image

    def start_stroke(self, x, y, canvas, color, borders, size):
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                if not self.is_drawing_line:
                    self.first_pixel.clear()
                 
                    self.first_pixel.append(x_pixel)
                    self.first_pixel.append(y_pixel)

                    self.is_drawing_line = True
                    #self.pixel_image.putpixel((x_pixel, y_pixel), tuple(self.hex_to_rgb(color)))
                    current_color = tuple(self.hex_to_rgb(color, True))
                    self.temp_image.putpixel((x_pixel, y_pixel), current_color)
                    #current_coord = self.coord_to_str(x_pixel, y_pixel)
                    #self.draw_pixel(canvas, current_coord, color, color, "stroke_line", borders)
                else:
                    
                    
                    canvas.delete("stroke_line")
                    #if polygon_point(self.borders, self.first_pixel[0], self.first_pixel[1]):
                    #if self.in_bounds(self.first_pixel[0], self.first_pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    current_coord = self.coord_to_str(self.first_pixel[0], self.first_pixel[1])
                    #if self.stroke_pixels:
                        #first pixel
                        #self.draw_pixel(canvas, current_coord, color, color, "stroke_line", borders) 

                    if self.first_pixel and self.last_pixel:
                        x1 = self.first_pixel[0]
                        y1 = self.first_pixel[1]
                        x2 = self.last_pixel[0]
                        y2 = self.last_pixel[1]

                        current_color = tuple(self.hex_to_rgb(color, True))
                        draw = ImageDraw.Draw(self.temp_image)
                        draw.line((x1, y1, x2, y2), fill=self.blank, width=round(size))
                        draw.line((x1, y1, x_pixel, y_pixel), fill=current_color, width=round(size))
                    
                  
                    
                    
                    self.render_image(canvas, borders)
                    self.render_temp_image(canvas, borders)
                    #self.render_image(canvas, borders)

                self.last_pixel.clear()
                if len(self.last_pixel) == 0:
                    self.last_pixel = [x_pixel, y_pixel]
                    
                    
                    
                                 
    def end_stroke(self, x, y, canvas, color, borders, size):
        #print("stroke")
        if self.is_drawing_line:
            #print("running")
            self.is_drawing_line = False
            
            
            if self.first_pixel and self.last_pixel:
                x1 = self.first_pixel[0]
                y1 = self.first_pixel[1]
                x2 = self.last_pixel[0]
                y2 = self.last_pixel[1]

                current_color = tuple(self.hex_to_rgb(color, True))
                draw = ImageDraw.Draw(self.pixel_image)
                draw.line((x1, y1, x2, y2), fill=current_color, width=round(size))

            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            canvas.update_idletasks()
            canvas.delete("stroke_line")
            self.stroke_pixels.clear()
            self.first_pixel.clear()
            self.last_pixel.clear()
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)

    # move_click, move_press, move_release
        # move_click scans the entire, image for non-transparent pixels, then stores their colors and coordinates
            # pixels and colors stored in temp_pixels and temp_colors
            # the current pixels are deleted and replaced with fake pixels made by draw_pixel method
        # move_press moves the pixels in temp_pixels and the fake pixels use the canvas.move() method  the method is used for any method that uses temp pixels
        # move_release takes the pixels and colors from temp_colors and temp_pixels and places them on the image and re-renders it

    def move_click(self, x, y, canvas, color, borders):
        #print("move")
        #
        self.last_pixel.clear()
        self.first_pixel.clear()
        if polygon_point(borders, x, y):
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            '''
            self.temp_colors.clear()
            self.temp_pixels.clear()
            self.temp_pixels = [[x, y] for y in range(len(self.pixel_grid)) for x in range(len(self.pixel_grid[y])) if self.pixel_grid[y][x]]
            self.temp_colors = [self.pixel_grid[pxl[1]][pxl[0]] for pxl in self.temp_pixels]
            '''
            self.temp_colors.clear()
            self.temp_pixels.clear()
            
            #canvas.delete("all")
            for y in range(self.pixel_canvas_height):
                for x in range(self.pixel_canvas_width):
                    if y == 0 and x == 0:
                        pass
                    rgba = self.pixel_image.getpixel((x, y))
                    if rgba[-1] != 0:
                        #print("ye")
                        current_color = self.rgb_to_hex(rgba[0], rgba[1], rgba[2])
                        current_coord = self.coord_to_str(x, y)
                        #current_color = self.pixel_grid[y][x]
                        self.pixel_image.putpixel((x, y), self.blank)
                        self.temp_image.putpixel((x, y), rgba)
                        #self.draw_pixel(canvas, current_coord, current_color, current_color, "shape", borders)
                        self.temp_pixels.append([x, y])
                        self.temp_colors.append(rgba)
                    else:
                        continue
                        
            self.render_temp_image(canvas, borders)
            self.render_image(canvas, borders)
            #x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y)

    def move_press(self, x, y, canvas, color, borders):
        #print("move")
        
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            #making sure current pixel and last pixel are in pixel coords so line_line_intersect works
            #gets deleted by render_grid
            '''
            del_coord = self.coord_to_str(x_pixel, y_pixel)
            self.draw_pixel(canvas, del_coord, "", "", "zip", borders) 
            if self.last_pixel:
                del_coord = self.coord_to_str(self.last_pixel[0], self.last_pixel[1])
                self.draw_pixel(canvas, del_coord, "", "", "zip", borders) 
            '''
            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                        
                        if self.last_pixel:
                            #strange error temp pixels forgotten
                            #print(len(self.temp_pixels))
                            
                            # https://misc.legendu.net/blog/python-pillow-image-shift/
                            # shifts image, will wrap around if it isn't chopped
                            dx, dy = x_pixel - self.last_pixel[0], y_pixel - self.last_pixel[1] 
                            self.temp_image = ImageChops.offset(self.temp_image, dx, dy)
                            
                        
                            #pixel grid coordinates
                        
                            
                            
                            for i in range(len(self.temp_pixels)):
                                pixel = self.temp_pixels[i]
                                new_px = pixel[0] + dx
                                new_py = pixel[1] + dy
                                
                                old_px = pixel[0]
                                old_py = pixel[1]

                                pixel[0] = new_px
                                pixel[1] = new_py

                                color = self.temp_colors[i]

                                if not in_bounds(old_px, old_py, self.pixel_canvas_width, self.pixel_canvas_height): 
                                    continue

                                # This is to cancel out the wrap around effect of ImageChops offset wrap-around
                                if not in_bounds(new_px, new_py, self.pixel_canvas_width, self.pixel_canvas_height): 
                                    
                                
                                    self.temp_image.putpixel((new_px % self.pixel_canvas_width, new_py % self.pixel_canvas_height), self.blank)
                                else:
                                    self.temp_image.putpixel((new_px % self.pixel_canvas_width, new_py % self.pixel_canvas_height), color)
                            
                            

                            
                            self.render_image(canvas, borders)
                            self.render_temp_image(canvas, borders)
                            #canvas.update_idletasks()
                            
            #canvas.delete("zip")
            #self.render_image(canvas, borders, self.pixel_image)
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]
 
    def move_release(self, x, y, canvas, color, borders):
        canvas.delete("lasso")
        canvas.delete("lassoline")
        canvas.delete("shape")

        #print("move")
        for i in range(len(self.temp_pixels)):
            pixel = self.temp_pixels[i]
            px = pixel[0]
            py = pixel[1]
            current_color = self.temp_colors[i]
            #print(px, py)
            if in_bounds(px, py, self.pixel_canvas_width, self.pixel_canvas_height): 
                #self.pixel_grid[py][px] = current_color
                #print("yep")
                rgba = current_color
                
                self.pixel_image.putpixel((px, py), rgba)
                #self.temp_image.putpixel((px, py), self.blank)
                current_coord = self.coord_to_str(px, py)
                current_color = self.rgb_to_hex(rgba[0], rgba[1], rgba[2])
                #self.draw_pixel(canvas, current_coord, current_color, current_color, current_coord, borders) 

        self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
        self.temp_pixels.clear()
        self.temp_colors.clear()
        self.last_pixel.clear()
        self.render_temp_image(canvas, borders)
        self.render_image(canvas, borders)

    # translate_borders
        # translates the image borders

    def translate_borders(self, x, y, canvas, color, borders):

        # the borders array
        # [
            # self.top_left.get_X(),     self.top_left.get_Y(),
            # self.top_right.get_X(),    self.top_right.get_Y(),
            # self.bottom_right.get_X(), self.bottom_right.get_Y(),
            # self.bottom_left.get_X(),  self.bottom_left.get_Y()  
        # ]
        if self.last_pixel:
            dx, dy = x - self.last_pixel[0], y - self.last_pixel[1] 
            for i in range(0, len(borders), 2):
                borders[i] = borders[i] + dx
                borders[i + 1] = borders[i + 1] + dy

        self.last_pixel.clear()
        if len(self.last_pixel) == 0:
            
            self.last_pixel = [x, y]

        self.render_image(canvas, borders)
        return borders

    # pick_color
        # gets the color of the pixel in the image 

    def pick_color(self, x, y, canvas, borders):
        #print("pick")
        if polygon_point(borders, x, y):
        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                #color_under_cursor = self.pixel_grid[y_pixel][x_pixel]
                color_under_cursor = self.pixel_image.getpixel((x_pixel, y_pixel))
                #print(color_under_cursor)
                if color_under_cursor[-1] != 0:
                    
                    return self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                    
                else:

                    return "#000000"

    # shape_click
        # this is used vefore rectangle_press, circle_press, and select
        # it initializes a rectangle, keeping track of it's origin point and it's with and height
    # shape_release
        # this method is used to place pixels and their colors from temp_colors and temp_pixels
        # it then empties these containers

    def shape_click(self, x, y, canvas, color, borders):
        #for rectangle cirdle and select
        #print("recircle")
        #self.image_pos_mouse_label.config(text = f"Image MX:{x} Image MY:{y}")
        if polygon_point(borders, x, y):
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            self.rect_x = x
            self.rect_y = y
            canvas.delete("shape")
            # create rectangle if not yet exist
            if not self.rect:
                #pass
                self.rect = canvas.create_rectangle(x, y, 1, 1, outline=color, tags=("shape")) 
    
    def shape_release(self, x, y, canvas, color, borders):
        #print("recircletemp")
        canvas.delete("lasso")
        canvas.delete("lassoline")
        canvas.delete("shape")
        
        self.pixel_image.alpha_composite(self.temp_image, (0, 0))

        self.temp_pixels.clear()
        self.temp_colors.clear()
        self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
        self.render_temp_image(canvas, borders)
        self.render_image(canvas, borders)

    # rectangle_press
        # draws a fake rectangle tracing the shape as it draws fake pixels

    def rectangle_press(self, x, y, canvas, color, borders, size):
        #print("rec")
        if polygon_point(borders, x, y):
            # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
            
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #print(f"RX {rx} RY {ry} MX {x} MY {y}")
            #if canvas.delete("shape") is put before create_rectangle the rectangle will be seen
            canvas.delete("shape")
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=color, tags=("shape"))
            
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            if not in_bounds(top_left[0], top_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(top_right[0], top_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_left[0], bottom_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_right[0], bottom_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
        
            x1 = top_left[0]
            y1 = top_left[1]
            x2 = bottom_right[0]
            y2 = bottom_right[1]

            current_color = tuple(self.hex_to_rgb(color, True))
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            draw = ImageDraw.Draw(self.temp_image)
            #draw.line((x1, y1, x2, y2), fill=self.blank, width=round(size))
            #draw.line((x1, y1, x2, y2), fill=current_color, width=round(size))
            if round(size) > 1:
                draw.rectangle((x1, y1, x2, y2), fill=current_color, outline=current_color)
                x1 = top_left[0] + round(size)
                y1 = top_left[1] + round(size)
                x2 = bottom_right[0] - round(size)
                y2 = bottom_right[1] - round(size)
                if x2 >= x1 and y2 >= y1:
                    draw.rectangle((x1, y1, x2, y2), fill=self.blank, outline=self.blank)
            else:
                draw.rectangle((x1, y1, x2, y2), fill=self.blank, outline=current_color)
            
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)

    # circle_press
        # uses the rectangle to draw a fake mid_point_ellipse


    def circle_press(self, x, y, canvas, color, borders, size):
        #print("circle")
        #midpoint mid_point_ellipse 
        # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
        if polygon_point(borders, x, y):
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #if canvas.delete("shape") is put before create_rectangle the rectangle will be seen
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=color, tags=("shape"))
            canvas.delete("shape")
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            if not in_bounds(top_left[0], top_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(top_right[0], top_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_left[0], bottom_left[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            if not in_bounds(bottom_right[0], bottom_right[1], len(self.pixel_grid[0]), len(self.pixel_grid)):
                return
            
            


            x1 = top_left[0] 
            y1 = top_left[1] 
            x2 = bottom_right[0] 
            y2 = bottom_right[1] 

            current_color = tuple(self.hex_to_rgb(color, True))
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            draw = ImageDraw.Draw(self.temp_image)
            #draw.line((x1, y1, x2, y2), fill=self.blank, width=round(size))
            #draw.line((x1, y1, x2, y2), fill=current_color, width=round(size))
            if round(size) > 1:
                draw.ellipse((x1, y1, x2, y2), fill=current_color, outline=current_color)
                x1 = math.floor(top_left[0] - size/2)
                y1 = math.floor(top_left[1] - size/2)
                x2 = math.floor(bottom_right[0] + size/2)
                y2 = math.floor(bottom_right[1] + size/2)

                x1 = top_left[0] + round(size)
                y1 = top_left[1] + round(size)
                x2 = bottom_right[0] - round(size)
                y2 = bottom_right[1] - round(size)
                if x2 >= x1 and y2 >= y1:
                    draw.ellipse((x1, y1, x2, y2), fill=self.blank, outline=self.blank)
            else:
                #draw.rectangle((x1, y1, x2, y2), fill=self.blank, outline=current_color)fill=self.blank, 
                draw.ellipse((x1, y1, x2, y2), outline=current_color)
            
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)
           

    # select
        # select_press
            # superficially mimis rectangle press, but puts all pixels within the rectangle area inside temp_colors and temp_pixels
        # select_release
            # sole purpose is to get the colors of the pixels inside temp_pixels

    def select_press(self, x, y, canvas, color, borders):
        #print("select")
        #standard rectangular select
        if polygon_point(borders, x, y):

            # expand rectangle as you drag the mouse
            # expand rectangle as you drag the mouse
            
            rw = x - self.rect_x
            rh = y - self.rect_y
            rx = self.rect_x
            ry = self.rect_y

            #
            
            
            if rw < 0:
                rx = abs(rx + rw)
                rw = abs(rw)
            if rh < 0:
                ry = abs(ry + rh)
                rh = abs(rh)

            
            #print(f"RX {rx} RY {ry} MX {x} MY {y}")
            canvas.delete("shape")
            #color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
           
            #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lassoline", borders) 
            

            
            #self.draw_pixel(canvas, left_coord, inverted_color, inverted_color, "shape", borders)
            
            
            
            #The Portions in the Box
            top_left = self.canvas_to_pixel(canvas, rx, ry, borders)
            top_right = self.canvas_to_pixel(canvas, rx + rw, ry, borders)
            bottom_left = self.canvas_to_pixel(canvas, rx, ry + rh, borders)
            bottom_right = self.canvas_to_pixel(canvas, rx + rw, ry + rh, borders)

            

            left_rect_side = DDA(
                top_left[0], top_left[1],
                bottom_left[0], bottom_left[1]
            )

            right_rect_side = DDA(
                top_right[0], top_right[1],
                bottom_right[0], bottom_right[1]
            )

            top_rect_side = DDA(
                top_left[0], top_left[1],
                top_right[0], top_right[1]
            )

            bottom_rect_side = DDA(
                bottom_left[0], bottom_left[1],
                bottom_right[0], bottom_right[1]
            )

            if self.temp_pixels:
                self.temp_pixels.clear()

            if self.temp_colors:
                self.temp_colors.clear()

            #self.draw_pixel(canvas, self.coord_to_str(top_left[0], top_left[1]), '', color, "shape", borders)
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            '''
            #bad because it even inverts the transparent pixels
            x1 = top_left[0] 
            y1 = top_left[1] 
            x2 = bottom_right[0] 
            y2 = bottom_right[1] 
            #Crop : Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
            #https://note.nkmk.me/en/python-pillow-invert/
            img_to_paste = self.pixel_image.crop((x1, y1, x2, y2)).convert("RGB")
            img_to_paste = ImageOps.invert(img_to_paste).convert("RGBA")

            self.temp_image.paste(img_to_paste, (x1, y1))
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)
            
            '''
            #going down each side as each parrellel side should be congruent
            #selecting the filled pixels, hench color_under_cursor
            #it would return either None or a Hexcode string
            #also
            
            for i in range(len(left_rect_side)):
                left_coord = self.coord_to_str(left_rect_side[i][0], left_rect_side[i][1])
                right_coord = self.coord_to_str(right_rect_side[i][0], right_rect_side[i][1])
                

                if in_bounds(left_rect_side[i][0], left_rect_side[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                    #color_under_cursor = self.pixel_grid[ left_rect_side[i][1] ][ left_rect_side[i][0] ]
                    color_under_cursor = self.pixel_image.getpixel((left_rect_side[i][0], left_rect_side[i][1]))
                    #A zero at index means the pixel is transparent
                    if color_under_cursor[-1] != 0:
                        self.temp_pixels.append(left_rect_side[i])
                        
                        #inverted_color = self.invert_color(color_under_cursor)
                        
                        color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                        inverted_color = self.invert_color(color)
                        
                        #self.draw_pixel(canvas, left_coord, inverted_color, inverted_color, "shape", borders)
                        inverted_color = self.hex_to_rgb(inverted_color, True)

                        #self.temp_colors.append(tuple(inverted_color))
                        #self.temp_image.putpixel(tuple(left_rect_side[i]), tuple(inverted_color))

                        self.temp_colors.append(color_under_cursor)
                        self.temp_image.putpixel(tuple(left_rect_side[i]),  color_under_cursor)
                    else:
                        #self.draw_pixel(canvas, left_coord, "", color, "shape", borders)
                        pass


                if in_bounds(right_rect_side[i][0], right_rect_side[i][1], self.pixel_canvas_width, self.pixel_canvas_height):
                    #color_under_cursor = self.pixel_grid[right_rect_side[i][1]][right_rect_side[i][0]]
                    color_under_cursor = self.pixel_image.getpixel((right_rect_side[i][0], right_rect_side[i][1]))
                    #A zero at index the last index is transparent
                    if color_under_cursor[-1] != 0:
                        self.temp_pixels.append(right_rect_side[i])
                        #inverted_color = self.invert_color(color_under_cursor)
                        color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                        inverted_color = self.invert_color(color)
                        #self.draw_pixel(canvas, right_coord, inverted_color, inverted_color, "shape", borders)
                        inverted_color = self.hex_to_rgb(inverted_color, True)

                        #self.temp_colors.append(tuple(inverted_color))
                        #self.temp_image.putpixel(tuple(right_rect_side[i]),  tuple(inverted_color))

                        self.temp_colors.append(color_under_cursor)
                        self.temp_image.putpixel(tuple(right_rect_side[i]),  color_under_cursor)
                    else:
                        #self.draw_pixel(canvas, right_coord, "", color, "shape", borders)
                        pass



                line_between = DDA(left_rect_side[i][0], left_rect_side[i][1], right_rect_side[i][0], right_rect_side[i][1])
                for j in range(len(line_between)):
                    coord = self.coord_to_str(line_between[j][0], line_between[j][1])


                    if in_bounds(line_between[j][0], line_between[j][1], self.pixel_canvas_width, self.pixel_canvas_height):
                        #color_under_cursor = self.pixel_grid[ line_between[j][1] ][ line_between[j][0] ]
                        color_under_cursor = self.pixel_image.getpixel((line_between[j][0], line_between[j][1]))
                        if color_under_cursor[-1] != 0:
                            self.temp_pixels.append(line_between[j])
                            color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                            inverted_color = self.invert_color(color)
                            #self.draw_pixel(canvas, coord, inverted_color, inverted_color, "shape", borders)
                            inverted_color = self.hex_to_rgb(inverted_color, True)

                            #self.temp_colors.append(tuple(inverted_color))
                            #self.temp_image.putpixel(tuple(line_between[j]),  tuple(inverted_color))

                            self.temp_colors.append(color_under_cursor)
                            self.temp_image.putpixel(tuple(line_between[j]),  color_under_cursor)
                        else:
                            #this would grid every pixel in the thing without the if
                            #as of now it just does the top and the bottom
                            if i == 0 or i == len(left_rect_side) - 1:
                                pass
                                #self.draw_pixel(canvas, coord, "", color, "shape", borders)
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)
            grid_x, grid_y = self.canvas_to_pixel(canvas, x, y, borders)
            color_under_cursor = self.pixel_image.getpixel((grid_x, grid_y))
            color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
            inverted_color = self.invert_color(color)
            self.rect = canvas.create_rectangle(rx, ry, rx + rw, ry + rh, outline=inverted_color, tags=("shape"))
           
            #could go top to bottom, but it would be 
            #repetitive as going right to left covers most of not all of the area
            
            '''
            for i in range(len(top_rect_side)):
                top_coord = self.coord_to_str(top_rect_side[i][0], top_rect_side[i][1])
                bottom_coord = self.coord_to_str(bottom_rect_side[i][0], bottom_rect_side[i][1])
                
                
                

                line_between = DDA(top_rect_side[i][0], top_rect_side[i][1], bottom_rect_side[i][0], bottom_rect_side[i][1])

                color_under_cursor = self.pixel_grid[ top_rect_side[i][1] ][ top_rect_side[i][0] ]
                if color_under_cursor:
                    self.temp_pixels.append(top_rect_side[i])
                    inverted_color = self.color_inversion(top_rect_side[i][0], top_rect_side[i][1])
                    self.draw_pixel(canvas, left_coord, '', inverted_color, "shape", borders)
                else:
                    self.draw_pixel(canvas, top_coord, '', color, "shape", borders)

                color_under_cursor = self.pixel_grid[ bottom_rect_side[i][1] ][ bottom_rect_side[i][0] ]
                if color_under_cursor:
                    self.temp_pixels.append(bottom_rect_side[i])
                    inverted_color = self.color_inversion(bottom_rect_side[i][0], bottom_rect_side[i][1])
                    self.draw_pixel(canvas, left_coord, '', inverted_color, "shape", borders)

                else:
                    self.draw_pixel(canvas, bottom_coord, '', color, "shape", borders)

                    
                
                for j in range(len(line_between)):
                    coord = self.coord_to_str(line_between[j][0], line_between[j][1])
                    #self.draw_pixel(canvas, coord, '', color, "shape", borders)
                    

                    color_under_cursor = self.pixel_grid[line_between[j][1]][line_between[j][0]]
                    if color_under_cursor:
                        self.temp_pixels.append(line_between[j])
                    #this would grid every pixel in the thing
                    #else:
                    #    self.draw_pixel(canvas, coord, "", color, "shape", borders)

                '''
    
    def select_release(self, x, y, canvas, color, borders):
        self.last_pixel.clear()


    # Lasso
        # Works by keeping track of pixels between a beginning and and end point
        # Then it fills in the pixels going from the smallest x pixel to the largest x pixel on a line
        # it adss this pixels and their colors to temp_colors and temp_pixels

    def lasso_click(self, x, y, canvas, color, borders):
        #DDA line between start and current
        #Fill in area edges

        #drawing an undecided line between two points
        self.last_pixel.clear()
        self.temp_pixels.clear()
        self.temp_colors.clear()
        self.lasso_polygon.clear()
        self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
        #self.render_borders(canvas)
        #if self.in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
        if polygon_point(borders, x, y):
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                self.lasso_polygon.extend([x, y])
                current_coord = self.coord_to_str(x_pixel, y_pixel)
                self.temp_pixels.append([x_pixel, y_pixel])
                current_color = self.pixel_image.getpixel((x_pixel, y_pixel))
                #if self.pixel_grid[y_pixel][x_pixel]:
                if current_color[-1] != 0:
                    #inverted_color = self.invert_color(self.pixel_grid[y_pixel][x_pixel])
                    #rgba = self.pixel_image.getpixel((x_pixel, y_pixel))
                    color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                    inverted_color = self.invert_color(color)
                    #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                    inverted_color = self.hex_to_rgb(inverted_color, True)

                    #self.temp_image.putpixel((x_pixel, y_pixel),  tuple(inverted_color))
                    self.temp_image.putpixel((x_pixel, y_pixel),  current_color)
                else:
                    
                    #self.draw_pixel(canvas, current_coord, "", color, "lasso", borders)
                    pass
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)
    
    def lasso_press(self, x, y, canvas, color, borders):
        #print("lasso")
        if polygon_point(borders, x, y):
            
            x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)
            if self.last_pixel != [x_pixel, y_pixel] and len(self.last_pixel) > 0:
                if in_bounds(x_pixel, y_pixel, self.pixel_canvas_width, self.pixel_canvas_height):
                    #first pixel
                    self.lasso_polygon.extend([x, y])
                    current_coord = self.coord_to_str(x_pixel, y_pixel)

                    current_color = self.pixel_image.getpixel((x_pixel, y_pixel))
                    #self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
                    #if self.pixel_grid[y_pixel][x_pixel]:
                    if current_color[-1] != 0:
                        #inverted_color = self.invert_color(self.pixel_grid[y_pixel][x_pixel])
                        #rgba = self.pixel_image.getpixel((x_pixel, y_pixel))
                        color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                        inverted_color = self.invert_color(color)
                        #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                        inverted_color = self.hex_to_rgb(inverted_color, True)

                        #self.temp_image.putpixel((x_pixel, y_pixel),  tuple(inverted_color))
                        #self.temp_image.putpixel((x_pixel, y_pixel),  current_color)
                    else:
                        #self.draw_pixel(canvas, current_coord, "", color, "lasso", borders) 
                        pass
                        
                    canvas.delete("lasso")
                    canvas.delete("lassoline")
                    #beginning to end line
                    for pixel in self.stroke_pixels:
                        px = pixel[0]
                        py = pixel[1]
                        current_coord = self.coord_to_str(pixel[0], pixel[1])
                        
                    if self.temp_pixels:
                        self.stroke_pixels = DDA(self.temp_pixels[0][0], self.temp_pixels[0][1], self.temp_pixels[-1][0], self.temp_pixels[-1][1])
                        for pixel in self.stroke_pixels:
                            current_coord = self.coord_to_str(pixel[0], pixel[1])
                            current_color = self.pixel_image.getpixel((pixel[0], pixel[1]))
                            #if self.pixel_gridpixel[1]][pixel[0]]:
                            if current_color[-1] != 0:
                                #inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                                #rgba = self.pixel_image.getpixel((x_pixel, y_pixel))
                                color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                                inverted_color = self.invert_color(color)
                                #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lassoline", borders)
                                inverted_color = self.hex_to_rgb(inverted_color, True)

                                #self.temp_image.putpixel((x_pixel, y_pixel),  tuple(inverted_color))
                                #self.temp_image.putpixel((x_pixel, y_pixel),  current_color)
                            else:
                                #self.draw_pixel(canvas, current_coord, "", color, "lassoline", borders)
                                pass

                        #draw drag
                        if x_pixel >= 0 and y_pixel >= 0 and x_pixel < self.pixel_canvas_width and y_pixel < self.pixel_canvas_height:
                            between = DDA(x_pixel, y_pixel, self.last_pixel[0], self.last_pixel[1])
                            for pixel in between:
                                #print("X Pixel:{} Y Pixel:{}".format(x_pixel, y_pixel))
                                #hexadecimal [1] rbg [0] red [0][0] green [0][1] blue [0][2]
                                #self.pixel_grid[pixel[1]][pixel[0]] = color     
                                self.temp_pixels.append([pixel[0], pixel[1]])
                                current_coord = self.coord_to_str(pixel[0], pixel[1])
                                current_color = self.pixel_image.getpixel((pixel[0], pixel[1]))
                                #if self.pixel_gridpixel[1]][pixel[0]]:
                                if current_color[-1] != 0:
                                    #inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                                    #rgba = self.pixel_image.getpixel((x_pixel, y_pixel))
                                    color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                                    inverted_color = self.invert_color(color)
                                    #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lassoline", borders) 
                                    inverted_color = self.hex_to_rgb(inverted_color, True)

                                    #self.temp_image.putpixel((x_pixel, y_pixel),  tuple(inverted_color))
                                    #self.temp_image.putpixel((x_pixel, y_pixel),  current_color)
                                else:
                                    #self.draw_pixel(canvas, current_coord, "", color, "lassoline", borders) 
                                    pass
                                    
                        self.render_image(canvas, borders)
                        self.render_temp_image(canvas, borders)
                    
                    grid_x, grid_y = self.canvas_to_pixel(canvas, x, y, borders)
                    color_under_cursor = self.pixel_image.getpixel((grid_x, grid_y))
                    color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                    inverted_color = self.invert_color(color)
                    canvas.create_polygon(
                        self.lasso_polygon,
                        fill = '',
                        outline = inverted_color,
                        tag = ("lasso")
                    )
            #canvas.delete("lassoline")
                            
            self.last_pixel.clear()
            if len(self.last_pixel) == 0:
                self.last_pixel = [x_pixel, y_pixel]
         
    def lasso_release(self, x, y, canvas, color, borders):
        #print("lasso")
        if self.temp_pixels:
           
            #print(self.temp_pixels)
            #drawing a line between the beginning and end pixel
            self.temp_pixels.extend(self.stroke_pixels)
            #sorting by y coordinate
            self.temp_pixels = sorted(self.temp_pixels, key=lambda pair: pair[1])
            #print(self.temp_pixels)
            lines = []
            i = 0
            j = 0
            #getting the coordinates of the empty space in in the lasso
            while j < len(self.temp_pixels):
                #detects when y changes and makes a line between the coordinate with smallest x value and the largest. 
                if self.temp_pixels[i][1] != self.temp_pixels[j][1]:
                    lines.extend([self.temp_pixels[i]] + DDA(self.temp_pixels[i][0], self.temp_pixels[i][1], self.temp_pixels[j - 1][0], self.temp_pixels[j - 1][1]))
                    i = j

                    
                j = j + 1

            
            

            #filling out the missed spots
            filled_pixels = []
            self.temp_pixels.extend(lines)
            for pixel in self.temp_pixels:
                if in_bounds(pixel[0] , pixel[1], self.pixel_canvas_width, self.pixel_canvas_height):
                    current_coord = self.coord_to_str(pixel[0], pixel[1])
                    #color_under_cursor = self.pixel_grid[ pixel[1] ][ pixel[0] ]
                    color_under_cursor = self.pixel_image.getpixel((pixel[0], pixel[1]))
                    #if color_under_cursor:
                    if color_under_cursor[-1] != 0:
                        if pixel not in filled_pixels:
                            filled_pixels.append(pixel)
                            #inverted_color = self.invert_color(self.pixel_grid[pixel[1]][pixel[0]])
                            #rgba = self.pixel_image.getpixel((pixel[0], pixel[1]))
                            color = self.rgb_to_hex(color_under_cursor[0], color_under_cursor[1], color_under_cursor[2])
                            inverted_color = self.invert_color(color)
                            #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders) 
                            inverted_color = self.hex_to_rgb(inverted_color, True)

                            #self.temp_image.putpixel((pixel[0], pixel[1]),  tuple(inverted_color))
                            self.temp_image.putpixel((pixel[0], pixel[1]),  color_under_cursor)
                    
                    #this was to show all the pixels in temp pixels
                    #self.draw_pixel(canvas, self.coord_to_str(pixel[0], pixel[1]), "", color, "lasso", borders) 
            
            self.temp_pixels = filled_pixels
 
            
            #self.temp_colors = [self.pixel_grid[pxl[1]][pxl[0]] for pxl in self.temp_pixels]
            self.temp_colors = [self.temp_image.getpixel((pxl[0], pxl[1])) for pxl in self.temp_pixels]
            self.last_pixel.clear()
            self.stroke_pixels.clear()
            canvas.create_polygon(
                self.lasso_polygon,
                fill = '',
                outline = color,
                tag = ("lasso")
            )
            self.lasso_polygon.clear()
            #self.pixel_grid[y_pixel][x_pixel] = color
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)

    # select_move_click
        # temp_colors and temp_pixels should be filled with , after their released and their pixels moved accordingly
        # this methods is used by lasso, select, and wand_click to move the pixels selected by them

    def select_move_click(self, x, y, canvas, color, borders):
        #print("selectmove")
        if polygon_point(borders, x, y):
            canvas.delete("lasso")
            canvas.delete("lassoline")
            canvas.delete("shape")
            self.lasso_polygon.clear()
            self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
            #so it just doesn't duplicate pixels
            for i in range(len(self.temp_pixels)):
                pixel = self.temp_pixels[i]        
                px = pixel[0]
                py = pixel[1] 
                current_coord = self.coord_to_str(px, py)
                #canvas.delete(current_coord) 
                current_color = self.temp_colors[i] #self.pixel_image.getpixel((pixel[0], pixel[1]))
                #if current_color:
                if current_color[-1] != 0:
                    #inverted_color = self.invert_color(current_color)
                    #rgba = self.pixel_image.getpixel((pixel[0], pixel[1]))
                    
                    color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                    inverted_color = self.invert_color(color)
                    inverted_color = self.hex_to_rgb(inverted_color, True)
                    #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "shape", borders)
                    #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "shape", borders)
                    self.pixel_image.putpixel((px, py), self.blank)

                    #self.temp_image.putpixel((px, py), current_color)
                    self.temp_image.putpixel((px, py), tuple(inverted_color))
                    self.temp_colors[i] = tuple(inverted_color)
                    #self.pixel_grid[py][px] = None
                    #current_coord = self.coord_to_str(px, py)
                    #if self.pixel_coords.get(current_coord):
                    #    del self.pixel_coords[current_coord]
            self.render_image(canvas, borders)
            self.render_temp_image(canvas, borders)
   
            self.render_image(canvas, borders)
            canvas.tag_raise("shape")

    def select_move_release(self, x, y, canvas, color, borders):

        for i in range(len(self.temp_pixels)):
            pixel = self.temp_pixels[i]
            if not in_bounds(pixel[0], pixel[1], self.pixel_canvas_width, self.pixel_canvas_height): 
                print("hit bounds")
                continue
            coord = self.coord_to_str(pixel[0], pixel[1])
            current_color = self.temp_colors[i]
            if len(self.temp_colors) == 0:
                #print("L")
                #self.pixel_grid[pixel[1]][pixel[0]] = color
                current_color = self.pixel_image.getpixel((pixel[0], pixel[1]))
                color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                inverted_color = self.invert_color(color)
                #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                inverted_color = self.hex_to_rgb(inverted_color, True)
                self.temp_image.putpixel((pixel[0], pixel[1]),  tuple(inverted_color))
                #self.pixel_image.putpixel((pixel[0], pixel[1]), tuple(self.hex_to_rgb(color, True)))
                #self.draw_pixel(canvas, coord, color, color, coord, borders)
            else:
                #print("O")
                #self.pixel_grid[pixel[1]][pixel[0]] = self.temp_colors[i]
                #self.pixel_image.putpixel((pixel[0], pixel[1]), self.temp_colors[i])
                color = self.rgb_to_hex(current_color[0], current_color[1], current_color[2])
                inverted_color = self.invert_color(color)
                #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, "lasso", borders)
                inverted_color = self.hex_to_rgb(inverted_color, True)
                self.temp_image.putpixel((pixel[0], pixel[1]),  tuple(inverted_color))
                #current_color = self.rgb_to_hex(self.temp_colors[i][0], self.temp_colors[i][1], self.temp_colors[i][2])
                #self.draw_pixel(canvas, coord, current_color, current_color, coord, borders)

        self.pixel_image.alpha_composite(self.temp_image, (0, 0))
 

        self.temp_pixels.clear()
        self.temp_colors.clear()
        self.temp_image = Image.new("RGBA", (self.pixel_canvas_width, self.pixel_canvas_height), self.blank)
        self.render_temp_image(canvas, borders)
        self.render_image(canvas, borders)
        

    # wand_click
        # uses breadth first search (BFS) to collect all the pixels of a certain color
        # these values are added to temp_pixels and temp_colors

    def wand_click(self, x, y, canvas, color, borders):
        if not polygon_point(borders, x, y):
            return
            
        self.temp_colors.clear()
        self.temp_pixels.clear()
        
        border_x = borders[0]
        border_y = borders[1]
        border_width = borders[4] - borders[0]
        border_height = borders[5] - borders[1]
        true_pixel_width = border_width/self.pixel_canvas_width
        true_pixel_height = border_height/self.pixel_canvas_height
        scale = true_pixel_width

        x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)

        rgba = self.pixel_image.getpixel((x_pixel, y_pixel))
        
        color_tuple = rgba

        #only selecting not transparent colors
        if rgba[-1] == 0:
            return

        color_under_cursor = self.rgb_to_hex(rgba[0], rgba[1], rgba[2])
        #BFS flood fill
        #queue
        print("W:{} H:{} X:{} Y:{} XPix:{} YPix:{}".format(self.canvas_width, self.canvas_height , x, y, x_pixel, y_pixel))
        visited = set()
        queue = []
        queue.append((x_pixel, y_pixel))
        
        self.pixel_grid = self.pil_image_to_grid()
        #print(queue)
      
        i = 0
        max_area = 48 * 48
        while queue and len(visited) < max_area:
            #print(queue)
            
            
            #print("inside")
            cur = queue.pop(0)
            rgba = (0, 0, 0, 0)
            try:
                rgba = self.pixel_image.getpixel((cur[0], cur[1]))
            except:
                rgba = (0, 0, 0, 0)

            if not in_bounds(cur[0], cur[1], self.pixel_canvas_width, self.pixel_canvas_height) or rgba != color_tuple or (cur[0], cur[1]) in visited: 
                continue
            else:

                current_coord = self.coord_to_str(cur[0], cur[1])


                if (cur[0] + 1, cur[1]) not in visited:
                    queue.append((cur[0] + 1, cur[1]))

                if (cur[0] - 1, cur[1]) not in visited:
                    queue.append((cur[0] - 1, cur[1]))

                if (cur[0], cur[1] + 1) not in visited:
                    queue.append((cur[0], cur[1] + 1))

                if (cur[0], cur[1] - 1) not in visited:
                    queue.append((cur[0], cur[1] - 1))

        
                
                if (cur[0], cur[1]) not in visited:
                    if rgba[-1] != 0:
                        if rgba == color_tuple:
                            
                            inverted_color = self.invert_color(self.rgb_to_hex(rgba[0], rgba[1], rgba[2]))
                            #self.draw_pixel(canvas, current_coord, inverted_color, inverted_color, current_coord, borders) 
                            inverted_color = self.hex_to_rgb(inverted_color, True)
                            self.temp_image.putpixel((cur[0], cur[1]),  rgba)
                            self.temp_pixels.append([cur[0], cur[1]])
                            self.temp_colors.append(rgba)
                            

                #if (cur[0], cur[1]) not in visited:
                visited.add((cur[0], cur[1]))

                
                #canvas.update_idletasks()
            
                #print(i, self.color, cur)
                #i += 1

        self.pixel_grid = [[None] * self.pixel_canvas_width for _ in range(self.pixel_canvas_height)]
        self.render_image(canvas, borders)
        self.render_temp_image(canvas, borders)
        visited.clear()

    # bucket fill
        # fills the empty pixels of the image use BFS

    def bucket_fill(self, x, y, canvas, color, borders):
        #an edited version of the flood fill

        if not polygon_point(borders, x, y):
            return
        
     
        x_pixel, y_pixel = self.canvas_to_pixel(canvas, x, y, borders)

  

        #print("W:{} H:{} X:{} Y:{} XPix:{} YPix:{}".format(self.canvas_width, self.canvas_height , x, y, x_pixel, y_pixel))
        visited = set()
        queue = []
        queue.append((x_pixel, y_pixel))
        
        #print(queue)
        ImageDraw.floodfill(self.pixel_image, (x_pixel, y_pixel), tuple(self.hex_to_rgb(color, True)), thresh=50)
        im_width, im_height = self.pixel_image.size
        self.render_image(canvas, borders)
        


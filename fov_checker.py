from math import pi
from math import tan
from math import cos
from math import sin
from math import atan
from math import degrees
from math import sqrt

import cv2
import numpy as np
import tkinter as tk
from edge import Edge
## Constants ##

MAX_NUM_INF = 1e9
WINDOW_BIAS_PERCENTAGE = 30
ROOM_LINE_BIAS_PERCENTAGE = 20
POLY_LINE_BIAS_PERCENTAGE = 30 


# HFOV claim 120 but test 90
# VHOV measured as 52
HFOV = 90
VFOV = 52

H_HFOV = HFOV/2
H_VFOV = VFOV/2

WINDOW_NAME = 'FOV Checker'

# the default value for maximum distance for VFOV
# when camera placement degree smaller than VHOV/2, should always use this value
MAX_V_DISTANCE=1500


# configurable variables

# if cam face horizontal, face_vdeg=0, if cam face down to floor, face_vdeg=90
# valid range: 0 <= cam_face_vdeg <= 90
cam_face_vdeg = 0
# cam_height: camera placement height. valid range: 180 ~ 300
cam_height = 250

# global variables
room_width = 10.0
room_height = 10.0




## functions ## 
def nothing(pos):
    pass

def cal_v_max_distance(height,facedeg,v_fov):
    max_d = height * (tan( (90- (facedeg - v_fov)) *pi/180 )) 
    return round(max_d/100,1)


def cal_v_min_distance(height,facedeg,v_fov): 
    min_d = height * (tan( (90- (facedeg + v_fov))*pi/180 ))
    return  round(min_d/100,1)


def cal_h_distance(v_distance,h_fov,cam_height_cm):
    cam_height_m = cam_height_cm/100
    distance = sqrt((v_distance**2 + cam_height_m**2))
    hor_distance = 2* distance * tan(h_fov*pi/180)
    return round(hor_distance,1)



def window_init(window_name):
    ''' initiate the parameters of the trackbar in the window:
        window_init('foc_chker')     

    Args:
        window_name (str): the name of the trackbar window

        CamFacVDeg (str): the vertical camera face degree. valid range: 0-90 degree
        CamFacHDeg (str): the horizontal camera face degree. valid range: 0-180 degree
        CamLoc_H (str): the height to set the camera. valid range: 150-300 cm
        CamLoc_W (str): the width to set the camera. valid range: 0 - room_width*100 cm
        Person_H (str): the height of the human. To check the range we can see whole human.
                      valid range: 130-200 cm


    Returns:
        bool: The return value. True for success, False otherwise.

    '''                  

    global room_width

    # create window
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)#WINDOW_AUTOSIZE, WINDOW_NORMAL
    cv2.createTrackbar('CamFacVDeg', window_name, 0, 90, nothing)
    cv2.createTrackbar('CamFacHDeg', window_name, 0, 180, nothing)    
    cv2.createTrackbar('CamLoc_H', window_name, 0, 300, nothing)
    cv2.createTrackbar('CamLoc_W', window_name, 0, int(room_width*100), nothing)
    cv2.createTrackbar('Person_H', window_name, 0, 200, nothing)

    # set default value
    cv2.setTrackbarPos('CamFacVDeg', window_name, 45)
    cv2.setTrackbarPos('CamFacHDeg', window_name, 90)    
    cv2.setTrackbarPos('CamLoc_H', window_name, 250)
    cv2.setTrackbarPos('CamLoc_W', window_name, int(room_width*100/2))
    cv2.setTrackbarPos('Person_H', window_name, 180)

    return True    


def get_trackbar_values(window_name):
    ''' get_trackbar_values('foc_chker')

    Args:
        window_name (str): the window_name which you create by window_init()

    Returns:
        face_vdeg (int): the vertical camera face degree. valid range: 0-90 degree
        face_hdeg (int): the horizontal camera face degree. valid range: 0-180 degree        
        cam_height (int): the height to set the camera. valid range: 150-300 cm
        cam_width  (int): the width to set the camera. valid range: 0- room_width  cm
        p_height (int): the height of the human. To check the range we can see whole human.
                        valid range: 130-200 cm


    '''

    face_vdeg = cv2.getTrackbarPos('CamFacVDeg', window_name)
    face_hdeg = cv2.getTrackbarPos('CamFacHDeg', window_name)    
    cam_height = cv2.getTrackbarPos('CamLoc_H', window_name)
    cam_width = cv2.getTrackbarPos('CamLoc_W', window_name)
    p_height = cv2.getTrackbarPos('Person_H', window_name)
    return face_vdeg,face_hdeg,cam_height,cam_width,p_height


def cal_theorical_min_max_distance(face_vdeg,height,half_vfov,half_hfov):
    '''calculate the visible range with camera placement height.
       The range is defined with intersection with horizon

    Args:
        face_vdeg (int): the vertical camera face degree. valid range: 0-90 degree
        height (int): the height to set the camera. valid range: 150-300 cm
        half_vfov (float): the half of camera vertical FOV. valid range: 0-180 degree
        half_hfov (float): the half of camera horizontal FOV. valid range: 0-180 degree

    Returns:
        min_v_distance (float/str): the minimum visible vertical distance of camera. valid range: 0-Inf
        max_v_distance (float/str): the maximum visible vertical distance of camera. valid range: 0-Inf
        min_h_distance (float/str): the minimum visible horizontal distance of camera. valid range: 0-Inf
        max_h_distance (float/str): the minimum visible horizontal distance of camera. valid range: 0-Inf

    '''    

    #check max and min distance condition
    #max cant measure condition
    if face_vdeg <= half_vfov:
        max_v_distance = 'Inf'
        min_v_distance = cal_v_min_distance(height,face_vdeg,half_vfov) 

        max_h_distance = 'Inf'
        min_h_distance = cal_h_distance(min_v_distance,half_hfov,height)

    # min can't measure condition
    elif face_vdeg+ half_vfov > 90 :
        max_v_distance = cal_v_max_distance(height,face_vdeg,half_vfov)  
        min_v_distance = 0

        max_h_distance = cal_h_distance(max_v_distance,half_hfov,height)
        min_h_distance = cal_h_distance(min_v_distance,half_hfov,height)

    # normal condition (camera basically face down )
    else:
        max_v_distance = cal_v_max_distance(height,face_vdeg,half_vfov)
        min_v_distance = cal_v_min_distance(height,face_vdeg,half_vfov)
        max_h_distance = cal_h_distance(max_v_distance,half_hfov,height)
        min_h_distance = cal_h_distance(min_v_distance,half_hfov,height)
    return min_v_distance, max_v_distance, min_h_distance, max_h_distance   


def cal_min_max_distance_with_human_height(p_height, height,min_v_distance, max_v_distance, face_vdeg, half_vfov,half_hfov):

    '''calculate the visible range with camera placement height and consider human height.
       The range is defined with intersection with horizon

    Args:
        p_height (int): human height. valid range: 100-200 cm
        height (int): the height to set the camera. valid range: 150-300 cm
        min_v_distance (float/str): the minimum visible vertical distance of camera. valid range: 0-Inf
        max_v_distance (float/str): the maximum visible vertical distance of camera. valid range: 0-Inf        
        face_vdeg (int): the vertical camera face degree. valid range: 0-90 degree
        half_vfov (float): the half of camera vertical FOV. valid range: 0-180 degree
        half_hfov (float): the half of camera horizontal FOV. valid range: 0-180 degree

    Returns:
        min_v_distance_person (float): the minimum visible vertical distance of camera. valid range: 0-Inf,Invalid
        max_v_distance_person (float): the maximum visible vertical distance of camera. valid range: 0-Inf,Invalid

    Notes:
        when max_v_distance_person < min_v_distance_person, both will return 'Invalid'       

    '''  

    # add person condition here 
    # camera higher than person, only change max distance 
    if p_height < height:
        min_v_distance_person = min_v_distance
        min_h_distance_person = cal_h_distance(min_v_distance_person,half_hfov,height)

        if face_vdeg <= half_vfov:
            max_v_distance_person = 'Inf'
            max_h_distance_person = 'Inf'
        else:    
            max_v_distance_person = round(max_v_distance - ((max_v_distance/height)*p_height),1)
            max_h_distance_person = cal_h_distance(max_v_distance_person,half_hfov,height)

        # check if max is larger than min distance
        if (type(max_v_distance_person ) ==float) & (type(min_v_distance_person) == float):
            if max_v_distance_person < min_v_distance_person:
                max_v_distance_person = min_v_distance_person = 'Invalid'
                max_h_distance_person = min_h_distance_person = 'Invalid'


    elif p_height == height:
        if face_vdeg <= half_vfov:
            max_v_distance_person = 'Inf'
            max_h_distance_person = 'Inf'

            min_v_distance_person = min_v_distance
            min_h_distance_person = cal_h_distance(min_v_distance_person,half_hfov,height)


        else:
            max_v_distance_person = min_v_distance_person = 'Invalid'
            max_h_distance_person = min_h_distance_person = 'Invalid'
            

    # camera lower than person, only change min distance
    else:
        if face_vdeg < half_vfov:
            min_v_distance_person = round((p_height-height)/tan((half_vfov-face_vdeg)*pi/180),1)
            min_h_distance_person = cal_h_distance(min_v_distance_person,half_hfov,height)

            max_v_distance_person = 'Inf'
            max_h_distance_person = 'Inf'
        else:
            max_v_distance_person = min_v_distance_person = 'Invalid'
            max_h_distance_person = min_h_distance_person = 'Invalid'

    return min_v_distance_person, max_v_distance_person, min_h_distance_person, max_h_distance_person     


def get_distance_color(distance):
    ''' get the color of the string of distance.

    Args:
        distance (float/str): 0-Infinite,'Inf','Invalid'

    Returns:
        color (set): (B,G,R) of the color. each value should be 0-255

    '''

    if distance == 'Inf':
        # color is green for Infinite
        color = (0,255,0)
    elif distance == 'Invalid':
        #color is red for Invalid
        color = (0,0,255)    
    else:
        # color is white in normal case
        color = (255,255,255)
    return color        


def set_min_max_distance_colormap(max_v_distance,min_v_distance,max_h_distance,min_h_distance,max_v_distance_person,min_v_distance_person,max_h_distance_person,min_h_distance_person):

    max_v_color = get_distance_color(max_v_distance)
    min_v_color = get_distance_color(min_v_distance)
    max_h_color = get_distance_color(max_h_distance)
    min_h_color = get_distance_color(min_h_distance)
    max_v_person_color = get_distance_color(max_v_distance_person)
    min_v_person_color = get_distance_color(min_v_distance_person)
    max_h_person_color = get_distance_color(max_h_distance_person)
    min_h_person_color = get_distance_color(min_h_distance_person)

    return max_v_color, min_v_color, max_h_color, min_h_color, max_v_person_color, min_v_person_color, max_h_person_color, min_h_person_color


def intersect(polygon1, polygon2):
    """
    The given polygons must be convex and their vertices must be in anti-clockwise order (this is not checked!)
    Example: polygon1 = [[0,0], [0,1], [1,1]]
    """
    polygon3 = list()
    polygon3.extend(_get_vertices_lying_in_the_other_polygon(polygon1, polygon2))
    polygon3.extend(_get_edge_intersection_points(polygon1, polygon2))
    return _sort_vertices_anti_clockwise_and_remove_duplicates(polygon3)


def _get_vertices_lying_in_the_other_polygon(polygon1, polygon2):
    vertices_lying_in_the_other_polygon = list()
    for corner in polygon1:
        if _polygon_contains_point(polygon2, corner):
            vertices_lying_in_the_other_polygon.append(corner)
    for corner in polygon2:
        if _polygon_contains_point(polygon1, corner):
            vertices_lying_in_the_other_polygon.append(corner)
    return vertices_lying_in_the_other_polygon


def _get_edge_intersection_points(polygon1, polygon2):
    intersection_points = list()
    for i in range(len(polygon1)):
        edge1 = Edge(polygon1[i-1], polygon1[i])
        for j in range(len(polygon2)):
            edge2 = Edge(polygon2[j-1], polygon2[j])
            intersection_point = edge1.get_intersection_point(edge2)
            if intersection_point is not None:
                intersection_points.append(intersection_point)
    return intersection_points


def _polygon_contains_point(polygon, point):
    for i in range(len(polygon)):
        a = np.subtract(polygon[i], polygon[i-1])
        b = np.subtract(point, polygon[i-1])
        # why
        if np.cross(a,b) < 0:
            return False
    return True


def _sort_vertices_anti_clockwise_and_remove_duplicates(polygon, tolerance=1e-7):
    polygon = sorted(polygon, key=lambda p: _get_angle_in_radians(_get_inner_point(polygon), p))

    def vertex_not_similar_to_previous(polygon, i):
        diff = np.subtract(polygon[i-1], polygon[i])
        return i==0 or np.linalg.norm(diff, np.inf) > tolerance

    return [p for i, p in enumerate(polygon) if vertex_not_similar_to_previous(polygon, i)]

def _get_angle_in_radians(p1, p2):
    return np.arctan2(p2[1]-p1[1], p2[0]-p1[0])


def _get_inner_point(polygon):
    x_coords = [p[0] for p in polygon]
    y_coords = [p[1] for p in polygon]
    return [(np.max(x_coords)+np.min(x_coords)) / 2.,(np.max(y_coords)+np.min(y_coords)) / 2.]


def get_visible_range_points_in_room (rotate_polygon,room_polygon,intersection_polygon):
    # keep the points in the room of the rotate_polygon 
    rotate_polygon_in_room_list = []
    for point in rotate_polygon:
        if _point_in_polygon(point,room_polygon):
            rotate_polygon_in_room_list.append(point)

    # keep the room point which is in the rotate_polygon
    room_point_in_rotate_polygon_list = []
    for point in room_polygon:
        if _point_in_polygon(point,rotate_polygon):
            room_point_in_rotate_polygon_list.append(point)       



    # keep the points in the rotate_polygon of the room

    rotate_final_list = []
    rotate_final_list.extend(rotate_polygon_in_room_list)
    rotate_final_list.extend(room_point_in_rotate_polygon_list)
    rotate_final_list.extend(intersection_polygon)
    rotate_final_list=_sort_vertices_anti_clockwise_and_remove_duplicates(rotate_final_list)

    return rotate_final_list

def _point_in_polygon(point,polygon):
    point_x , point_y = point[0], point[1]
    pos_cnt = neg_cnt = 0
    num_poly = len(polygon)
    for i in range(num_poly):
        poly1_x = polygon[i][0]
        poly1_y = polygon[i][1]
        poly2_x = polygon[i-1][0]
        poly2_y = polygon[i-1][1]
        result = ( point_y - poly1_y ) * (poly2_x - poly1_x) - (point_x - poly1_x) * (poly2_y - poly1_y)
        
        if result >0: # point lies on left of the polygon
            pos_cnt +=1
        elif result <0: # point lies on right of the polygon 
            neg_cnt +=1
        else:
            pass        
    # all in same direction indicates point out of the polygon
    if (pos_cnt == num_poly) or (neg_cnt == num_poly):
        return True
    else:
        return False 


class TkApp:
    def __init__(self, master):
        self.master = master
        master.title("Room Parameter Controller")

        self.canvas1 = tk.Canvas(master, width = 600, height = 400)
        self.canvas1.pack()
        self.label1 = tk.Label(master, text='Input Room Width (0.0 - 30.0) m ')
        self.canvas1.create_window(200, 25, window=self.label1)
        self.entry1 = tk.Entry (master) 
        self.canvas1.create_window(400, 25, window=self.entry1)
        self.label2 = tk.Label(master, text='Input Room Height (0.0 - 30.0) m ')
        self.canvas1.create_window(200, 50, window=self.label2)
        self.entry2 = tk.Entry (master) 
        self.canvas1.create_window(400, 50, window=self.entry2)

        self.label3 = tk.Label(master, text= '')
        self.canvas1.create_window(300, 200, window=self.label3)
        self.label4 = tk.Label(master, text= '')
        self.canvas1.create_window(300, 250, window=self.label4)


        self.button1 = tk.Button(text='Start Calculate', command=self.check_width_height_value)
        self.canvas1.create_window(300, 100, window=self.button1)


    def check_width_height_value (self):  
        global room_width, room_height
        room_width = self.entry1.get()
        room_height = self.entry2.get()

        room_width_str = ''
        room_height_str = ''
        room_width_valid = False
        room_height_valid = False

        try: 
            if (float(room_width)<=30.0) & ((float(room_width)>=0.0)):
                room_width_str = 'The room_width is '+room_width
                room_width_valid = True
                room_width = float(room_width)
            else:
                room_width_str = 'Error range for room_width! please key the value in 0.0-30.0'
        except ValueError:
                room_width_str = 'Please input float number for room_width!! , type it again'

        self.label3.configure(text=room_width_str)

        try: 
            if (float(room_height)<=30.0) & ((float(room_height)>=0.0)):
                room_height_str  ='The room_height is ' +room_height
                room_height_valid = True
                room_height = float(room_height)
            else:
                room_height_str = 'Error range for room_height! please key the value in 0.0-30.0'
        except ValueError:
                room_height_str = 'Please input float number for room_height!! , type it again'

        self.label4.configure(text=room_height_str)


        if room_width_valid & room_height_valid:
            self.master.destroy()


# main thread
if __name__ == '__main__':

    # create Tk window to let user input room size
    root = tk.Tk()
    my_gui = TkApp(root)
    root.mainloop()

    # Create window and setup the initial values of the trackbar in window
    window_init(WINDOW_NAME)

    while (True):
        base_img = np.zeros((400,1400,3))

        # read back trackbar values (face_vdeg, face_hdeg, height, width, p_height)
        face_vdeg, face_hdeg, height, width, p_height =  get_trackbar_values(WINDOW_NAME)

        # Calculate the theorical range of the camera visible area
        min_v_distance ,max_v_distance, min_h_distance, max_h_distance = cal_theorical_min_max_distance(
            face_vdeg,
            height,
            H_VFOV,
            H_HFOV)

        # Calculate the range consider with human height
        min_v_distance_person, max_v_distance_person,min_h_distance_person, max_h_distance_person = cal_min_max_distance_with_human_height(
            p_height,
            height,
            min_v_distance,
            max_v_distance,
            face_vdeg,
            H_VFOV,
            H_HFOV)

        # Get the color of each distance
        max_v_color, min_v_color, max_h_color, min_h_color, max_v_person_color, min_v_person_color, max_h_person_color, min_h_person_color = set_min_max_distance_colormap(
            max_v_distance,
            min_v_distance,
            max_h_distance,
            min_h_distance,
            max_v_distance_person,
            min_v_distance_person,
            max_h_distance_person,
            min_h_distance_person)

        cv2.putText(base_img, f'Horizontal FOV: {HFOV} degree, Vertical FOV: {VFOV} degree', (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(base_img, f'==== Before Consider human height ====', (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the max vertical distance is {max_v_distance} m', (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, max_v_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the min vertical distance is {min_v_distance} m', (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, min_v_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the max horizontal distance is {max_h_distance} m', (20,180), cv2.FONT_HERSHEY_SIMPLEX, 0.75, max_h_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the min horizontal distance is {min_h_distance} m', (20,220), cv2.FONT_HERSHEY_SIMPLEX, 0.75, min_h_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'==== After Consider human height ====', (600,60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,155,255), 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the max vertical distance is {max_v_distance_person} m', (600,100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, max_v_person_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the min vertical distance is {min_v_distance_person} m', (600,140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, min_v_person_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the max horizontal distance is {max_h_distance_person} m', (600,180), cv2.FONT_HERSHEY_SIMPLEX, 0.75, max_h_person_color, 1, cv2.LINE_AA)
        cv2.putText(base_img, f'the min horizontal distance is {min_h_distance_person} m', (600,220), cv2.FONT_HERSHEY_SIMPLEX, 0.75, min_h_person_color, 1, cv2.LINE_AA)
        # Start to calculate visible range for coordinate point

        cam_x_pos =  width/100 # x position in m
        cam_y_pos =  room_height
        left_top_add_en = 0
        right_top_add_en = 0


        ## Greg test

        #change value for Inf to MAX_NUM_INF
        if min_v_distance == 'Inf':
            min_v_distance = MAX_NUM_INF
        if min_h_distance == 'Inf':
            min_h_distance = cal_h_distance(min_v_distance,H_HFOV,height)
        if max_v_distance == 'Inf':
            max_v_distance = MAX_NUM_INF
        if max_h_distance == 'Inf':
            max_h_distance = cal_h_distance(max_v_distance,H_HFOV,height)

        # user chosen camera face horizontal degree
        # face_hdeg       : 0    45    90   135   180
        # rotate_deg_user : 90   45    0    -45   -90
        rotate_deg_user = (face_hdeg * (-1) + 90) 

        left_bottom_y = right_bottom_y = (cam_y_pos - min_v_distance)
        left_bottom_x = cam_x_pos - min_h_distance/2
        right_bottom_x = cam_x_pos + min_h_distance/2

        left_top_y = right_top_y = cam_y_pos - max_v_distance
        left_top_x = cam_x_pos - max_h_distance/2
        right_top_x = cam_x_pos + max_h_distance/2

        # calculate right_bottom x,y after rotation
        try:
            deg = degrees(atan((right_bottom_y*(1)-cam_y_pos*(1))/(right_bottom_x - cam_x_pos)))
        except:
            print('degree error')    
        rotate_deg = ( (deg-rotate_deg_user) *pi /180)
        distance = sqrt((right_bottom_y -cam_y_pos)**2 + (right_bottom_x - cam_x_pos )**2) 

        rotate_right_bottom_x = cam_x_pos + (distance) * cos(rotate_deg)
        rotate_right_bottom_y = cam_y_pos + (distance) * sin(rotate_deg)
        

        # calculate right_top x,y after rotation
        try:
            deg = degrees(atan((right_top_y*(1)-cam_y_pos*(1))/(right_top_x - cam_x_pos)))
        except:
            print('degree error')        
        rotate_deg = ( (deg-rotate_deg_user) *pi /180)
        distance = sqrt((right_top_y -cam_y_pos)**2 + (right_top_x - cam_x_pos )**2) 

        rotate_right_top_x = cam_x_pos + (distance) * cos(rotate_deg)
        rotate_right_top_y = cam_y_pos + (distance) * sin(rotate_deg)

        # calculate left_bottom x,y after rotation
        try:
            deg = degrees(atan((left_bottom_y*(1)-cam_y_pos*(1))/(left_bottom_x - cam_x_pos)))
        except:
            print('degree error')    
        rotate_deg = ( (deg-rotate_deg_user) *pi /180)
        distance = sqrt((left_bottom_y -cam_y_pos)**2 + (left_bottom_x - cam_x_pos )**2) 
        rotate_left_bottom_x = cam_x_pos - (distance) * cos(rotate_deg)
        rotate_left_bottom_y = cam_y_pos - (distance) * sin(rotate_deg)


        # calculate left_top x,y after rotation
        try:
            deg = degrees(atan((left_top_y*(1)-cam_y_pos*(1))/(left_top_x - cam_x_pos)))
        except:
            print('degree error')     
        rotate_deg = ( (deg-rotate_deg_user) *pi /180)
        distance = sqrt((left_top_y -cam_y_pos)**2 + (left_top_x - cam_x_pos )**2) 
        rotate_left_top_x = cam_x_pos - (distance) * cos(rotate_deg)
        rotate_left_top_y = cam_y_pos - (distance) * sin(rotate_deg)

        # find intersection with room and rotate_polygon!!!
        room_polygon = [[0,0],[0,room_height],[room_width,room_height],[room_width,0]]
        rotate_polygon = [ [rotate_left_top_x,rotate_left_top_y],\
                           [rotate_left_bottom_x,rotate_left_bottom_y],\
                           [rotate_right_bottom_x,rotate_right_bottom_y],\
                           [rotate_right_top_x,rotate_right_top_y] ]

        rotate_polygon_intersection = intersect(room_polygon, rotate_polygon)
        rotate_final_list = get_visible_range_points_in_room (rotate_polygon,room_polygon,rotate_polygon_intersection)
        ## Greg Test Done        

        cv2.imshow(WINDOW_NAME, base_img)
        if cv2.waitKey(1) == ord('q'):
            break


        # plot for visible range
        window_height_bias = room_height * 100 * WINDOW_BIAS_PERCENTAGE / 100
        window_width_bias = room_width * 100 * WINDOW_BIAS_PERCENTAGE /100
        window_bias = max(window_height_bias,window_width_bias)
        room_line_bias = window_bias * ROOM_LINE_BIAS_PERCENTAGE /100
        poly_line_bias = window_bias * POLY_LINE_BIAS_PERCENTAGE /100 

        
        window_height = int(room_height*100+window_bias)
        window_width = int(room_width*100+window_bias)

        new_img = np.zeros((window_height,window_width,3),np.uint8)
        room_height_cm_int = int(room_height*100)
        room_width_cm_int = int(room_width*100)


        # map the min, max distance to x,y axis
        room_list_arr = np.array([ [0,0],[0,room_height],[room_width,room_height],[room_width,0] ],dtype=float)
        room_pts = room_list_arr*100 + room_line_bias
        room_pts = room_pts.astype(np.int32)
        # map coordinate to (頂點數量, 1, 2) array
        room_pts = room_pts.reshape((-1, 1, 2))

        cv2.namedWindow('ROOM', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_AUTOSIZE)
        # # plot the visible range
        rot_point_arr = np.array(rotate_final_list)
        rot_point_pts = rot_point_arr*100 + room_line_bias
        rot_point_pts = rot_point_pts.astype(np.int32)
        rot_point_pts = rot_point_pts.reshape((-1,1,2))
        cv2.polylines(new_img, [rot_point_pts], True, (255, 50, 255), 4)
        cv2.fillPoly(new_img, [rot_point_pts], (255,50,255)) 


        # get scale of font size

        ratio = 600 / max(window_height,window_width)
        resize_window_width = round(window_width * ratio)
        resize_window_height = round(window_height * ratio)
        fontScale = 1/ratio

        if max(window_height,window_width) < 512:
            font_thickness = 1
        elif max(window_height,window_width) < 1024:
            font_thickness = 2
        elif max(window_height,window_width) < 2048:
            font_thickness = 4    
        else:
            font_thickness = 8    

        # print rotation coordinate
        for i in range(len(rot_point_arr)):
            cv2.putText(new_img, f'({rot_point_arr[i][0]:.1f},{rot_point_arr[i][1]:.1f}) ', tuple(rot_point_pts[i][0]), cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale,  (0,0,255), font_thickness, cv2.LINE_AA)

        # print room coordinate
        for i in range(len(room_list_arr)):
            cv2.putText(new_img, f'({room_list_arr[i][0]:.1f},{room_list_arr[i][1]:.1f}) ', tuple(room_pts[i][0]), cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale,  (0,0,255), font_thickness, cv2.LINE_AA)

        cv2.polylines(new_img, [room_pts], True, (255, 255, 255), 4)


        new_img = cv2.resize(new_img, (resize_window_width,resize_window_height),interpolation=cv2.INTER_CUBIC)

        cv2.imshow('ROOM', new_img)
        if cv2.waitKey(1) == ord('q'):
            break        


    cv2.destroyAllWindows()

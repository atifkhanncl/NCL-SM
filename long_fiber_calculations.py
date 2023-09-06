from PIL import Image
import PIL.ImageOps  
import numpy as np
import pandas as pd
import os
import cv2
import csv
Image.MAX_IMAGE_PIXELS = None
from tqdm import tqdm
import operator
import mahotas
import matplotlib.pyplot as plt
from skimage.morphology import convex_hull_image




def add_border(mask, inflate_pixels=10):
    
    h,w = mask.shape
    Dw,Dh = inflate_pixels,inflate_pixels
    img = np.zeros((h+2*Dh,w+2*Dw))
    img[:,:] = mask.min()
    img[Dh:(Dh+h),Dw:(Dw+w)] = mask
    
    return img

def fiber_at_border(mask):
    border_fiber= False
    if (any(pixel !=0 for pixel in mask[0,:-1]) or
        any(pixel !=0 for pixel in mask[:-1,-1]) or
        any(pixel !=0 for pixel in mask[-1,::-1]) or
        any(pixel !=0 for pixel in mask[-2:0:-1,0])):
        border_fiber= True
    return border_fiber



def perimeter_length(mask, neighbours=4):
    mask_border= np.uint8(add_border(mask))
    perimeter_length= mahotas.labeled.bwperim(mask_border, neighbours).sum()
    return perimeter_length


    
    

def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)

def calculate_aspect(i: int, j: int):
    def gcd(a, b):
        """The GCD (greatest common divisor) is the highest number that evenly divides both width and height."""
        return a if b == 0 else gcd(b, a % b)
    length= max(i,j)
    width=min(i,j)

    r = gcd(width, length)
    x = int(length / r)
    y = int(width / r)
    aspect_ratio = x/y

    return aspect_ratio

def aspect_ratio_for_contour (contour):
    
    ellipse = cv2.fitEllipse(contour)
    (xc,yc),(d_minor,d_major),angle = ellipse
    i= int(d_minor)
    j= int(d_major)
    aspect_ratio= calculate_aspect(i,j)
    
    
    return aspect_ratio, i, j

def aspect_ratio_for_mask (mask):
    segmentation = np.nonzero(mask)
    if len(segmentation) != 0 and len(segmentation[1]) != 0 and len(segmentation[0]) != 0:
        x_min = int(np.min(segmentation[1]))
        x_max = int(np.max(segmentation[1]))
        y_min = int(np.min(segmentation[0]))
        y_max = int(np.max(segmentation[0]))
            
        i= int(x_max-x_min)
        j= int(y_max-y_min)
        width= min(i,j)
        length= max(i,j)
        aspect_ratio= calculate_aspect(i,j)
        
    return aspect_ratio,width,length

def contour_finder (mask):
    
    # Find fibres from mask_GT
    contours,hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP,2)
    # Ensure only looking at holes inside contours...
    contours = [c for i,c in enumerate(contours) if hierarchy[0][i][3] != -1]
    return contours

def biggest_contour(mask, canny_thershold=100):
    
    mask_border= np.uint8(add_border(mask))
    mask_border_edge  = cv2.Canny(mask_border,canny_thershold, canny_thershold * 2)
    
    contours= contour_finder (mask_border_edge)
    contour_lengths=[]
    for contour in contours:
        contour_lengths.append(len(contour))
    biggest_cont= [] if len(contour_lengths)==0 else contours[contour_lengths.index(max(contour_lengths))]
    
    return biggest_cont
        


def all_long_fiber_metrics_instance_mask (instance_mask, filename, min_area=10, canny_thershold=100): # min_area will be used to remove small accidental annotations
    
            
    mask= np.copy(instance_mask)
    mask_border= add_border(mask)
    unique, counts = np.unique(mask[np.nonzero(mask)], return_counts=True)
    pixel_val_count= dict(zip(unique, counts))
    pixels_ids_and_area= {k:v for k, v in pixel_val_count.items() if v > min_area}
    unique_colours= list(pixels_ids_and_area.keys())
    
    
    
    # counter for detecting multiple contour for same annotation, usually happens when a pixel is sharing anedge with the contour
    multi_contour_annotation=0
    all_calculations = []
    for colour in unique_colours:
        
        # using 'mask' to calculate contours and ellipse
        unique_colour_mask = np.array(((mask == colour)*255),dtype=np.uint8)
        contour= biggest_contour(unique_colour_mask, canny_thershold)
        
        aspect_ratio_e, width_e, length_e = (0,0,0) if len(contour) <10 else aspect_ratio_for_contour (contour)
        aspect_ratio_bbox, width_bbox, length_bbox = aspect_ratio_for_mask (unique_colour_mask)
        lengthSquaredbyArea_e= (length_e *length_e)/pixels_ids_and_area[colour]
        lengthSquaredbyArea_bbox= (length_bbox *length_bbox)/pixels_ids_and_area[colour]
        convexity = (np.count_nonzero(convex_hull_image(unique_colour_mask)))/pixels_ids_and_area[colour]
        Fiber_on_Border= fiber_at_border(unique_colour_mask)
        fiber_perimeter= perimeter_length(unique_colour_mask)
        fiber_peri_by_rectangular_peri= fiber_perimeter/((2*width_bbox)+(2*length_bbox))
        all_calculation= (filename, colour,Fiber_on_Border, pixels_ids_and_area[colour],fiber_perimeter,convexity, width_e, length_e, aspect_ratio_e,lengthSquaredbyArea_e , width_bbox, length_bbox,aspect_ratio_bbox,lengthSquaredbyArea_bbox,fiber_peri_by_rectangular_peri, multi_contour_annotation)
        all_calculations.append(all_calculation)
        
                
                   
    return all_calculations


inp_mask_dir = './sample_data/QIF_masks/'
out_dir = './sample_data/outputs/'


dir_create(out_dir)
element_size = 2 # set 2 for IMC or 6 for QIF


mask_list = [f for f in
            os.listdir(inp_mask_dir)
            if os.path.isfile(os.path.join(inp_mask_dir, f))]



out_file_path = os.path.join(out_dir, 'all_Fiber_Calculations_QIF' + '.csv')
header = ['FileName','Fibre_ID','Fiber_on_Border','Fiber_Area','Fiber_Perimeter','Convexity','Fiber_Width_Ellipse', 'Fiber_Length_Ellipse','Aspect_Ratio_Ellipse','lengthsquared_by_Area_Ellipse','Fiber_Width_Bbox', 'Fiber_Length_Bbox','Aspect_Ratio_Bbox','lengthsquared_by_area_Bbox','Fiber_Perimeter_by_Rectangular_Perimeter','Multi_Contour_Detected' ]
with open(out_file_path, "a", encoding="UTF8",newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

for infile in tqdm(mask_list, desc='files processed'):
    
    infile_mask_path = os.path.join(inp_mask_dir, infile)
    
    filename= infile.split('.')[0]
    
    mask = cv2.imread(infile_mask_path,2)
    all_calculations= all_long_fiber_metrics_instance_mask (mask, filename, min_area=25)
    

    
    with open(out_file_path, "a", encoding="UTF8",newline='') as f:
        writer = csv.writer(f)       
        writer.writerows(all_calculations)
   








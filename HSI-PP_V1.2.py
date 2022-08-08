"""
@author: %(Ahmed Islam ElManawy)
a.elmanawy_90@agr.suez.edu.eg
"""
######### import packages
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from math import pi, atan
from sklearn.cluster import KMeans
import win32com.client as wincl
import xlrd
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression as PLSR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.ensemble import RandomForestRegressor as RFR
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import SVC, SVR
import datetime
import numpy as np
import pandas as pd
import tkinter
import tkinter.filedialog
import tkinter.simpledialog
from tkinter import ttk, StringVar
import os, time
import cv2
import re
import xlsxwriter
from scipy.io import loadmat, savemat
import pickle
import collections
from spectral import * 
from spectral import settings
from win32 import win32gui
import pyautogui
import skimage.measure
from skimage.morphology import convex_hull_image, closing, square
from skimage.feature import greycomatrix, greycoprops
from skimage.filters import threshold_otsu
from skimage import img_as_ubyte as ubyte
from skimage.measure import shannon_entropy as entropy
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import threading
scaler = StandardScaler()
settings.envi_support_nonlowercase_params= True
from scipy.signal import savgol_filter as SG
from scipy.ndimage import rotate, zoom, grey_dilation, grey_erosion
from sklearn.utils.multiclass import check_classification_targets, unique_labels
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict
from sklearn.linear_model import LinearRegression
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from genetic_selection import GeneticSelectionCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import matplotlib.pyplot as plt
import matplotlib
# matplotlib.use('TkAgg')
matplotlib.use('Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image, ImageEnhance
font = FontProperties()
font.set_family('serif')
font.set_name('Times New Roman')
font.set_size('5')
font.set_weight('normal')
font.set_style('normal')
#%% ####### create different functions which nicessary for this software
def open_hsi_img(infile):# Function_1 to open Hyperspectral image with all extinsion except mat file
    HSI_Img = open_image(infile[:-4]+'.hdr')
    a=infile.split('/')
    path=infile[:-len(a[-1])]
    save_rgb(path+'1.tiff', HSI_Img, stretch=((0.02, 0.98), (0.02, 0.98), (0.02, 0.98)))
    return HSI_Img
def extract_hsi(HSI_Img):
    hsi_img=HSI_Img[:,:,0:]
    return hsi_img
def open_mat_img(infile): # Function_1.1 to open mat files
    Name=[]
    Image_mat=loadmat(infile)
    for n in Image_mat:
        Name.append(n)
    Image=Image_mat[Name[-1]]
    Wave_Length=wavelength(infile, 'txt')#open_hdr_file(infile, 'txt')[0].split(',')
    RGB_bands=wave2index(Wave_Length, [640, 550, 460])
    Index=int(Image.shape[2]/2)
    masked_img_green, Binarry_IMAGE=extract_color_img(Image, RGB_bands, Index)
    return Wave_Length, Image, masked_img_green
def open_rgb_img(infile):# Function_2 to open RGB image
    a=infile.split('/')
    path=infile[:-len(a[-1])]
    RGB_Image=cv2.imread(path+'/1.tiff', 1)
    return RGB_Image
def wavelength(INFILE, Ext): #Function_3 get wavelength values from header file
    meanband, first_part, last_part=open_hdr_file(INFILE, Ext)
    wave_length=meanband.split(',')
    Wave_Length=[]
    for WL in wave_length:
        Wave_Length.append(float(WL))
    Wave_Length=np.asarray(Wave_Length)
    return Wave_Length
def white_calib(HSI_Img, img_binarry_white_board): #Function_4
    speak('Please wait for extract reference board reflection!')
    img_RGB=np.ones([HSI_Img.shape[0], HSI_Img.shape[1], 3])
    Image_HSI_white=hsi_segment(img_binarry_white_board, HSI_Img.copy(), img_RGB)[0]     ## get white board reflection
    Image_HSI_white=remove_Outliers(Image_HSI_white, 2)
    for b in range(Image_HSI_white.shape[2]): ### remove outside area
        h,w=np.where(Image_HSI_white[:,:,b]<=0)
        H,W=np.where(Image_HSI_white[:,:,b]>0)
        Image_HSI_white[h,w,b]=np.mean(Image_HSI_white[H,W,b])
    Image_white=hsi_resize(Image_HSI_white, HSI_Img.shape[0], HSI_Img.shape[1], img_RGB)[0]
    Image_white = cv2.blur(Image_white,(20,20))
    speak('Please wait for image normalization!')
    min_img=np.min(np.amin(HSI_Img, 0), 0)*np.ones(HSI_Img.shape)
    numerator=HSI_Img-min_img
    denominator=Image_white-min_img
    Image_calibrated=numerator/denominator
    Image_calibrated=Image_calibrated.astype('float32')
    return Image_calibrated
def vegetation_index(image, index, num): #Function_5 for calculate different vegetation indices
    index=np.sort(index)
    if num==20:
        i1,i2=index
        i1=int(i1)
        i2=int(i2)  
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        my_VI=band_1/band_0
    elif num==4 or num==10 or num==13 or num==17 or num==23 or num==9 or num==11: ## NDVI normalized different vegetation index,## PRI Photochemical reflection index, Green NDVI, Red-edge NDVI, ##VARIgreen visible atmospherically resistant indices, NCPI normalized pigment Chlorophyll ratio index, NDWI Normalized Difference Water Index
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        up=band_1-band_0
        down=band_1+band_0
        my_VI=up/down 
    elif num==6: ### MCARI (Modified chlorophyll absorption in reflectance index) (DAUGHTRY et al., 2000) Estimating corn leaf chlorophyll concentration from leaf and canopy reflectance.
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        a=band_2-band_1
        b=0.2*(band_2-band_0)
        c=band_2/band_1
        my_VI= (a-b)*c
    elif num==15: ##the red edge inflection point (REIP) (Guyot et al., 1988)
        i1,i2,i3,i4=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        i4=int(i4)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        band_3=image[:,:,i4]
        a=(band_0+band_3)/2
        b=band_2-band_1
        c=(a-band_1)/b
        my_VI=700+(40*c)
    elif num==3: ## EVI Enhanced Vegetation Index
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        up=2.5*((band_2)-band_1)
        down=(band_2)+(6*(band_1))-(7.5*band_0)+1
        my_VI=up/down
    elif num==0 or num==1: ##CIgreen and CI red edge Chlorophyll index
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        my_VI=(band_1/band_0)-1
    elif num==8: ## MSR Modified Simple Ratio
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        a=band_1/band_0
        my_VI=(a-1)/((a+1)**0.5)
    elif num==22: ##TCARI (the transformed chlorophyll Absorption and Reflectance Index)
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        a=band_2-band_1
        b=band_2-band_0
        c=band_2/band_1
        d=(0.2*b*c)
        my_VI=3*(a-d)
    elif num==19: ###SIPI (Structural Independent Pigment Index)
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        a=band_0/band_2
        my_VI=band_2-a-band_1
    elif num==2 or num==14: ##PSRI (Plant Senescence Reflectance Index) and Early plant vigour(EPVI) High-throughput phenotypingearlyplantvigourofwinterwheat
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        b=band_1-band_0
        my_VI=b/band_2
    elif num==16: ## RNDVI Renormalized difference vegetation index Detection of multi-tomato leaf diseases
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        up=(band_1[:,:,0]-band_0[:,:,0])
        down=(band_1[:,:,0]+band_0[:,:,0])
        my_VI=up/(down**0.5)
    elif num==12: ## OSAV Optimization of Soil-Adjusted Vegetation Indices
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        up=(band_1-band_0)
        down=(band_1+band_0)+0.16
        my_VI=up/down
    elif num==24: ## modified Normalized Differences mND In vivo noninvasive detection of chlorophyll distribution in cucumber
        i1,i2,i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        up=(band_2-band_1)
        down=(band_2+band_1)-(2*band_0)
        my_VI=up/down
    elif num==18: ## SD
        i1,i2=index
        i1=int(i1)
        i2=int(i2)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        my_VI=band_1-band_0
    elif num==7: ###MDATT
        i1,i2, i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        up=band_2-band_0
        down=band_2-band_1
        my_VI=up/down
    elif num==5: ###GreenNDVI-NDVI
        i1,i2, i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        up=band_2-band_0
        down=band_2+band_0
        a=up/down
        UP=band_2-band_1
        DOWN=band_2+band_1
        B=UP/DOWN
        my_VI=a-B
    elif num==21: ###TBDR
        i1,i2, i3=index
        i1=int(i1)
        i2=int(i2)
        i3=int(i3)
        band_0=image[:,:,i1]
        band_1=image[:,:,i2]
        band_2=image[:,:,i3]
        up=band_2
        down=band_1-band_0
        my_VI=up/down
    my_VI[np.where(my_VI==np.inf)]=0
    my_VI[np.where(np.isnan(my_VI))]=0
    return my_VI
def image_segmentation(RGB_Image, hsv, min_H, max_H, min_S, max_S, min_V, max_V): #Function_6 ### for rgb threshold segmenetation method
    lower_green = np.array([min_H, min_S, min_V]) 
    upper_green = np.array([max_H, max_S, max_V])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    masked_img_green = cv2.bitwise_and(RGB_Image, RGB_Image, mask=opened_mask)
    gray=cv2.cvtColor(masked_img_green, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0.75)
    ret,img_binarry = cv2.threshold(blur, 0, 255,cv2.THRESH_BINARY)
    kernel_binarry = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    img_binarry = cv2.morphologyEx(img_binarry, cv2.MORPH_OPEN, kernel_binarry)
    Binarry_image=np.zeros(masked_img_green.shape)
    Binarry_image[:,:,0]=img_binarry
    Binarry_image[:,:,1]=img_binarry
    Binarry_image[:,:,2]=img_binarry
    kernel = np.ones((5,5),np.uint8)
    Binarry_image = cv2.morphologyEx(Binarry_image, cv2.MORPH_OPEN, kernel)
    return img_binarry, masked_img_green, Binarry_image
def modify_binarry(img_binarry):
    img_binarry = cv2.medianBlur(img_binarry,9)
    kernel_binarry = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50)) 
    img_binarry = cv2.morphologyEx(img_binarry, cv2.MORPH_OPEN, kernel_binarry)
    return img_binarry
def hsi_segment(img_binarry, HSI_Img, RGB_imgs): #Function_7 apply mask image on HSI
    # img_binarry = cv2.medianBlur(img_binarry,9)
    kernel_binarry = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    img_binarry = cv2.morphologyEx(img_binarry, cv2.MORPH_OPEN, kernel_binarry)
    hsi_Img=HSI_Img
    Height, Width= np.where(img_binarry != 255)
    hsi_Img[Height, Width,:]=0
    RGB_imgs[Height, Width,:]=0
    Height, Width= np.where(img_binarry == 255)
    roi_hsi_img=hsi_Img[min(Height):max(Height), min(Width):max(Width),:]
    img_RGB_seg=RGB_imgs[min(Height):max(Height), min(Width):max(Width),:]
    return roi_hsi_img, img_RGB_seg
def hsi_filter (HSI_Img, min_R, max_R, H, RGB_img, remove_spec, median_filter): #Function_8 remove bad pixels or create ROI using specific band
    if np.min(HSI_Img[:,:,H])==min_R and np.max(HSI_Img[:,:,H])==max_R:
        Image_HSI=HSI_Img
        RGB_img_seg=RGB_img
        height2, width2=np.where(Image_HSI[:,:,H]>min_R)
        Binarry_IMAGEs=np.zeros([Image_HSI.shape[0], Image_HSI.shape[1],3])
        Binarry_IMAGEs[height2, width2,:]=255
        Binarry_IMAGEs=Binarry_IMAGEs.astype(np.uint8)
    else:
        roi_hsi_img=HSI_Img.copy()
        if remove_spec==1:#np.max(HSI_Img[:,:,H])>=1 and np.max(HSI_Img[:,:,H])<=2:
            if np.max(HSI_Img[:,:,H])==max_R:
                max_R=1
            speak('Please wait for specular remove!')
            spec_img=np.zeros((roi_hsi_img.shape[0], roi_hsi_img.shape[1]), np.uint8)
            h,w=np.where(roi_hsi_img[:,:,H]>=max_R)
            if len(h)>0:
                spec_img[h,w]=255
                spec_img=spec_img.astype(np.uint8)
                for b in range(roi_hsi_img.shape[2]):
                    roi_hsi_img[:,:,b] = cv2.inpaint(roi_hsi_img[:,:,b], spec_img, 7, cv2.INPAINT_NS)
        else:
            roi_hsi_img[:,:,H]=np.where(roi_hsi_img[:,:,H]<max_R, roi_hsi_img[:,:,H], 0) 
        roi_hsi_img[:,:,H]=np.where(roi_hsi_img[:,:,H]>min_R, roi_hsi_img[:,:,H], 0)
        height2, width2=np.where(roi_hsi_img[:,:,H]<=min_R)
        Binarry_IMAGE=np.zeros([roi_hsi_img.shape[0], roi_hsi_img.shape[1],3])
        roi_hsi_img[height2, width2,:]=0
        RGB_img[height2, width2,:]=0
        height2, width2=np.where(roi_hsi_img[:,:,H]>min_R)
        Binarry_IMAGE[height2, width2,:]=255
        Binarry_IMAGE=Binarry_IMAGE.astype(np.uint8)
        Image_HSI=roi_hsi_img[min(height2):max(height2), min(width2):max(width2),:]
        RGB_img_seg=RGB_img[min(height2):max(height2), min(width2):max(width2),:]
        Binarry_IMAGEs=Binarry_IMAGE[min(height2):max(height2), min(width2):max(width2),:]
        if median_filter==1:
            Image_HSI=cv2.medianBlur(Image_HSI,3)
            RGB_img_seg=cv2.medianBlur(RGB_img_seg,3)
            Binarry_IMAGEs=cv2.medianBlur(Binarry_IMAGEs,3)
    return Image_HSI, RGB_img_seg, Binarry_IMAGEs
def remove_Outliers(Image, STD): #Function_9 remove outliers pixels from every bands
    Image_HSI=Image.copy()
    if STD>0:
        if len(Image_HSI.shape)==3:
            for b in range(Image_HSI.shape[2]):
                my_img=Image_HSI[:,:,b]
                low_outliers=np.mean(my_img[np.where(my_img>0)])-(STD*np.std(my_img[np.where(my_img>0)]))
                high_outliers=np.mean(my_img[np.where(my_img>0)])+(STD*np.std(my_img[np.where(my_img>0)]))
                h,w=np.where((my_img<low_outliers) & (my_img > 0))
                if len(h)>0:
                    my_img[h,w]=np.median(my_img[np.where(my_img>0)])
                else:
                    pass
                h,w=np.where(my_img>high_outliers)
                if len(h)>0:
                    my_img[h,w]=np.median(my_img[np.where(my_img>0)])
                else:
                    pass
        elif len(Image_HSI.shape)==2:
            for H in range(7, Image_HSI.shape[0]-8, 15):
                for W in range(7, Image_HSI.shape[1]-8, 15):
                    img=Image_HSI[(H-7):(H+8), (W-7):(W+8)]
                    if len(np.where(img>0)[0])>0:
                        low_outliers=np.mean(img[np.where(img>0)])-(STD*np.std(img[np.where(img>0)]))
                        high_outliers=np.mean(img[np.where(img>0)])+(STD*np.std(img[np.where(img>0)]))
                        img[np.where((img<low_outliers) & (img > 0))]=np.median(img[np.where(img>0)])
                        img[np.where(img>high_outliers)]=np.median(img[np.where(img>0)])
        else:
            speak('There is error in remove outliersl')
    else:
        pass
    return Image_HSI
def sg(img, wd, ployorder, dev): ##Function_10 savitziky golay smoothing and derivative
    def sg_image(image, wd, ployorder, dev):
        if wd>ployorder:
            new_img=SG(image, wd, ployorder, deriv=dev)
        else:
            A=np.array([3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
            wd=A[np.where(A>ployorder)[0][0]]
            new_img=SG(image, wd, ployorder, deriv=dev)
        index=int(image.shape[2]/2)
        my_img=image[:,:,index]
        non_zero=np.nonzero(my_img)
        min_value=np.min(my_img[non_zero])
        height, width=np.where(my_img>min_value)
        data_mean_derv=np.mean(new_img[height, width,:], 0)
        return new_img, data_mean_derv
    if len(img.shape)==3:
        new_img, data_mean_derv=sg_image(img, wd, ployorder, dev)
        data_mean_derv=np.asarray(data_mean_derv).reshape(-1, 1).T
    elif len(img.shape)==1 or len(img.shape)==4:
        new_img=[]
        data_mean_derv=[]
        for i in range(img.shape[0]):
            sub_image=img[i]
            new_imgs, data_mean_dervs=sg_image(sub_image, wd, ployorder, dev)
            new_img.append(new_imgs)
            data_mean_derv.append(data_mean_dervs)
        new_img=np.asarray(new_img)
        data_mean_derv=np.asarray(data_mean_derv)
    return new_img, data_mean_derv
def MSC_image(Images): #Function_11 calculate multi scatter correction
    def msc(input_data):
        for i in range(input_data.shape[0]): # mean centre correction
            input_data[i,:] -= input_data[i,:].mean()
        ref = np.mean(input_data, axis=0)
        data_msc = np.zeros_like(input_data) # Define a new array and populate it with the corrected data
        for i in range(input_data.shape[0]):
            fit = np.polyfit(ref, input_data[i,:], 1, full=True) # Run regression
            data_msc[i,:] = (input_data[i,:] - fit[0][1]) / fit[0][0]  # Apply correction
        return data_msc
    if len(Images.shape)==3:
        H=int(Images.shape[2]/2)
        h,w=np.where(Images[:,:,H]>0)
        image_msc=np.zeros(Images.shape)
        image_msc[h,w,:]=msc(Images[h,w,:])
        mean_msc=np.mean(msc(Images[h,w,:]),0)
        mean_msc=np.asarray(mean_msc).reshape(-1, 1).T
    elif len(Images.shape)==1 or len(Images.shape)==4:
        image_msc=[]
        mean_msc=[]
        for i in range(Images.shape[0]):
            sub_image=Images[i]
            H=int(sub_image.shape[2]/2)
            h,w=np.where(sub_image[:,:,H]>0)
            sub_image_msc=np.zeros(sub_image.shape)
            sub_image_msc[h,w,:]=msc(sub_image[h,w,:])
            mean_sub_image_msc=np.mean(msc(sub_image[h,w,:]),0)
            image_msc.append(sub_image_msc)
            mean_msc.append(mean_sub_image_msc.T)
        mean_msc=np.asarray(mean_msc)
        image_msc=np.asarray(image_msc)
    return mean_msc, image_msc
def SNV_image(Images): #Function_12 calculate standard normal variate 
    def SNV(input_data):
        scaler.fit(input_data.T) ## because it work in axis=0 only
        SNV=scaler.transform(input_data.T).T
        return (SNV)
    if len(Images.shape)==3:
        H=int(Images.shape[2]/2)
        h,w=np.where(Images[:,:,H]>0)
        image_snv=np.zeros(Images.shape)
        image_snv[h,w,:]=SNV(Images[h,w,:])
        mean_snv=np.mean(SNV(Images[h,w,:]),0).reshape(-1, 1).T
    elif len(Images.shape)==1 or len(Images.shape)==4:
        image_snv=[]
        mean_snv=[]
        for i in range(Images.shape[0]):
            sub_image=Images[i]
            H=int(sub_image.shape[2]/2)
            h,w=np.where(sub_image[:,:,H]>0)
            sub_image_snv=np.zeros(sub_image.shape)
            sub_image_snv[h,w,:]=SNV(sub_image[h,w,:])
            mean_sub_image_snv=np.mean(SNV(sub_image[h,w,:]),0)
            image_snv.append(sub_image_snv)
            mean_snv.append(mean_sub_image_snv)
        mean_snv=np.asarray(mean_snv)
        image_snv=np.asarray(image_snv)
    return mean_snv, image_snv
def plot_spectrum(IMAGE, WAVE, Hh, frame, FigSize, Title, legend, path, name): #Function_13 
    if len(IMAGE.shape)==3:
        img=IMAGE[:,:,Hh]
        non_zero=np.nonzero(img)
        min_value=np.min(img[non_zero])
        height, width=np.where(img>min_value)
        image_mean=np.mean(IMAGE[height, width,:], 0)
        image_std_positive=image_mean+np.std(IMAGE[height, width,:], 0)
        image_std_negative=image_mean-np.std(IMAGE[height, width,:], 0)
        image_max=np.max(IMAGE[height, width,:], 0)
        image_min=np.min(IMAGE[height, width,:], 0)
        fig = Figure(figsize=FigSize, tight_layout=True, dpi=300, facecolor='lightyellow')
        ax = fig.add_subplot(111)
        ax.plot(WAVE, image_mean, 'b', label='Mean', linewidth=0.5)
        ax.plot(WAVE, image_std_positive, 'g', label='+Stdev', linewidth=0.5)
        ax.plot(WAVE, image_std_negative, 'g', label='-Stdev', linewidth=0.5)
        ax.plot(WAVE, image_max, 'r', label='Max', linewidth=0.5)
        ax.plot(WAVE, image_min, 'y', label='Min', linewidth=0.5)
    elif len(IMAGE.shape)==2:
        Data=IMAGE
        color=['b', 'k', 'r','y', 'g', 'c', 'm']
        marker=['o', 'v', '^', 's', 'p', '*', '+', 'H']
        fig = Figure(figsize=(3,2), tight_layout=True, dpi=300,facecolor='lightyellow')
        ax = fig.add_subplot(111)
        Data=np.asarray(Data)
        for I in range(Data.shape[0]):
            if I<7:
                ax.plot(WAVE, Data[I,:], color=color[I], label=I+1, linewidth=0.5)
            else:
                pass
    ax.set_title(Title, fontproperties=font)
    ax.set_xlabel("Wavelength (nm)", fontproperties=font)
    ax.set_ylabel('Reflection', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    max_lim = round(max(WAVE))
    min_lim = round(min(WAVE))
    ax.set_xticks(np.arange(min_lim, max_lim, 50)) ## maybe chnage it 
    if legend==1:
        ax.legend(prop =font)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row = 0, column=0)
    canvas.draw()
    if len(path)>0:
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
    return fig
def crop_image(hsi, Binarry, img_color):#, img_color, path, name): #Function_14 split image into sub images
    Hh=int(hsi.shape[2]/2)
    blur = cv2.GaussianBlur(Binarry, (15, 15), 2)
    image=cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = threshold_otsu(image)
    bw = closing(image > thresh, square(8))
    label_image = skimage.measure.label(bw,  connectivity=2)
    a=[]
    a_mean=[]
    cordinates=[]
    for region in skimage.measure.regionprops(label_image):
        if region.area >= 50:
            minr, minc, maxr, maxc = region.bbox
            cordinates.append([minr, minc, maxr, maxc])
            new_color_img=cv2.rectangle(img_color, (minc, minr), (maxc, maxr), color=(0,0,255), thickness=1)
    cordinates2=cords(cordinates)
    for cor in cordinates2:
        A=hsi[cor[0]:cor[2], cor[1]:cor[3],:]
        A=np.asarray(A)
        a.append(A)
        H,W=np.where(A[:,:,Hh]!=0)
        image_mean=np.mean(A[H,W,:],0)
        a_mean.append(image_mean)
    a=np.asarray(a)
    a_mean=np.asarray(a_mean)
    return a, a_mean, new_color_img
def hsi_binnings( Wave_Length, img, Bin): #Function_15 for spectral 
    while True:
        try:
            if Bin>1:
                    bands_binning=int(img.shape[2]/Bin)
                    band0=img.shape[2]-(bands_binning*Bin)
                    Img=img[:,:,band0:]
                    WAVE_length=[]
                    image_binning=np.zeros([Img.shape[0], Img.shape[1], bands_binning])
                    k=0
                    for B in range(0, Img.shape[2], Bin):
                        image_binning[:,:,k]=(np.mean(Img[:,:,B:(B+Bin)], 2)) ## get the binning in spectral dimension
                        if len (Wave_Length)>0:
                            WAVE_length.append(np.mean(Wave_Length[B:(B+Bin)]))
                        k+=1
                    break
        except:
            image_binning=img
            break
    return image_binning, WAVE_length
def hsi_spat_bin(img ,n, img_color): ##Function_16 spatial binning
    if len(img.shape)==3:
        h,w,b=img.shape
        new_img=cv2.resize(img.copy(), (int(w/n), int(h/n)))
        new_img=np.asarray(new_img)
        binarry_img=np.zeros((new_img.shape[0], new_img.shape[1], 3))
        H,W=np.where(new_img[:,:,int(b/2)]!=0)
        binarry_img[H,W, :]=255
        binarry_img=np.asarray(binarry_img).astype(np.uint8)
        img_colors=cv2.resize(img_color.copy(), (int(w/n), int(h/n)))
        img_colors=np.asarray(img_colors).astype(np.uint8)
    elif len(img.shape)==1 or len(img.shape)==4:
        new_img=[]
        for i in range(img.shape[0]):
            my_img=img[i]
            h,w,b=my_img.shape
            New_Image=cv2.resize(my_img.copy(), (int(w/n), int(h/n)))
            new_img.append(New_Image)
        new_img=np.asarray(new_img)
        binarry_img=[]
        img_colors=[]
    return new_img, binarry_img, img_colors
def hsi_resize(img, X_size, Y_size, img_color): ##Function_17 spatial resize
    if len(img.shape)==3:
        h,w,b=img.shape
        new_Image=cv2.resize(img.copy(), (Y_size, X_size))
        binarry_img=np.zeros((new_Image.shape[0], new_Image.shape[1], 3))
        H,W=np.where(new_Image[:,:,int(b/2)]!=0)
        binarry_img[H,W, :]=255
        img_colors=cv2.resize(img_color.copy(), (Y_size, X_size))
        binarry_img=np.asarray(binarry_img).astype(np.uint8)
        img_colors=np.asarray(img_colors).astype(np.uint8)
    elif len(img.shape)==1 or len(img.shape)==4:
        new_Image=[]
        for i in range(img.shape[0]):
            my_img=img[i]
            New_Image=cv2.resize(my_img.copy(), (Y_size, X_size))
            new_Image.append(New_Image)
        new_Image=np.asarray(new_Image)
        binarry_img=[]
        img_colors=[]
    return new_Image, binarry_img, img_colors
def Data_aug(Image): ##Function_18 image augmentation;
    def horizontal_flip(img): ##flipped image
        out=img.copy()
        out = np.fliplr(out)
        return out
    def width_shift_range(img, shift_factor): ###translations
        w= img.shape[1]
        if shift_factor>0: ## right
            ws=int(w*shift_factor)
            out = np.zeros(img.shape)
            out[:,ws:, :]=img[:,:(w-ws),:]
        if shift_factor<0: ##left
            ws=int(w*abs(shift_factor))
            out = np.zeros(img.shape)
            out[:,:(w-ws), :]=img[:,ws:,:]
        return out
    def height_shift_range(img, shift_factor): ###translations
        h= img.shape[0]
        if shift_factor>0: ## downward
            hs=int(h*shift_factor)
            out = np.zeros(img.shape)
            out[hs:,:, :]=img[:(h-hs),:,:]
        if shift_factor<0: ##upward
            hs=int(h*abs(shift_factor))
            out = np.zeros(img.shape)
            out[:(h-hs),:, :]=img[hs:,:,:]
        return out
    def rotation_range(img, rotation_factor): ##rotat
        out=rotate(img, rotation_factor, reshape=False)
        return out
    def clipped_zoom(img, zoom_factor): #zooming
        h, w = img.shape[:2] ## get the first two dimensions
        zoom_tuple = (zoom_factor,) * 2 + (1,) * (img.ndim - 2) # get the zoom in x, y only but z remaining as it is
        if zoom_factor < 1:
            zh = round(h * zoom_factor)
            zw = round(w * zoom_factor)
            top = (h - zh) // 2
            left = (w - zw) // 2
            out = np.zeros(img.shape)
            out[top:top+zh, left:left+zw] = zoom(img, zoom_tuple)
        elif zoom_factor > 1:
            zh = round(h * zoom_factor)
            zw = round(w * zoom_factor)
            top = (zh - h) // 2
            left = (zw - w) // 2
            img_zoom=zoom(img, zoom_tuple)
            out = img_zoom[top:top+h, left:left+w]
        else:
            out = img
        return out
    def shear_range(img, shear_factor): #shear
        out=img
        h,w=out.shape[:2]
        K=int(shear_factor*w)
        step=int(h/K)
        for i in range(0, h, step):
            out[i:(i+step),:]=np.roll(out[i:(i+step),:], K, axis=1)
            out[i:(i+step),:K]=0
            K=K-1
        return out
    img_agu=[]
    if len(Image.shape)==3:
        flipped_img=horizontal_flip(Image)
        w_right = width_shift_range(Image, 0.3)
        w_left = width_shift_range(Image, -0.3)
        h_down = height_shift_range(Image, 0.3)
        h_up = height_shift_range(Image, -0.3)
        img_rotate=rotation_range(Image, 40)
        zm_out =clipped_zoom(Image, 0.7)
        zm_in = clipped_zoom(Image, 1.3)
        img_shear=shear_range(Image, 0.4)
        img_agu.append(flipped_img)
        img_agu.append(w_right)
        img_agu.append(w_left)
        img_agu.append(h_down)
        img_agu.append(h_up)
        img_agu.append(img_rotate)
        img_agu.append(zm_out)
        img_agu.append(zm_in)
        img_agu.append(img_shear)
    elif len(Image.shape)==1 or len(Image.shape)==4:
        for i in range(Image.shape[0]):
            my_image=Image[i]
            flipped_img=horizontal_flip(my_image)
            w_right = width_shift_range(my_image, 0.3)
            w_left = width_shift_range(my_image, -0.3)
            h_down = height_shift_range(my_image, 0.3)
            h_up = height_shift_range(my_image, -0.3)
            img_rotate=rotation_range(my_image, 40)
            zm_out =clipped_zoom(my_image, 0.7)
            zm_in = clipped_zoom(my_image, 1.3)
            img_shear=shear_range(my_image, 0.4)
            img_agu.append(flipped_img)
            img_agu.append(w_right)
            img_agu.append(w_left)
            img_agu.append(h_down)
            img_agu.append(h_up)
            img_agu.append(img_rotate)
            img_agu.append(zm_out)
            img_agu.append(zm_in)
            img_agu.append(img_shear)
    img_agu=np.asarray(img_agu)
    return img_agu
def texture_features( img, angles, steps): #Function_19 alculate different texture features from GLCM
    def cal_TextureFeatures( My_image, angles, steps):
        Entropy=[]
        corr_mat=[]
        cont_mat=[]
        eng_mat=[]
        homg_mat=[]
        Correlation=[]
        Contrast=[]
        Homogenity=[]
        Energy=[]
        for b in range(My_image.shape[2]):
            corr=[]
            cont=[]
            eng=[]
            homg=[]
            A=np.asarray(My_image[:,:,b])
            if np.min(A)<-1 or np.max(A)>1:
                A=MinMaxScaler().fit(A).transform(A)
            im = ubyte(A)
            im //= 32
            for I in steps: ## number of pixels
                glcm = greycomatrix(im, [I], angles, 8, symmetric=True, normed=True) ## number of angles
                corr.append(greycoprops(glcm, 'correlation'))
                cont.append(greycoprops(glcm, 'contrast'))
                eng.append(greycoprops(glcm, 'energy'))
                homg.append(greycoprops(glcm, 'homogeneity'))
            Entropy.append(entropy(im))
            cont=np.asarray(cont)
            eng=np.asarray(eng)
            homg=np.asarray(homg)
            corr=np.asarray(corr)
            cont_mat.append(cont[:,0,:])
            corr_mat.append(corr[:,0,:])
            eng_mat.append(eng[:,0,:])
            homg_mat.append(homg[:,0,:])
        corr_mat=np.asarray(corr_mat)
        cont_mat=np.asarray(cont_mat)
        eng_mat=np.asarray(eng_mat)
        homg_mat=np.asarray(homg_mat)
        Entropy=np.asarray(Entropy).T
        Homogenity.append(np.mean(np.mean(homg_mat, 2), 1))
        Homogenity=np.asarray(Homogenity)
        Correlation.append(np.mean(np.mean(corr_mat, 2), 1))
        Correlation=np.asarray(Correlation)
        Contrast.append(np.mean(np.mean(cont_mat, 2), 1))
        Contrast=np.asarray(Contrast)
        Energy.append(np.mean(np.mean(eng_mat, 2), 1))
        Energy=np.asarray(Energy)
        return Entropy, Homogenity, Correlation, Contrast, Energy
    if len(img.shape)==3:
        my_Entropy, my_Homogenity, my_Correlation, my_Contrast, my_Energy=cal_TextureFeatures( img, angles, steps)
    else:
        my_Entropy=[]
        my_Homogenity=[]
        my_Correlation=[]
        my_Contrast=[]
        my_Energy=[]
        for my_image in img:
           Entropy, Homogenity, Correlation, Contrast, Energy=cal_TextureFeatures( my_image, angles, steps)
           my_Entropy.append(Entropy)
           my_Homogenity.append(Homogenity[0])
           my_Correlation.append(Correlation[0])
           my_Contrast.append(Contrast[0])
           my_Energy.append(Energy[0])
        my_Entropy=np.asarray(my_Entropy)
        my_Homogenity=np.asarray(my_Homogenity)
        my_Correlation=np.asarray(my_Correlation)
        my_Contrast=np.asarray(my_Contrast)
        my_Energy=np.asarray(my_Energy)
        speak('The features have been calculated!')
    return my_Entropy, my_Homogenity, my_Correlation, my_Contrast, my_Energy
def cords(cordinates):
    cordinates2=cordinates.copy()
    c=[]
    for i in range(1, len(cordinates)):
        if np.abs(cordinates[i][0]-cordinates[i-1][0])<=30:
            c.append(cordinates[i-1])
            if i==len(cordinates)-1:
                c.append(cordinates[i])
                c=sorted(c, key=lambda I: [I[1]])
                if len(c)>1:
                    cordinates2[-2]=c[-2]
                    cordinates2[-1]=c[-1]
                break
        else:
            c.append(cordinates[i-1])
            c=sorted(c, key=lambda I: [I[1]])
            if len(c)>0:
                cordinates2[i-len(c): i]=c
            c=[]
    return cordinates2
def calculate_morphology(img, path, name, color_img, display): #Function_20 calculate geometric  features
    blur = cv2.GaussianBlur(img, (5, 5),0.75)
    img2=blur/255
    myimg1=img.copy()
    contours = skimage.measure.find_contours(img2[:,:,0], 0.02, fully_connected='high')
    plant_edge=np.zeros(img.shape)
    fig1 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax1 = fig1.add_subplot(1,1,1)
    ax1.set_title('Plant premeter', fontsize=5)
    ax1.imshow(color_img)
    for n, contour in enumerate(contours):
        ax1.plot(contour[:, 1], contour[:, 0], '-r',linewidth=0.5)
        for i in range(contour.shape[0]):
            plant_edge[int(contour[i,0]), int(contour[i,1]),:]=255
    ax1.set_xticks([])
    ax1.set_yticks([])
    my_parameter=[]
    image=cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = threshold_otsu(image)
    bw = closing(image > thresh, square(8))
    label_image = skimage.measure.label(bw,  connectivity=2)
    parts=np.max(label_image)+1
    if parts==1:
        h,w=np.where(img[:,:,0]>5)
        Proj_area=len(h)        #projected area
        kernel = np.ones((1,2), np.uint8)  # note this is a horizontal kernel
        d_im = cv2.dilate(plant_edge, kernel, iterations=6)
        e_im = cv2.erode(d_im, kernel, iterations=5)
        My_img=(e_im[:,:,2]>0)
        plant_prem=skimage.measure.perimeter(My_img, neighbourhood=4) # plant premeter
        myimg1[My_img,:]=[255,0,0]
        my_img=(img[:,:,0]>0)
        chull = convex_hull_image(my_img)
        h,w=np.where(chull==True)
        convex_area=len(h) # convex hull
        convex_pre=skimage.measure.perimeter(chull, neighbourhood=8)  
        fig2 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax2=fig2.add_subplot(1,1,1)
        ax2.imshow(chull, cmap=plt.cm.gray)
        ax2.set_title('convex hull', fontsize=5)
        ax2.set_xticks([])
        ax2.set_yticks([])
        compact=Proj_area*100/convex_area ### compacteness
        stock=(4*np.pi*Proj_area)/plant_prem**2 ### Stockiness
        convex_edge=np.zeros(chull.shape)
        convex_edge[np.where(chull==True)]=1 # convex edge
        contours = skimage.measure.find_contours(convex_edge,0.2, fully_connected='high')
        fig3 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax3=fig3.add_subplot(1,1,1)
        ax3.imshow(chull, cmap=plt.cm.gray)#color_img)
        ax3.set_title('convex premeter', fontsize=5)
        for n, contour in enumerate(contours):
            ax3.plot(contour[:, 1], contour[:, 0], '-r',linewidth=0.5)
        ax3.set_xticks([])
        ax3.set_yticks([])
        label_image = skimage.measure.label(convex_edge,  connectivity=2)
        regions = skimage.measure.regionprops(label_image)
        minr, minc, maxr, maxc = regions[0].bbox
        y0, x0 = regions[0].centroid
        H,W=np.where(img[:,:,0]>0)
        h_max=np.where(H==max(H))[0][0]
        h_min=np.where(H==min(H))[0][0]
        w_max=np.where(W==max(W))[0][0]
        w_min=np.where(W==min(W))[0][0]
        r = round((((H[h_max]-H[h_min])**2)+((W[h_max]-W[h_min])**2))**0.5) ##circle and axis
        c = round((((H[w_max]-H[w_min])**2)+((W[w_max]-W[w_min])**2))**0.5) ##circle and axis
        fig4 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax4=fig4.add_subplot(1,1,1)
        ax4.set_title('plant diameter', fontsize=5)
        angle=atan((W[h_max]-W[h_min])/(H[h_max]-H[h_min]))*180/pi
        if img.shape[0]>img.shape[1]:
            circle = mpatches.Ellipse((x0, y0), min(r,c), max(r,c), angle=angle, edgecolor='red', fill=False)
        else:
            circle = mpatches.Ellipse((x0, y0), max(r,c), min(r,c), angle=angle, edgecolor='red', fill=False)
        dy=(W[h_max]-W[h_min])
        dx=(H[h_max]-H[h_min])
        x_long, y_long=minc+W[h_min], minr+H[h_min]
        line1=mpatches.FancyArrow(x_long, y_long,dy,dx,width=2, head_width=5, head_length=1, color='r')
        dx=(H[w_max]-H[w_min])
        dy=(W[w_max]-W[w_min])
        x_width, y_width=minc+W[w_min], minr+H[w_min]
        line2=mpatches.FancyArrow(x_width, y_width,dy,dx,width=2, head_width=5, head_length=1, color='b')
        ax4.imshow(color_img, cmap='gray', interpolation='nearest')
        ax4.add_patch(circle)
        ax4.add_patch(line1)
        ax4.add_patch(line2)
        ax4.axis('off')
        axesLength = (int(c/2), int(r/2))
        circleimg=np.zeros(img.shape,np.uint8)## ellipse premiter
        center_coordinates = (int(x0), int(y0))
        angle = 0
        startAngle = 0
        endAngle = 360
        color = (255, 255, 255) 
        thickness = -1
        circleimg = cv2.ellipse(circleimg, center_coordinates, axesLength, angle, startAngle, endAngle, color, thickness)
        My_img=circleimg[:,:,2]>0
        circle_prem=skimage.measure.perimeter(My_img, neighbourhood=8)
        my_parameter.append([Proj_area, plant_prem, convex_area, convex_pre, max(r,c), min(r,c), circle_prem, compact, stock])
    elif parts>1:
        chull_img=np.zeros(img.shape)
        fig4 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax4=fig4.add_subplot(1,1,1)
        ax4.set_title('Plant diameter', fontsize=5)
        ax4.imshow(color_img, cmap='gray', interpolation='nearest')
        ax4.axis('off')
        cordinates=[]
        for region in skimage.measure.regionprops(label_image):
            if region.area >= 50:
                minr, minc, maxr, maxc = region.bbox
                cordinates.append([minr, minc, maxr, maxc])
        cordinates2=cords(cordinates)
        for cor in cordinates2:
            img_part=img[cor[0]:cor[2], cor[1]:cor[3],0]
            img_parts=img2[cor[0]:cor[2], cor[1]:cor[3],0]
            img_parts=np.asarray(img_parts, np.uint8)
            H,w=np.where(img_part>5)
            projected_leave_area=len(H)
            contours = skimage.measure.find_contours(img_parts, 0.02, fully_connected='high')
            region_img_parts=np.zeros(img_parts.shape)
            for n, contour in enumerate(contours):
                for i in range(contour.shape[0]):
                    region_img_parts[int(contour[i,0]), int(contour[i,1])]=255
            kernel = np.ones((1,2), np.uint8)  # note this is a horizontal kernel
            d_im = cv2.dilate(region_img_parts, kernel, iterations=6)
            e_im = cv2.erode(d_im, kernel, iterations=5)
            region_prem=(e_im>0)
            plant_prem=skimage.measure.perimeter(region_prem, neighbourhood=4)
            Img_Parts=img_parts>0
            chull = convex_hull_image(Img_Parts)
            h,w=np.where(chull==True)
            projected_convex_area=len(h)
            convex_pre=skimage.measure.perimeter(chull, neighbourhood=8) # convex hull
            chull_img[cor[0]:cor[2], cor[1]:cor[3],0]=chull
            chull_img[cor[0]:cor[2], cor[1]:cor[3],1]=chull
            chull_img[cor[0]:cor[2], cor[1]:cor[3],2]=chull
            if projected_convex_area>0:
                compact=projected_leave_area*100/projected_convex_area ### compacteness
            else:
                compact=np.nan
            if plant_prem>0:
                stock=(4*np.pi*projected_leave_area)/plant_prem**2 ### Stockiness
            else:
                stock=np.nan
            minR, minC, maxR, maxC=cor[0],cor[1], cor[2],cor[3]
            y0, x0 = minR+(maxR-minR)/2, minC+(maxC-minC)/2
            H,W=np.where(img_parts>0)
            h_max=np.where(H==max(H))[0][0]
            h_min=np.where(H==min(H))[0][0]
            w_max=np.where(W==max(W))[0][0]
            w_min=np.where(W==min(W))[0][0]
            r = round((((H[h_max]-H[h_min])**2)+((W[h_max]-W[h_min])**2))**0.5) ## minmum radiuse
            c = round((((H[w_max]-H[w_min])**2)+((W[w_max]-W[w_min])**2))**0.5) ## maximum radiuse
            angle=atan((W[h_max]-W[h_min])/(H[h_max]-H[h_min]))*180/pi
            if img_parts.shape[0]>img_parts.shape[1]:
                circle = mpatches.Ellipse((x0, y0), min(r,c), max(r,c), angle=angle, edgecolor='red', fill=False)
            else:
                circle = mpatches.Ellipse((x0, y0), max(r,c), min(r,c), angle=angle, edgecolor='red', fill=False)
            ax4.add_patch(circle)
            axesLength = (int(c/2), int(r/2))
            circleimg=np.zeros(img.shape,np.uint8) 
            center_coordinates = (int(x0), int(y0)) ##filled circle
            angle = 0
            startAngle = 0
            endAngle = 360
            color = (255, 255, 255) 
            thickness = -1
            circleimg = cv2.ellipse(circleimg, center_coordinates, axesLength, 
                       angle, startAngle, endAngle, color, thickness) ## ellipse premiter
            My_img=circleimg[:,:,2]>0
            circle_prem=skimage.measure.perimeter(My_img, neighbourhood=8)
            my_parameter.append([projected_leave_area, plant_prem, projected_convex_area, convex_pre, max(r,c), min(r,c), circle_prem, compact, stock])
        fig2 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax2=fig2.add_subplot(1,1,1)
        ax2.imshow(chull_img, cmap=plt.cm.gray)
        ax2.set_title('Convex hull', fontsize=5)
        ax2.set_xticks([])
        ax2.set_yticks([])
        contours = skimage.measure.find_contours(chull_img[:,:,0],0.2, fully_connected='high')
        fig3 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax3=fig3.add_subplot(1,1,1)
        ax3.imshow(color_img)
        ax3.set_title('Convex premeter', fontsize=5)
        for n, contour in enumerate(contours):
            ax3.plot(contour[:, 1], contour[:, 0], '-r',linewidth=0.5)
        ax3.set_xticks([])
        ax3.set_yticks([])
    if display==True:
        colums=['Proj_area', 'plant_prem', 'convex_area', 'convex_pre', 'Major_axis', 'Minor_axis', 'circle_prem', 'Compactness', 'Stockiness']
        df_all_parameter=pd.DataFrame(my_parameter, columns=colums)
        try:
            os.mkdir(path+'/Excel files')
            writer = pd.ExcelWriter(path+'/Excel files/'+name+'_geometric.xlsx', engine='xlsxwriter')
        except:
            writer = pd.ExcelWriter(path+'/Excel files/'+name+'_geometric.xlsx', engine='xlsxwriter')
        writer.book.use_zip64()
        df_all_parameter.to_excel(writer, index=False)
        writer.save()
        speak('The morphological features saved')
        root3=tkinter.Tk()
        root3.title("Plant geometric features")
        root3.wm_iconbitmap('DAAI logo.ico')
        root3.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        canvas = FigureCanvasTkAgg(fig1, master=root3)
        canvas.get_tk_widget().grid(row = 0, column=0)
        canvas.draw()
        canvas = FigureCanvasTkAgg(fig2,master=root3)
        canvas.get_tk_widget().grid(row = 0, column=1)
        canvas.draw()
        canvas = FigureCanvasTkAgg(fig3,master=root3)
        canvas.get_tk_widget().grid(row = 1, column=0)
        canvas.draw()
        canvas = FigureCanvasTkAgg(fig4, master=root3)
        canvas.get_tk_widget().grid(row = 1, column=1)
        canvas.draw()
        fig1.savefig(path+'/'+name+'_Plant premeter.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        fig2.savefig(path+'/'+name+'_Convex hull.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        fig3.savefig(path+'/'+name+'_Convex premeter.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        fig4.savefig(path+'/'+name+'_Plant diameter.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        root3.mainloop()
    else:
        pass
    my_parameter=np.asarray(my_parameter)
    return my_parameter
def save_excel(INFILE, IMAGE, WAVE, names, H): #Function_21 for save excel file
    MY_PATH=INFILE.split('/')
    name=MY_PATH[-1].split('.')
    my_path='/'.join(MY_PATH[:-1])
    try:
        os.mkdir(my_path+'/Excel files')
        writer = pd.ExcelWriter(my_path+'/Excel files/'+name[0]+'_'+names+'_HSI_PP.xlsx', engine='xlsxwriter')
    except: 
        writer = pd.ExcelWriter(my_path+'/Excel files/'+name[0]+'_'+names+'_HSI_PP.xlsx', engine='xlsxwriter')
    writer.book.use_zip64()
    Hh=int(H)
    if len(IMAGE.shape)==3:
        img=IMAGE[:,:,Hh]
        non_zero=np.nonzero(img)
        min_value=np.min(img[non_zero])
        height, width=np.where(img>min_value)
        image_mean=np.mean(IMAGE[height, width,:], 0)
        df_image_mean=pd.DataFrame([image_mean], columns=WAVE)
        df_image_mean.to_excel(writer, sheet_name='reflect', index=False)
    elif len(IMAGE.shape)==2:
        image_mean=IMAGE
        df_image_mean=pd.DataFrame(image_mean, columns=WAVE)
        df_image_mean.to_excel(writer, sheet_name='reflect', index=False)    
    writer.save()
    if os.path.isfile(my_path+'/Excel files/'+name[0]+'_'+names+'_HSI_PP.xlsx'):
        speak('The excel file have been saved')
def save_mat_file(INFILE, image, wavelength, names, spek): #Function_22 for save mat file
    if spek==1:
        speak('Please wait for saving hypercube')
    MY_PATH=INFILE.split('/')
    name=MY_PATH[-1].split('.')
    my_path='/'.join(MY_PATH[:-1])
    if name[1]=='mat':
        meanband, first_part, last_part=open_hdr_file(INFILE, 'txt')
    else:
        meanband, first_part, last_part=open_hdr_file(INFILE, 'hdr')
    def save_mats(images, namess):
        try:
            os.mkdir(my_path+'/Mat files')
            savemat(my_path+'/Mat files/'+name[0]+'_'+namess+'_HSI_PP.mat', mdict={'img': images})
        except: 
            savemat(my_path+'/Mat files/'+name[0]+'_'+namess+'_HSI_PP.mat', mdict={'img': images})
        if 'samples' in first_part:
            file_start1=re.search('\nsamples', first_part)
            First_part=first_part[:file_start1.start()]
        else:
            First_part=first_part
        Default_Bands=wave2index(wavelength, [640, 550, 460])
        middle_part=convert(wavelength, 1)
        author="This program designed by: \n\t\t\t  (Ahmed Islam ElManawy) \nfor contact: \n\t   a.elmanawy_90@agr.suez.edu.eg\n"
        f=open(my_path+'/Mat files/'+name[0]+'_'+namess+'_HSI_PP.txt', 'w') ##for only write some thing at the end of the file this is append mode
        f.write(author)
        f.write(First_part)
        f.write('\nsamples = '+str(images.shape[1]))
        f.write('\nlines = '+str(images.shape[0]))
        try:
            f.write('\nbands = '+str(images.shape[2]))
        except:
            f.write('\nbands = 1')
        f.write('\ndefault bands={')
        f.write(convert(Default_Bands, 0))
        f.write('}\n')
        f.write('wavelength  = {')
        f.write(middle_part)
        f.write('}\n')
        f.write(last_part)
        f.close()
    if len(image.shape)==3 or len(image.shape)==2:
        save_mats(image, names)
    elif len(image.shape)==1 or len(image.shape)==4:
        for I in range(image.shape[0]):
            namess=names+' '+str(I+1)
            save_mats(image[I], namess)
    if spek==1:
        speak('The hypercube has been saved!')
def select_infile(filt=None,title=None,mask=None, name=None): ## window for select image file or excel file
    root = tkinter.Tk()
    root.withdraw()
    if filt is None:
        filetypes=[('anyfile','*.*')]
    else:
        filetypes=[(name,filt)]
    filename = tkinter.filedialog.Open(filetypes=filetypes,title=title).show()
    root.destroy()
    if filename == '':
        return None
    if mask:
        root = tkinter.Tk()
        root.withdraw()
        filetypes=[('anyfile','*.*')]
        maskname = tkinter.filedialog.Open(filetypes=filetypes,title='associated mask').show()
        root.destroy()
        if maskname:
            return (filename,maskname)
        else:
            return (filename,None)
    else:
        return filename
def convert(list, a):  
    s = [str(round(i, 4)) for i in list]
    if a ==1:
        res = ",\n".join(s)
    else:
        res = ",".join(s)
    return(res)
def open_hdr_file(INFILE, Ext): ##function_23 for open header file hdr or txt
    infile=INFILE[:-4]
    file_read=open(infile+'.'+Ext, 'r').read()
    if 'Wavelength' in file_read:
        FileSearch1=re.search('Wavelength', file_read)
    elif 'wavelength' in file_read:
        FileSearch1=re.search('wavelength', file_read)
    first_part=file_read[:FileSearch1.start()]
    File=file_read[FileSearch1.end():]
    FileSearch2=re.search('{', File)
    beginband=FileSearch2.end()
    File=File[beginband:]
    FileSearch3=re.search('}', File)
    endband=FileSearch3.start()
    meanband=File[:endband]
    last_part=File[endband:]
    return (meanband, first_part, last_part)
engine = wincl.Dispatch("SAPI.SpVoice")
engine.Volume = 100 # Volume 0-100
engine.Rate = 1 # Speed percent
def speak(audio): #function_24
    engine.speak(audio)
def greatMe():
    currentH = int(datetime.datetime.now().hour)
    if currentH >= 0 and currentH < 12:
        speak('Good Morning sir!')
    if currentH >= 12 and currentH < 18:
        speak('Good Afternoon sir!')
    if currentH >= 18 and currentH !=0:
        speak('Good Evening sir!')
def wave2index(wavelength, bands):
    wave=[]
    for WL in wavelength:
        wave.append(round(WL,4))   
    wave=np.asarray(wave)
    H=[]
    for I in range(len(bands)):
        min_wave=min(wave[np.nonzero(wave)])
        max_wave=max(wave[np.nonzero(wave)])
        if round(bands[I])>min_wave and round(bands[I])<max_wave: #in range or not
            if bands[I] in wave:
                h0=np.where(wave==bands[I])
                H.append(h0[0][0])
            elif bands[I] not in wave:
                h1=np.where(wave<bands[I])
                lowe=wave[h1[0][-1]] ## nearest low
                h2=np.where(wave>bands[I])
                heigh=wave[h2[0][0]] ## nearest high
                if (bands[I]-lowe)>(heigh-bands[I]):
                    H.append(h2[0][0])
                else:
                    H.append(h1[0][-1])
        elif round(bands[I])<=min_wave:
            h0=np.where(wave==min_wave)
            H.append(h0[0][0])
        elif round(bands[I])>=max_wave:
            h0=np.where(wave==max_wave)
            H.append(h0[0][0])
    Item=[]
    for item, count in collections.Counter(H).items(): # to remove repeat values
        if count > 1 or count==1:
            Item.append(item)
    return Item
def is_number(s):
    try:
        float(str(s))
        return 1
    except ValueError:
        return 0
def HDR_test(path):
    try:
        file=open(path[:-4]+'.hdr', 'r').read()
        return 1
    except:
        return 0
def adjust_gamma(image, gamma=1.0):
   invGamma = 1.0 / gamma
   table = np.array([((i / 255.0) ** invGamma) * 255
      for i in np.arange(0, 256)]).astype("uint8")
   return cv2.LUT(image, table)
def white(img):
    min_value=np.min(img)
    max_value=np.max(img)
    min_img=min_value*np.ones(img.shape)
    max_img=max_value*np.ones(img.shape)
    numerator=img-min_img
    denominator=max_img-min_img
    img_calib=numerator/denominator
    return img_calib
def extract_color_img(filterdImg, DefaultBands, Index):#Function_25
    DefaultBands.sort()
    image_segmented=np.zeros([filterdImg.shape[0], filterdImg.shape[1],3])
    br=1.2
    for c in range(image_segmented.shape[2]):
        img_default_band=filterdImg[:,:,DefaultBands[c]].copy()
        if np.max(img_default_band)>1:
            img_default_band=white(img_default_band)
            br=4.4
        image_segmented[:,:,c]=img_default_band*255
    image_segmented=image_segmented.astype(np.uint8)
    image_filter = Image.fromarray(image_segmented)
    brightness = ImageEnhance.Brightness(image_filter)
    image_filter2=brightness.enhance(br)## for image brightness 
    contrast=ImageEnhance.Contrast(image_filter2)
    image_filter4=contrast.enhance(2.2)## for change image contrast
    sharpness=ImageEnhance.Sharpness(image_filter4)
    image_filter3=sharpness.enhance(1.7) ## for image sharpness
    image_segmented = cv2.cvtColor(np.array(image_filter3), cv2.COLOR_RGB2BGR) #to convert from pil to cv2
    h,w=np.where(filterdImg[:, :, Index]>0)
    Binarry_IMAGE=np.zeros([filterdImg.shape[0], filterdImg.shape[1],3])
    Binarry_IMAGE[h,w,:]=255
    Binarry_IMAGE=Binarry_IMAGE.astype(np.uint8)
    masked_img_green=np.zeros(image_segmented.shape, image_segmented.dtype)
    masked_img_green[h,w,:]=image_segmented[h,w,:]
    masked_img_green = adjust_gamma(masked_img_green, gamma=1.5)
    return masked_img_green, Binarry_IMAGE
def plot_confusion_matrix(y_true, y_pred, frame, path, name, ACC, Acc_valid, labelnames, tabname): #Function_26
    window_title="Statistical measures_"+name
    cm = metrics.confusion_matrix(y_true, y_pred)
    cm = cm.astype('float')*100 / cm.sum(axis=1)[:, np.newaxis]
    if len(labelnames)>1:
        class_names =labelnames
    else:
        class_names =unique_labels(y_true, y_pred)
    trick=[]
    st=int(min(y_true))
    end=int(max(y_true))
    for i in range(st,end+1):
        trick.append(str(i))
    fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax= fig.add_subplot(111)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set(xticks=np.arange(cm.shape[1]), yticks=np.arange(cm.shape[0]), xticklabels=class_names, yticklabels=class_names)
    ax.tick_params(axis='x', colors='k', grid_color='w',labelsize=5)
    ax.tick_params(axis='y', colors='k',grid_color='w',labelsize=5)
    ax.set_xlabel('Predicted label', fontproperties=font)
    ax.set_ylabel('True label', fontproperties=font)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor") # Rotate the tick labels and set their alignment.
    thresh = cm.max() 
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], '.1f')+'%',
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "red", fontproperties=font)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    cm = metrics.confusion_matrix(y_true, y_pred)
    FP = cm.sum(axis=0) - np.diag(cm)  
    FN = cm.sum(axis=1) - np.diag(cm)
    TP = np.diag(cm)
    TN = cm.sum() - (FP + FN + TP)
    try:
        F_measure=metrics.f1_score(y_true, y_pred) #F-score or F-measure
    except:
        F_measure=metrics.f1_score(y_true, y_pred, average='weighted') #F-score or F-measure
    Prec = TP/(TP+FP) # Precision or positive predictive value
    Sens = TP/(TP+FN) # Sensitivity, hit rate, recall, or true positive rate
    Spec = TN/(TN+FP)  # Specificity or true negative rate
    MAc=sum(np.diag(cm))/cm.sum()
    root = tkinter.Tk()
    root.title(window_title)
    style = ttk.Style(root)
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.configure(highlightthickness=3, highlightbackground="black")
    root.resizable(0, 0)
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    cells = {}
    i=0
    b = ttk.Label(root, text = '', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0)
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '\t'+str(class_names[j-1])+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=1
    b = ttk.Label(root, text = '------------------', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0)
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '------------------', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=2
    b = ttk.Label(root, text = '\tTP:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(TP[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=3
    b = ttk.Label(root, text = '\tFP:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(FP[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=4
    b = ttk.Label(root, text = '\tFN:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(FN[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=5
    b = ttk.Label(root, text = '\tTN:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(TN[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=6
    b = ttk.Label(root, text = '     Precision:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(Prec[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=7
    b = ttk.Label(root, text = '     Sensitivity:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(Sens[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=8
    b = ttk.Label(root, text = '     Specificity:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    for j in range(1,cm.shape[0]+1): #Columns
        b = ttk.Label(root, text = '|\t'+str(format(Spec[j-1],'.2f'))+'\t|', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
        b.grid(row=i, column=j)
        cells[(i,j)] = b
    i=9
    b = ttk.Label(root, text = 'F-measure:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    b = ttk.Label(root, text = '|\t'+str(format(F_measure,'.2f'))+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=1)
    i=10
    b = ttk.Label(root, text = 'Accuracy_valid:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    b = ttk.Label(root, text = '|\t'+str(format((MAc*100),'.2f'))+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=1)
    i=11
    b = ttk.Label(root, text = 'Accuracy_valid:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    b = ttk.Label(root, text = '|\t'+Acc_valid.split(',')[0]+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=1)
    b = ttk.Label(root, text = '|\t'+Acc_valid.split(',')[1]+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=2)
    i=12
    b = ttk.Label(root, text = 'Accuracy_calib:', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=0, sticky='ew')
    b = ttk.Label(root, text = '|\t'+str(format((ACC*100),'.2f'))+'\t', width = 15, style="BW.TLabel", font=('Times New Roman', 15))
    b.grid(row=i, column=1)
    def save_plot(path, name):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_'+tabname+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        try:
            root.deiconify()
            raise_above_all(root)
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                x, y, x1, y1 = win32gui.GetClientRect(hwnd)
                x, y = win32gui.ClientToScreen(hwnd, (x, y))
                x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
                im = pyautogui.screenshot(region=(x, y, x1, y1))
                im.save(my_path+'/'+names[0]+'_'+tabname+'_'+window_title+'.jpg')
        except:
            pass
        speak('The plot has been saved')
    ttk.Button(frame, text = "Save plot", command=lambda:save_plot(path, name), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
    root.mainloop()
def VI_bandselection(path, X_data, label, Y_data, statusbar): #Function_27
    root = tkinter.Tk()
    root.title("VIs band selection")
    style = ttk.Style(root)
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.configure(highlightthickness=3, highlightbackground="black")
    root.resizable(0, 0)
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    def select_bands(X,Y,VI):
        VI+=1
        results=np.zeros((X.shape[1], X.shape[1]))
        MSE=[]
        try:# for classification
            check_classification_targets(Y)
            estimator = LDA(solver='lsqr', shrinkage='auto')
            score=1
        except:
            estimator=LinearRegression()
            MSE=np.zeros((X.shape[1], X.shape[1]))
            score=2
        for n in range(X.shape[1]):
            for h in range(X.shape[1]):
                if n!=h:
                    if VI==1:
                        VIS=(X[:,n]-X[:,h])/((X[:,n]+X[:,h])) #NDVI
                    elif VI==2:
                        VIS=(X[:,n]-X[:,h])/((X[:,n]+X[:,h])**0.5) #RNDVI
                    elif VI==3:
                        VIS=1.16*((X[:,n]-X[:,h])/((X[:,n]+X[:,h])+0.16)) #OSAV
                    elif VI==4:
                        VIS=(X[:,n]/X[:,h]) #SR
                    elif VI==5:
                        VIS=(X[:,n]/X[:,h])-1 #CI
                    elif VI==6:
                        VIS=((X[:,n]/X[:,h])-1)/(((X[:,n]/X[:,h])+1)**0.5) #MSR
                    elif VI==7:
                        VIS=(X[:,n]-X[:,h]) #SD
                    elif VI==8:
                        VIS=2.5*((X[:,n]-X[:,h])/(X[:,n]+(2.4*X[:,h])+1)) #EVI2 Jiang, Z., Huete, A.R., Didan, K., Miura, T., 2008. Development of a two-band enhanced vegetation index without a blue band. Remote Sens. Environ. 112, 3833–3845.
                    elif VI==9:
                        VIS=X[:,n]/((X[:,n]+X[:,h])) #FD Disease index Moshou, D., Bravo, C., Oberti, R., West, J., Bodria, L., McCartney, A., Ramon, H., 2005. Plant disease detection basedondata fusion of hyper-spectral and multi-spectral fluorescence imaging using Kohonen maps. Real-Time Imaging 11 (2), 75–83.
                    elif VI==10:
                        VIS=(1/X[:,n])-(1/X[:,h]) #VISS Gitelson AA, Gritz Y, Merzlyak MN. Relationships between leaf chlorophyll content and spectral reflectance and algorithms for nondestructive chlorophyll assessment in higher plant leaves. J Plant Physiol. 2003;160:271–82.
                    elif VI==11:
                        VIS=np.abs((X[:,n]-X[:,h]))/((X[:,n]+X[:,h])) #ND A robust vegetation index for remotely assessing chlorophyll content of dorsiventral leaves across several species in different seasons
                    elif VI==12:
                        VIS=((0.1*X[:,n])-X[:,h])/(((0.1*X[:,n])+X[:,h]))#Wide Dynamic Range Vegetation Index (WDRVI) Gitelson, A.A. (2004) Wide dynamic range vegetation index for remote quantification of biophysical characteristics of vegetation. Journal of Plant Physiology 161, 165–173.
                    VIS[np.where(VIS==np.inf)]=0
                    VIS[np.where(np.isnan(VIS))]=0
                    X_train, X_test, Y_train, Y_test=train_test_split(VIS, Y, test_size=(1/3), random_state=42)
                    X_train=X_train.reshape(-1,1)
                    X_test=X_test.reshape(-1,1)
                    model=estimator.fit(X_train, Y_train.ravel())
                    Y_pred=model.predict(X_test)
                    if score==1:
                        acc=round(metrics.accuracy_score(Y_test, Y_pred)*100, 2)
                    elif score==2:
                        acc=metrics.r2_score(Y_test, Y_pred) #R2
                        mse_p = metrics.mean_squared_error(Y_test, Y_pred)
                        MSE[n,h]=mse_p
                    results[n,h]=acc
                else:
                    pass
        if score==1:
            band1, band2=np.where(results==np.max(results))
        elif score==2:
            min_mse=min(MSE[np.nonzero(MSE)])
            band1, band2=np.where(MSE==min_mse)
        return results, band1, band2
    def select_VI(X, n, h, VI):
        VI+=1
        if VI==1:
            VIS2=(X[:,n]-X[:,h])/((X[:,n]+X[:,h])) #NDVI
        elif VI==2:
            VIS2=(X[:,n]-X[:,h])/((X[:,n]+X[:,h])**0.5) #RNDVI
        elif VI==3:
            VIS2=1.16*((X[:,n]-X[:,h])/((X[:,n]+X[:,h])+0.16)) #OSAV
        elif VI==4:
            VIS2=(X[:,n]/X[:,h]) #SR
        elif VI==5:
            VIS2=(X[:,n]/X[:,h])-1 #CI
        elif VI==6:
            VIS2=((X[:,n]/X[:,h])-1)/(((X[:,n]/X[:,h])+1)**0.5) #MSR
        elif VI==7:
            VIS2=(X[:,n]-X[:,h]) #SD
        elif VI==8:
            VIS2=2.5*((X[:,n]-X[:,h])/(X[:,n]+(2.4*X[:,h])+1)) #EVI2 Jiang, Z., Huete, A.R., Didan, K., Miura, T., 2008. Development of a two-band enhanced vegetation index without a blue band. Remote Sens. Environ. 112, 3833–3845.
        elif VI==9:
            VIS2=X[:,n]/((X[:,n]+X[:,h])) #FD Disease index Moshou, D., Bravo, C., Oberti, R., West, J., Bodria, L., McCartney, A., Ramon, H., 2005. Plant disease detection basedondata fusion of hyper-spectral and multi-spectral fluorescence imaging using Kohonen maps. Real-Time Imaging 11 (2), 75–83.
        elif VI==10:
            VIS2=(1/X[:,n])-(1/X[:,h]) #VISS Gitelson AA, Gritz Y, Merzlyak MN. Relationships between leaf chlorophyll content and spectral reflectance and algorithms for nondestructive chlorophyll assessment in higher plant leaves. J Plant Physiol. 2003;160:271–82.
        elif VI==11:
            VIS2=np.abs((X[:,n]-X[:,h]))/((X[:,n]+X[:,h])) #ND A robust vegetation index for remotely assessing chlorophyll content of dorsiventral leaves across several species in different seasons
        elif VI==12:
            VIS2=((0.1*X[:,n])-X[:,h])/(((0.1*X[:,n])+X[:,h]))
        VIS2=np.asarray(VIS2)
        VIS2[np.where(VIS2==np.inf)]=0
        VIS2[np.where(np.isnan(VIS2))]=0
        return VIS2
    VIs=['NDVI', 'RNDVI', 'OSAV', 'SR', 'CI', 'MSR', 'SD', 'EVI2', 'FD', 'VISS', 'ND', 'WDRVI']
    VI=ttk.Combobox(root, values=VIs, width=10, font=('Times New Roman', 15), justify='center')
    VI.set("NDVI")
    VI.grid( row = 0, column = 2, sticky='ew')
    ttk.Label(root, text='VI', style="BW.TLabel", font=('Times New Roman', 15)).grid( row = 0, column = 1,  sticky='ew')
    def VI_cal(X, Y, Index, label, path):
        statusbar['text']='calculate best bands for '+ VIs[Index]+'...'
        speak('Please wait for calculate '+ VIs[Index])
        results, b1, b2=select_bands(X,Y,Index)
        VIS2=select_VI(X, b1[0], b2[0],Index)
        YA=XA=label
        min_value=min(results[np.nonzero(results)])
        max_value=max(results[np.nonzero(results)])
        fig = Figure(figsize=(3,3), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax = fig.add_subplot(111)
        contour = ax.contourf(XA, YA, results, levels=np.linspace(min_value,max_value,100), cmap=plt.get_cmap('rainbow'))#(float('%.3f'%min(Map_band)),float('%.3f'%max(Map_band)), int(4*max(Map_band)/min(Map_band))))
        ax.set_xlim(YA[0], YA[-1])
        ax.set_ylim(XA[0], XA[-1])
        ax.tick_params(axis='x', colors='k', grid_color='w',labelsize=5, labelrotation=45)
        ax.tick_params(axis='y', colors='k',grid_color='w',labelsize=5)
        fig.colorbar(contour, aspect=50, fraction=.12,pad=.02).ax.tick_params(labelsize=5)
        ax.set_xlabel('Wavelength1,(nm)', color='red', fontsize=5)
        ax.set_ylabel('Wavelength2,(nm)', color='red', fontsize=5)
        label=np.asarray(label)
        Band1=label[b1]
        Band2=label[b2]
        ax.set_title('Selected bands: '+str(Band1[0].astype(int))+","+str(Band2[0].astype(int)), fontsize=5)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().grid(row = 2, column=0, columnspan=4, rowspan=2, sticky='nswe')
        canvas.draw()
        def save_plot(path):
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            fig.savefig(my_path+'/'+names[0]+'_'+VIs[Index]+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
            speak('The plot has been saved')
        def save_excel(path, Y_data, VIS2, B1, B2):
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            h=[B1, B2]
            bands_value=X[:, h]
            df_vis = pd.DataFrame(VIS2, columns=[VIs[Index]])
            df_y = pd.DataFrame(Y_data, columns=['Y'])
            df_value=pd.DataFrame(bands_value, columns=[str(Band1[0].astype(int)), str(Band2[0].astype(int))])
            writer = pd.ExcelWriter(my_path+'/'+names[0]+'_'+VIs[Index]+'.xlsx', engine='xlsxwriter')
            writer.book.use_zip64()
            df_value.to_excel(writer, sheet_name=VIs[Index], index=False)
            df_vis.to_excel(writer, sheet_name=VIs[Index], index=False, startcol=2)
            df_y.to_excel(writer, sheet_name=VIs[Index], index=False, startcol=3)
            writer.save()
            speak('The excel file has been saved')
        ttk.Button(root, text = "Save excel", command=lambda:save_excel(path, Y_data, VIS2, b1[0], b2[0]), style='my.TButton', width=20).grid( row = 1, column = 1, columnspan=2, sticky='ew')
        ttk.Button(root, text = "Save plot", command=lambda:save_plot(path), style='my.TButton', width=20).grid( row = 1, column = 3, sticky='ew')
    ttk.Button(root, text = "Calculate", command=lambda:VI_cal(X_data, Y_data, VI.current(), label, path), style='my.TButton', width=20).grid( row = 1, column = 0, sticky='ew')
    ttk.Button(root, text = "Save plot",  style='my.TButton', width=20).grid( row = 1, column = 3, sticky='ew')
    root.mainloop()
def wavelength_CFS(path, X_data, label, Y_data): #Function_28 CORRELATION-BASED FEATURE SELECTION (CFS) correlation coefficient between features and the output variable
    root = tkinter.Tk()
    root.title("CFS")
    style = ttk.Style(root)
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.configure(highlightthickness=3, highlightbackground="black")
    root.resizable(0, 0)
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    def CFS(X,Y):
        results=[]
        MSE=[]
        try:# for classification
            check_classification_targets(Y)
            estimator = LDA(solver='lsqr', shrinkage='auto')
            score=1
        except:
            estimator=LinearRegression()
            score=2
        for n in range(X.shape[1]):       
            X_train, X_test, Y_train, Y_test=train_test_split(X[:,n], Y, test_size=(1/3), random_state=42)
            X_train=X_train.reshape(-1,1)
            X_test=X_test.reshape(-1,1)
            model=estimator.fit(X_train, Y_train.ravel())
            Y_pred=model.predict(X_test)
            if score==1:
                acc=round(metrics.accuracy_score(Y_test, Y_pred)*100, 2)
            elif score==2:
                acc=metrics.r2_score(Y_test, Y_pred) #R2
                mse_p = metrics.mean_squared_error(Y_test, Y_pred)
                MSE.append(mse_p)
            results.append(acc)
        return results, MSE
    try:# for classification
        check_classification_targets(Y_data)
        thresh=list(range(20,100, 5))
    except:
        thresh=list(np.arange(0,1, 0.1))
    thr=ttk.Combobox(root, values=thresh, width=10, font=('Times New Roman', 15), justify='center')
    thr.set(thresh[0])
    thr.grid( row = 0, column = 2, sticky='ew')
    ttk.Label(root, text='Threshold', style="BW.TLabel", font=('Times New Roman', 15)).grid( row = 0, column = 1,  sticky='ew')
    results, MSE=CFS(X_data,  Y_data)
    ACC=np.asarray(results)
    MSE=np.asarray(MSE)
    fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax = fig.add_subplot(111)
    ax.plot(label, ACC, color='r', label='o', linewidth=0.5)
    if len(MSE)>0:
        ax2 = ax.twinx()
        ax2.plot(label, MSE, color='k', label='*', linewidth=0.5)
        ax2.set_ylabel('MSE', fontproperties=font)
        ax.set_ylabel('R2',  color='r', fontproperties=font)
        ax2.tick_params(axis='y', labelsize=5)
    else:
        ax.set_ylabel('Accuracy (%)', fontproperties=font)
    ax.set_xlabel('Wavelength (nm)', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row = 2, column=0, columnspan=4, sticky='nswe')
    canvas.draw()
    def save_plot(path):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_CFS.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        speak('The plot has been saved')
    def CFS_cal(ACC, MSE, X, Y, label, path, thresh):
        h=np.where(ACC>thresh)
        x_selected=X[:,h[0]]
        labels=np.asarray(label)
        labels_select=labels[h[0]]
        if x_selected.shape[0]>0:
            fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
            ax = fig.add_subplot(111)
            ax.plot(label, ACC, color='r', label='o', linewidth=0.5)
            if len(MSE)>0:
                ax2 = ax.twinx()
                ax2.plot(label, MSE, color='k', label='*', linewidth=0.5)
                ax2.set_ylabel('MSE', fontproperties=font)
                ax.set_ylabel('R2',  color='r', fontproperties=font)
                ax2.tick_params(axis='y', labelsize=5)
            else:
                ax.set_ylabel('Accuracy (%)', fontproperties=font)
            ax.scatter(labels_select, ACC[h[0]], c='blue', edgecolors='blue', s=5)
            ax.set_xlabel('Wavelength (nm)', fontproperties=font)
            ax.tick_params(axis='x', labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().grid(row = 2, column=0, columnspan=4, sticky='nswe')
            canvas.draw()
            ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, x_selected, Y, labels_select), style='my.TButton').grid(row = 4, column=1, columnspan=2, sticky='w') 
            def excel_save(path, x_selector, Y_data, labels):
                MY_PATH=path.split('/')
                my_path='/'.join(MY_PATH[:-1])
                names=MY_PATH[-1].split('.')
                df_X = pd.DataFrame(x_selector, columns=labels)
                df_y = pd.DataFrame(Y_data)
                writer = pd.ExcelWriter(my_path+'/'+names[0]+'_CFS.xlsx', engine='xlsxwriter')
                writer.book.use_zip64()
                df_X.to_excel(writer, sheet_name='X_select', index=False)
                df_y.to_excel(writer, sheet_name='X_select', index=False, startcol=int(x_selector.shape[1]))
                writer.save()
                fig.savefig(my_path+'/'+names[0]+'_uncorrelated.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
                speak('The excel file has been saved')
    ttk.Button(root, text = "Save plot", command=lambda:save_plot(path), style='my.TButton', width=20).grid( row = 1, column =3, columnspan=2, sticky='w')
    ttk.Button(root, text = "Select features", command=lambda:CFS_cal(ACC, MSE, X_data, Y_data, label, path, float(thr.get())), style='my.TButton', width=20).grid( row = 1, column = 0, columnspan=2, sticky='w')
    root.mainloop()
def WavelengthCorr(path, required_data, label, Y_data):#Function_29
    root = tkinter.Tk()
    root.title("Data correlation")
    style = ttk.Style(root)
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.configure(highlightthickness=3, highlightbackground="black")
    root.resizable(0, 0)
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    X_data=np.asarray(required_data.copy())
    X_datascale=StandardScaler().fit(X_data.T).transform(X_data.T).T
    required_datascale=np.asarray(required_data.copy())
    required_datascale=StandardScaler().fit(required_datascale.T).transform(required_datascale.T).T
    df = pd.DataFrame(data=required_datascale)
    correlation=df.corr(method='pearson')
    correlation=np.triu(correlation, k=-1)
    H,W=np.where(correlation==0)
    correlation[H,W]=2
    X=Y=label
    fig = Figure(figsize=(3,3), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax = fig.add_subplot(111)
    contour = ax.contourf(X, Y, correlation, levels=np.linspace(-1,1,50), cmap=plt.get_cmap('rainbow'))
    ax.set_xlim(Y[0], Y[-1])
    ax.set_ylim(X[0], X[-1])
    ax.tick_params(axis='x', colors='k', grid_color='w',labelsize=5, labelrotation=45)
    ax.tick_params(axis='y', colors='k',grid_color='w',labelsize=5)
    fig.colorbar(contour, aspect=50, fraction=.12,pad=.02).ax.tick_params(labelsize=5)
    ax.set_xlabel('Wavelength1,(nm)', color='red', fontsize=5)
    ax.set_ylabel('Wavelength2,(nm)', color='red', fontsize=5)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row = 2, column=0, columnspan=4, rowspan=2, sticky='nswe')
    canvas.draw()
    thresh=[]
    for t in range(50,100,5):
        thresh.append(t/100)
    THRESH=ttk.Combobox(root, values=thresh, width=5, font=('Times New Roman', 15), justify='center')
    THRESH.set("0.5")
    THRESH.grid( row = 0, column = 1, sticky='w')
    std_label=ttk.Label(root, text='Threshold', style="BW.TLabel", font=('Times New Roman', 15))
    std_label.grid( row = 0, column = 0,  sticky='e')
    ttk.Button(root, text = "Select feature", command=lambda:Threshold(required_datascale, float(THRESH.get()), label, Y_data), style='my.TButton').grid( row = 0, column = 2, sticky='w')
    def save_plot(path):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_corr.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        speak('The plot has been saved')
    ttk.Button(root, text = "Save plot", command=lambda:save_plot(path), style='my.TButton').grid( row = 4, column = 0, sticky='w')
    def Threshold(required_datascale, thresh, label, Y_data):
        label=np.asarray(label)
        while True:
            try:
                df = pd.DataFrame(data=required_datascale)
                correlat=df.corr(method='pearson')
                crr=np.asarray(np.abs(correlat))
                h,w=np.where((crr>thresh)& (crr<1))
                index=np.where((crr[:,min(h)]>thresh) & (crr[:,min(h)]<1))
                required_datascale=np.delete(required_datascale, index, 1)
            except:
                break
        required_datascale=np.asarray(required_datascale)
        selected_label=[]
        selected_index=[]
        for i in required_datascale[0,:]:
            H=np.where(X_datascale[0,:]==i)
            selected_label.append(label[H[0][0]])
            selected_index.append(H[0][0])
        selected_label=np.asarray(selected_label)
        selected_index=np.asarray(selected_index)
        X_selected=X_data[:,selected_index]
        if selected_label.shape[0]>0:
            fig = Figure(figsize=(3,3), tight_layout=True, dpi=300, facecolor='lightyellow')
            ax = fig.add_subplot(111)
            contour = ax.contourf(X, Y, correlation, levels=np.linspace(-thresh,thresh,40), cmap=plt.get_cmap('rainbow'))
            ax.set_xlim(Y[0], Y[-1])
            ax.set_ylim(X[0], X[-1])
            ax.tick_params(axis='x', colors='k', grid_color='w',labelsize=5, labelrotation=45)
            ax.tick_params(axis='y', colors='k',grid_color='w',labelsize=5)
            fig.colorbar(contour, aspect=50, fraction=.12,pad=.02).ax.tick_params(labelsize=5)
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().grid(row = 1, column=0, columnspan=4, rowspan=2, sticky='nswe')
            canvas.draw()
            ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, X_selected, Y_data, selected_label), style='my.TButton').grid(row = 0, column=3, ipadx=1, ipady=1, sticky='w') 
            def excel_save(path, x_selector, Y_data, labels):
                MY_PATH=path.split('/')
                my_path='/'.join(MY_PATH[:-1])
                names=MY_PATH[-1].split('.')
                df_X = pd.DataFrame(x_selector, columns=labels)
                df_y = pd.DataFrame(Y_data)
                writer = pd.ExcelWriter(my_path+'/'+names[0]+'_uncorrelated.xlsx', engine='xlsxwriter')
                writer.book.use_zip64()
                df_X.to_excel(writer, sheet_name='X_select', index=False)
                df_y.to_excel(writer, sheet_name='X_select', index=False, startcol=int(x_selector.shape[1]))
                writer.save()
                fig.savefig(my_path+'/'+names[0]+'_uncorrelated.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
                speak('The excel file has been saved')
    root.mainloop()
def plot_contour(img, min_value, max_value, frame, title, path, name, figsize,facecolor):#Function_30
    X_axis=np.array(range(img.shape[0])) ## lines direction ys
    Y_axis=np.array(range(img.shape[1])) ## sample direction xs
    fig = matplotlib.figure.Figure(figsize=figsize, tight_layout=True, dpi=300, facecolor=facecolor)
    ax2 = fig.add_subplot(111)
    if min_value==0 and max_value==0:
        min_value=min(img[np.nonzero(img)])
        max_value=max(img[np.nonzero(img)])
        ax1 = ax2.contourf(Y_axis, X_axis, img, levels=np.linspace(min_value,max_value,50), cmap=plt.get_cmap('CMRmap'))
    elif min_value==0 and max_value>0:
        min_value=min(img[np.nonzero(img)])
        ax1 = ax2.contourf(Y_axis, X_axis, img, levels=np.linspace(min_value,max_value,50), cmap=plt.get_cmap('CMRmap'))
    elif min_value==-1 and max_value>0:
        ax1 = ax2.contourf(Y_axis, X_axis, img, levels=range(min_value,max_value), cmap=plt.get_cmap('rainbow'))
    else:
        ax1 = ax2.contourf(Y_axis, X_axis, img, levels=np.linspace(min_value,max_value,50), cmap=plt.get_cmap('CMRmap'))
    ax2.set_xlim(Y_axis[0], Y_axis[-1])
    ax2.set_ylim(X_axis[-1], X_axis[0])
    fig.colorbar(ax1, ax=ax2, aspect=50, fraction=.12,pad=.02).ax.tick_params(labelsize=5)
    ax2.set_yticks([])
    ax2.set_xticks([])
    if title==[]:
        pass#ax2.set_title([])
    else:
        ax2.set_title(title, fontsize=5)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row = 0, column=0, rowspan=2, sticky='nswe')
    canvas.draw()
    if len(path)>0:
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
def plot_regression(Y_test, Y_predict, Y_train, Y_calibrate, frame, path, name, tab_name):#Function_31
    name=name+'_'+tab_name
    R2=metrics.r2_score(Y_test, Y_predict)
    mse=metrics.mean_squared_error(Y_test, Y_predict)
    RMSE=np.sqrt(mse) ## sqrt(np.mean((Y_test-Y_predict)**2))
    Rc2=metrics.r2_score(Y_train, Y_calibrate)
    msec=metrics.mean_squared_error(Y_train, Y_calibrate)
    RMSEC=np.sqrt(msec) ## sqrt(np.mean((Y_test-Y_predict)**2)) random error
    rangex = max(Y_test) - min(Y_test)
    fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax = fig.add_subplot(111)
    Max_lim=max(max(Y_test),  max(Y_predict))
    Min_lim=min(min(Y_predict), min(Y_test))
    try:
        min_lim = float(round(Min_lim[0], 1))
    except:
        min_lim = float(round(Min_lim, 1))
    try:
        max_lim = float(round(Max_lim[0], 1))
    except:
        max_lim = float(round(Max_lim, 1))
    ax.scatter(Y_test, Y_predict, c='red', edgecolors='red', s=5)
    ax.plot(np.arange(min_lim, max_lim+1), np.arange(min_lim, max_lim+1), color='black', linewidth=0.5)
    ax.set_xlabel('Measured %', fontproperties=font)
    ax.set_ylabel('Predicted %', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    handles = [mpatches.Rectangle((0, 0), 1, 1, fc="white", ec="white", lw=0, alpha=0)] * 4
    labels = []
    labels.append("$R_c^2$: {0:.4g}".format(np.round(Rc2, 2)))
    labels.append("$RMSE_c$: {0:.4g}".format(np.round(RMSEC, 2)))
    labels.append("$R_p^2$: {0:.4g}".format(np.round(R2, 2)))
    labels.append("$RMSE_p$: {0:.4g}".format(np.round(RMSE, 2)))
    ax.legend(handles, labels, loc='best', prop=font,  fancybox=True, framealpha=0.01, handlelength=0, handletextpad=0)
    step=round((max_lim-min_lim)/6, 1)
    ax.set_xlim(min_lim, max_lim+step)
    ax.set_ylim(min_lim, max_lim+step)
    try:
        ax.xaxis.set_ticks(np.arange(min_lim, max_lim+step, step))
        ax.yaxis.set_ticks(np.arange(min_lim, max_lim+step, step))
    except:
        ax.xaxis.set_ticks(np.arange(min_lim, max_lim+step, 0.05))
        ax.yaxis.set_ticks(np.arange(min_lim, max_lim+step, 0.05))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    def save_plot(path, name):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        df_Y_test = pd.DataFrame(Y_test, columns=['Test'])
        df_Y_predict = pd.DataFrame(Y_predict, columns=['Predict'])
        df_Y_train = pd.DataFrame(Y_train, columns=['Train'])
        df_Y_calibrate = pd.DataFrame(Y_calibrate, columns=['Calibrate'])
        writer = pd.ExcelWriter(my_path+'/'+names[0]+'_'+tab_name+'_'+name+'.xlsx', engine='xlsxwriter')
        writer.book.use_zip64()
        df_Y_test.to_excel(writer, sheet_name='TEST', index=False)
        df_Y_predict.to_excel(writer, sheet_name='TEST', index=False, startcol=1)
        df_Y_train.to_excel(writer, sheet_name='TRAIN', index=False)
        df_Y_calibrate.to_excel(writer, sheet_name='TRAIN', index=False, startcol=1)
        writer.save()
        speak('The plot has been saved')
    ttk.Button(frame, text = "Save plot", command=lambda:save_plot(path, name), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
def kennardstonealgorithm(x_variables, k):#Function_32
    x_variables = np.array(x_variables)
    original_x = x_variables
    distance_to_average = ((x_variables - np.tile(x_variables.mean(axis=0), (x_variables.shape[0], 1))) ** 2).sum(axis=1)
    max_distance_sample_number = np.where(distance_to_average == np.max(distance_to_average))
    max_distance_sample_number = max_distance_sample_number[0][0]
    selected_sample_numbers = list()
    selected_sample_numbers.append(max_distance_sample_number)
    remaining_sample_numbers = np.arange(0, x_variables.shape[0], 1)
    x_variables = np.delete(x_variables, selected_sample_numbers, 0)
    remaining_sample_numbers = np.delete(remaining_sample_numbers, selected_sample_numbers, 0)
    for iteration in range(1, k):
        selected_samples = original_x[selected_sample_numbers, :]
        min_distance_to_selected_samples = list()
        for min_distance_calculation_number in range(0, x_variables.shape[0]):
            distance_to_selected_samples = ((selected_samples - np.tile(x_variables[min_distance_calculation_number, :], (selected_samples.shape[0], 1))) ** 2).sum(axis=1)
            min_distance_to_selected_samples.append(np.min(distance_to_selected_samples))
        max_distance_sample_number = np.where(
            min_distance_to_selected_samples == np.max(min_distance_to_selected_samples))
        max_distance_sample_number = max_distance_sample_number[0][0]
        selected_sample_numbers.append(remaining_sample_numbers[max_distance_sample_number])
        x_variables = np.delete(x_variables, max_distance_sample_number, 0)
        remaining_sample_numbers = np.delete(remaining_sample_numbers, max_distance_sample_number, 0)
    return selected_sample_numbers, remaining_sample_numbers
def split_data(X,Y,perc):
    n,m=X.shape
    if n<500:
        number_of_selected_samples = round(n*perc)
        autoscaled_X = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
        test_sample, train_sample = kennardstonealgorithm(autoscaled_X, number_of_selected_samples)
        X_train=X[train_sample,:]
        X_test=X[test_sample, :]
        Y_train=Y[train_sample]
        Y_test=Y[test_sample]
    elif n>500:
        X_train, X_test,  Y_train, Y_test = train_test_split(X, Y, test_size=perc, random_state=42)
    return X_train, X_test,  Y_train, Y_test
def save_model(path, model, name):#Function_33
    filename=path+"/"+name+'.sav'
    pickle.dump(model, open(filename, 'wb'))
    speak('The model have been saved')
def loocv(mlp, x,  y):#Function_34
    i=x.shape[0]
    h=np.asarray(range(i))
    MSE=[]
    for I in range(i):
        h=np.delete(h,I)
        X_Train=x[h,:]
        Y_Train=y[h]
        X_test=x[I,:].reshape(-1,1).T
        Y_test=y[I].reshape(-1,1)
        model=mlp.fit(X_Train,  Y_Train)
        Y_Predict_Test=model.predict(X_test).reshape(-1,1)
        mse=metrics.mean_squared_error(Y_test, Y_Predict_Test)
        MSE.append(mse)
        h=np.asarray(range(i))
    MSE=np.asarray(MSE)
    return MSE
def Remove_Outliers(path, X,Y, X_name, col_name, statusbar, tab_name):#Function_35
    statusbar['text'] = ('Remove outliers from data.....')
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+' clean'
    h,w=X.shape
    root=tkinter.Tk()
    root.title("Remove outliers")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    pca=PCA(n_components=5).fit(X)
    score=pca.fit_transform(X.copy())
    n=3
    X_data=np.asarray(score)
    x_mean=np.mean(X_data, 0)
    x_std=np.std(X_data, 0)
    X_outliers1=x_mean+(n*x_std)
    X_outliers2=x_mean-(n*x_std)
    outlier_index=[]
    for i in range( X_outliers1.shape[0]):
       h=np.where(X_data[:,i]>=X_outliers1[i])
       if len(h[0])>0:
           for H in h[0]:
               outlier_index.append(H)
       h=np.where(X_data[:,i]<=X_outliers2[i])
       if len(h[0])>0:
           for H in h[0]:
               outlier_index.append(H)
    fig = Figure(figsize=(3,3), tight_layout=True, dpi=300, facecolor='lightyellow')
    color=['b', 'k', 'r','y', 'g', 'c', 'm']
    marker=['o', 'v', '^', 's', 'p', '*', '+']
    ax = fig.add_subplot(111)
    for I in range(int(min(Y)), int(max(Y))+1):
        if I<=7:
            h=np.where(Y==I)[0]
            ax.scatter(x=score[:,0][h], y=score[:,1][h], s=10, marker=marker[I], color=color[I], alpha=0.5, label=I)
        else:
            pass
    if len(outlier_index)>0:
        X_clean=np.asarray(np.delete(X, outlier_index, 0))
        Y_clean=np.asarray(np.delete(Y, outlier_index, 0))
        if len(X_name)>0:
            name_clean=np.asarray(np.delete(X_name, outlier_index, 0))
            df_name_clean=pd.DataFrame(name_clean)
        df_X = pd.DataFrame(X_clean, columns=col_name)
        df_y = pd.DataFrame(Y_clean)
        writer = pd.ExcelWriter(my_path+'/'+name+tab_name+'.xlsx', engine='xlsxwriter')
        writer.book.use_zip64()
        if len(X_name)>0:
            df_name_clean.to_excel(writer, sheet_name=tab_name, index=False)
        df_X.to_excel(writer, sheet_name=tab_name, index=False, startcol=1)
        df_y.to_excel(writer, sheet_name=tab_name, index=False, startcol=int(X_clean.shape[1])+1)
        writer.save()
        for I in outlier_index:
            ax.scatter(score[I,0], score[I,1], s=10, facecolors='none', edgecolors='r')
        statusbar['text'] = ('Outliers have been removed') 
    else:
        statusbar['text'] = ('No outliers') 
        X_clean=X
        Y_clean=Y
        pass
    ax.set_xlabel("PC1", fontproperties=font)
    ax.set_ylabel('PC2', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    fig.savefig(my_path+'/'+name+tab_name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
    return(X_clean, Y_clean)
def pca_cal(path, X,Y, statusbar, tab_name):#Function_36
    statusbar['text'] = ('Calculate PCA.....')
    time.sleep(1)
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' pca_model'
    h,w=X.shape
    root=tkinter.Tk()
    root.title("PCA")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    pca=PCA(n_components=min(h,w)).fit(X) ## you havenumber of component equal to x.shape[1]
    eigenvalue=(pca.explained_variance_ratio_)## to get the most important componenet wich introduce more variance
    fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax= fig.add_subplot(111)
    ax.plot(range(1,min(h,w)+1), np.cumsum(eigenvalue), linewidth=0.5)
    ax.set_xlabel('number of components', fontproperties=font)
    ax.set_ylabel('cumulative explained variance', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    ttk.Label(root, text='N comp',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
    N_comps=list(range(2, min(h,w)+1))
    N_compent = ttk.Combobox(root, values=N_comps,  width=15, font=('Times New Roman', 15), justify='center')
    N_compent.set('2')
    N_compent.grid( row = 0, column = 1, columnspan=2, sticky='ew')
    ttk.Button(root, text = "Calcualte", command = lambda:calulate(int(N_compent.get()), X), style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='w') 
    def calulate(N_comp, X):
        statusbar['text'] = ('Calculate PCA.....')
        time.sleep(1)
        pca=PCA(n_components=N_comp).fit(X) ## you havenumber of component equal to x.shape[1]
        eigenvectors=pca.components_ ## loading to get all components
        if eigenvectors.shape[0]>1:
            ttk.Label(root, text='PC',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=3, column=1,  ipadx=1, ipady=1, sticky='ew')
            ttk.Label(root, text='PC',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=4, column=1,  ipadx=1, ipady=1, sticky='ew')
            first_pc=list(range(1, N_comp+1))
            First_pc = ttk.Combobox(root, values=first_pc, width=15, font=('Times New Roman', 15), justify='center')
            First_pc.set('1')
            First_pc.grid( row = 3, column = 2, sticky='ew')
            Second_pc = ttk.Combobox(root, values=first_pc[1:], width=15, font=('Times New Roman', 15), justify='center')
            Second_pc.set('2')
            Second_pc.grid( row = 4, column = 2, sticky='ew')
            ttk.Button(root, text = "Plot score", command = lambda:plot_score(pca, X, Y,int(First_pc.get()),int(Second_pc.get())), style='my.TButton').grid(row = 3, column=0, ipadx=1, ipady=1, sticky='w') 
            ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, pca.fit_transform(X.copy()), pca.components_, Y), style='my.TButton').grid(row = 5, column=0, ipadx=1, ipady=1, sticky='w') 
            ttk.Button(root, text = "Generate model", command = lambda:save_model(my_path, pca, name), style='my.TButton').grid(row = 5, column=1, ipadx=1, ipady=1, sticky='w') 
            statusbar['text'] = ('Scores and loading have been calculated') 
            fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
            color=['b', 'k', 'r','y', 'g', 'c', 'm']
            marker=['o', 'v', '^', 's', 'p', '*', '+', 'H']
            ax = fig.add_subplot(111)
            Data=np.asarray(eigenvectors)
            for I in range(Data.shape[0]):
                if I<7:
                    ax.plot(Data[I,:], color=color[I], label='PCA '+str(I+1), linewidth=0.5)
                elif I<15:
                    ax.plot(Data[I,:], color=color[I-8], marker=marker[I-8], label='PCA '+str(I+1), linewidth=0.5)
                else:
                    pass
            ax.legend(prop =font)
            ax.set_xlabel("Wavelength (nm)", fontproperties=font)
            ax.set_ylabel('Loading', fontproperties=font)
            ax.tick_params(axis='x', labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
            canvas.draw()
    def plot_score(pca, X, Y, pc_1, pc_2):
        score=pca.fit_transform(X.copy())
        eigenvalue=(pca.explained_variance_ratio_)
        pc1=pc_1-1
        pc2=pc_2-1
        Y=np.asarray(Y)
        if score.shape[0]>1:
            fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
            color=['b', 'k', 'r','y', 'g', 'c', 'm']
            marker=['o', 'v', '^', 's', 'p', '*', '+']
            ax = fig.add_subplot(111)
            try:
                for I in range(int(min(Y)), int(max(Y))+1):
                    if I<=7:
                        h=np.where(Y==I)[0]
                        ax.scatter(x=score[:,pc1][h], y=score[:,pc2][h], s=10, marker=marker[I], color=color[I], alpha=0.5, label=I)
                    else:
                        pass
            except:
                ax.scatter(x=score[:,pc1], y=score[:,pc2], s=10, marker=marker[0], color=color[0], alpha=0.5)
            ax.legend(prop =font)
            ax.set_xlabel("PC"+str(pc_1)+' '+str("%.3f" % eigenvalue[pc1]), fontproperties=font)
            ax.set_ylabel('PC'+str(pc_2)+' '+str("%.3f" % eigenvalue[pc2]), fontproperties=font)
            ax.tick_params(axis='x', labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
            canvas.draw()
            def save_plot(path, name):
                MY_PATH=path.split('/')
                my_path='/'.join(MY_PATH[:-1])
                names=MY_PATH[-1].split('.')
                fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
                speak('The plot has been saved')
            ttk.Button(root, text = "Save plot", command=lambda:save_plot(path, 'PCA_Score'), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
    def excel_save(path, score, loading, Y):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        df = pd.DataFrame(loading)
        df1 = pd.DataFrame(score)
        df_y=pd.DataFrame(Y)
        writer = pd.ExcelWriter(my_path+'/'+names[0]+'_pca.xlsx', engine='xlsxwriter')
        writer.book.use_zip64()
        df1.to_excel(writer, sheet_name='Score', index=False)
        df_y.to_excel(writer, sheet_name='Score', index=False,startcol=int(score.shape[1]))
        df.to_excel(writer, sheet_name='Loading', index=False)
        writer.save()
        speak('The excel file has been saved')
    root.mainloop()
def sfs(path,X,Y, statusbar, y_label, tab_name):#Function_37
    speak('please wait for select the best features')
    h,w=X.shape
    root=tkinter.Tk()
    root.title("SFS")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    try:
        check_classification_targets(Y) # for classification
        X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=42)
        error = []
        I=[]
        for i in range(2, 40):
            knn = KNN(n_neighbors=i)
            knn.fit(X_train, y_train.ravel())
            pred_i = knn.predict(X_test)
            error.append(np.mean(pred_i != y_test))
            I.append(i)
        error=np.asarray(error)
        k=np.where(error==min(error))
        estimator = KNN(n_neighbors=k[0][0]+1)
        score='accuracy'
    except:
        # for regression
        estimator = LinearRegression()
        score='r2'
    ttk.Label(root, text='N feature',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
    N_feature=list(range(2, w))
    N_Features = ttk.Combobox(root, values=N_feature,  width=15, font=('Times New Roman', 15), justify='center')
    N_Features.set('2')
    N_Features.grid( row = 0, column = 1,  sticky='ew')
    ttk.Button(root, text = "Calcualte", command = lambda:calulate(int(N_Features.get()),estimator, X,Y, y_label), width=20, style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='w') 
    def calulate(N, estimator,X,Y, y_label):
        sfs = SFS(estimator, k_features=N, scoring=score, cv=5, n_jobs=-1)
        sfs1 = sfs.fit(X, Y.ravel())
        x_selector=X[:,sfs1.k_feature_idx_]
        A=sfs.get_metric_dict().keys()
        ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, x_selector, Y, sfs1.k_feature_idx_, y_label), width=20, style='my.TButton').grid(row = 2, column=1, ipadx=1, ipady=1, sticky='w') 
        ttk.Button(root, text = "Save plot", command=lambda:save_plot(path), width=20, style='my.TButton').grid( row = 4, column = 0, sticky='w')
        statusbar['text'] = ('The best features have been selected') 
        scores=[]
        for i in A:
            scores.append(sfs.get_metric_dict()[i]['avg_score'])
        fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax = fig.add_subplot(111)
        ax.plot(A, scores, '-v', color = 'blue', mfc='blue', linewidth=0.5)
        ax.set_xlabel('Number of features', fontproperties=font)
        ax.set_ylabel('Performance', fontproperties=font)
        ax.tick_params(axis='x', labelsize=5)
        ax.tick_params(axis='y', labelsize=5)
        ax.set_title('Performance= '+str(format((sfs1.k_score_*100), '.2f')), fontsize=5)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().grid(row = 3, column=0, columnspan=4)
        canvas.draw()
        def excel_save(path, x_selector, Y, idx, y_label):
            y_label=np.asarray(y_label)
            col=[]
            for index in idx:
                col.append(y_label[index])
            col=np.asarray(col)
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            df_X = pd.DataFrame(x_selector, columns=col)
            df_y = pd.DataFrame(Y)
            writer = pd.ExcelWriter(my_path+'/'+names[0]+'_'+tab_name+'_SFS.xlsx', engine='xlsxwriter')
            writer.book.use_zip64()
            df_X.to_excel(writer, sheet_name=tab_name, index=False)
            df_y.to_excel(writer, sheet_name=tab_name, index=False, startcol=int(x_selector.shape[1]))
            writer.save()
            speak('The excel file has been saved')
        def save_plot(path):
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            fig.savefig(my_path+'/'+names[0]+"_"+tab_name+'_SFS.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
            speak('The plot has been saved')
    if w>20 and w<=500:
        calulate(20,estimator, X,Y, y_label)
    elif w>500:
        calulate(50,estimator, X,Y, y_label)
    elif w<=20:
        calulate('best',estimator, X,Y, y_label)
    root.mainloop()
def gen(path,X,Y, statusbar, y_label, tab_name):#Function_38
    speak('please wait for select the best features')
    h,w=X.shape
    root=tkinter.Tk()
    root.title("Genetic algorithm")
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    try:# for classification
        check_classification_targets(Y)
        X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=42)
        error = []
        I=[]
        for i in range(2, 40):         # Calculating error for K values between 1 and 40
            knn = KNN(n_neighbors=i)
            knn.fit(X_train, y_train.ravel())
            pred_i = knn.predict(X_test)
            error.append(np.mean(pred_i != y_test))
            I.append(i)
        error=np.asarray(error)
        k=np.where(error==min(error))
        estimator = KNN(n_neighbors=k[0][0]+1)
        score='accuracy'
    except:# for regression
        estimator = LinearRegression()
        score='r2'
    if X.shape[1]>20:
        selector = GeneticSelectionCV(estimator,max_features=20,cv=5, scoring=score,n_jobs=1)
    else:
        selector = GeneticSelectionCV(estimator,max_features=X.shape[1],cv=5, scoring=score,n_jobs=1)
    selector = selector.fit(X, Y.ravel())
    x_selector=X[:,selector.support_]
    index=np.where(selector.support_==True)
    Index=[]
    for i in range(x_selector.shape[1]):
        Index.append(index[0][i])
    Index=np.asarray(Index)
    col=[]
    for index in Index:
        col.append(y_label[index])
    col=np.asarray(col)
    ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, x_selector, Y, Index, y_label), style='my.TButton').grid(row = 2, column=1, ipadx=1, ipady=1, sticky='w') 
    ttk.Button(root, text = "Save plot", command=lambda:save_plot(path), width=20, style='my.TButton').grid( row = 2, column = 0, sticky='w')
    statusbar['text'] = ('The best features have been selected') 
    fig = Figure(figsize=(3,3), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax = fig.add_subplot(111)
    ax.plot(y_label, X[0,:], '-', color = 'blue', linewidth=0.5)
    ax.plot(col ,x_selector[0,:], 'X', ms=3, mfc='red', linewidth=0.5)
    ax.set_xlabel('wavelength index', fontproperties=font)
    ax.set_ylabel('Reflection', fontproperties=font)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    def save_plot(path):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+"_"+tab_name+'_SFS.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        speak('The plot has been saved')
    def excel_save(path, x_selector, Y, Index, y_label):
        y_label=np.asarray(y_label)
        col=[]
        for index in Index:
            col.append(y_label[index])
        col=np.asarray(col)
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        df_X = pd.DataFrame(x_selector, columns=col)
        df_y = pd.DataFrame(Y)
        writer = pd.ExcelWriter(my_path+'/'+names[0]+'_'+tab_name+'_GA_select.xlsx', engine='xlsxwriter')
        writer.book.use_zip64()
        df_X.to_excel(writer, sheet_name=tab_name, index=False)
        df_y.to_excel(writer, sheet_name=tab_name, index=False, startcol=int(x_selector.shape[1]))
        writer.save()
        speak('The excel file has been saved')
    root.mainloop()
def plot_latent(X, Y, n, frame, path, name):#Function_39
    mse = []
    component = np.arange(1, n)
    for i in component:
        pls = PLSR(n_components=i)
        mse_p = loocv(pls, X,  Y)
        mse.append(mse_p.mean())
    msemin = np.argmin(mse)
    fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
    ax = fig.add_subplot(111)
    ax.plot(component, np.array(mse), '-v', color = 'blue', mfc='blue', linewidth=0.5)
    ax.plot(component[msemin], np.array(mse)[msemin], 'P', ms=3, mfc='red', linewidth=0.5)
    ax.set_xlabel('Number of latent factors', fontproperties=font)
    ax.set_ylabel('RMSECV', fontproperties=font)
    ax.set_title('Best n_comp= '+ str(msemin), fontsize=5)
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    ax.text(max(mse),component[-5], msemin, fontproperties=font)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
    canvas.draw()
    def save_plot(path, name):
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
        speak('The plot has been saved')
    ttk.Button(frame, text = "Save plot", command=lambda:save_plot(path, name), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
def test_data(statusbar, Y):
    try:
        check_classification_targets(Y) # for classificati
        continues=1
    except:
        continues=0
        statusbar['text'] = ('Y matrix have to be integer')
        speak('Y matrix have to be integer')
    return continues
def pls_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, tab_name, X,Y, y_label):#Function_40
    statusbar['text'] = ('Calculate PLSR...')
    time.sleep(1)
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' PLS_model'
    root=tkinter.Tk()
    root.title("PLSR")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    n=min(min(X_train.shape), 100)
    ttk.Label(root, text='N comp',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=1,  ipadx=1, ipady=1, sticky='w')
    N_comps=list(range(2, n+1))
    N_compent = ttk.Combobox(root, values=N_comps,  width=15, font=('Times New Roman', 15), justify='center')
    N_compent.set('2')
    N_compent.grid( row = 0, column = 2, sticky='ew')
    Names=file_name+'_'+tab_name
    ttk.Button(root, text = "Plot latent factors", command = lambda: plot_latent(X_train, Y_train, n, root, path, Names), style='my.TButton').grid(row = 0, column=0, ipadx=1, ipady=1, sticky='ew') 
    ttk.Button(root, text = "Calculate PLSR", command = lambda: cal_plsr(X_train, X_test,  Y_train, Y_test, int(N_compent.get())), style='my.TButton').grid(row = 1, column=0, ipadx=1, ipady=1, sticky='ew') 
    def cal_plsr(X_train, X_test,  Y_train, Y_test, N):
        PLS_model=PLSR(n_components=N, scale=False, max_iter=500, tol=1e-06, copy=True)
        PLS=PLS_model.fit(X_train, Y_train.ravel())
        Y_predict = PLS.predict(X_test)
        Y_calibrate=PLS.predict(X_train)
        ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, PLS, name), style='my.TButton').grid(row = 1, column=1, ipadx=1, ipady=1, sticky='ew') 
        ttk.Button(root, text = "PLS_VS", command = lambda:pls_variable_selection(path, X_train, X_test,  Y_train, Y_test, N, statusbar, tab_name, X,Y, y_label), style='my.TButton').grid(row = 1, column=2, ipadx=1, ipady=1, sticky='ew')
        if Y_predict.shape[0]>1:
            plot_regression(Y_test, Y_predict, Y_train, Y_calibrate, root, path, 'PLSR', tab_name)
            statusbar['text'] = ('Regression model generated') 
    root.mainloop()
def BPNNC_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, labelnames, tab_name):#Function_41
    continues=test_data(statusbar, Y_train)
    if continues==1:
        statusbar['text'] = ('Calculate BPNN classification...')
        time.sleep(1)
        p=path.split('/')
        my_path='/'.join(p[:-1])
        file_name=p[-1].split('.')[0]
        name=file_name+'_'+tab_name+' BPNNC_model'
        root=tkinter.Tk()
        root.title("MLP class")
        s = ttk.Style(root)
        s.configure('new.TFrame', background="lightyellow")
        topframe=ttk.LabelFrame(root, style='new.TFrame')
        topframe.grid(row=0, column=0, columnspan=2, stick='nswe')
        style = ttk.Style(root)
        s = ttk.Style(root)
        s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
        style.configure("BW.TLabel", foreground="black", background="lightyellow")
        root.resizable(0, 0) # this prevents from resizing the window
        root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        root.wm_iconbitmap('DAAI logo.ico')
        Activation=['logistic', 'tanh', 'relu', 'identity']
        Solver=['lbfgs', 'sgd', 'adam']
        Alpha=[0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000]
        first_layer=list(range(3,201))
        first_layer.insert(0,0)
        second_layer=list(range(3,101))
        second_layer.insert(0,0)
        ttk.Label(topframe, text='First layer',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
        L_1 = ttk.Combobox(topframe, values=first_layer,  width=15, font=('Times New Roman', 15), justify='center')
        L_1.set('0')
        L_1.grid( row = 0, column = 1, sticky='ew')
        ttk.Label(topframe, text='Second layer',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=2,  ipadx=1, ipady=1, sticky='w')
        L_2 = ttk.Combobox(topframe, values=second_layer,  width=15, font=('Times New Roman', 15), justify='center')
        L_2.set('0')
        L_2.grid( row = 0, column = 3, sticky='ew')
        ttk.Label(topframe, text='Activation',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
        activ = ttk.Combobox(topframe, values=Activation,  width=15, font=('Times New Roman', 15), justify='center')
        activ.set('logistic')
        activ.grid( row = 1, column = 1, sticky='ew')
        ttk.Label(topframe, text='Solver',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=2,  ipadx=1, ipady=1, sticky='w')
        solv = ttk.Combobox(topframe, values=Solver,  width=15, font=('Times New Roman', 15), justify='center')
        solv.set('lbfgs')
        solv.grid( row = 1, column = 3, sticky='ew')
        ttk.Label(topframe, text='Alpha',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=2, column=0,  ipadx=1, ipady=1, sticky='w')
        alpha = ttk.Combobox(topframe, values=Alpha,  width=15, font=('Times New Roman', 15), justify='center')
        alpha.set('0.00001')
        alpha.grid( row = 2, column = 1, sticky='ew')
        ttk.Button(topframe, text = "Calculate BPNN", command = lambda: cal_BPNN(X_train, X_test,  Y_train, Y_test, int(L_1.get()), int(L_2.get()), float(alpha.get()), activ.get(), solv.get()), style='my.TButton').grid(row = 2, column=3, columnspan=2, ipadx=1, ipady=1, sticky='ew') 
        def cal_BPNN(X_train, X_test,  Y_train, Y_test, l_1, l_2, alpha, activ, solv):
            statusbar['text'] = ('Calculate BPNN classification...')
            time.sleep(1)
            if l_1==0:
                length=[]
                Acc=[]
                acc=[]
                neuron=[]
                for i in range(3, 101):
    #                speak('Please wait for select parameters')
                    length.append(len(Acc))
                    if len(length)>10 and length[-1]==length[-6]:
                            Acc=np.asarray(Acc)
                            h=np.where(Acc==Acc[-1])
                            selected_neuron=neuron[h[0][0]]
                            break
                    elif len(Acc)>10:
                        if Acc[-1]==Acc[-6]:
                            Acc=np.asarray(Acc)
                            h=np.where(Acc==Acc[-1])
                            selected_neuron=neuron[h[0][0]]
                            break
                    if l_2>0:
                        mlp=MLPClassifier(hidden_layer_sizes=(i, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                    else:
                        mlp=MLPClassifier(hidden_layer_sizes=(i), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                    model=mlp.fit(X_train,  Y_train.ravel())
                    Y_predict_test=model.predict(X_test)
                    Y_predict_train=model.predict(X_train)
                    Accuracy_test=metrics.accuracy_score(Y_test, Y_predict_test)
                    Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
                    acc.append(Accuracy_test)
                    if Accuracy_test>=max(acc):
                        neuron.append(i)
                        print(i,Accuracy_train, Accuracy_test )
                        Acc.append(max(acc))    
                if l_2>0:
                    mlp=MLPClassifier(hidden_layer_sizes=(selected_neuron, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                else:
                    mlp=MLPClassifier(hidden_layer_sizes=(selected_neuron), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                model=mlp.fit(X_train,  Y_train.ravel())
                Y_predict_test=model.predict(X_test)
                Y_predict_train=model.predict(X_train)
                Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
                L_1.set(str(selected_neuron))
            else:
                if l_2>0:
                    mlp=MLPClassifier(hidden_layer_sizes=(l_1, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                else:
                    mlp=MLPClassifier(hidden_layer_sizes=(l_1), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                model=mlp.fit(X_train,  Y_train.ravel())
                Y_predict_test=model.predict(X_test)
                Y_predict_train=model.predict(X_train)
                Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
            def imporatnce_wavelength(mlp):
                numerator=np.sum((abs(mlp.coefs_[0])/np.sum(abs(mlp.coefs_[0]), axis=0))*(np.sum(abs(mlp.coefs_[1]), axis=1)), axis=1)
                M=numerator/sum(numerator) ## important wavelength
                Mm=MinMaxScaler().fit(M.reshape(-1, 1)).transform(M.reshape(-1, 1))
                def smooth_curve(points, factor=0.7):
                    smoothed_points = []
                    for point in points:
                        if smoothed_points:
                            previous = smoothed_points[-1]
                            smoothed_points.append(previous * factor + point * (1 - factor))
                        else:
                            smoothed_points.append(point)
                    return smoothed_points
                mm=smooth_curve(Mm)
                fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                ax = fig.add_subplot(111)
                ax.plot(mm, '-.', color = 'red', mfc='blue', linewidth=0.5)
                ax.set_xlabel('Wavelength number', fontproperties=font)
                ax.set_ylabel('Normalized M', fontproperties=font)
                ax.tick_params(axis='x', labelsize=5)
                ax.tick_params(axis='y', labelsize=5)
                canvas = FigureCanvasTkAgg(fig, master=root)
                canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
                canvas.draw()
                def save_plot(path, name):
                    MY_PATH=path.split('/')
                    my_path='/'.join(MY_PATH[:-1])
                    names=MY_PATH[-1].split('.')
                    fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
                    speak('The plot has been saved')
                ttk.Button(root, text = "Save plot", command=lambda:save_plot(path, 'imporatnce_wavelength'), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
                def excel_save(path,  mm):
                    MY_PATH=path.split('/')
                    my_path='/'.join(MY_PATH[:-1])
                    names=MY_PATH[-1].split('.')
                    df = pd.DataFrame(mm)
                    writer = pd.ExcelWriter(my_path+'/'+names[0]+'_important wavelength.xlsx', engine='xlsxwriter')
                    writer.book.use_zip64()
                    df.to_excel(writer, index=False, startcol=1)
                    writer.save()
                    speak('The excel file has been saved')
                ttk.Button(root, text = "Save excel", command = lambda:excel_save(path, mm), style='my.TButton').grid(row = 7, column=1, ipadx=1, ipady=1, sticky='w') 
            if Y_predict_test.shape[0]>1:
                statusbar['text'] = ('Classification model generated')
                scores=cross_val_score(estimator=model,X=X_train,y=Y_train.ravel(),cv=10,scoring='accuracy')## add to software for classification and regression
                Acc_valid=("%0.2f,+/-%0.2f" % (scores.mean()*100,scores.std()*100))
                ttk.Button(topframe, text = "Generate model", command = lambda: save_model(my_path, model, name), style='my.TButton').grid(row = 3, column=0, columnspan=2, ipadx=1, ipady=1, sticky='ew') 
                ttk.Button(topframe, text = "Importance wavelength", command = lambda: imporatnce_wavelength(mlp), style='my.TButton').grid(row = 3, column=2, columnspan=2,ipadx=1, ipady=1, sticky='ew') 
                plot_confusion_matrix(Y_test, Y_predict_test, root, path, 'BPNNC', Accuracy_train, Acc_valid, labelnames, tab_name)
        root.mainloop()
    else:
        pass
def MLR_cal (path, X_train, X_test,  Y_train, Y_test, statusbar,tab_name):#Function_42
    statusbar['text'] = ('Calculate MLP regression...')
    time.sleep(1)
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' MLR_model'
    root=tkinter.Tk()
    root.title("Multi linear regression")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    reg = LinearRegression().fit(X_train, Y_train)
    Y_predict=reg.predict(X_test)
    Y_calibrate=reg.predict(X_train)
    ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, reg, name), style='my.TButton').grid(row = 2, column=3, ipadx=1, ipady=1, sticky='ew') 
    plot_regression(Y_test, Y_predict, Y_train, Y_calibrate, root, path, 'MLR', tab_name)
    statusbar['text'] = ('Regression model generated') 
    root.mainloop()
def BPNNR_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, tab_name):#Function_43
    statusbar['text'] = ('Calculate BPNN regression...')
    time.sleep(1)
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' BPNNR_model'
    root=tkinter.Tk()
    root.title("MLP regression")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    Activation=['logistic', 'tanh', 'relu', 'identity']
    Solver=['lbfgs', 'sgd', 'adam']
    Alpha=[0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000]
    first_layer=list(range(3,201))
    first_layer.insert(0,0)
    second_layer=list(range(3,101))
    second_layer.insert(0,0)
    ttk.Label(root, text='First layer',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
    L_1 = ttk.Combobox(root, values=first_layer,  width=15, font=('Times New Roman', 15), justify='center')
    L_1.set('0')
    L_1.grid( row = 0, column = 1, sticky='ew')
    ttk.Label(root, text='Second layer',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=2,  ipadx=1, ipady=1, sticky='w')
    L_2 = ttk.Combobox(root, values=second_layer,  width=15, font=('Times New Roman', 15), justify='center')
    L_2.set('0')
    L_2.grid( row = 0, column = 3, sticky='ew')
    ttk.Label(root, text='Activation',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
    activ = ttk.Combobox(root, values=Activation,  width=15, font=('Times New Roman', 15), justify='center')
    activ.set('logistic')
    activ.grid( row = 1, column = 1, sticky='ew')
    ttk.Label(root, text='Solver',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=2,  ipadx=1, ipady=1, sticky='w')
    solv = ttk.Combobox(root, values=Solver,  width=15, font=('Times New Roman', 15), justify='center')
    solv.set('lbfgs')
    solv.grid( row = 1, column = 3, sticky='ew')
    ttk.Label(root, text='Alpha',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=2, column=0,  ipadx=1, ipady=1, sticky='w')
    alpha = ttk.Combobox(root, values=Alpha,  width=15, font=('Times New Roman', 15), justify='center')
    alpha.set('0.00001')
    alpha.grid( row = 2, column = 1, sticky='ew')
    ttk.Button(root, text = "Calculate BPNN", command = lambda: cal_BPNN(X_train, X_test,  Y_train, Y_test, int(L_1.get()), int(L_2.get()), float(alpha.get()), activ.get(), solv.get()), style='my.TButton').grid(row = 2, column=2, ipadx=1, ipady=1, sticky='ew') 
    def cal_BPNN(X_train, X_test,  Y_train, Y_test, l_1, l_2, alpha, activ, solv):
        statusbar['text'] = ('Calculate BPNN regression...')
        time.sleep(1)
        if l_1==0:
            length=[]
            R2PP=[]
            R2P=[]
            neuron=[]
            R2PC=[]
            RmseP=[]
            RmseC=[]
            for i in range(3, 101):
                length.append(len(R2PP))
                if len(length)>10 and length[-1]==length[-6]:
                        R2PP=np.asarray(R2PP)
                        h=np.where(R2PP==R2PP[-1])
                        selected_neuron=neuron[h[0][0]]
                        break
                elif len(R2PP)>10:
                    if R2PP[-1]==R2PP[-6]:
                        R2PP=np.asarray(R2PP)
                        h=np.where(R2PP==R2PP[-1])
                        selected_neuron=neuron[h[0][0]]
                        break
                if l_2>0:
                    mlp=MLPRegressor(hidden_layer_sizes=(i, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                else:
                    mlp=MLPRegressor(hidden_layer_sizes=(i), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
                model=mlp.fit(X_train,  Y_train.ravel())
                Y_predict_test=model.predict(X_test)
                Y_predict_train=model.predict(X_train)
                R2=metrics.r2_score(Y_test, Y_predict_test)
                mse=metrics.mean_squared_error(Y_test, Y_predict_test)
                RMSE=np.sqrt(mse) ## sqrt(np.mean((Y_test-Y_predict)**2))
                Rc2=metrics.r2_score(Y_train, Y_predict_train)
                msec=metrics.mean_squared_error(Y_train, Y_predict_train)
                RMSEC=np.sqrt(msec) ## sqrt(np.mean((Y_test-Y_predict)**2)) random error
                R2P.append(R2)
                if R2>=max(R2P):
                    neuron.append(i)
                    print(i,Rc2, R2, RMSEC, RMSE )
                    R2PP.append(R2)
                    R2PC.append(Rc2)
                    RmseP.append(RMSE)
                    RmseC.append(RMSEC)
            if l_2>0:
                mlp=MLPRegressor(hidden_layer_sizes=(selected_neuron, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
            else:
                mlp=MLPRegressor(hidden_layer_sizes=(selected_neuron), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
            model=mlp.fit(X_train,  Y_train.ravel())
            Y_predict_test=model.predict(X_test)
            Y_predict_train=model.predict(X_train)
            ttk.Label(root, text='First layer',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
            L_1.set(str(selected_neuron))
        else:
            if l_2>0:
                mlp=MLPRegressor(hidden_layer_sizes=(l_1, l_2), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
            else:
                mlp=MLPRegressor(hidden_layer_sizes=(l_1), alpha=alpha, activation=activ,solver=solv, max_iter=20000,verbose=False, tol=1e-4, random_state=42)
            model=mlp.fit(X_train,  Y_train.ravel())
            Y_predict_test=model.predict(X_test)
            Y_predict_train=model.predict(X_train)
        if Y_predict_test.shape[0]>1:
            statusbar['text'] = ('Regression model generated')
            plot_regression(Y_test, Y_predict_test, Y_train, Y_predict_train, root, path, 'BPNNR', tab_name)
            ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, model, name), style='my.TButton').grid(row = 2, column=3, ipadx=1, ipady=1, sticky='ew') 
    root.mainloop()
def KNN_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, labelnames, tab_name):#Function_44
    continues=test_data(statusbar, Y_train)
    if continues==1:
        statusbar['text'] = ('Calculate k-nearest nighbour classification...') 
        p=path.split('/')
        my_path='/'.join(p[:-1])
        file_name=p[-1].split('.')[0]
        name=file_name+'_'+tab_name+' KNN_model'
        root=tkinter.Tk()
        root.title("KNN")
        style = ttk.Style(root)
        s = ttk.Style(root)
        s.configure('my.TButton', font=('Times New Roman', 15)) ## button font
        style.configure("BW.TLabel", foreground="black", background="lightyellow")
        root.resizable(0, 0) # this prevents from resizing the window
        root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        root.wm_iconbitmap('DAAI logo.ico')
        error = []
        m,n=X_train.shape
        if m<51:
            M=m
        else:
            M=51
        for i in range(2, M):
            knn = KNN(n_neighbors=i)
            knn.fit(X_train, Y_train.ravel())
            pred_i = knn.predict(X_test)
            error.append(metrics.accuracy_score(pred_i, Y_test))
        error=np.asarray(error)
        k=np.where(error==max(error))
        fig = Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
        ax = fig.add_subplot(111)
        ax.plot(range(2, M), error, color='red', linestyle='dashed', marker='o',
             markerfacecolor='blue', markersize=5, linewidth=0.5)
        ax.set_xlabel('K Value', fontproperties=font)
        ax.set_ylabel('Accuracy', fontproperties=font)
        ax.tick_params(axis='x', labelsize=5)
        ax.tick_params(axis='y', labelsize=5)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().grid(row = 6, column=0, columnspan=4)
        canvas.draw()
        def save_plot(path, name):
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            fig.savefig(my_path+'/'+names[0]+'_'+name+'.jpg',pad_inches=0.001, bbox_inches='tight', dpi=300)
            speak('Your plot has been saved')
        ttk.Button(root, text = "Save plot", command=lambda:save_plot(path, name), width=20, style='my.TButton').grid( row = 7, column = 0, sticky='ew')
        Ks=list(range(2,51))
        ttk.Label(root, text='K',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  columnspan=2, ipadx=1, ipady=1, sticky='w')
        KS = ttk.Combobox(root, values=Ks,  width=15, font=('Times New Roman', 15), justify='center')
        KS.set(str(k[0][0]+2))
        KS.grid( row = 0, column = 1, sticky='ew')
        ttk.Button(root, text = "Calculate KNN", command = lambda: cal_KNN(X_train, X_test,  Y_train, Y_test, int(KS.get())), style='my.TButton').grid(row = 1, column=0, ipadx=1, ipady=1, sticky='ew') 
        def cal_KNN(X_train, X_test,  Y_train, Y_test, K):
            statusbar['text'] = ('Calculate k-nearest nighbour classification...') 
            knn = KNN(n_neighbors=K)
            knn.fit(X_train, Y_train.ravel())
            Y_predict_test=knn.predict(X_test)
            Y_predict_train=knn.predict(X_train)
            Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
            scores=cross_val_score(estimator=knn,X=X_train,y=Y_train.ravel(),cv=10,scoring='accuracy')## add to software for classification and regression
            Acc_valid=("%0.2f,+/-%0.2f" % (scores.mean()*100,scores.std()*100))
            if Y_predict_test.shape[0]>1:
                statusbar['text'] = ('Classification model generated')
                ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, knn, name), style='my.TButton').grid(row = 1, column=1, ipadx=1, ipady=1, sticky='ew') 
                plot_confusion_matrix(Y_test, Y_predict_test, root, path, 'KNN', Accuracy_train, Acc_valid, labelnames)
        root.mainloop()
    else:
        pass
def RFR_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, tab_name):#Function_45
    statusbar['text'] = ('Calculate random forest regression...')
    time.sleep(1)
    m,n=X_train.shape
    if n>=800:
        M=200
    elif n>100:
        M=int(n/4)
    else:
        M=n
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' RFR_model'
    root=tkinter.Tk()
    root.title("Random Forest regression")
    style = ttk.Style(root)
    s = ttk.Style(root)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    Tree=list(range(10,201))
    Features=list(range(3,X_train.shape[1]-2))
    ttk.Label(root, text='Number of tree',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
    l_1 = ttk.Combobox(root, values=Tree,  width=15, font=('Times New Roman', 15), justify='center')
    l_1.set('0')
    l_1.grid( row = 0, column = 1, sticky='ew')
    ttk.Label(root, text='Feature',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
    l_2 = ttk.Combobox(root, values=Features,  width=15, font=('Times New Roman', 15), justify='center')
    l_2.set('3')
    l_2.grid( row = 1, column = 1, sticky='ew')
    ttk.Button(root, text = "Calculate RF", command = lambda: cal_RFR(X_train, X_test,  Y_train, Y_test, int(l_1.get()), int(l_2.get())), style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='ew') 
    def cal_RFR(X_train, X_test,  Y_train, Y_test, tree, feature):
        statusbar['text'] = ('Calculate random forest regression...')
        if tree==0:
            length=[]
            Tree=[]
            Feat=[]
            R2PP=[]
            R2PC=[]
            RmseP=[]
            RmseC=[]
            R2P=[]
            for tree in range(10,206, 5):
                length.append(len(R2PP))
                if len(length)>10 and length[-1]==length[-6]:
                        R2PP=np.asarray(R2PP)
                        h=np.where(R2PP==R2PP[-1])
                        selected_tree=Tree[h[0][0]]
                        num_features=Feat[h[0][0]]
                        print(Tree[h[0][0]], Feat[h[0][0]])
                        break
                elif len(R2PP)>10:
                    if R2PP[-1]==R2PP[-6]:
                        R2PP=np.asarray(R2PP)
                        h=np.where(R2PP==R2PP[-1])
                        selected_tree=Tree[h[0][0]]
                        num_features=Feat[h[0][0]]
                        print(Tree[h[0][0]], Feat[h[0][0]])
                        break
                for feat in range(3, M):
                    clf_RF = RFR(n_estimators=tree, max_features = feat, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
                    Y_predict_test=clf_RF.predict(X_test)
                    Y_predict_train=clf_RF.predict(X_train)
                    R2=metrics.r2_score(Y_test, Y_predict_test)
                    mse=metrics.mean_squared_error(Y_test, Y_predict_test)
                    RMSE=np.sqrt(mse) ## sqrt(np.mean((Y_test-Y_predict)**2))
                    Rc2=metrics.r2_score(Y_train, Y_predict_train)
                    msec=metrics.mean_squared_error(Y_train, Y_predict_train)
                    RMSEC=np.sqrt(msec) ## sqrt(np.mean((Y_test-Y_predict)**2)) random error
                    R2P.append(R2)
                    if R2>=max(R2P):
                        print(R2,Rc2,RMSE,RMSEC, tree, feat)
                        Tree.append(tree)
                        Feat.append(feat)
                        R2PP.append(R2)
                        R2PC.append(Rc2)
                        RmseP.append(RMSE)
                        RmseC.append(RMSEC)
            l_1.set(str(selected_tree))
            l_2.set(str(num_features))
            clf_RF = RFR(n_estimators=selected_tree, max_features = num_features, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
            Y_predict_test=clf_RF.predict(X_test)
            Y_predict_train=clf_RF.predict(X_train)
        else:
            clf_RF = RFR(n_estimators=tree, max_features = feature, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
            Y_predict_test=clf_RF.predict(X_test)
            Y_predict_train=clf_RF.predict(X_train)
        if Y_predict_test.shape[0]>1:
            statusbar['text'] = ('Regression model generated')
            plot_regression(Y_test, Y_predict_test, Y_train, Y_predict_train, root, path, 'RFR', tab_name)
            ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, clf_RF, name), style='my.TButton').grid(row = 2, column=1, ipadx=1, ipady=1, sticky='ew') 
    root.mainloop()
def RFC_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, labelnames, tab_name):#Function_46
    continues=test_data(statusbar, Y_train)
    if continues==1:
        statusbar['text'] = ('Calculate random forest classification...')
        m,n=X_train.shape
        if n>=800:
            M=200
        elif n>100:
            M=int(n/4)
        else:
            M=n
        p=path.split('/')
        my_path='/'.join(p[:-1])
        file_name=p[-1].split('.')[0]
        name=file_name+'_'+tab_name+' RFC_model'
        root=tkinter.Tk()
        root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        root.title("Random Forest class")
        style = ttk.Style(root)
        s = ttk.Style(root)
        s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
        style.configure("BW.TLabel", foreground="black", background="lightyellow")
        root.resizable(200, 200) # this prevents from resizing the window
        root.wm_iconbitmap('DAAI logo.ico')
        Tree=list(range(10,201))
        Features=list(range(3,n-2))
        ttk.Label(root, text='Number of tree',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
        l_1 = ttk.Combobox(root, values=Tree,  width=15, font=('Times New Roman', 15), justify='center')
        l_1.set('0')
        l_1.grid( row = 0, column = 1, sticky='ew')
        ttk.Label(root, text='Feature',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
        l_2 = ttk.Combobox(root, values=Features,  width=15, font=('Times New Roman', 15), justify='center')
        l_2.set('3')
        l_2.grid( row = 1, column = 1, sticky='ew')
        ttk.Button(root, text = "Calculate RF", command = lambda: cal_RFC(X_train, X_test,  Y_train, Y_test, int(l_1.get()), int(l_2.get()), name), style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='ew') 
        def cal_RFC(X_train, X_test,  Y_train, Y_test, tree, feature, name):
            statusbar['text'] = ('Calculate random forest classification...')
            if tree==0:
                speak('please wait for select the best number of tree')
                statusbar['text'] = ('Selecting the best number of tree...')
                length=[]
                Tree=[]
                Feat=[]
                Acc=[]
                acc=[]
                for tree in range(10,206,5):
                    length.append(len(Acc))
                    if len(length)>10 and length[-1]==length[-6]:
                            Acc=np.asarray(Acc)
                            h=np.where(Acc==Acc[-1])
                            selected_tree=Tree[h[0][0]]
                            num_features=Feat[h[0][0]]
                            print(Tree[h[0][0]], Feat[h[0][0]])
                            break
                    elif len(Acc)>10:
                        if Acc[-1]==Acc[-6]:
                            Acc=np.asarray(Acc)
                            h=np.where(Acc==Acc[-1])
                            selected_tree=Tree[h[0][0]]
                            num_features=Feat[h[0][0]]
                            print(Tree[h[0][0]], Feat[h[0][0]])
                            break
                    for feat in range(3, M):
                        clf_RF = RFC(n_estimators=tree, max_features = feat, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
                        Y_predict_test=clf_RF.predict(X_test)
                        Y_predict_train=clf_RF.predict(X_train)
                        Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
                        Accuracy_test=metrics.accuracy_score(Y_test, Y_predict_test)
                        acc.append(Accuracy_test)
                        if Accuracy_test>=max(acc):
                            print(Accuracy_test, Accuracy_train, tree, feat)
                            Tree.append(tree)
                            Feat.append(feat)
                            Acc.append(max(acc))
                l_1.set(str(selected_tree))
                l_2.set(str(num_features))
                clf_RF = RFC(n_estimators=selected_tree, max_features = num_features, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
                Y_predict_test=clf_RF.predict(X_test)
                Y_predict_train=clf_RF.predict(X_train)
                Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
            else:
                clf_RF = RFC(n_estimators=tree, max_features = feature, random_state=0, n_jobs=-1).fit(X_train, Y_train.ravel())
                Y_predict_test=clf_RF.predict(X_test)
                Y_predict_train=clf_RF.predict(X_train)
                Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
            scores=cross_val_score(estimator=clf_RF,X=X_train,y=Y_train.ravel(),cv=10,scoring='accuracy')## add to software for classification and regression
            Acc_valid=("%0.2f,+/-%0.2f" % (scores.mean()*100,scores.std()*100))
            if Y_predict_test.shape[0]>1:
                statusbar['text'] = ('Classification model generated')
                ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, clf_RF, name), style='my.TButton').grid(row = 2, column=1, ipadx=1, ipady=1, sticky='ew') 
                plot_confusion_matrix(Y_test, Y_predict_test, root, path, 'RFC', Accuracy_train, Acc_valid, labelnames, tab_name)
        root.mainloop()
    else:
        pass
def SVMC_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, labelnames, tab_name):#Function_47
    continues=test_data(statusbar, Y_train)
    if continues==1:
        statusbar['text'] = ('Calculate SVM classification...')
        time.sleep(1)
        p=path.split('/')
        my_path='/'.join(p[:-1])
        file_name=p[-1].split('.')[0]
        name=file_name+'_'+tab_name+' SVMC_model'
        root=tkinter.Tk()
        root.title("SVM class")
        style = ttk.Style(root)
        s = ttk.Style(root)
        s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font
        style.configure("BW.TLabel", foreground="black", background="lightyellow")
        root.resizable(0, 0) # this prevents from resizing the window
        root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        root.wm_iconbitmap('DAAI logo.ico')
        Kernel=['linear', 'poly','rbf', 'sigmoid']
        ttk.Label(root, text='Kernel',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
        Kl = ttk.Combobox(root, values=Kernel,  width=15, font=('Times New Roman', 15), justify='center')
        Kl.set('linear')
        Kl.grid( row = 0, column = 1, sticky='ew')
        C_parm=[]
        C_parm.append(0)
        for c in range (-200, 1, 3):
            C_parm.append(np.abs(c))
        ttk.Label(root, text='Regu_param',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
        l_2 = ttk.Combobox(root, values=C_parm,  width=15, font=('Times New Roman', 15), justify='center')
        l_2.set('0')
        l_2.grid( row = 1, column = 1, sticky='ew')
        ttk.Button(root, text = "Calculate SVM", command = lambda: cal_SVMC(X_train, X_test,  Y_train, Y_test,  int(l_2.get()),Kl.get()), style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='ew') 
        def cal_SVMC(X_train, X_test,  Y_train, Y_test,  C_Reg,kernel):
            if C_Reg==0:
                acc=[]
                acc_test=[]
                acc_train=[]
                C_reg=[]
                for c in range (-201, 0, 3):
                    c=np.abs(c)
                    clf_RF = SVC(C=c, kernel=kernel, degree=3, gamma='auto',  tol=0.0001,  decision_function_shape='ovo').fit(X_train, Y_train.ravel())
                    Y_predict_test=clf_RF.predict(X_test)
                    Y_predict_train=clf_RF.predict(X_train)
                    Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
                    Accuracy_test=metrics.accuracy_score(Y_test, Y_predict_test)
                    acc.append(Accuracy_test)
                    if Accuracy_test>=max(acc):
                        acc_test.append(Accuracy_test)
                        acc_train.append(Accuracy_train)
                        C_reg.append(c)
                        print(Accuracy_test, Accuracy_train, c)
                    elif c<102 and Accuracy_test<max(acc):
                        break
                h=np.where(acc_test==max(acc_test))
                C_Reg=C_reg[h[0][0]]
                l_2.set(str(C_Reg))
            clf_RF = SVC(C=C_Reg, kernel=kernel, degree=3, gamma='auto',  tol=0.0001,  decision_function_shape='ovo').fit(X_train, Y_train.ravel())
            Y_predict_test=clf_RF.predict(X_test)
            Y_predict_train=clf_RF.predict(X_train)
            Accuracy_train=metrics.accuracy_score(Y_train, Y_predict_train)
            scores=cross_val_score(estimator=clf_SVC,X=X_train,y=Y_train.ravel(),cv=10,scoring='accuracy')## add to software for classification and regression
            Acc_valid=("%0.2f,+/-%0.2f" % (scores.mean()*100,scores.std()*100))
            if Y_predict_test.shape[0]>1:
                statusbar['text'] = ('Classification model generated') 
                ttk.Button(root,text = "Generate model", command = lambda: save_model(my_path, clf_RF, name), style='my.TButton').grid(row = 2, column=1, ipadx=1, ipady=1, sticky='ew') 
                plot_confusion_matrix(Y_test, Y_predict_test, root, path, 'SVMC', Accuracy_train, Acc_valid, labelnames, tab_name)
        root.mainloop()
    else:
        pass
def LDA_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, labelnames, tab_name):#Function_48
    continues=test_data(statusbar, Y_train)
    if continues==1:
        statusbar['text'] = ('Calculate LDA classification...')
        p=path.split('/')
        my_path='/'.join(p[:-1])
        file_name=p[-1].split('.')[0]
        name=file_name+'_'+tab_name+' LDA_model'
        root=tkinter.Tk()
        root.title("LDA class")
        style = ttk.Style(root)
        s = ttk.Style(root)
        s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font
        style.configure("BW.TLabel", foreground="black", background="lightyellow")
        root.resizable(0, 0) # this prevents from resizing the window
        root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        root.wm_iconbitmap('DAAI logo.ico')
        Accuracy=[]
        lda1 = LDA(solver='lsqr', shrinkage='auto').fit(X_train, Y_train.ravel())
        ypred1=lda1.predict(X_test)
        ypredtrain1=lda1.predict(X_train)
        acctrain1=metrics.accuracy_score(Y_train, ypredtrain1)
        Accuracy.append(metrics.accuracy_score(Y_test, ypred1)*100)
        lda2 = LDA(solver='lsqr', shrinkage=None).fit(X_train, Y_train.ravel())
        ypred2=lda2.predict(X_test)
        ypredtrain2=lda2.predict(X_train)
        acctrain2=metrics.accuracy_score(Y_train, ypredtrain2)
        Accuracy.append(metrics.accuracy_score(Y_test, ypred2)*100)
        lda3 = LDA(solver='svd', shrinkage=None).fit(X_train, Y_train.ravel())
        ypred3=lda3.predict(X_test)
        ypredtrain3=lda1.predict(X_train)
        acctrain3=metrics.accuracy_score(Y_train, ypredtrain3)
        Accuracy.append(metrics.accuracy_score(Y_test, ypred3)*100)
        lda4 = LDA(solver='eigen', shrinkage='auto').fit(X_train, Y_train.ravel())
        ypred4=lda4.predict(X_test)
        ypredtrain4=lda4.predict(X_train)
        acctrain4=metrics.accuracy_score(Y_train, ypredtrain4)
        Accuracy.append(metrics.accuracy_score(Y_test, ypred4)*100)
        try:
            lda5 = LDA(solver='eigen', shrinkage=None).fit(X_train, Y_train.ravel())
            ypred5=lda5.predict(X_test)
            ypredtrain5=lda1.predict(X_train)
            acctrain5=metrics.accuracy_score(Y_train, ypredtrain5)
            Accuracy.append(metrics.accuracy_score(Y_test, ypred5)*100)
        except:
            pass
        Accuracy=np.asarray(Accuracy)
        index=np.where(Accuracy==np.max(Accuracy))
        if index[0][0]==0:
            Y_predict_test=ypred1
            model=lda1
            Accuracy_train=acctrain1
        elif index[0][0]==1:
            Y_predict_test=ypred2
            model=lda2
            Accuracy_train=acctrain2
        elif index[0][0]==2:
            Y_predict_test=ypred3
            model=lda3
            Accuracy_train=acctrain3
        elif index[0][0]==3:
            Y_predict_test=ypred4
            model=lda4
            Accuracy_train=acctrain4
        else:
            Y_predict_test=ypred5
            model=lda5
            Accuracy_train=acctrain5
        scores=cross_val_score(estimator=model,X=X_train,y=Y_train.ravel(),cv=10,scoring='accuracy')## add to software for classification and regression
        Acc_valid=("%0.2f,+/-%0.2f" % (scores.mean()*100,scores.std()*100))
        print(model)
        statusbar['text'] = ('Classification model generated')
        ttk.Button(root,text = "Generate model", command = lambda: save_model(my_path, model, name), style='my.TButton').grid(row = 1, column=0, ipadx=1, ipady=1, sticky='ew') 
        plot_confusion_matrix(Y_test, Y_predict_test, root, path, 'LDA', Accuracy_train, Acc_valid, labelnames, tab_name)
        root.mainloop()
    else:
        pass
def SVMR_cal(path, X_train, X_test,  Y_train, Y_test, statusbar, tab_name):#Function_49
    statusbar['text'] = ('Calculate SVM regression...')
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+'_'+tab_name+' SVMR_model'
    root=tkinter.Tk()
    root.title("SVM regression")
    root.resizable(0, 0) # this prevents from resizing the window
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    Kernel=['linear', 'poly','rbf', 'sigmoid']
    style = ttk.Style(root)
    s = ttk.Style(root)
    style.configure("BW.TLabel", foreground="black", background="lightyellow")
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font
    ttk.Label(root, text='Kernel',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=0, column=0,  ipadx=1, ipady=1, sticky='w')
    Kl = ttk.Combobox(root, values=Kernel,  width=15, font=('Times New Roman', 15), justify='center')
    Kl.set('linear')
    Kl.grid( row = 0, column = 1, sticky='ew')
    C_parm=[]
    C_parm.append(0)
    for c in range (-200, 0, 3):
        C_parm.append(np.abs(c))
    ttk.Label(root, text='Regu_param',width = 15, style="BW.TLabel", font=('Times New Roman', 15)).grid(row=1, column=0,  ipadx=1, ipady=1, sticky='w')
    l_2 = ttk.Combobox(root, values=C_parm,  width=15, font=('Times New Roman', 15), justify='center')
    l_2.set('0')
    l_2.grid( row = 1, column =1, sticky='ew')
    ttk.Button(root, text = "Calculate SVM", command = lambda: cal_SVMR(X_train, X_test,  Y_train, Y_test,  int(l_2.get()),Kl.get()), style='my.TButton').grid(row = 2, column=0, ipadx=1, ipady=1, sticky='ew') 
    def cal_SVMR(X_train, X_test,  Y_train, Y_test, C_Reg,kernel):
        if C_Reg==0:
            R2P=[]
            R2PP=[]
            R2PC=[]
            RmseP=[]
            RmseC=[]
            C_reg=[]
            for c in range (-201, 0, 3):
                c=np.abs(c)
                clf_RF = SVR(C=c, kernel=kernel, degree=3, gamma='auto',  tol=0.0001).fit(X_train, Y_train.ravel())
                Y_predict_test=clf_RF.predict(X_test)
                Y_predict_train=clf_RF.predict(X_train)
                R2=metrics.r2_score(Y_test, Y_predict_test)
                mse=metrics.mean_squared_error(Y_test, Y_predict_test)
                RMSE=np.sqrt(mse) ## sqrt(np.mean((Y_test-Y_predict)**2))
                Rc2=metrics.r2_score(Y_train, Y_predict_train)
                msec=metrics.mean_squared_error(Y_train, Y_predict_train)
                RMSEC=np.sqrt(msec) ## sqrt(np.mean((Y_test-Y_predict)**2)) random error
                R2P.append(R2)
                if R2>=max(R2P):
                    C_reg.append(c)
                    R2PP.append(R2)
                    R2PC.append(Rc2)
                    RmseP.append(RMSE)
                    RmseC.append(RMSEC)
                    print(c, R2, RMSE, Rc2, RMSEC)
                elif c<102 and R2<max(R2P):
                    break
            h=np.where(R2PP==max(R2PP))
            C_Reg=C_reg[h[0][0]]
            l_2.set(str(C_Reg))
        clf_RF = SVR(C=C_Reg, kernel=kernel, degree=3, gamma='auto',  tol=0.0001).fit(X_train, Y_train.ravel())
        Y_predict_test=clf_RF.predict(X_test)
        Y_predict_train=clf_RF.predict(X_train)
        if Y_predict_test.shape[0]>1:
            statusbar['text'] = ('Regression model generated')
            plot_regression(Y_test, Y_predict_test, Y_train, Y_predict_train, root, path, 'SVNR', tab_name)
            ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, clf_RF, name), style='my.TButton').grid(row = 1, column=3, ipadx=1, ipady=1, sticky='ew') 
    root.mainloop()
def pls_variable_selection(path, X_train, X_test,  y_train, y_test, N, statusbar, tab_name, X,Y, y_label):#Function_50
    p=path.split('/')
    my_path='/'.join(p[:-1])
    file_name=p[-1].split('.')[0]
    name=file_name+' BVSPLS_model'
    root=tkinter.Tk()
    root.title("PLS variable selection")
    root.resizable(0, 0)
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    root.wm_iconbitmap('DAAI logo.ico')
    root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    ttk.Button(root, text = "BVSPLS", command = lambda: BVSPLS(X_train, X_test,  y_train, y_test, N, X, Y, y_label), style='my.TButton').grid(row = 0, column=0, ipadx=1, ipady=1, sticky='ew') 
    def BVSPLS(X_train, X_test,  y_train, y_test, N, X, Y, y_label):
        max_comp=N
        mse = np.zeros((max_comp,X_train.shape[1])) 
        for i in range(max_comp):
            pls1 = PLSR(n_components=i+1)
            pls1.fit(X_train, y_train.ravel())
            sorted_ind = np.argsort(np.abs(pls1.coef_[:,0])) 
            Xc = X_train[:,sorted_ind] 
            for j in range(Xc.shape[1]-(i+1)): 
                pls2 = PLSR(n_components=i+1)
                pls2.fit(Xc[:, j:], y_train)
                y_cv = cross_val_predict(pls2, Xc[:, j:], y_train, cv=10)
                mse[i,j] = metrics.mean_squared_error(y_train, y_cv)
        mseminx,mseminy = np.where(mse==np.min(mse[np.nonzero(mse)]))
        pls = PLSR(n_components=mseminx[0]+1)
        pls.fit(X_train, y_train.ravel()) 
        sorted_ind = np.argsort(np.abs(pls.coef_[:,0]))
        Xc = X_train[:,sorted_ind]
        h=sorted_ind[mseminy[0]:]
        Nn=mseminx[0]+1
        h.sort()
        X_train_select=X_train[:,h]
        X_test_select=X_test[:,h]
        X_selected=X[:,h]
        PLS_final=PLSR(n_components=Nn).fit(X_train_select, y_train)
        Y_predict_select = PLS_final.predict(X_test_select)
        Y_calibrate_select=PLS_final.predict(X_train_select)
        ttk.Button(root, text = "Generate model", command = lambda: save_model(my_path, PLS_final, name), style='my.TButton').grid(row = 0, column=1, ipadx=1, ipady=1, sticky='ew') 
        if Y_predict_select.shape[0]>1:
            statusbar['text'] = ('Regression model generated')
            plot_regression(y_test, Y_predict_select, y_train, Y_calibrate_select, root, path, 'BVSPLS', tab_name)
            y_label=np.asarray(y_label)
            col=[]
            for index in h:
                col.append(y_label[index])
            col=np.asarray(col)
            MY_PATH=path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            names=MY_PATH[-1].split('.')
            df_X = pd.DataFrame(X_selected, columns=col)
            df_y = pd.DataFrame(Y)
            writer = pd.ExcelWriter(my_path+'/'+names[0]+'_'+tab_name+'_X_select_BVSPLS.xlsx', engine='xlsxwriter')
            writer.book.use_zip64()
            df_X.to_excel(writer, sheet_name=tab_name, index=False)
            df_y.to_excel(writer, sheet_name=tab_name, index=False, startcol=int(X_selected.shape[1]))
            writer.save()
            speak('The excel file has been saved')
    root.mainloop()
def plot_3dcube(Image_mat, path, name, frame):#Function_51
    def plot_3dcube_thread():
        root3=tkinter.Tk()
        root3.title("3D cube")
        root3.wm_iconbitmap('DAAI logo.ico')
        root3.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
        speak('Please wait for build 3d cube')
        time2=time.time()
        x,y,z=Image_mat.shape
        ax=x+0j
        ay=y+0j
        az=z+0j
        Z, X= np.mgrid[0:x:ax, 0:y:ay]
        Xx, Y= np.mgrid[0:y:ay, 0:z:az]
        Zz, Yy= np.mgrid[0:x:ax, 0:z:az]
        fig = matplotlib.figure.Figure(figsize=(3,2), facecolor='lightyellow', edgecolor='white')
        ax = fig.add_subplot(111, projection='3d')
        YY = np.zeros(X.shape)
        sb=int(Image_mat.shape[-1]/2)
        T = Image_mat[:,:,sb]
        min_value=min(T[np.nonzero(T)])
        max_value=max(T[np.nonzero(T)])
        norm = matplotlib.colors.Normalize(vmin=min_value, vmax=max_value)
        z_scale,x_scale,y_scale=Image_mat.shape
        scale=np.diag([x_scale, y_scale, z_scale, 1.0])
        scale=scale*(1.0/scale.max())
        scale[3,3]=1.0
        def short_proj():
          return np.dot(Axes3D.get_proj(ax), scale)
        ax.get_proj=short_proj
        ax.plot_surface(X, YY, Z, facecolors=plt.cm.CMRmap(norm(T)), rstride=1, cstride=1, antialiased=False)
        Top=np.max(Image_mat, axis=0)
        ZZ = np.ones(Top.shape)
        norm = matplotlib.colors.Normalize(vmin=Top.min(), vmax=Top.max())
        ax.plot_surface(Xx, Y, ZZ, facecolors=plt.cm.rainbow(norm(Top)), rstride=5, cstride=5, antialiased=False)
        Side=np.max(Image_mat, axis=1)
        XX = np.ones(Side.shape)*y
        norm = matplotlib.colors.Normalize(vmin=Side.min(), vmax=Side.max())
        ax.plot_surface(XX, Yy, Zz, facecolors=plt.cm.rainbow(norm(Side)), rstride=1, cstride=1, antialiased=False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.set_axis_off()
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.grid(False)
        ax.set_zlim(np.max(Z), np.min(Z))
        MY_PATH=path.split('/')
        my_path='/'.join(MY_PATH[:-1])
        names=MY_PATH[-1].split('.')
        PATH=my_path+'/'+names[0]+'_'+name+'_cube.tiff'
        canvas = FigureCanvasTkAgg(fig, master=root3)
        canvas.get_tk_widget().grid(row = 0, column=0, rowspan=2, sticky='nswe')
        canvas.draw()
        if PATH[-4:]=='.tiff':
            fig.savefig(PATH,pad_inches=0.001, bbox_inches='tight', dpi=300)
            image=cv2.imread(PATH,1)
            h,w=np.where(image[:,:,0]<=230)
            image_bgr=image[min(h):max(h), min(w):max(w),:]
            cv2.imwrite(PATH,image_bgr)
            image_RGB=cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        fig2 = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='white', edgecolor='white')
        ax = fig2.add_subplot(1,1,1)
        ax.imshow(image_RGB)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_axis_off()
        canvas = FigureCanvasTkAgg(fig2, master=frame)
        canvas.get_tk_widget().grid(row = 0, column=0, rowspan=2, sticky='nswe')
        canvas.draw()
        root3.destroy()
        root3.mainloop()
    t_plt3d = threading.Thread(target=plot_3dcube_thread)
    t_plt3d.setDaemon(True)
    t_plt3d.start()
def open_gif(root):
    frames = [tkinter.PhotoImage(file='HSI_PP.gif',format = 'gif -index %i' %(i)) for i in range(80)]
    def update(ind):
        frame = frames[ind]
        ind += 1
        if ind>79: #With this condition it will play gif infinitely
            ind = 0
        label.configure(image=frame)
        root.after(80, update, ind)
    label = tkinter.Label(root)
    label.pack()
    root.after(0, update, 0)
def raise_above_all(window):
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)
def time_convert(time):
    if time>3600:
        my_time=str(round(time/3600,2))+' hr'
    elif time>60 and time<3600:
        my_time=str(round(time/60,2))+' min'
    else:
        my_time=str(round(time, 2))+' sec'
    return my_time
def save_img(path, name, img):
    try:
        os.mkdir(path)
        cv2.imwrite(path+'/'+name+'.tiff', img)
    except:
       cv2.imwrite(path+'/'+name+'.tiff', img)
#%% hyperspectral image analysis
def HSI_analysis():
    class GUI:      
        def __init__(self, window):
            window.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
            self.input_text = StringVar(window)
            self.input_text1=StringVar(window)
            s = ttk.Style(window)
            s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font
            window.wm_iconbitmap('DAAI logo.ico')
            window.title("HSI analysis")
            window.resizable(0,0)
            window.deiconify()
            raise_above_all(window)
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            ttk.Button(window, text = "Load image", command = lambda: self.set_path_users_field(), width = 18, style='my.TButton').grid(row = 0, column = 0,  padx=2, pady=2, sticky='ew') 
            self.preprocessing_button=ttk.Button(window, text = "Image preprocessing", command = self.image_preprocessing , width = 18, style='my.TButton')
            self.preprocessing_button.grid(row = 1, column=1, padx=3, pady=2, sticky='ew') 
            self.preprocessing_button.config(state=tkinter.DISABLED)
            self.allimage_button=ttk.Button(window, text = "Batch processing",  command = self.All_images,width = 18, style='my.TButton')
            self.allimage_button.grid(row = 1, column=4, padx=3, pady=2, sticky='ew') 
            self.allimage_button.config(state=tkinter.DISABLED)
            self.feature_button=ttk.Button(window, text = "Feature extraction", command = self.feature_extract, width = 18, style='my.TButton')
            self.feature_button.grid(row = 1, column=2, padx=3, pady=2, sticky='ew') 
            self.feature_button.config(state=tkinter.DISABLED)
            self.model_button2=ttk.Button(window, text = "Analysis by model", width=18, command=self.import_model, style='my.TButton')
            self.model_button2.grid( row = 1, column = 3, padx=3, pady=2, sticky='ew')
            self.model_button2.config(state=tkinter.DISABLED)
            self.statusbar = tkinter.Label(window,text="Contact us: a.elmanawy_90@agr.suez.edu.eg",bd=1,relief=tkinter.SUNKEN,font='Tahoma 10 bold', bg='LightYellow2')
            self.statusbar.grid(row=6,column=0,columnspan=6, rowspan=2, sticky='ew')
            self.statusbar.config(width="100",anchor="w")
            ttk.Entry(window, textvariable = self.input_text, width = 60, font=('Times New Roman', 15), justify='left').grid( row = 0, column = 1,  columnspan=4, padx=2, pady=2, sticky='ew') 
        def destroy_frames(self):
            try:
                self.select_VI.destroy()
            except:
                pass
            try:
                self.cal_Button.destroy()
            except:
                pass
            try:
                self.button_frame.destroy()
            except:
                pass
            try:
                self.result_box.destroy()
            except:
                pass
            try:
                self.result_txt.destroy()
            except:
                pass
            try:
                self.results_frame.destroy()
            except:
                pass
            try:
                self.feature_frame.destroy()
            except:
                pass
            try:
                self.input_frame.destroy()
            except:
                pass
            try:
                self.Check_Frame.destroy()
            except:
                pass
            try:
                self.check_frame.destroy()
            except:
                pass
            try:
                self.output_frame.destroy()
            except:
                pass
            try:
                self.Done_button_crop.destroy()
            except:
                pass
        def set_path_users_field(self):
            self.destroy_frames()
            self.STD=0
            self.x_size=0
            self.y_size=0
            self.Windows=0
            self.order=0
            self.Windowsd=0
            self.orderd=0
            self.Derv=0
            self.morph_num=1
            self.path = ''
            self.path2=''
            self.time1=time.time()
            self.angles=[]
            self.steps=[]
            ## restart GUI ######################################
            self.preprocessing_button.config(state=tkinter.DISABLED)
            self.allimage_button.config(state=tkinter.DISABLED)
            self.feature_button.config(state=tkinter.DISABLED)
            self.model_button2.config(state=tkinter.DISABLED)
            try:
                self.canvas_frame.destroy()
            except:
                pass
            try:
                self.List_Frame.destroy()
            except:
                pass
            try:
                self.statusbar.destroy()
            except:
                pass
            try:
                self.canvas_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
                self.canvas_frame.grid(row=5, column=0, columnspan=4, sticky='w')
                self.List_Frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
                self.List_Frame.grid(row=5, column=4, sticky='nsw')
                self.statusbar = tkinter.Label(window,text="Contact us: a.elmanawy_90@agr.suez.edu.eg",bd=1,relief=tkinter.SUNKEN,font='Tahoma 10 bold', bg='LightYellow2')
                self.statusbar.grid(row=6,column=0,columnspan=6, rowspan=2, sticky='ew')
                self.statusbar.config(width="100",anchor="w")
            except:
                pass
            try:
                self.root_imgprocess.destroy()
                self.preprocessing_button2.destroy()
                root3.destroy()
            except:
                pass
            self.statusbar["text"]='please wait for extract HSI....'
            self.Max_hue=255
            self.min_hue=0
            self.min_VI=[]
            self.max_VI=[]
            self.Hs=[]
            self.max_saturation=255
            self.min_saturation=0
            self.max_value=255
            self.min_value=0
            self.image2crop=np.zeros([1,1,0])
            self.image_SNV=np.zeros([1,1,0])
            self.img_derv=np.zeros([1,1,0])
            self.image_msc=np.zeros([1,1,0])
            self.hsv=np.zeros([1,1,0])
            self.YCrCb=np.zeros([1,1,0])
            self.data_color=np.zeros([1,1])
            self.data_band=np.zeros([1,1])
            self.data_VI=np.zeros([1,1])
            self.LAB=np.zeros([1,1,0])
            self.image_filtered=np.zeros([1,1,0])
            self.img_selected=np.zeros([1,1,0])
            self.remove_specular=0
            self.median_filter=0
            self.path = select_infile(filt=['.raw', '.dat', '.mat', '.img', '.tif', '.bil'], title='Select HSI file', name='HSI file')
            self.input_text.set(self.path[-79:])
            self.K=0
            self.Bin=0
            self.x_size=0
            self.y_size=0
            self.spat_Bin=0
            self.path1 = ''
            self.image2crop=np.zeros([1,1,1])
            self.hsi_croped_image=np.zeros([1,1,1])
            self.all_parameter=np.zeros([1,1])
            self.HSI_Img_calib=np.zeros([1,1,1])
            self.HSI_Img=np.zeros([1,1,1])
            self.Image_bin=np.zeros([1,1,1])
            self.My_Vegetation=np.zeros([1,1])
            self.myvegetation=np.zeros([1,1])
            self.masked_img_green=np.zeros([1,1,0])
            self.hypercube=np.zeros([1,1,1])
            self.my_wave=[]
            author="'''\nThis program designed by: \n\t\t\t  (Ahmed Islam ElManawy) \nfor contact: \n\t   a.elmanawy_90@agr.suez.edu.com\n'''\nglobal Type, analysis_img\n"
            MY_PATH=self.path.split('/')
            my_path='/'.join(MY_PATH[:-1])
            global prj_path_creat, F_file
            prj_path_creat=my_path+'/HSI_PP prj.py'
            self.f=open(my_path+'/HSI_PP prj.py', 'w')
            self.f.write(author)
            F_file=self.f
            self.my_path_prj=my_path+'/HSI_PP prj.py'
            if self.path.endswith('.raw') or self.path.endswith('.dat') or self.path.endswith('.img') or self.path.endswith('.tif') or self.path.endswith('.bil'):
                speak('plaese wait for extract hyper spectral image')
                self.preprocessing_button.config(state=tkinter.ACTIVE)
                self.INFILE=self.path
                a=HDR_test(self.path)
                self.f.write("\ndef Type():\n\tType= "+"'"+self.path[-4:]+"'"+"\n\treturn Type")
                self.f.write("\ndef analysis_img(image_path, statusbar, wc, SR, BS, CS, Sb, Spc, Sc, Spb, Spz):\n\tMY_PATH=image_path.split('/')\n\tname=MY_PATH[-1].split('.')[0]\n\tmy_path='/'.join(MY_PATH[:-1])")
                if a==1:
                    self.HSI_Img = open_hsi_img(self.INFILE)
                    self.RGB_Image=open_rgb_img(self.INFILE)
                    self.wave_length=wavelength(self.INFILE, 'hdr')
                    self.my_wave=self.wave_length
                    self.hypercube=self.HSI_Img
                    self.file_type=self.path[-4:]
                    self.f.write("\n\thypercube = open_hsi_img(image_path)\n\thypercube=extract_hsi(hypercube)\n\tRGB_Image=open_rgb_img(image_path)\n\t")
                    self.f.write("wave_length=wavelength(image_path, 'hdr')\n\tif 0 in wave_length:\n\t\th_0=np.where(wave_length==0)\n\t\twave_length=np.delete(wave_length, h_0[0])\n\t\thypercube=np.delete(hypercube, h_0[0], axis=2)\n\t")
                    self.f.write("speak(name[:6]+' hyper spectral image extracted')\n\tstatusbar['text']=name+' extracted'\n\t")
                else:
                    self.statusbar["text"]='Error! header file not available'
            elif self.path.endswith('.mat'):
                zero_wavelength=1
                self.preprocessing_button.config(state=tkinter.ACTIVE)
                self.f.write("\ndef Type():\n\tType= "+"'"+self.path[-4:]+"'"+"\n\treturn Type")
                self.f.write("\ndef analysis_img(image_path, statusbar, wc, SR, BS, CS, Sb, Spc, Sc, Spb, Spz):\n\tMY_PATH=image_path.split('/')\n\tname=MY_PATH[-1].split('.')[0]\n\tmy_path='/'.join(MY_PATH[:-1])")
                try:
                    self.wave_length, self.HSI_Img, self.RGB_Image = open_mat_img(self.path)
                    cv2.imwrite(self.path[:-4]+'.tiff',  self.RGB_Image)
                    self.my_wave=self.wave_length
                    self.hypercube=self.HSI_Img
                    self.f.write("\n\twave_length, HSI_Img, RGB_Image = open_mat_img(image_path)\n\thypercube=HSI_Img\n\t")
                    self.f.write("speak(name[:6]+' image extracted')\n\tstatusbar['text']=name+' extracted'\n\t")
                except Exception as e:
                    self.statusbar["text"]=e 
                self.file_type=self.path[-4:]
            else:
                speak('This type of file is unknown')
            if self.HSI_Img.shape[2]>1:
                raise_above_all(window)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.RGB_Image)
                ax.set_yticks([])
                ax.set_xticks([])
                ax.set_title('Color image', fontsize=5)
                canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                canvas.get_tk_widget().grid(row = 0, column=0, columnspan=3)
                canvas.draw()
                zero_wavelength=0
                raise_above_all(window)
                if 0 in self.wave_length:
                    raise_above_all(window)
                    zero_wavelength=1
                    h_0=np.where(self.wave_length==0)
                    self.wave_length=np.delete(self.wave_length, h_0[0])
                    self.HSI_Img=extract_hsi(self.HSI_Img)
                    self.HSI_Img=np.delete(self.HSI_Img, h_0[0], axis=2)
                    self.my_wave=self.wave_length
                def get_list(event):
                    self.statusbar["text"]='Display The band....'
                    self.index = self.listNodes.curselection()[0]
                    self.seltext = self.listNodes.get(self.index)
                    self.Band=self.hypercube[:,:,self.index]
                    name=str(self.seltext[3])+' nm'
                    title='Reflection heat map at ' + name
                    plot_contour(self.Band, 0, 0, self.canvas_frame, title, self.path, name, (2,2), 'lightyellow')
                    self.statusbar["text"]='Display band '+name
                def Get_list():
                    self.statusbar["text"]='Display The bands....'
                    index = self.listNodes.curselection()
                    fig = matplotlib.figure.Figure(figsize=(4,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                    X_axis=np.array(range(self.hypercube.shape[0])) ## lines direction ys
                    Y_axis=np.array(range(self.hypercube.shape[1])) ## sample direction xs
                    row=round((len(index)/2)+0.1)
                    i=0
                    for INDEX in index:
                        i+=1
                        seltext = self.listNodes.get(INDEX)
                        Band=self.hypercube[:,:,INDEX] #####
                        ax2 = fig.add_subplot(row,2,i)
                        ax1=ax2.contourf(Y_axis, X_axis, Band, levels=np.linspace(np.amin(Band),np.amax(Band),50), cmap=plt.get_cmap('CMRmap'))
                        ax2.set_xlim(Y_axis[0], Y_axis[-1])
                        ax2.set_ylim(X_axis[-1], X_axis[0])
                        fig.colorbar(ax1, ax=ax2, aspect=50, fraction=.12,pad=.02).ax.tick_params(labelsize=5)
                        ax2.set_yticks([])
                        ax2.set_xticks([])
                        ax2.set_title('Reflection heat map at  ' + str(seltext[3])+' nm', fontsize=5)
                        self.statusbar["text"]='Display The bands'
                        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                        canvas.get_tk_widget().grid(row = 0, column=0, sticky='e')
                        canvas.draw()
                style = ttk.Style(window)
                style.configure("BW.TLabel", foreground="black", background="lightyellow")
                select=ttk.Label(self.List_Frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15))
                select.grid( row = 0, column = 0, padx=2, pady=2, sticky='n')
                self.oks=ttk.Button(self.List_Frame, text='OK', command=Get_list, style='my.TButton')
                self.oks.grid( row = 2, column = 0, padx=2, pady=2, sticky='s')
                self.listNodes = tkinter.Listbox(self.List_Frame, width=18, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                self.listNodes.grid(row=1, column=0, sticky='ns')
                scrollbar = ttk.Scrollbar(self.List_Frame, orient="vertical")
                scrollbar.config(command=self.listNodes.yview) ## connected scrollbar with listnodes
                scrollbar.grid(row=1, column=1, sticky='ns')
                self.listNodes.config(yscrollcommand=scrollbar.set) ## connected listnodes with scrollbar
                self.listNodes.bind('<Double-1>', get_list)
                self.my_ListNodes=self.listNodes
                Xx=0
                for x in self.wave_length:
                    Xx+=1
                    self.listNodes.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                raise_above_all(window)
                if zero_wavelength==0:
                    self.HSI_Img=extract_hsi(self.HSI_Img)
                    self.hypercube=self.HSI_Img
                raise_above_all(window)
                speak('The image has been extracted')
                self.statusbar["text"]='The image has been extracted'
        def feature_extract(self):
            try:
                self.preprocessing_button2.destroy()
            except:
                pass
            try:
                self.root_imgprocess.destroy()
            except:
                pass
            self.destroy_frames()
            self.statusbar["text"]='Please select feature/s to extract from hypercube'
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.feature_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.feature_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky='ewn')
            self.reduction_button=ttk.Button(self.feature_frame, text = "Data augmentation", command = self.Data_augmentation, width = 20, style='my.TButton')
            self.reduction_button.grid(row = 0, column=0, padx=5, pady=2, sticky='ew') 
            self.texture_button=ttk.Button(self.feature_frame, text = "Texture features", command = self.Texture_Features, width = 20, style='my.TButton')
            self.texture_button.grid(row = 1, column=0, padx=5, pady=2, sticky='ew') 
            self.morphology_button=ttk.Button(self.feature_frame, text = "Geometric features", command=self.Morphology, width = 20, style='my.TButton')
            self.morphology_button.grid(row = 0, column=1, padx=5, pady=2, sticky='ew') 
            ttk.Button(self.feature_frame, text = "Vegetation indices",  command=self.HSI_index, width = 15, style='my.TButton').grid(row = 1, column=1, padx=5, pady=2, sticky='ew') 
        def Texture_Features(self):
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, columnspan=2, sticky='ew')
            angle_frame=tkinter.LabelFrame(self.input_frame, bg='lightyellow', bd=0)
            angle_frame.grid(row=0, column=0, sticky='ew')
            step_frame=tkinter.LabelFrame(self.input_frame, bg='lightyellow', bd=0)
            step_frame.grid(row=0, column=1, sticky='ew')
            speak('Please select angles and step for calculate texture features')
            self.statusbar['text']= 'Please select angles and step for calculate texture features'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
            def calculate():
                self.statusbar["text"]=('Calcualte texture features.....')
                Entropy, Homogenity, Correlation, Contrast, Energy=texture_features(Images,self.angles,self.steps)
                df_Entropy=pd.DataFrame(Entropy)
                df_Homogenity=pd.DataFrame(Homogenity)
                df_Correlation=pd.DataFrame(Correlation)
                df_Contrast=pd.DataFrame(Contrast)
                df_Energy=pd.DataFrame(Energy)
                try:
                    os.mkdir(self.my_path+'/Excel files')
                    writer = pd.ExcelWriter(self.my_path+'/Excel files/'+self.name+'_texture_feature.xlsx', engine='xlsxwriter')
                except:
                    writer = pd.ExcelWriter(self.my_path+'/Excel files/'+self.name+'_texture_feature.xlsx', engine='xlsxwriter')
                writer.book.use_zip64()
                df_Entropy.to_excel(writer, sheet_name='Entropy', index=False)
                df_Homogenity.to_excel(writer, sheet_name='Homogenity', index=False)
                df_Correlation.to_excel(writer, sheet_name='Correlation', index=False)
                df_Contrast.to_excel(writer, sheet_name='Contrast', index=False)
                df_Energy.to_excel(writer, sheet_name='Energy', index=False)
                writer.save()
                speak('The features have been saved!')
                self.statusbar["text"]=('Texture features calculated')
            def Get_angle():
                speak('The angles are selected.')
                angles=[]
                self.index_angle = anglelist.curselection()
                angle=[0, np.pi/4, np.pi/2, 3*np.pi/4]
                for i in self.index_angle:
                    angles.append(angle[i])
                self.angles=np.asarray(angles)
            def Get_step():
                speak('The steps are selected.')
                steps=[]
                self.index_step = steplist.curselection()
                for i in self.index_step:
                    steps.append(i+1)
                self.steps=np.asarray(steps)
            ttk.Button(self.input_frame, text='Angle', command=Get_angle, width=10, style='my.TButton').grid(row=1, column=0,  padx=2, pady=2)
            anglelist = tkinter.Listbox(angle_frame, width=10, height=4, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
            anglelist.grid(row=0, column=0)
            scrollbar2 = ttk.Scrollbar(angle_frame, orient="vertical")
            scrollbar2.config(command=anglelist.yview) ## connected scrollbar with listnodes
            scrollbar2.grid(row=0, column=1, sticky='ns')
            anglelist.config(yscrollcommand=scrollbar2.set) ## connected listnodes with scrollbar
            for x in range(0,180,45):
                anglelist.insert(tkinter.END, (int(x)))
            ttk.Button(self.input_frame, text='Step', command=Get_step, style='my.TButton').grid(row=1, column=1,  padx=2, pady=2)
            steplist = tkinter.Listbox(step_frame, width=10, height=4, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
            steplist.grid(row=0, column=0)
            scrollbar2 = ttk.Scrollbar(step_frame, orient="vertical")
            scrollbar2.config(command=steplist.yview) ## connected scrollbar with listnodes
            scrollbar2.grid(row=0, column=1, sticky='ns')
            steplist.config(yscrollcommand=scrollbar2.set) ## connected listnodes with scrollbar
            for x in range(1,11):
                steplist.insert(tkinter.END, (int(x)))
            ttk.Button(self.input_frame, text='Calculate', command=calculate, style='my.TButton').grid( row = 2, column = 0, columnspan=2, padx=2, pady=2, sticky='n')
        def Morphology(self):
            self.destroy_frames()
            speak('Please wait for calculate morphological features')
            self.statusbar["text"]='Calculate morphological features.....'
            img=cv2.imread(self.my_path+'/binarry/'+self.name+'.tiff', 1)
            self.all_parameter=calculate_morphology(img, self.my_path, self.name, self.masked_img_green, display=True)
        def radiometric_calib(self):
            self.destroy_frames()
            self.statusbar["text"]='Extract reference board.......'
            def Extract_white_board():
                speak('Segment reference board by choicing threshold values')
                self.blur_white = cv2.GaussianBlur(self.RGB_Image, (5, 5), 0.75)
                self.hsv_white = cv2.cvtColor(self.blur_white, cv2.COLOR_BGR2HSV)
                self.Max_hue_white=255
                self.min_hue_white=0
                self.max_saturation_white=255
                self.min_saturation_white=0
                self.max_value_white=255
                self.min_value_white=0
                white_board_extraction(self.hsv_white)
            def get_scale_value_min_1(val):
                self.Max_hue_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_1(val):
                self.min_hue_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_min_2(val):
                self.max_saturation_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_2(val):
                self.min_saturation_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_min_3(val):
                self.max_value_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_3(val):
                self.min_value_white=int(val)
                self.img_binarry_white_board, self.masked_white_board, Binarry_white_board=image_segmentation(self.RGB_Image, self.hsv_white, self.min_hue_white, self.Max_hue_white, self.min_saturation_white, self.max_saturation_white, self.min_value_white, self.max_value_white)
                rgb_frame=tkinter.LabelFrame(self.root_hsv_white, text='Segmented Image')
                rgb_frame.grid(row=2, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_white_board)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def white_board_extraction(hsv):
                try:
                    self.root_hsv_white.destroy()
                    self.hue_window.destroy()
                    self.value_window.destroy()
                    self.saturat_window.destroy()
                except:
                    pass
                self.root_hsv_white=tkinter.Tk()
                self.root_hsv_white.title("Extract reference board")
                self.root_hsv_white.wm_iconbitmap('DAAI logo.ico')
                self.root_hsv_white.configure()
                self.root_hsv_white.resizable(False, False)
                self.hue_window=tkinter.Tk()
                self.hue_window.title("Hue")
                self.hue_window.wm_iconbitmap('DAAI logo.ico')
                self.hue_window.configure()
                self.hue_window.resizable(False, False)
                plot_contour(hsv[:,:,0], 0, 0, self.hue_window, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.hue_window, from_=np.amax(hsv[:,:,0]), to=np.amin(hsv[:,:,0]), length=100, command=get_scale_value_min_1, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,0]))
                w2 = tkinter.Scale(self.hue_window, from_=np.amax(hsv[:,:,0]), to=np.amin(hsv[:,:,0]), length=100, command=get_scale_value_max_1, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,0]))
                self.saturat_window=tkinter.Tk()
                self.saturat_window.title("Saturat")
                self.saturat_window.wm_iconbitmap('DAAI logo.ico')
                self.saturat_window.configure()
                plot_contour(hsv[:,:,1], 0, 0, self.saturat_window, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.saturat_window, from_=np.amax(hsv[:,:,1]), to=np.amin(hsv[:,:,1]), length=100, command=get_scale_value_min_2, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,1]))
                w2 = tkinter.Scale(self.saturat_window, from_=np.amax(hsv[:,:,1]), to=np.amin(hsv[:,:,1]), length=100, command=get_scale_value_max_2, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,1]))
                value_frame=tkinter.LabelFrame(self.root_hsv_white, text='v')
                value_frame.grid(row=2, column=1)
                self.value_window=tkinter.Tk()
                self.value_window.title("Value")
                self.value_window.wm_iconbitmap('DAAI logo.ico')
                self.value_window.configure()
                plot_contour(hsv[:,:,2], 0, 0, self.value_window, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.value_window, from_=np.amax(hsv[:,:,2]), to=np.amin(hsv[:,:,2]), length=100, command=get_scale_value_min_3, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,2]))
                w2 = tkinter.Scale(self.value_window, from_=np.amax(hsv[:,:,2]), to=np.amin(hsv[:,:,2]), length=100, command=get_scale_value_max_3, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,2]))
                def hsi_calib():
                    try:
                        self.root_hsv_white.destroy()
                    except:
                        pass
                    try:
                        self.hue_window.destroy()
                    except:
                        pass
                    try:
                        self.value_window.destroy()
                    except:
                        pass
                    try:
                        self.saturat_window.destroy()
                    except:
                        pass
                    self.statusbar["text"]='Wait for image calibration.......'
                    self.img_binarry_white_board=modify_binarry(self.img_binarry_white_board)
                    cv2.imwrite(self.path.split('.')[0]+'_white.jpg', self.img_binarry_white_board)
                    self.HSI_Img_calib=white_calib(self.HSI_Img, self.img_binarry_white_board)
                    if self.HSI_Img_calib.shape[2]>1:
                      self.statusbar["text"]='The image has been calibrated'
                      speak('The image has been calibrated')
                      self.hypercube=self.HSI_Img_calib
                      self.f.write("\n\tif wc==1:\n\t\tspeak('Please wait for radiometric '+ name+' calibrating')\n\t\tstatusbar['text']=name+' calibrating....'\n\t\tblur_white = cv2.GaussianBlur(RGB_Image, (5, 5), 0.75)\n\t\thsv_white = cv2.cvtColor(blur_white, cv2.COLOR_BGR2HSV)\n\t\t")
                      self.f.write("img_binarry_white_board, masked_white_board, Binarry_white_board=image_segmentation(RGB_Image, hsv_white, "+str(self.min_hue_white)+','+ str(self.Max_hue_white)+',' +str(self.min_saturation_white)+',' +str(self.max_saturation_white)+',' +str(self.min_value_white)+',' +str(self.max_value_white)+")")
                      self.f.write("\n\t\timg_binarry_white_board=modify_binarry(img_binarry_white_board)\n\t\tcv2.imwrite(my_path+'/'+name+'_white.jpg', img_binarry_white_board)\n\t\thypercube=white_calib(hypercube, img_binarry_white_board)\n\t\tstatusbar['text']=name+' calibrated'\n\t\tspeak(name+' calibrated')\n\t")
                      def get_list(event):
                          self.statusbar["text"]='Display The selected band....'
                          self.index = self.listnodes.curselection()[0]
                          self.seltext = self.listnodes.get(self.index)
                          self.Band=self.HSI_Img_calib[:,:,self.index]
                          name=str(self.seltext[3])+' nm after calibration'
                          title='Reflection heat map at ' + name
                          plot_contour(self.Band[:,:], 0, 0, self.canvas_frame, title, self.path, name, (2,2), 'lightyellow')
                          self.statusbar["text"]='Display band '+name
                    select=ttk.Label(self.List_Frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15))
                    select.grid( row = 0, column = 0, padx=2, pady=2, sticky='n')
                    self.listnodes = tkinter.Listbox(self.List_Frame, width=18, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                    self.listnodes.grid(row=1, column=0, sticky='ns')
                    scrollbar = ttk.Scrollbar(self.List_Frame, orient="vertical")
                    scrollbar.config(command=self.listnodes.yview) ## connected scrollbar with listnodes
                    scrollbar.grid(row=1, column=1, sticky='ns')
                    self.listnodes.config(yscrollcommand=scrollbar.set) ## connected listnodes with scrollbar
                    self.listnodes.bind('<Double-1>', get_list)
                    self.my_ListNodes=self.listnodes
                    Xx=0
                    for x in self.wave_length:
                        Xx+=1
                        self.listnodes.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                ttk.Button(self.root_hsv_white, text='Extract', command=hsi_calib, style='my.TButton').grid(row=0, column=0)
                self.root_hsv_white.mainloop()
                self.hue_window.mainloop()
                self.value_window.mainloop()
                self.saturat_window.mainloop()
            Extract_white_board()
        def HSI_index(self):
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=1, columnspan=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            speak('please select vegetation index from list.')
            self.statusbar["text"]='Please select vegetation index'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
            def select_vegetation():
                 self.Vi=VI.current()
                 NUM=[ 0,  1,  4,  8,  9, 10, 11, 12, 13, 16, 17, 18, 20, 23]
                 if self.Vi in NUM:
                     speak('Please select two bands from list')
                     self.statusbar["text"]='Please select two bands from bands list'
                 elif self.Vi==15:
                     speak('Please select four bands from list')
                     self.statusbar["text"]='Please select four bands from bands list'
                 else:
                     speak('please select three bands from list')
                     self.statusbar["text"]='Please select three bands from bands list'
            ttk.Button(self.input_frame, text = "OK",command=select_vegetation,  width=20, style='my.TButton').grid( row = 1, column = 0, sticky='ew')
            def calculate_index():
                speak('Please wait for calculate '+self.Values[self.Vi])
                self.statusbar["text"]='Please wait '+self.Values[self.Vi]+ ' calculating.....'
                self.IVs=[]
                self.veg_wave=[]
                selection = Listbox.curselection()
                for s in selection:
                    seltext = Listbox.get(s)
                    self.IVs.append(seltext[1]-1)
                    self.veg_wave.append(round(seltext[3]))
                if self.masked_img_green.shape[2]>1:
                    if len(Images.shape)==3:
                        self.myvegetation=vegetation_index(Images, self.IVs, self.Vi)
                        self.myvegetation=np.asarray(self.myvegetation)
                        vegetation=self.myvegetation
                        name=self.My_name+'_'+self.Values[self.Vi]
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.myvegetation, self.veg_wave, name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                    elif len(Images.shape)==1 or len(Images.shape)==4:
                        self.myvegetation=[]
                        for i in range(Images.shape[0]):
                            sub_image=Images[i]
                            My_Vegetation=vegetation_index(sub_image, self.IVs, self.Vi)
                            My_Vegetation=np.asarray(My_Vegetation)
                            self.myvegetation.append(My_Vegetation)
                            name=self.My_name+'_'+self.Values[self.Vi]+str(i+1)
                            save_mat_file(self.path, My_Vegetation, self.veg_wave, name, 0)
                        speak('The vegetation index have been saved')
                        self.myvegetation=np.asarray(self.myvegetation)
                        vegetation=self.myvegetation[0]
                else:
                    self.My_Vegetation=vegetation_index(Images, self.IVs, self.Vi)
                    self.My_Vegetation=np.asarray(self.My_Vegetation)
                    self.VI=self.Vi
                    self.IVS=self.IVs
                    vegetation=self.My_Vegetation
                if len(vegetation.shape)>2:
                    vegetation=vegetation[:,:,0]
                    self.My_Vegetation=vegetation
                else:
                    pass
                plot_contour(vegetation, 0, 0, self.canvas_frame, self.Values[self.Vi], self.path, self.Values[self.Vi], (2,2), 'lightyellow')
                self.statusbar["text"]=self.Values[self.Vi]+' has been calculated'
            self.select_VI=ttk.Button(self.List_Frame, text = "Select", command = calculate_index, style='my.TButton')
            self.select_VI.grid( row = 2, column = 0, padx=2, pady=2, sticky='s')
            self.Values=['CI green', 'CI red', 'EPVI', 'EVI', 'Green NDVI','GreenNDVI-NDVI', 'MCARI', 'MDATT', 'MSR', 'NCPI', 'NDVI', 'NDWI','OSAV', 'PRI', 'PSRI', 'REIP', 'RNDVI', 'Red-edge NDVI', 'SD','SIPI', 'SR', 'TBDR', 'TCARI', 'VARI green', 'mND']
            VI = ttk.Combobox(self.input_frame, values=self.Values, width=20, font=('Times New Roman', 15), justify='center')
            VI.set("CI green")
            VI.grid( row = 0, column = 0, sticky='ew')
        def image_preprocessing(self):
            def img_process2():
                raise_above_all(self.root_imgprocess)
            self.preprocessing_button2=ttk.Button(window, text = "Image preprocessing", command=img_process2, width = 20, style='my.TButton')
            self.preprocessing_button2.grid(row = 1, column=1, padx=5, pady=2, sticky='ew') 
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.root_imgprocess=tkinter.Tk()
            self.root_imgprocess.title("Image preprocessing")
            self.root_imgprocess.wm_iconbitmap('DAAI logo.ico')
            self.root_imgprocess.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
            self.root_imgprocess.resizable(False, False) # this prevents from resizing the window
            s = ttk.Style(self.root_imgprocess)
            s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font
            self.vegetation_button=ttk.Button(self.root_imgprocess, text = "Vegetation indices",  command=self.HSI_index, width = 20, style='my.TButton')
            self.vegetation_button.grid(row = 0, column=1, padx=5, pady=2, sticky='ew')
            self.calib_button=ttk.Button(self.root_imgprocess, text = "Radiometric calib", command=self.radiometric_calib, width = 20, style='my.TButton')
            self.calib_button.grid(row = 0, column=0, padx=5, pady=2, sticky='ew')
            self.segmentation_button=ttk.Button(self.root_imgprocess, text = "Image segmentation", command = self.image_segmentation , width = 20, style='my.TButton')
            self.segmentation_button.grid(row = 1, column=0,  padx=2, pady=2,sticky='ew') 
            self.reout_button=ttk.Button(self.root_imgprocess, text='Remove outliers', command=self.remove_outliers, width = 20, style='my.TButton')
            self.reout_button.grid(row=1, column=1,  padx=2, pady=2,sticky='ew')
            self.msc_button=ttk.Button(self.root_imgprocess, text='MSC', command=self.MSC, width = 20, style='my.TButton')
            self.msc_button.grid(row=3, column=0,  padx=2, pady=2,sticky='ew')
            self.SNV_button=ttk.Button(self.root_imgprocess, text='SNV', command=self.SNV, width = 20, style='my.TButton')
            self.SNV_button.grid(row=3, column=1,  padx=2, pady=2,sticky='ew')
            self.sgs_button=ttk.Button(self.root_imgprocess, text='SG_smooth', command=self.SG_smooth, width = 20, style='my.TButton')
            self.sgs_button.grid(row=2, column=0,  padx=2, pady=2,sticky='ew')
            self.sgd_button=ttk.Button(self.root_imgprocess, text='SG_derv', command=self.SG_derv, width = 20, style='my.TButton')
            self.sgd_button.grid(row=2, column=1,  padx=2, pady=2,sticky='ew')
            self.binning_button=ttk.Button(self.root_imgprocess, text = "Spectral binning", command = self.hsi_binning, width = 20, style='my.TButton')
            self.binning_button.grid(row = 4, column=0, padx=2, pady=2, sticky='ew') 
            self.spatial_binning_button=ttk.Button(self.root_imgprocess, text = "Spatial binning", command = self.spat_binning,width = 20, style='my.TButton')
            self.spatial_binning_button.grid(row = 6, column=0, padx=2, pady=2, sticky='ew') 
            self.crop_button=ttk.Button(self.root_imgprocess, text = "Spectral crop", command = self.hsi_crop, width = 20, style='my.TButton')
            self.crop_button.grid(row = 4, column=1, padx=2, pady=2, sticky='ew') 
            self.spatial__crop_button=ttk.Button(self.root_imgprocess, text = "Spatial crop", command=self.Spatial_crop,  width = 20, style='my.TButton')
            self.spatial__crop_button.grid(row = 5, column=1, padx=2, pady=2, sticky='ew') 
            self.select_button=ttk.Button(self.root_imgprocess, text = "Select bands", command = self.select_bands, width = 20, style='my.TButton')
            self.select_button.grid(row = 5, column=0, padx=2, pady=2, sticky='ew') 
            self.resize_button=ttk.Button(self.root_imgprocess, text = "Spatial resize",  command = self.saptial_resize, width = 20, style='my.TButton')
            self.resize_button.grid(row = 6, column=1, padx=2, pady=2, sticky='ew') 
            if self.K==0:
                self.SNV_button.config(state=tkinter.DISABLED)
                self.msc_button.config(state=tkinter.DISABLED)
                self.reout_button.config(state=tkinter.DISABLED)
                self.sgd_button.config(state=tkinter.DISABLED)
                self.sgs_button.config(state=tkinter.DISABLED)
                self.binning_button.config(state=tkinter.DISABLED)
                self.spatial_binning_button.config(state=tkinter.DISABLED)
                self.crop_button.config(state=tkinter.DISABLED)
                self.spatial__crop_button.config(state=tkinter.DISABLED)
                self.select_button.config(state=tkinter.DISABLED)
                self.resize_button.config(state=tkinter.DISABLED)
            def destroy():
                self.root_imgprocess.destroy()
                try:
                    self.preprocessing_button2.destroy()
                except:
                    pass
            self.root_imgprocess.protocol('WM_DELETE_WINDOW', destroy)
            self.root_imgprocess.mainloop()
        def SG_smooth(self):
            self.destroy_frames()
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            values=[]
            for x in range(3, 23, 2):
                values.append((int(x)))
            self.windowss = ttk.Combobox(self.input_frame, values=values, width=5, font=('Times New Roman', 15), justify='center')
            self.windowss.set("3")
            self.windowss.grid( row = 0, column = 1, columnspan=2, sticky='w')
            window_label=ttk.Label(self.input_frame, text='Window size', style="BW.TLabel", font=('Times New Roman', 15))
            window_label.grid( row = 0, column = 0,  sticky='e')
            value=[]
            for x in range(2,10):
                value.append((int(x)))
            self.polyorders = ttk.Combobox(self.input_frame, values=value, width=5, font=('Times New Roman', 15), justify='center')
            self.polyorders.set("2")
            self.polyorders.grid( row = 1, column = 1, columnspan=2, sticky='w')
            poly_label=ttk.Label(self.input_frame, text='Polynomial', style="BW.TLabel", font=('Times New Roman', 15))
            poly_label.grid( row = 1, column = 0,  sticky='e')
            speak('Please select window size and polynomial degree')
            self.statusbar["text"]='Please select window size and polynomial degree'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            def accept():
               self.windowss.destroy()
               self.polyorders.destroy()
               self.ok_button.destroy()
               self.Done_button.destroy()
               window_label.destroy()
               poly_label.destroy()
               self.hypercube=self.smooth_img_cube
               self.statusbar["text"]='The image have been smoothed'
               self.My_name+='_smooth'
               ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.smooth_img_cube, Wave, self.My_name, 1), width=21, style='my.TButton').grid( row = 0, column = 0, columnspan=2, sticky='ew')
               ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.smooth_img_mean,Wave, self.My_name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
               ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.smooth_img_cube,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 2, column = 0,  columnspan=2,sticky='ew')
               self.f.write("hypercube=sg(hypercube, "+str( self.Windows)+","+str(self.order)+", 0)[0]\n\t")
            def smoothing():
                try:
                    self.Done_button.destroy()
                except:
                    pass
                speak('Please wait!')
                self.statusbar["text"]='Image smoothing....'
                self.Windows=int(self.windowss.get())
                self.order=int(self.polyorders.get())
                self.smooth_img_cube, self.smooth_img_mean=sg(Images, self.Windows, self.order, 0)
                if self.smooth_img_mean.shape[0]>=1:
                    self.statusbar["text"]='Image smoothed'
                    if len(self.smooth_img_cube.shape)==3:
                        plot_spectrum(self.smooth_img_cube, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title="Spectrum after smoothing", legend=1, path=self.path, name="Spectrum after smoothing")
                    else:    
                        plot_spectrum(self.smooth_img_mean, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title="Spectrum after smoothing", legend=1, path=self.path, name="Spectrum after smoothing")
                    self.Done_button=ttk.Button(self.input_frame, text = "Done", command = accept, style='my.TButton')
                    self.Done_button.grid( row = 3, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
            self.ok_button=ttk.Button(self.input_frame, text = "OK", command = smoothing, style='my.TButton')
            self.ok_button.grid( row = 2, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
        def SG_derv(self):
            self.destroy_frames()
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            values=[]
            for x in range(3, 23, 2):
                values.append((int(x)))
            self.window = ttk.Combobox(self.input_frame, values=values, width=5, font=('Times New Roman', 15), justify='center')
            self.window.set("3")
            self.window.grid( row = 0, column = 1, columnspan=2, sticky='w')
            window_label=ttk.Label(self.input_frame, text='Window size', style="BW.TLabel", font=('Times New Roman', 15))
            window_label.grid( row = 0, column = 0,  sticky='e')
            value=[]
            for x in range(2,10):
                value.append((int(x)))
            self.polyorder = ttk.Combobox(self.input_frame, values=value, width=5, font=('Times New Roman', 15), justify='center')
            self.polyorder.set("2")
            self.polyorder.grid( row = 1, column = 1, columnspan=2, sticky='w')
            poly_label=ttk.Label(self.input_frame, text='Polynomial', style="BW.TLabel", font=('Times New Roman', 15))
            poly_label.grid( row = 1, column = 0,  sticky='e')
            Valued=[]
            for x in range(1,3):
                Valued.append((int(x)))
            self.derv = ttk.Combobox(self.input_frame, values=Valued, width=5, font=('Times New Roman', 15), justify='center')
            self.derv.set("1")
            self.derv.grid( row = 2, column = 1, columnspan=2, sticky='w')
            poly_label=ttk.Label(self.input_frame, text='Derv degree', style="BW.TLabel", font=('Times New Roman', 15))
            poly_label.grid( row = 2, column = 0,  sticky='e')
            speak('Please select window size, polynomial and derivative degree')
            self.statusbar["text"]='Please select window size, polynomial and derivative degree'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            def derivative():
                speak('Please wait!')
                self.statusbar["text"]='Image derivative....'
                self.Windowsd=int(self.window.get())
                self.orderd=int(self.polyorder.get())
                self.Derv=int(self.derv.get())
                self.img_derv_cube, self.img_derv=sg(Images, self.Windowsd, self.orderd, self.Derv)
                if self.Derv==1:
                    name=self.My_name+'_First dervative'
                else:
                    name=self.My_name+'_Second dervative'
                if self.img_derv.shape[0]>=1:
                    self.statusbar["text"]='Image derivative'
                    ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.img_derv,Wave, name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 3, column = 0, columnspan=2, sticky='ew')
                    ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.img_derv_cube, Wave, name, 1), width=21, style='my.TButton').grid( row = 0, column = 0, columnspan=2, sticky='ew')
                    plot_spectrum(self.img_derv, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title=name[-16:], legend=0, path=self.path, name=name)
                    self.statusbar["text"]=name+' is Calculated'
            self.ok_button=ttk.Button(self.input_frame, text = "OK", command = derivative, style='my.TButton')
            self.ok_button.grid( row = 3, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
        def MSC(self):
            self.destroy_frames()
            speak('Please wait')
            self.statusbar["text"]='Calculate MSC...'        
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            self.image_msc=np.asarray(MSC_image(Images)[0])
            self.imgae_msc_cube=MSC_image(Images)[1]
            name=self.My_name+' MSC'
            if self.image_msc.shape[1]>1:
                ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.image_msc,Wave, name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.imgae_msc_cube, Wave, name, 1), width=21, style='my.TButton').grid( row = 0, column = 0, columnspan=2, sticky='ew')
                plot_spectrum(self.image_msc, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title="MSC", legend=0, path=self.path, name='MSC')
                self.statusbar["text"]='MSC is Calculated'
        def SNV(self):
            self.destroy_frames()
            speak('Please wait')
            self.statusbar["text"]='Calculate SNV...'
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            self.image_SNV=np.asarray(SNV_image(Images)[0])
            self.image_snv_cube=SNV_image(Images)[1]
            name=self.My_name+' SNV'
            if self.image_SNV.shape[1]>1:
                ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.image_SNV,Wave, name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_snv_cube, Wave, name, 1), width=21, style='my.TButton').grid( row = 0, column = 0, columnspan=2, sticky='ew')
                plot_spectrum(self.image_SNV, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title="SNV", legend=0, path=self.path, name="SNV")        
                self.statusbar["text"]='SNV is Calculated'
        def remove_outliers(self):
            self.destroy_frames()
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            values=[]
            for x in np.arange(1.0, 6.1, 0.1):
                values.append((round(x,4)))
            self.CB = ttk.Combobox(self.input_frame, values=values, width=5, font=('Times New Roman', 15), justify='center')
            self.CB.set("0.0")
            self.CB.grid( row = 0, column = 1, columnspan=2, sticky='w')
            std_label=ttk.Label(self.input_frame, text='STD', style="BW.TLabel", font=('Times New Roman', 15))
            std_label.grid( row = 0, column = 0,  sticky='e')
            speak('Please select standard deviation threshold value')
            self.statusbar["text"]='Please select standard deviation threshold value'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
                    self.statusbar["text"]='Cant remove outlier pixels from multi-images, please remove outlier pixels before spatial crop'
            def accept():
               self.CB.destroy()
               self.ok_button.destroy()
               self.Done_button.destroy()
               std_label.destroy()
               self.STD=self.std
               speak('Outliers have been removed')
               self.statusbar["text"]='Outliers have been removed'
               self.hypercube=self.clean_img
               self.My_name+="_Without_outliers"
               ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.clean_img, Wave, self.My_name, 1), width=21, style='my.TButton').grid( row = 0, column = 0, columnspan=2, sticky='ew')
               ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.clean_img,Wave, self.My_name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
               ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.clean_img,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 2, column = 0,  columnspan=2,sticky='ew')
               self.f.write("hypercube=remove_Outliers(hypercube,"+str(self.std)+")\n\t")
            def outliers():
                try:
                    self.Done_button.destroy()
                except:
                    pass
                speak('Please wait!')
                self.statusbar["text"]='Remove outliers....'
                self.std=float(self.CB.get())
                self.clean_img=remove_Outliers(Images, self.std)
                if self.clean_img.shape[0]>1:
                    plot_spectrum(self.clean_img, Wave, int(len(Wave)/2), self.canvas_frame, FigSize=(3,2), Title="Spectrum after remove outliers", legend=1, path=self.path, name="Spectrum after remove outliers")
                    self.Done_button=ttk.Button(self.input_frame, text = "Done", command = accept, style='my.TButton')
                    self.Done_button.grid( row = 2, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
                    self.statusbar["text"]='Outliers removed'
            self.ok_button=ttk.Button(self.input_frame, text = "OK", command = outliers, style='my.TButton')
            self.ok_button.grid( row = 1, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
        def image_segmentation(self):
            self.destroy_frames()
            self.segmentation_button.config(state=tkinter.DISABLED)
            self.masked_img_green=np.zeros([1,1,0])
            self.statusbar["text"]='Please select segmentation method'
            root=tkinter.Tk()
            def routine(event):
                if str(tabControl.index(tabControl.select())) == "0":
                    speak('Please select color space')
                    self.statusbar["text"]='Please select color space'
                elif str(tabControl.index(tabControl.select())) == "1":
                    speak('Please select features')
                    self.statusbar["text"]='Please select features'
                else:
                    speak('Please press vegetation button')
                    self.statusbar["text"]='Please press vegetation button'
            root.title("Image segmentation")
            root.resizable(False, False) # this prevents from resizing the window
            root.wm_iconbitmap('DAAI logo.ico')
            root.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
            tab_style = ttk.Style(root)
            tab_style.theme_create('Cloud', settings={".": {"configure": {"background": 'whitesmoke', "font": 'red'}},
                "TNotebook": {"configure": {"background":'whitesmoke',"tabmargins": [0, 0, 0, 0], }},
                "TNotebook.Tab": {"configure": {"background": 'dark blue', "padding": [5, 2], "font":('Times New Roman', 15)},
                    "map": {"background": [("selected", '#aeb0ce')], "expand": [("selected", [1, 1, 1, 0])]}}})
            tab_style.theme_use('Cloud')
            tabControl=ttk.Notebook(root) ## creat one tab or more than one tab
            s = ttk.Style(tabControl)
            s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised') ## button font relief=[flat, groove, raised, ridge, solid, or sunken]
            tabControl.bind("<<NotebookTabChanged>>", routine)
            tab1=ttk.Frame(tabControl) ## creat tab
            tabControl.add(tab1, text='Threshold') ## add first tab
            tabControl.pack(expand=1, fill='both') ## show it
            tab2=ttk.Frame(tabControl) ## creat tab
            tabControl.add(tab2, text='K-means') ## add first tab
            tabControl.pack(expand=1, fill='both') ## show it
            button_frame=tkinter.LabelFrame(tab1, text='Select color space', bd=1, font=('Times New Roman', 15))
            button_frame.grid(row=0, column=0, columnspan=5, stick='we')
            self.f.write("speak('Please wait for '+name[:6]+' segmentation')\n\tstatusbar['text']=name+' segmenting....'\n\tblur = cv2.GaussianBlur(RGB_Image, (5, 5), 0.75)\n\t")
            ##### Threshold's tab#####################################
            self.Max_hue=255
            self.min_hue=0
            self.max_saturation=255
            self.min_saturation=0
            self.max_value=255
            self.min_value=0
            self.blur = cv2.GaussianBlur(self.RGB_Image, (5, 5), 0.75)
            self.hsv=np.zeros([1,1,0])
            self.YCrCb=np.zeros([1,1,0])
            self.LAB=np.zeros([1,1,0])
            self.Aimg=np.zeros([1,1,0])
            self.data=np.zeros([1,1])
            self.index_kmean=[]
            def imageshow_hsv():
                speak('choice threshold values by using scroll bar')
                self.f.write("Aimage=cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)\n\t")
                self.hsv = cv2.cvtColor(self.blur, cv2.COLOR_BGR2HSV)
                self.Aimg=self.hsv
                self.YCrCb=np.zeros([1,1,0])
                self.LAB=np.zeros([1,1,0])
                self.Max_hue=255
                self.min_hue=0
                self.max_saturation=255
                self.min_saturation=0
                self.max_value=255
                self.min_value=0
                imgshow(self.hsv)
            def imageshow_YCrCb():
                speak('choice threshold values by using scroll bar')
                self.f.write("Aimage=cv2.cvtColor(blur, cv2.COLOR_BGR2YCrCb)\n\t")
                self.YCrCb = cv2.cvtColor(self.blur, cv2.COLOR_BGR2YCrCb)
                self.Aimg=self.YCrCb
                self.Max_hue=255
                self.min_hue=0
                self.max_saturation=255
                self.min_saturation=0
                self.max_value=255
                self.min_value=0
                self.hsv=np.zeros([1,1,0])
                self.LAB=np.zeros([1,1,0])
                imgshow(self.YCrCb)
            def imageshow_lab():
                speak('choice threshold values by using scroll bar')
                self.f.write("Aimage=cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)\n\t")
                self.LAB = cv2.cvtColor(self.blur, cv2.COLOR_BGR2LAB)
                self.Aimg=self.LAB
                self.Max_hue=255
                self.min_hue=0
                self.max_saturation=255
                self.min_saturation=0
                self.max_value=255
                self.min_value=0
                self.hsv=np.zeros([1,1,0])
                self.YCrCb=np.zeros([1,1,0])
                imgshow(self.LAB)
            def get_scale_value_min_1(val):
                self.Max_hue=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_1(val):
                self.min_hue=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_min_2(val):
                self.max_saturation=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                fig.set_tight_layout(True)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_2(val):
                self.min_saturation=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_min_3(val):
                self.max_value=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def get_scale_value_max_3(val):
                self.min_value=int(val)
                self.img_binarry, self.masked_img_green, self.Binarry_image=image_segmentation(self.RGB_Image, self.Aimg, self.min_hue, self.Max_hue, self.min_saturation, self.max_saturation, self.min_value, self.max_value)
                rgb_frame=tkinter.LabelFrame(self.root_hsv, text='Segmented Image', bd=1, font=('Times New Roman', 15))
                rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def segment_done():
                try:
                    self.root_hsv.destroy()
                except:
                    pass
                try:
                    self.hue_root.destroy()
                except:
                    pass
                try:
                    self.saturat_root.destroy()
                except:
                    pass
                try:
                    self.value_root.destroy()
                except:
                    pass
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.masked_img_green)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=self.rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
            def imgshow(hsv):
                try:
                    self.root_hsv.destroy()
                except:
                    pass
                try:
                    self.hue_root.destroy()
                except:
                    pass
                try:
                    self.saturat_root.destroy()
                except:
                    pass
                try:
                    self.value_root.destroy()
                except:
                    pass
                self.root_hsv=tkinter.Tk()
                self.root_hsv.title("Image segmentation")
                self.root_hsv.wm_iconbitmap('DAAI logo.ico')
                self.root_hsv.configure()
                self.root_hsv.resizable(False, False)
                ttk.Button(self.root_hsv, text='Done', command=segment_done, style='my.TButton').grid(row=0, column=0) #try
                self.rgb_frame=tkinter.LabelFrame(tab1, text='Color image', bd=1, font=('Times New Roman', 15))
                self.rgb_frame.grid(row=1, column=0)
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(self.RGB_Image)
                ax.set_yticks([])
                ax.set_xticks([])
                canvas = FigureCanvasTkAgg(fig, master=self.rgb_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
                ## hue###################
                if self.LAB.shape[2]==3:
                    A='l'
                elif self.hsv.shape[2]==3:
                    A='h'
                elif self.YCrCb.shape[2]==3:
                    A='Y'
                self.hue_root=tkinter.Tk()
                self.hue_root.title(A)
                self.hue_root.wm_iconbitmap('DAAI logo.ico')
                self.hue_root.configure()
                self.hue_root.resizable(False, False)
                plot_contour(hsv[:,:,0], 0, 0, self.hue_root, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.hue_root, from_=np.amax(hsv[:,:,0]), to=np.amin(hsv[:,:,0]), length=100, command=get_scale_value_min_1, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,0]))
                w2 = tkinter.Scale(self.hue_root, from_=np.amax(hsv[:,:,0]), to=np.amin(hsv[:,:,0]), length=100, command=get_scale_value_max_1, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,0]))
                ## saturation####################
                if self.LAB.shape[2]==3:
                    B='a'
                elif self.hsv.shape[2]==3:
                    B='s'
                elif self.YCrCb.shape[2]==3:
                    B='Cb'
                self.saturat_root=tkinter.Tk()
                self.saturat_root.title(B)
                self.saturat_root.wm_iconbitmap('DAAI logo.ico')
                self.saturat_root.configure()
                self.saturat_root.resizable(False, False)
                plot_contour(hsv[:,:,1], 0, 0, self.saturat_root, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.saturat_root, from_=np.amax(hsv[:,:,1]), to=np.amin(hsv[:,:,1]), length=100, command=get_scale_value_min_2, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,1]))
                w2 = tkinter.Scale(self.saturat_root, from_=np.amax(hsv[:,:,1]), to=np.amin(hsv[:,:,1]), length=100, command=get_scale_value_max_2, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,1]))
                ## value############################
                if self.LAB.shape[2]==3:
                    c='b'
                elif self.hsv.shape[2]==3:
                    c='v'
                elif self.YCrCb.shape[2]==3:
                    c='Cr'
                self.value_root=tkinter.Tk()
                self.value_root.title(c)
                self.value_root.wm_iconbitmap('DAAI logo.ico')
                self.value_root.configure()
                self.value_root.resizable(False, False)
                plot_contour(hsv[:,:,2], 0, 0, self.value_root, [], [], [], (2,2), 'whitesmoke')
                w1 = tkinter.Scale(self.value_root, from_=np.amax(hsv[:,:,2]), to=np.amin(hsv[:,:,2]), length=100, command=get_scale_value_min_3, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                w1.set(np.amax(hsv[:,:,2]))
                w2 = tkinter.Scale(self.value_root, from_=np.amax(hsv[:,:,2]), to=np.amin(hsv[:,:,2]), length=100, command=get_scale_value_max_3, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                w2.set(np.amin(hsv[:,:,2]))
                self.saturat_root.mainloop()
                self.hue_root.mainloop()
                self.value_root.mainloop()
                self.root_hsv.mainloop()
            ttk.Button(button_frame, text='HSV', command=imageshow_hsv, style='my.TButton').grid(row=0, column=0, padx=2, pady=2)
            ttk.Button(button_frame, text='l*a*b*', command=imageshow_lab, style='my.TButton').grid(row=0, column=1, padx=2, pady=2)
            ttk.Button(button_frame, text='YCbCr', command=imageshow_YCrCb, style='my.TButton').grid(row=0, column=3, padx=2, pady=2)
            #### K_means tab#####################################################################################
            left_frame=tkinter.LabelFrame(tab2, text='Select clusters number', bd=1, font=('Times New Roman', 15))
            left_frame.grid(row=0, column=0, sticky='new')
            right_frame=tkinter.LabelFrame(tab2, text='Select features', bd=1, font=('Times New Roman', 15))
            right_frame.grid(row=0, column=1, sticky='new')
            Rright_frame=tkinter.LabelFrame(right_frame)
            Rright_frame.grid(row=0, column=1, sticky='ne')
            Lright_frame=tkinter.LabelFrame(right_frame)
            Lright_frame.grid(row=0, column=2, sticky='nw')
            def Get_color_list():
                self.index_color = colorlist.curselection()
                if len(self.index_color)>0:
                    blur = cv2.GaussianBlur(self.RGB_Image, (5, 5), 0.75)
                    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
                    HSV=hsv.reshape((self.RGB_Image.shape[0]*self.RGB_Image.shape[1]),3)
                    YCrCb = cv2.cvtColor(blur, cv2.COLOR_BGR2YCrCb)
                    YRB=YCrCb.reshape((self.RGB_Image.shape[0]*self.RGB_Image.shape[1]),3)
                    LAB = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)
                    lab=LAB.reshape((self.RGB_Image.shape[0]*self.RGB_Image.shape[1]),3)
                    RGB=blur.reshape((self.RGB_Image.shape[0]*self.RGB_Image.shape[1]),3)
                    Image=[]
                    for I in range(3):
                        Image.append(HSV[:,I])
                    for I in range(3):
                        Image.append(YRB[:,I])
                    for I in range(3):
                        Image.append(lab[:,I])
                    for I in range(3):
                        Image.append(RGB[:,I])
                    Image=np.asarray(Image)
                    self.data_color=Image[self.index_color, :].T
                    self.data=self.data_color
                    speak('please select number of cluster')
                    self.statusbar['text']= 'please select number of cluster'
                else:
                    speak('please select color features')
            def Get_band_list():
                self.index_band = bandlist.curselection()
                if len(self.index_band)>0:
                    self.data=[]
                    self.data_band=self.HSI_Img[:,:,self.index_band].reshape((self.HSI_Img.shape[0]*self.HSI_Img.shape[1]),len(self.index_band))
                    self.data=self.data_band
                    speak('please select number of cluster')
                    self.statusbar['text']= 'please select number of cluster'
                else:
                    speak('please select spectral features')
            def open_vegtation():
                data=self.My_Vegetation.reshape((self.My_Vegetation.shape[0]*self.My_Vegetation.shape[1]),1)
                self.data_VI=data
                self.data=self.data_VI
                speak('please select number of cluster')
                self.statusbar['text']= 'please select number of cluster'
            if self.My_Vegetation.shape[1]>1:
                ttk.Button(Lright_frame, text=self.Values[self.Vi], command=open_vegtation, style='my.TButton').grid(row=2, column=0, columnspan=2, padx=2, pady=2)
            colorlist = tkinter.Listbox(Rright_frame, width=12, height=6, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
            colorlist.grid(row=0, column=0)
            scrollbar = ttk.Scrollbar(Rright_frame, orient="vertical")
            scrollbar.config(command=colorlist.yview) ## connected scrollbar with listnodes
            scrollbar.grid(row=0, column=1, sticky='ns')
            colorlist.config(yscrollcommand=scrollbar.set) ## connected listnodes with scrollbar
            color_feature=['h', 's', 'v', 'l*', 'a*', 'b*', 'Y', "Cb", "Cr", "R", "G", "B"]
            for x in color_feature:
                colorlist.insert(tkinter.END, (x))
            ttk.Button(Rright_frame, text='Select color features', command=Get_color_list, style='my.TButton').grid(row=1, column=0, columnspan=2, padx=2, pady=2)
            bandlist = tkinter.Listbox(Lright_frame, width=12, height=6, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
            bandlist.grid(row=0, column=0)
            scrollbar2 = ttk.Scrollbar(Lright_frame, orient="vertical")
            scrollbar2.config(command=bandlist.yview) ## connected scrollbar with listnodes
            scrollbar2.grid(row=0, column=1, sticky='ns')
            bandlist.config(yscrollcommand=scrollbar2.set) ## connected listnodes with scrollbar
            Xx=0
            for x in self.wave_length:
                Xx+=1
                bandlist.insert(tkinter.END, ('Band',Xx))
            ttk.Button(Lright_frame, text='Select spectral features', command=Get_band_list, style='my.TButton').grid(row=1, column=0, columnspan=2, padx=2, pady=2)
            def on_select():
                speak('please wait for segmentation')
                self.num_clusters= cb.get()
                kmeans=KMeans(n_clusters=int(self.num_clusters), random_state=0).fit(self.data)
                self.center=kmeans.cluster_centers_
                label=kmeans.labels_.reshape(self.RGB_Image.shape[0],self.RGB_Image.shape[1])
                BOTTOM_frame=tkinter.LabelFrame(tab2, text='Results', bd=1, font=('Times New Roman', 15))
                BOTTOM_frame.grid(row=1, column=0, columnspan=2, sticky='new')
                plot_contour(label, -1, np.amax(label)+1, BOTTOM_frame, 'Segmentation result', self.path, 'kmeans', (2,2), 'whitesmoke')
                CB=tkinter.Listbox(left_frame, width=12, height=3, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                CB.grid(row=2, column=0, padx=2, pady=2)
                CB_scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
                CB_scrollbar.config(command=CB.yview) ## connected scrollbar with listnodes
                CB_scrollbar.grid(row=2, column=2, sticky='ns')
                CB.config(yscrollcommand=CB_scrollbar.set) ## connected listnodes with scrollbar
                for x in range(0, (int(self.num_clusters))):
                    CB.insert(tkinter.END, (x))
                def binarry():
                    self.index_kmean = CB.curselection()
                    bin_img=np.zeros(self.RGB_Image[:,:,1].shape)
                    if len(self.index_kmean)>0:
                        for i in range(len(self.index_kmean)):
                            Xx,Yy=np.where(label==self.index_kmean[i])
                            bin_img[Xx,Yy]=255
                            bin_img+=bin_img
                    XX,YY=np.where(bin_img>0)
                    image_segmented=np.zeros(self.RGB_Image.shape)
                    for i in range(3):
                        image_segmented[XX,YY,i]=self.RGB_Image[XX,YY,i]
                    self.masked_img_green=image_segmented.astype(np.uint8)
                    gray=cv2.cvtColor(self.masked_img_green, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray,(5,5),0.75)
                    ret,self.img_binarry = cv2.threshold(blur, 0, 255,cv2.THRESH_BINARY)
                    self.Binarry_image=np.zeros(self.RGB_Image.shape)
                    for i in range(3):
                        self.Binarry_image[:,:,i]=self.img_binarry
                    self.Binarry_image=self.Binarry_image.astype(np.uint8)
                    fig = matplotlib.figure.Figure(figsize=(2,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                    ax = fig.add_subplot(1,1,1)
                    ax.imshow(self.masked_img_green)
                    ax.set_yticks([])
                    ax.set_xticks([])
                    canvas = FigureCanvasTkAgg(fig, master=BOTTOM_frame)
                    canvas.get_tk_widget().grid(row=0, column=0)
                    canvas.draw()
                speak('Please select plant class or classes')
                self.statusbar['text']= 'Please select plant class/es'
                ttk.Button(left_frame, text='Select plant cluster', command=binarry, style='my.TButton').grid(row=3, column=0, columnspan=2)
            values=list(range(2, 21))
            all_comboboxes = []
            cb = ttk.Combobox(left_frame, values=values, font=('Times New Roman', 15))
            cb.set("2")
            cb.grid(row=0, column=0, padx=2, pady=2, sticky='n')       
            all_comboboxes.append(cb)
            b = ttk.Button(left_frame, text="Segment image", command=on_select, style='my.TButton')
            b.grid(row=1, column=0, padx=2, pady=2)
    #        #### vegetation tab######################################################################################################################
            if self.My_Vegetation.shape[1]>1:
                tab3=ttk.Frame(tabControl) ## creat tab
                tabControl.add(tab3, text='Vegetation_Index') ## add first tab
                tabControl.pack(expand=1, fill='both') ## show it
                Top_Frame=tkinter.LabelFrame(tab3)
                Top_Frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
                Left_Frame=tkinter.LabelFrame(tab3)
                Left_Frame.grid(row=1, column=0, sticky='nsew')
                Right_Frame=tkinter.LabelFrame(tab3)
                Right_Frame.grid(row=1, column=1, sticky='nsew')
                def open_vegtation():
                    speak('please choise threshold values by using scroll bar')
                    def get_scale_VI_max(val):
                        self.max_VI=float(val)
                        self.img_binarry=np.ones(self.My_Vegetation.shape)*255
                        self.img_binarry[np.where(self.My_Vegetation==0)]=0
                        self.img_binarry[np.where(self.My_Vegetation>self.max_VI)]=0
                        self.img_binarry[np.where(self.My_Vegetation<self.min_VI)]=0
                        Xx,Yy=np.where(self.img_binarry==255)
                        image_segmented=np.zeros(self.RGB_Image.shape)
                        for i in range(3):
                            image_segmented[Xx,Yy,i]=self.RGB_Image[Xx,Yy,i]
                        self.masked_img_green=image_segmented.astype(np.uint8)
                        self.Binarry_image=np.zeros(self.RGB_Image.shape)
                        for i in range(3):
                            self.Binarry_image[:,:,i]=self.img_binarry
                        self.Binarry_image=self.Binarry_image.astype(np.uint8)
                        fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                        ax2 = fig.add_subplot(1,1,1)
                        ax2.imshow(self.Binarry_image)
                        ax2.set_yticks([])
                        ax2.set_xticks([])
                        ax2.set_title('Segmented', fontsize=5)
                        canvas = FigureCanvasTkAgg(fig, master=Left_Frame)
                        canvas.get_tk_widget().grid(row = 0, column=0, rowspan=2, sticky='nswe')
                        canvas.draw()
                    def get_scale_VI_min(val):
                        self.min_VI=float(val)
                        self.img_binarry=np.ones(self.My_Vegetation.shape)*255
                        self.img_binarry[np.where(self.My_Vegetation==0)]=0
                        self.img_binarry[np.where(self.My_Vegetation<self.min_VI)]=0
                        self.img_binarry[np.where(self.My_Vegetation>self.max_VI)]=0
                        Xx,Yy=np.where(self.img_binarry==255)
                        image_segmented=np.zeros(self.RGB_Image.shape)
                        for i in range(3):
                            image_segmented[Xx,Yy,i]=self.RGB_Image[Xx,Yy,i]
                        self.masked_img_green=image_segmented.astype(np.uint8)
                        self.Binarry_image=np.zeros(self.RGB_Image.shape)
                        for i in range(3):
                            self.Binarry_image[:,:,i]=self.img_binarry
                        self.Binarry_image=self.Binarry_image.astype(np.uint8)
                        fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='whitesmoke')
                        ax2 = fig.add_subplot(1,1,1)
                        ax2.imshow(self.Binarry_image)
                        ax2.set_yticks([])
                        ax2.set_xticks([])
                        ax2.set_title('Segmented', fontsize=5)
                        canvas = FigureCanvasTkAgg(fig, master=Left_Frame)
                        canvas.get_tk_widget().grid(row = 0, column=0, rowspan=2, sticky='nswe')
                        canvas.draw()
                    plot_contour(self.My_Vegetation, 0, 0, Right_Frame, 'Segmentation result', [], [], (2,2), 'whitesmoke')
                    h,w=np.where(self.My_Vegetation!=0)
                    minem=np.min(self.My_Vegetation[h,w])
                    w1 = tkinter.Scale(Right_Frame, from_=np.amax(self.My_Vegetation), to=minem, length=100, resolution=0.1, command=get_scale_VI_max, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                    w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                    w1.set(np.amax(self.My_Vegetation))
                    w2 = tkinter.Scale(Right_Frame, from_=np.amax(self.My_Vegetation), to=minem, length=100,  resolution=0.1, command=get_scale_VI_min, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                    w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                    w2.set(minem)
                ttk.Button(Top_Frame, text=self.Values[self.Vi], command=open_vegtation, style='my.TButton').grid(row=0, column=0)
            def Save_RGB_image():
                try:
                    self.root_hsv.destroy()
                except:
                    pass
                try:
                    self.hue_root.destroy()
                except:
                    pass
                try:
                    self.saturat_root.destroy()
                except:
                    pass
                try:
                    self.value_root.destroy()
                except:
                    pass
                MY_PATH=self.path.split('/')
                self.name=MY_PATH[-1].split('.')[0]
                self.my_path='/'.join(MY_PATH[:-1])
                self.statusbar["text"]='Please wait for HSI segmentation...'
                self.My_name=self.name
                try:
                    self.Binarry_image.shape
                except:
                    self.Binarry_image=np.ones(self.RGB_Image.shape, np.uint8)*255
                    self.masked_img_green=np.ones(self.RGB_Image.shape, np.uint8)*255
                if self.Binarry_image.dtype!='uint8':
                    self.Binarry_image=self.Binarry_image.astype(np.uint8)
                else:
                    pass
                save_img(self.my_path+'/binarry', self.name, self.Binarry_image)
                save_img(self.my_path+'/segmented', self.name, self.masked_img_green)
                root.destroy()
                save_img(self.my_path+'/binarry', '1', self.Binarry_image)
                self.Binarry_image=cv2.imread(self.my_path+'/binarry/1.tiff', 1)
                self.f.write("if SR==1:\n\t\tsave_img(my_path+'/binarry', name, Binarry_image)\n\t\tsave_img(my_path+'/segmented', name, masked_img_green)\n\tsave_img(my_path+'/binarry', '1', Binarry_image)\n\t")
                if self.Binarry_image.shape[2]>0: ## filteration
                    speak('please wait for hyper spectral image segmentation!')
                    self.Image_HSI,  self.masked_img_green=hsi_segment(self.Binarry_image[:,:,0], self.hypercube,  self.RGB_Image)
                    self.hypercube=self.Image_HSI
                    self.f.write("img_binarries=cv2.imread(my_path+'/binarry/1.tiff', 1)\n\thypercube, masked_img_green=hsi_segment(img_binarries[:,:,1], hypercube, RGB_Image)\n\t")
                    save_img(self.my_path+'/segmented', self.name, self.masked_img_green)
                    root2=tkinter.Tk()
                    Hh=int(len(self.wave_length)/2)
                    self.Image_HSI_show=self.Image_HSI[:,:,Hh]
                    root2.title("Image filter")
                    root2.wm_iconbitmap('DAAI logo.ico')
                    root2.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
                    s = ttk.Style(window)
                    s.configure('new.TFrame', background='#7AC5CD')
                    self.hsi_frame=ttk.LabelFrame(root2, style='new.TFrame')
                    self.hsi_frame.grid(row=0, column=1, stick='nswe')
                    self.list_frame=ttk.LabelFrame(root2, style='new.TFrame')
                    self.list_frame.grid(row=0, column=2, stick='nswe')
                    speak('To remove undesirable pixels please select appropriate band')
                    self.min_reflect=0
                    def get_scale_value_max_hsi(val):
                        self.Max_reflect=float(val)
                        s = ttk.Style(window)
                        s.configure('new.TFrame', background='#7AC5CD')
                        self.hsi_Frame=ttk.LabelFrame(root2, style='new.TFrame')
                        self.hsi_Frame.grid(row=0, column=0, stick='nswe')
                        self.Image_HSI_show=self.Image_HSI[:,:,self.Index]
                        title='HSI at Band ' + str(self.seltext[1])+' after delete bad pixels'
                        plot_contour(self.Image_HSI_show, self.min_reflect, self.Max_reflect, self.hsi_Frame, title, self.path, str(self.seltext[1]), (2,2), 'lightyellow')
                    def get_scale_value_min_hsi(val):
                        self.min_reflect=float(val)
                        self.Image_HSI_show=self.Image_HSI[:,:,self.Index]
                        self.hsi_Frame=ttk.LabelFrame(root2, style='new.TFrame')
                        self.hsi_Frame.grid(row=0, column=0, stick='nswe')
                        title='HSI at Band ' + str(self.seltext[1])+' after delete bad pixels'
                        try:
                            plot_contour(self.Image_HSI_show, self.min_reflect, self.Max_reflect, self.hsi_Frame, title, self.path, str(self.seltext[1]), (2,2), 'lightyellow')
                        except:
                            Max_reflect=np.max(self.Image_HSI[:,:,self.Index])
                            plot_contour(self.Image_HSI_show, self.min_reflect, Max_reflect, self.hsi_Frame, title, self.path, str(self.seltext[1]), (2,2), 'lightyellow')
                    def get_list(event):
                        speak('select minimum and maximum reflection values by scorol bar')
                        self.Index = self.listNodes.curselection()[0]
                        self.seltext = self.listNodes.get(self.Index)
                        self.Image_HSI_show=self.Image_HSI[:,:,self.Index]
                        w1 = tkinter.Scale(self.hsi_frame, from_=np.amax(self.Image_HSI_show), to=np.amin(self.Image_HSI_show), digits = 3, resolution = 0.001, length=100, command=get_scale_value_max_hsi, highlightthickness=0, borderwidth=0, troughcolor='gray', sliderlength=20)
                        w1.grid(row=0, column=1, stick='nsw', pady = (0,0))
                        w1.set(np.amax(self.Image_HSI_show))
                        w2 = tkinter.Scale(self.hsi_frame, from_=np.amax(self.Image_HSI_show), to=np.amin(self.Image_HSI_show), digits = 3, resolution = 0.001, length=100, command=get_scale_value_min_hsi, highlightthickness=0,borderwidth=0, troughcolor='gray', sliderlength=20)
                        w2.grid(row=1, column=1, stick='nse', pady = (0,0))
                        w2.set(min(self.Image_HSI_show[np.nonzero(self.Image_HSI_show)]))
                        title='Reflection heat map at Band ' + str(self.seltext[1])
                        plot_contour(self.Image_HSI_show, 0, 0, self.hsi_frame, title, self.path, str(self.seltext[1]), (2,2), 'lightyellow')
                    style = ttk.Style(window)
                    style.configure("BW.TLabel", foreground="black", background="lightyellow")
                    ttk.Label(self.list_frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15)).grid( row = 0, column = 0, columnspan=3, padx=2, pady=2, sticky='s')
                    self.listNodes = tkinter.Listbox(self.list_frame, width=10, height=18, font=('Times New Roman', 15))
                    self.listNodes.grid(row=1, column=0, columnspan=2, sticky='ns')
                    scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical")
                    scrollbar.config(command=self.listNodes.yview) ## connected scrollbar with listnodes
                    scrollbar.grid(row=1, column=2, sticky='ns')
                    self.listNodes.config(yscrollcommand=scrollbar.set) ## connected listnodes with scrollbar
                    self.listNodes.bind('<Double-1>', get_list)
                    Xx=0
                    for x in self.wave_length:
                        Xx+=1
                        self.listNodes.insert(tkinter.END, ('Band',Xx))
                    def Save_hsi_image():
                        self.K=1
                        self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
                        self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
                        speak('Please wait')
                        try:
                            self.Index=self.Index
                        except:
                            self.Index=int(self.Image_HSI.shape[-1]/2)
                        try:
                            self.Max_reflect=self.Max_reflect
                        except:
                            self.Max_reflect=np.max(self.Image_HSI[:,:,self.Index])
                        if RSC.get()==1:
                            self.remove_specular=1
                        else:
                            self.remove_specular=0
                        if MFB.get()==1:
                           self.median_filter=1
                        else:
                            self.median_filter=0
                        self.image_filtered, self.masked_img_green, self.Binarry_image=hsi_filter(self.hypercube, self.min_reflect, self.Max_reflect, self.Index, self.masked_img_green, self.remove_specular, self.median_filter)
                        self.f.write("min_R, max_R, Index="+str(self.min_reflect)+','+str(self.Max_reflect)+','+str(self.Index)+"\n\thypercube, masked_img_green, Binarry_image=hsi_filter(hypercube,  min_R, max_R, Index, masked_img_green, "+str(self.remove_specular)+','+str(self.median_filter)+")\n\tmy_wave=wave_length\n\tnames=''\n\t")
                        cv2.imwrite(self.my_path+'/1.tiff',  self.masked_img_green)
                        save_img(self.my_path+'/binarry', self.name, self.Binarry_image)
                        save_img(self.my_path+'/segmented', self.name, self.masked_img_green)
                        self.hypercube=self.image_filtered
                        self.f.write("if SR==1:\n\t\tsave_img(my_path+'/binarry', name, Binarry_image)\n\t\tsave_img(my_path+'/segmented', name, masked_img_green)\n\tsave_img(my_path+'/binarry', '1', Binarry_image)\n\tsave_img(my_path, '1', masked_img_green)\n\t")
                        root2.destroy()
                        self.feature_button.config(state=tkinter.ACTIVE)
                        self.allimage_button.config(state=tkinter.ACTIVE)
                        self.model_button2.config(state=tkinter.ACTIVE)
                        self.msc_button.config(state=tkinter.ACTIVE)
                        self.SNV_button.config(state=tkinter.ACTIVE)
                        self.reout_button.config(state=tkinter.ACTIVE)
                        self.sgd_button.config(state=tkinter.ACTIVE)
                        self.sgs_button.config(state=tkinter.ACTIVE)
                        self.binning_button.config(state=tkinter.ACTIVE)
                        self.spatial_binning_button.config(state=tkinter.ACTIVE)
                        self.crop_button.config(state=tkinter.ACTIVE)
                        self.spatial__crop_button.config(state=tkinter.ACTIVE)
                        self.select_button.config(state=tkinter.ACTIVE)
                        self.resize_button.config(state=tkinter.ACTIVE)
                        self.segmentation_button.config(state=tkinter.ACTIVE)
                        def GET_LIST(event):
                            self.INDEX = self.listNodes2.curselection()[0]
                            self.seltext = self.listNodes2.get(self.INDEX)
                            title='Reflection heat map at Band ' + str(self.seltext[1])
                            plot_contour(self.hypercube[:,:,self.INDEX], 0, 0, self.canvas_frame, title, self.path, str(self.seltext[1]), (2,2), 'lightyellow')
                        self.style = ttk.Style(window)
                        self.style.configure("BW.TLabel", foreground="black", background="lightyellow", font=('Times New Roman', 20))
                        select=ttk.Label(self.List_Frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15))
                        select.grid( row = 0, column = 0, padx=2, pady=2, sticky='n')
                        self.listNodes2 = tkinter.Listbox(self.List_Frame, width=20, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                        self.listNodes2.grid(row=1, column=0, sticky='ns')
                        scrollbar = ttk.Scrollbar(self.List_Frame, orient="vertical")
                        scrollbar.config(command=self.listNodes2.yview) ## connected scrollbar with listnodes
                        scrollbar.grid(row=1, column=1, sticky='ns')
                        self.listNodes2.config(yscrollcommand=scrollbar.set) ## connected listnodes with scrollbar
                        self.listNodes2.bind('<Double-1>', GET_LIST)
                        self.oks.destroy()
                        self.my_ListNodes=self.listNodes2
                        Xx=0
                        for x in self.wave_length:
                            Xx+=1
                            self.listNodes2.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                        self.statusbar["text"]='The HSI has been segmented'
                        self.f.write("speak(name[:6]+' segmented')\n\tstatusbar['text']=name+' segmented'\n\tspeak('Please wait for '+name[:6]+' preprocessing')\n\tstatusbar['text']=name+' preprocessing....'\n\t")
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_filtered, self.wave_length, self.My_name+'_Full spectral cube', 1), width=21, style='my.TButton').grid( row = 0, column = 0, sticky='ew')
                        ttk.Button(self.results_frame, text = "Plot spectrum", command=lambda:plot_spectrum(self.image_filtered, self.wave_length, self.Index, self.canvas_frame, FigSize=(3,2), Title="Spectrum", legend=1, path=self.path, name='Full spectral'), width=20, style='my.TButton').grid( row = 0, column = 1,  sticky='ew')
                        ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.image_filtered, self.wave_length, 'Full spectral', self.Index), width=20, style='my.TButton').grid( row = 1, column = 0, sticky='ew')
                        ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.image_filtered,  self.path, 'Full spectral', self.canvas_frame), width=20, style='my.TButton').grid( row = 1, column = 1,  sticky='ew')
                        Hh=self.Index
                        title='Reflection heat map at band ' + str(self.Index)
                        plot_contour(self.image_filtered[:,:,Hh], 0, 0, self.canvas_frame, title, self.path, str(self.Index), (2,2), 'lightyellow')
                    RSC=tkinter.IntVar(root2)
                    tkinter.Checkbutton(self.list_frame, text="Remove specular", variable=RSC).grid(row=4, column=0, columnspan=3)
                    MFB=tkinter.IntVar(root2)
                    tkinter.Checkbutton(self.list_frame, text="Apply median_fil", variable=MFB).grid(row=5, column=0, columnspan=3)
                    ttk.Button(self.list_frame, text='Apply and exit', command=Save_hsi_image, style='my.TButton').grid(row=6, column=0, columnspan=3)
                    title='Reflection heat map at band ' + str(Hh)
                    plot_contour(self.Image_HSI[:,:,Hh], 0, 0, self.hsi_frame, title, self.path, str(Hh), (2,2), 'lightyellow')
                    root2.protocol('WM_DELETE_WINDOW', donothing)
                    root2.mainloop()
            def donothing():
                speak('please click save and exit button')
                self.statusbar["text"]='ROI is ready for save or analysis'
                pass
            root.protocol('WM_DELETE_WINDOW', donothing)
            def color_threshold():
                try:
                    self.Binarry_image.shape
                    self.f.write("min_H, max_H, min_S, max_S, min_V, max_V="+ str(self.min_hue)+','+ str( self.Max_hue)+','+ str( self.min_saturation)+','+ str( self.max_saturation)+','+ str( self.min_value)+','+ str( self.max_value)+'\n\t')
                    self.f.write("img_binarry, masked_img_green, Binarry_image=image_segmentation(RGB_Image, Aimage, min_H, max_H, min_S, max_S, min_V, max_V)\n\tmasked_img_green=masked_img_green.astype(np.uint8)\n\tBinarry_image=Binarry_image.astype(np.uint8)\n\t")
                except:
                    self.f.write("Binarry_image=np.ones(RGB_Image.shape, np.uint8)*255\n\t")
                    self.f.write("masked_img_green=np.asarray(RGB_Image.shape, np.uint8)\n\t")
                    pass
                Save_RGB_image()
            def VI_threshold():
                try:
                    self.Binarry_image.shape
                    self.f.write("My_Vegetation=np.asarray(vegetation_index(HSI_Img,["+convert( self.IVS, 0)+'],'+str( self.VI)+"))\n\timg_binarry=np.ones(My_Vegetation.shape)*255\n\timg_binarry[np.where(My_Vegetation==0)]=0\n\timg_binarry[np.where(My_Vegetation>"+str(self.max_VI)+")]=0\n\timg_binarry[np.where(My_Vegetation<"+str(self.min_VI)+")]=0\n\tXx,Yy=np.where(img_binarry==255)\n\timage_segmented=np.zeros(RGB_Image.shape)\n\t")
                    self.f.write("for i in range(3):\n\t\timage_segmented[Xx,Yy,i]=RGB_Image[Xx,Yy,i]\n\tmasked_img_green=image_segmented.astype(np.uint8)\n\tBinarry_image=np.zeros(RGB_Image.shape)\n\tfor i in range(3):\n\t\tBinarry_image[:,:,i]=img_binarry\n\tBinarry_image=Binarry_image.astype(np.uint8)\n\t")
                except:
                    self.f.write("Binarry_image=np.ones(RGB_Image.shape, np.uint8)*255\n\t")
                    self.f.write("masked_img_green=np.asarray(RGB_Image.shape, np.uint8)\n\t")
                    pass
                Save_RGB_image()
            def kmeans_segment():
                try:
                    self.Binarry_image.shape
                    if self.data_color.shape[0]>1 and (self.data==self.data_color).all():
                        HSV="HSV = (cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)).reshape((RGB_Image.shape[0]*RGB_Image.shape[1]),3)\n\t"
                        YCrCb ="YCrCb = (cv2.cvtColor(blur, cv2.COLOR_BGR2YCrCb)).reshape((RGB_Image.shape[0]*RGB_Image.shape[1]),3)\n\t"
                        LAB ="LAB = (cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)).reshape((RGB_Image.shape[0]*RGB_Image.shape[1]),3)\n\t"
                        RGB="RGB=blur.reshape((RGB_Image.shape[0]*RGB_Image.shape[1]),3)\n\t"
                        img="Image=[]\n\t"
                        loop="for I in range(3):\n\t\tImage.append(HSV[:,I])\n\tfor I in range(3):\n\t\tImage.append(YCrCb[:,I])\n\tfor I in range(3):\n\t\tImage.append(LAB[:,I])\n\tfor I in range(3):\n\t\tImage.append(RGB[:,I])\n\t"
                        Image="Image=np.asarray(Image)\n\t"
                        index="Index="+str(self.index_color)+'\n\t'
                        data="data=Image[Index, :].T\n\t"
                        for i in (HSV, YCrCb, LAB, RGB, img, loop, Image, index, data):
                            self.f.write(i)
                    if self.data_band.shape[0]>1 and (self.data==self.data_band).all():
                        self.f.write("Index=["+convert(self.index_band, 0)+"]\n\tdata=HSI_Img[:,:,Index].reshape((HSI_Img.shape[0]*HSI_Img.shape[1]),len(Index))\n\t")
                    if self.data_VI.shape[0]>1 and (self.data==self.data_VI).all():
                        self.f.write("My_Vegetation=vegetation_index(hypercube,["+ convert(self.IVS, 0)+"]," +str(self.VI)+")\n\tMy_Vegetation=np.asarray(My_Vegetation)\n\tdata=My_Vegetation.reshape((My_Vegetation.shape[0]*My_Vegetation.shape[1]),1)\n\t")
                    center=[]
                    for n in self.center:
                        for m in n:
                            center.append(m)
                    kmeans_center="kmeans_center=np.asarray("+str(center)+").reshape("+str(self.num_clusters)+",data.shape[1])\n\t"
                    self.f.write(kmeans_center)
                    kmeans="num_clusters="+str(self.num_clusters)+"\n\tkmeans=KMeans(n_clusters=int(num_clusters), random_state=0, init=kmeans_center, n_init=1).fit(data)\n\tlabel=kmeans.labels_.reshape(RGB_Image.shape[0],RGB_Image.shape[1])\n\tbin_img=np.zeros(RGB_Image[:,:,1].shape)\n\t"
                    self.f.write(kmeans)
                    kmean_index="kmean_index="+str(self.index_kmean)+"\n\tfor i in range(len(kmean_index)):\n\t\tXx,Yy=np.where(label==kmean_index[i])\n\t\tbin_img[Xx,Yy]=255\n\t\tbin_img+=bin_img\n\t"
                    self.f.write(kmean_index)
                    binarry="XX,YY=np.where(bin_img>0)\n\timage_segmented=np.zeros(RGB_Image.shape)\n\tfor i in range(3):\n\t\timage_segmented[XX,YY,i]=RGB_Image[XX,YY,i]\n\tmasked_img_green=image_segmented.astype(np.uint8)\n\tgray=cv2.cvtColor(masked_img_green, cv2.COLOR_BGR2GRAY)\n\tblur = cv2.GaussianBlur(gray,(5,5),0.75)\n\tret,img_binarry = cv2.threshold(blur, 0, 255,cv2.THRESH_BINARY)\n\tBinarry_image=np.zeros(RGB_Image.shape)\n\tfor i in range(3):\n\t\tBinarry_image[:,:,i]=img_binarry\n\tBinarry_image=Binarry_image.astype(np.uint8)\n\t"
                    self.f.write(binarry)
                except:
                    self.f.write("Binarry_image=np.ones(RGB_Image.shape, np.uint8)*255\n\t")
                    self.f.write("masked_img_green=np.asarray(RGB_Image.shape, np.uint8)\n\t")
                    pass
                Save_RGB_image()
            ttk.Button(button_frame, text='Save and exit', command=color_threshold, style='my.TButton').grid(row=0, column=4) #%% color
            ttk.Button(left_frame, text='Save and exit', command=kmeans_segment, style='my.TButton').grid(row=4, column=0) #%% kmeans
            try:
                ttk.Button(Top_Frame, text='Save and exit', command=VI_threshold, style='my.TButton').grid(row=0, column=1) #%% VI threshold
            except:
                pass
            root.mainloop()
        def Data_augmentation(self):
            self.destroy_frames()
            speak('please wait for image augmentation')
            self.statusbar["text"]='Image augmentation......'
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            self.image_aug=Data_aug(Images)
            self.wave_aug=Wave
            if self.image_aug.shape[0]>1:
                speak('Image augmentation done')
                self.statusbar["text"]='Image augmentation done'
                speak('Please wait for augmented images saving')
                self.statusbar["text"]='Image augmentation saving....'
                save_mat_file(self.path, self.image_aug, self.wave_aug, 'DA', 1)
                self.statusbar["text"]='Image augmentation saved'
        def saptial_resize(self):
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            speak('For spatial resize please select x and y size')
            self.statusbar["text"]='please select x and y size'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            def done():
                self.x_size= int(x_size.get())
                self.y_size= int(y_size.get())
                if self.x_size>1 and self.y_size>1:
                    self.image_resize, binarry_img, color_img=hsi_resize(Images, self.x_size, self.y_size, self.masked_img_green)
                    self.f.write("if Spz==1:\n\t\thypercube, binarry_img, color_img=hsi_resize(hypercube,"+str(self.x_size)+','+str( self.y_size)+','+" masked_img_green)\n\t\tnames+='_spat_resize'\n\t")
                    try:
                        binarry_img.shape
                        save_img(self.my_path+'/binarry', self.name, binarry_img)
                        save_img(self.my_path+'/segmented', self.name, color_img)
                    except:
                        pass
                    self.image_resize=np.asarray(self.image_resize) 
                    self.my_wave=Wave
                    self.hypercube=self.image_resize
                    if len(self.image_resize.shape)==3:
                        self.wave_resize=Wave
                        self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                        self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                        self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                        self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                        A=[]
                        for i in range(3):
                            A.append(self.image_resize.shape[i])
                        self.input_text1.set(convert(A, 0))
                        self.My_name+='_resized cube'
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_resize, self.wave_resize, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                        ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.image_resize,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 2, column = 0, columnspan=2, sticky='ew')
                        Hh=int(len(self.wave_resize)/2)
                        title='Reflection heat map at Band ' + str(Hh)
                        plot_contour(self.image_resize[:,:,Hh], 0, 0, self.canvas_frame, title,self.path,str(Hh), (2,2), 'lightyellow')
                    elif len(self.image_resize.shape)==4:
                        A=[]
                        self.wave_resize=Wave
                        self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                        self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                        self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                        self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                        for i in range(3):
                            A.append(self.image_resize[0].shape[i])
                        self.input_text1.set(convert(A, 0))
                        self.My_name+='_resized cube'
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_resize, self.wave_resize, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                        self.statusbar["text"]='The image has been resized'
            ttk.Button(self.input_frame, text = "OK", command = done, style='my.TButton').grid( row = 2, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
            X_value=[]
            for x in range(50, 1000, 50):
                X_value.append(int(x))
            x_size = ttk.Combobox(self.input_frame, values=X_value, width=5, font=('Times New Roman', 15))
            x_size.set("50")
            x_size.grid( row = 0, column = 1, sticky='ew')
            ttk.Label(self.input_frame, text='X size', style="BW.TLabel", font=('Times New Roman', 10)).grid( row = 0, column = 0,  sticky='e')
            Y_value=[]
            for y in range(50, 1000, 50):
                Y_value.append(int(y))
            y_size = ttk.Combobox(self.input_frame, values=Y_value, width=5, font=('Times New Roman', 15))
            y_size.set("50")
            y_size.grid( row = 1, column = 1, sticky='ew')
            ttk.Label(self.input_frame, text='Y size', style="BW.TLabel", font=('Times New Roman', 10)).grid( row = 1, column = 0,  sticky='e')
        def spat_binning(self):
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            speak('For spatial binning please select binning value')
            self.statusbar["text"]='Please select binning value'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            def done():
                self.spat_Bin= int(CB.get())
                if self.spat_Bin>1:
                    self.image_Bin_spat, binarry_img, color_img=hsi_spat_bin(Images ,self.spat_Bin, self.masked_img_green)
                    self.f.write("if Spb==1:\n\t\thypercube, binarry_img, color_img=hsi_spat_bin(hypercube ,"+str(self.spat_Bin)+','+"masked_img_green)\n\t\tnames+='_spat_bin'\n\t")
                    try:
                        binarry_img.shape
                        save_img(self.my_path+'/binarry', self.name, binarry_img)
                        save_img(self.my_path+'/segmented', self.name, color_img)
                    except:
                        pass
                    self.wave_spat_bin=Wave
                    self.hypercube=self.image_Bin_spat
                    self.my_wave=Wave
                    self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                    self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                    self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                    self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                    if len(self.image_Bin_spat.shape)==3:
                        A=[]
                        for i in range(3):
                            A.append(self.image_Bin_spat.shape[i])
                        self.input_text1.set(convert(A, 0))
                        Hh=int(len(self.wave_spat_bin)/2)
                        title='Reflection heat map at Band ' + str(Hh)
                        self.My_name+='_Spat_bin'
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_Bin_spat, self.wave_spat_bin, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, sticky='ew')
                        plot_contour(self.image_Bin_spat[:,:,Hh], 0, 0, self.canvas_frame, title, self.path, str(Hh), (2,2), 'lightyellow')
                    elif len(self.image_Bin_spat.shape)==1 or len(self.image_Bin_spat.shape)==4:
                        A=[]
                        self.wave_spat_bin=Wave
                        for i in range(3):
                            A.append(self.image_Bin_spat[0].shape[i])
                        self.input_text1.set(convert(A, 0))
                        self.My_name+='_Spat_bin'
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image_Bin_spat, self.wave_spat_bin, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, sticky='ew')
                    self.statusbar["text"]='The image has been binned'
            ttk.Button(self.input_frame, text = "OK", command = done, style='my.TButton').grid( row = 1, column = 0, columnspan=2, padx=2, pady=2, sticky='s')
            CB = ttk.Combobox(self.input_frame, values=('2', '4', '8', '16', '32', '64'), width=5, font=('Times New Roman', 15))
            CB.set("2")
            CB.grid( row = 0, column = 1, sticky='ew')
            ttk.Label(self.input_frame, text='Bin_value', style="BW.TLabel", font=('Times New Roman', 15)).grid( row = 0, column = 0,  sticky='e')        
        def hsi_binning(self):
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            try:
               self.listNodes3.destroy()
               self.scrollbar_bin.destroy()
            except:
                pass
            try:
                self.Done_button.destroy()
            except:
                pass
            speak('For spectral binning please select start and end band from list and binning value:') ##402, 997
            self.statusbar["text"]='Please select start and end band from list and binning value'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
                    self.statusbar["text"]='Cant spectral binning from multi-images, please select spectral binning before spatial crop'
            def delete(listbox):
                speak('Please wait')
                Ss=[]
                selection = listbox.curselection()
                for s in selection:
                    seltext = listbox.get(s)
                    Ss.append(seltext[-2])
                self.H=wave2index(Wave, Ss)
                if len(self.H)>0:
                    self.wavebin=Wave[self.H[0]:(self.H[-1]+1)]
                    image2bin=Images[:,:,self.H[0]:(self.H[-1]+1)]
                    self.Bin= int(CB.get())
                    if self.Bin>1:
                        self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                        self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                        self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                        self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                        self.Image_bin, self.WAVE_Length_binning=hsi_binnings(self.wavebin, image2bin, self.Bin)
                        def GET_LIST(event):
                            self.INDEX2 = self.listNodes3.curselection()[0]
                            self.seltext2 = self.listNodes3.get(self.INDEX2)
                            title='Reflection heat map at Band ' + str(self.seltext2[1])
                            plot_contour(self.Image_bin[:,:,self.INDEX2], 0, 0, self.canvas_frame, title,self.path,str(self.seltext2[1]), (2,2), 'lightyellow')
                        select=ttk.Label(self.List_Frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15))
                        select.grid( row = 0, column = 0, padx=2, pady=2, sticky='n')
                        self.listNodes3 = tkinter.Listbox(self.List_Frame, width=20, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                        self.listNodes3.grid(row=1, column=0, sticky='ns')
                        self.scrollbar_bin = ttk.Scrollbar(self.List_Frame, orient="vertical")
                        self.scrollbar_bin.config(command=self.listNodes3.yview) ## connected scrollbar with listnodes
                        self.scrollbar_bin.grid(row=1, column=1, sticky='ns')
                        self.listNodes3.config(yscrollcommand=self.scrollbar_bin.set) ## connected listnodes with scrollbar
                        self.listNodes3.bind('<Double-1>', GET_LIST)
                        Xx=0
                        for x in self.WAVE_Length_binning:
                            Xx+=1
                            self.listNodes3.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                        A=[]
                        for i in range(3):
                            A.append(self.Image_bin.shape[i])
                        self.input_text1.set(convert(A, 0))
                        Hh=int(len(self.WAVE_Length_binning)/2)
                        title='Reflection heat map at Band ' + str(Hh)
                        plot_contour(self.Image_bin[:,:,Hh], 0, 0, self.canvas_frame, title, self.path,str(Hh), (2,2), 'lightyellow')
                        self.statusbar["text"]='The image has been binned'
                        def done_bin():
                            self.hypercube=self.Image_bin
                            self.f.write("if BS==1:\n\t\thypercube=hypercube[:,:,"+str(self.H[0])+':'+str(self.H[-1]+1)+"]\n\t\tmy_wave=my_wave["+str(self.H[0])+':'+str(self.H[-1]+1)+"]\n\t\thypercube, my_wave=hsi_binnings(my_wave, hypercube,"+str(self.Bin)+")\n\t\tnames+='_Spect_bin'\n\t")
                            self.my_ListNodes=self.listNodes3
                            self.my_wave=self.WAVE_Length_binning
                            self.My_name+='_Spect_bin'
                            ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.Image_bin, self.WAVE_Length_binning, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0,  sticky='ew')
                            ttk.Button(self.results_frame, text = "Plot spectrum", command=lambda:plot_spectrum(self.Image_bin, self.WAVE_Length_binning, int(len(self.WAVE_Length_binning)/2), self.canvas_frame, FigSize=(3,2), Title="Spectrum after bin", legend=1, path=self.path, name='Binning cube'), width=20, style='my.TButton').grid( row = 1, column = 1, sticky='ew')
                            ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.Image_bin,self.WAVE_Length_binning, self.My_name, int(len(self.WAVE_Length_binning)/2)), width=20, style='my.TButton').grid( row = 2, column = 0, sticky='ew')
                            ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.Image_bin,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 2, column = 1,  sticky='ew')
                            self.Done_button.destroy()
                            self.input_frame.destroy()
                            self.select_bin_button.destroy()
                        self.Done_button=ttk.Button(self.List_Frame, text = "Done", command = done_bin, style='my.TButton')
                        self.Done_button.grid( row = 3, column = 0, padx=2, pady=2, sticky='s')
            self.select_bin_button=ttk.Button(self.List_Frame, text = "Select", command = lambda: delete(Listbox), style='my.TButton')
            self.select_bin_button.grid( row = 2, column = 0, padx=2, pady=2, sticky='s')
            CB = ttk.Combobox(self.input_frame, values=('2', '4', '8', '16', '32', '64'), width=5, font=('Times New Roman', 15))
            CB.set("2")
            CB.grid( row = 0, column = 1, sticky='ew')
            ttk.Label(self.input_frame, text='Bin_value', style="BW.TLabel", font=('Times New Roman', 15)).grid( row = 0, column = 0,  sticky='e')
        def hsi_crop(self):
            self.destroy_frames()
            try:
               self.listNodes4.destroy()
               self.scrollbar_crop.destroy()
            except:
                pass
            try:
                self.Done_button.destroy()
            except:
                pass
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            speak('For spectral crop please select bands you want to delete from list')
            self.statusbar["text"]='For spectral crop please select bands you want to delete from list'
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
                    self.statusbar["text"]='Cant spectral crop from multi-images, please select spectral crop before spatial crop'
            def delete(listbox, images, wave):
                all_index=np.asarray(range(len(wave))) #### get the index for all wavelength
                selection = listbox.curselection()
                if len(selection)>0:
                    SS=np.asarray(selection)
                    self.wavecrop=np.delete(wave, SS)
                    self.all_Index=np.delete(all_index, SS)
                    self.image2crop=images[:,:,self.all_Index]
                    if self.image2crop.shape[2]>1:
                        self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                        self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                        self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                        self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                        A=[]
                        for i in range(3):
                            A.append(self.image2crop.shape[i])
                        self.input_text1.set(convert(A, 0))
                        self.listNodes4 = tkinter.Listbox(self.List_Frame, width=20, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                        self.listNodes4.grid(row=1, column=0, sticky='ns')
                        Xx=0
                        for x in self.wavecrop:
                            Xx+=1
                            self.listNodes4.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                        self.scrollbar_crop = ttk.Scrollbar(self.List_Frame, orient="vertical")
                        self.scrollbar_crop.config(command=self.listNodes4.yview) ## connected scrollbar with listnodes
                        self.scrollbar_crop.grid(row=1, column=1, sticky='ns')
                        self.listNodes4.config(yscrollcommand=self.scrollbar_crop.set) ## connected listnodes with scrollbar
                        SNR=np.delete(self.SNR, SS)
                        self.delete_bands.destroy()
                        fig= matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                        ax = fig.add_subplot(1,1,1)
                        ax.plot(self.wavecrop, SNR, 'b', linewidth=0.5)
                        ax.set_xticks(np.arange(int(min(Wave)), int(max(Wave)+1), 50))
                        ax.set_title('Signal/Noise', fontsize=5)
                        ax.set_xlabel("Wavelength (nm)", fontproperties=font)
                        ax.set_ylabel('SNR', fontproperties=font)
                        ax.tick_params(axis='x', labelsize=5)
                        ax.tick_params(axis='y', labelsize=5)
                        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                        canvas.get_tk_widget().grid(row = 0, column=0)
                        canvas.draw()
                        def done_bin():
                            self.hypercube=self.image2crop
                            self.my_ListNodes=self.listNodes4
                            self.my_wave=self.wavecrop
                            self.My_name+='_Spect_crop'
                            self.f.write("if CS==1:\n\t\thypercube=hypercube[:,:,["+convert(self.all_Index, 0)+"]]\n\t\tmy_wave=my_wave[["+convert(self.all_Index, 0)+"]]\n\t\tnames+='_Spect_crop'\n\t")
                            ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.image2crop, self.wavecrop, self.My_name,1), width=21, style='my.TButton').grid( row = 1, column = 0, sticky='ew')
                            ttk.Button(self.results_frame, text = "Plot spectrum", command=lambda:plot_spectrum(self.image2crop, self.wavecrop, int(len(self.wavecrop)/2), self.canvas_frame, FigSize=(3,2), Title="Spectrum after crop", legend=1, path=self.path, name="croped_image"), width=20, style='my.TButton').grid( row = 1, column = 1, sticky='ew')
                            ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.image2crop,self.wavecrop, self.My_name, int(len(self.wavecrop)/2)), width=20, style='my.TButton').grid( row = 2, column = 0, sticky='ew')
                            ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.image2crop,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 2, column = 1,  sticky='ew')
                            self.Done_button.destroy()
                            self.statusbar["text"]='The image has been cropped'
                        self.Done_button=ttk.Button(self.List_Frame, text = "Done", command = done_bin, style='my.TButton')
                        self.Done_button.grid( row = 3, column = 0, padx=2, pady=2, sticky='s')
            self.delete_bands=ttk.Button(self.List_Frame, text = "Delete bands", command = lambda: delete(Listbox, Images, Wave), style='my.TButton')
            self.delete_bands.grid( row = 2, column = 0, padx=2, pady=2, sticky='s')
            Hh=int(len(Wave)/2)
            my_img=Images[:,:,Hh]
            non_zero=np.nonzero(my_img)
            min_value=np.min(my_img[non_zero])
            height, width=np.where(my_img>min_value)
            hsi2d= Images[height, width,:]
            self.SNR=np.mean(hsi2d, axis=0)/np.std(hsi2d, axis=0)
            fig= matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
            ax = fig.add_subplot(1,1,1)
            ax.plot(Wave, self.SNR, 'b', linewidth=0.5)
            ax.set_xticks(np.arange(int(min(Wave)), int(max(Wave)+1), 50))
            ax.set_title('Signal/Noise', fontsize=5)
            ax.set_xlabel("Wavelength (nm)", fontproperties=font)
            ax.set_ylabel('SNR', fontproperties=font)
            ax.tick_params(axis='x', labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.get_tk_widget().grid(row = 0, column=0)
            canvas.draw()
        def select_bands(self):
            try:
                self.Done_button.destroy()
            except:
                pass
            try:
                self.listNodes5.destroy()
            except:
                pass
            self.destroy_frames()
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            speak('Please select bands from the list')
            self.statusbar["text"]=('Please select bands from the list')
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    Images=self.hypercube
                    Listbox=self.my_ListNodes
                    Wave=self.my_wave
                    self.statusbar["text"]='Cant spectral selection from multi-images, please select bands before spatial crop'
            def delete(listbox, images, wave):
                Ss=[]
                selection = listbox.curselection()
                for s in selection:
                    seltext = listbox.get(s)
                    Ss.append(seltext[-2])
                self.Hs=wave2index(wave, Ss)
                wave=np.asarray(wave)
                if len(self.Hs)>1:
                    self.selected_wavelength=wave[self.Hs]
                    self.img_selected=images[:,:,self.Hs]
                    def get_list(event):
                        self.statusbar["text"]='Display The band....'
                        self.index = self.listNodes5.curselection()[0]
                        self.seltext = self.listNodes5.get(self.index)
                        self.Band=self.img_selected[:,:,self.index]
                        name=str(self.seltext[3])+' nm'
                        title='Reflection heat map at ' + name
                        plot_contour(self.Band, 0, 0, self.canvas_frame, title, self.path, name, (2,2), 'lightyellow')
                        self.statusbar["text"]='Display band '+name
                    select=ttk.Label(self.List_Frame, text='Select band', style="BW.TLabel", font=('Times New Roman', 15))
                    select.grid( row = 0, column = 0, padx=2, pady=2, sticky='n')
                    self.listNodes5 = tkinter.Listbox(self.List_Frame, width=20, height=18, font=('Times New Roman', 15), selectmode=tkinter.EXTENDED)
                    self.listNodes5.grid(row=1, column=0, sticky='ns')
                    self.scrollbar_bin = ttk.Scrollbar(self.List_Frame, orient="vertical")
                    self.scrollbar_bin.config(command=self.listNodes5.yview) ## connected scrollbar with listnodes
                    self.scrollbar_bin.grid(row=1, column=1, sticky='ns')
                    self.listNodes5.config(yscrollcommand=self.scrollbar_bin.set) ## connected listnodes with scrollbar
                    self.listNodes5.bind('<Double-1>', get_list)
                    Xx=0
                    for x in self.selected_wavelength:
                        Xx+=1
                        self.listNodes5.insert(tkinter.END, ('Band',Xx,'(',round(x,4), ')'))
                    if self.img_selected.shape[2]>0:
                        self.cube_entry=ttk.Entry(self.results_frame, textvariable = self.input_text1, width = 15, font=('Helvetica', '12'))
                        self.cube_entry.grid( row = 0, column = 1, padx=2, pady=2) # this is placed in 0 1
                        self.cube_size=ttk.Label(self.results_frame, text='Cube size', style="BW.TLabel", font=('Times New Roman', 15))
                        self.cube_size.grid( row = 0, column = 0, padx=2, pady=2)
                        A=[]
                        for i in range(3):
                            A.append(self.img_selected.shape[i])
                        self.input_text1.set(convert(A, 0))
                        def done_bin():
                            self.hypercube=self.img_selected
                            self.my_wave=self.selected_wavelength
                            self.my_ListNodes=self.listNodes5
                            self.My_name+='_selected_bands'
                            self.f.write("if Sb==1:\n\t\tmy_wave=np.asarray(my_wave)[["+convert(self.Hs, 0)+"]]\n\t\thypercube=hypercube[:,:,["+convert(self.Hs, 0)+"]]\n\t\tnames+='_selected_bands'\n\t")
                            ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.img_selected, self.selected_wavelength, self.My_name, 1), width=21, style='my.TButton').grid( row = 1, column = 0, columnspan=2, sticky='ew')
                            ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.img_selected,self.selected_wavelength, self.My_name, int(len(self.selected_wavelength)/2)), width=20, style='my.TButton').grid( row = 2, column = 0, columnspan=2, sticky='ew')
                            ttk.Button(self.results_frame, text = "Build 3d cube", command=lambda:plot_3dcube(self.img_selected,  self.path, self.My_name, self.canvas_frame), width=20, style='my.TButton').grid( row = 3, column = 0, columnspan=2, sticky='ew')
                            self.Done_button.destroy()
                            self.selct_band_button.destroy()
                        self.Done_button=ttk.Button(self.List_Frame, text = "Done", command = done_bin, style='my.TButton')
                        self.Done_button.grid( row = 3, column = 0, padx=2, pady=2, sticky='s')
            self.selct_band_button=ttk.Button(self.List_Frame, text = "Select", command = lambda: delete(Listbox, Images, Wave), style='my.TButton')
            self.selct_band_button.grid( row = 2, column = 0, padx=2, pady=2, sticky='s')
        def Spatial_crop(self):
            self.destroy_frames()
            speak('Please wait for split hyperspectral image')
            self.statusbar["text"]='Please wait for split hyperspectral image into subimages...'
            self.input_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.input_frame.grid(row=3, column=2, sticky='ew')
            self.results_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
            self.results_frame.grid(row=3, column=3, columnspan=2, sticky='ew')
            try:
                if self.hypercube.shape[2]>1:
                    Images=self.hypercube
                    Wave=self.my_wave
            except:
                if self.hypercube[0].shape[2]>1:
                    pass
            try:
                self.Done_button.destroy()
            except:
                pass
            img_binarries=cv2.imread(self.my_path+'/binarry/'+self.name+'.tiff', 1)
            self.hsi_croped_image, self.all_data_mean, color_img=crop_image(Images, img_binarries, self.masked_img_green)
            save_img(self.my_path+'/segmented', self.name+'_crop', color_img)
            self.hsi_croped_wave=Wave
            if self.hsi_croped_image.shape[0]>0:
                self.statusbar["text"]='The hypercube have been cropped'
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                col=round((self.hsi_croped_image.shape[0]/3)+0.1)
                i=0
                for INDEX in range(self.hsi_croped_image.shape[0]):
                    i+=1
                    imge=self.hsi_croped_image[INDEX]
                    HH=int(imge.shape[2]/2)
                    Band=imge[:,:,HH]
                    ax2 = fig.add_subplot(3,col,i)
                    ax2.imshow(Band)
                    ax2.set_yticks([])
                    ax2.set_xticks([])
                    def done_crop():
                        self.hypercube=self.hsi_croped_image
                        self.my_wave=Wave
                        self.Done_button_crop.destroy()
                        self.My_name+='_spat_crop'
                        self.f.write("if Spc==1:\n\t\timg_binarries=cv2.imread(my_path+'/binarry/1.tiff', 1)\n\t\thypercube, all_data_mean, color_img=crop_image(hypercube, img_binarries, masked_img_green)\n\t\tsave_img(my_path+'/segmented', name+'_crop', color_img)\n\t\tnames+='_spat_crop'\n\t")
                        ttk.Button(self.results_frame, text = "Save cube",  command=lambda:save_mat_file(self.path, self.hsi_croped_image, Wave, self.My_name, 1), width=21, style='my.TButton').grid( row = 0, column = 0,  sticky='ew')
                        ttk.Button(self.results_frame, text = "Save spectrum", command=lambda:save_excel(self.path, self.all_data_mean,Wave, self.My_name, int(len(Wave)/2)), width=20, style='my.TButton').grid( row = 1, column = 0,  sticky='ew')
                        ttk.Button(self.results_frame, text = "Plot spectrum", command=lambda:plot_spectrum(self.all_data_mean, Wave, 0, self.canvas_frame, FigSize=(3,2), Title="Spectrum", legend=1, path=self.path, name="spatial_cropped"), width=20, style='my.TButton').grid( row = 2, column = 0, sticky='ew')
                    canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                    canvas.get_tk_widget().grid(row = 0, column=0, sticky='e')
                    canvas.draw()
                    self.Done_button_crop=ttk.Button(self.input_frame, text = "Done", command = done_crop, style='my.TButton')
                    self.Done_button_crop.grid( row = 3, column = 0, padx=2, pady=2, sticky='s')
        def import_model(self):
            try:
                self.root_imgprocess.destroy()
            except:
                pass
            try:
                self.preprocessing_button2.destroy()
            except:
                pass
            self.destroy_frames()
            my_time=time_convert(time.time()-self.time1)
            self.statusbar["text"]=('Single image analysis time:'+my_time)  
            try:
                self.List_Frame.destroy()
            except:
                pass
            try:
                self.canvas_frame.destroy()
            except:
                pass
            speak('please select The model')
            self.statusbar["text"]='please select The model'
            self.path2 = select_infile(filt='.sav')
            self.input_text.set(self.path2[-79:])
            if self.path2:
                try:
                    self.canvas_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=0)
                    self.canvas_frame.grid(row=5, column=0, columnspan=4, sticky='w')
                except:
                    pass
                self.loaded_model = pickle.load(open(self.path2, 'rb'))
                self.statusbar["text"]='The model loaded'
                ready=0
                try:
                    if self.hypercube.shape[2]>1:
                        My_Images=self.hypercube
                        names=self.My_name
                    else:
                        pass
                except:
                    if self.hypercube[0].shape[2]>1:
                        self.statusbar['text']="error: cant analysis spatial crop image"
                        pass
                    else:
                        pass
                if len(My_Images.shape)==3:
                    if self.image_SNV.shape[1]>1:
                        My_Images=SNV_image(My_Images)[1]
                        names=names+' after SNV'
                    elif self.image_msc.shape[1]>1:
                        My_Images=MSC_image(My_Images)[1]
                        names=names+' after MSC'
                    elif self.img_derv.shape[0]>1:
                        My_Images=sg(My_Images, self.Windowsd, self.orderd, self.Derv)[0]
                        names=names+' after derivative'
                    self.Data_cube=My_Images
                if self.myvegetation.shape[1]>2:
                    self.Data_cube=self.myvegetation
                    names='Vegetation index'
                self.statusbar['text']=names
                if self.Data_cube.shape[2]:
                    self.Data_cube2D=self.Data_cube.reshape((self.Data_cube.shape[0]*self.Data_cube.shape[1]),self.Data_cube.shape[2])
                    ready=1
                else:
                    self.Data_cube2D=self.Data_cube.reshape((self.Data_cube.shape[0]*self.Data_cube.shape[1]),1)
                    ready=1
                if ready==1:
                    try:
                        Data_result=self.loaded_model.predict(self.Data_cube2D)
                        Data_result_cube=Data_result.reshape(self.Data_cube.shape[0], self.Data_cube.shape[1])
                        Hh=int(My_Images.shape[2]/2)
                        height, width=np.where(My_Images[:,:,Hh]==0)
                        Data_result_cube=remove_Outliers(Data_result_cube, 2)
                        try:
                            check_classification_targets(Data_result)
                            Data_result_cube[height, width]=-2
                            plot_contour(Data_result_cube, -1, int(np.amax(Data_result)+1), self.canvas_frame,  'Classification result', self.path, 'class result', (2,2), 'lightyellow')
                        except:
                            Data_result_cube[height, width]=0
                            plot_contour(Data_result_cube, 0, 0, self.canvas_frame, 'Regression result', self.path, 'Reg result', (2,2), 'lightyellow')
                    except Exception as e:
                        self.statusbar["text"]=e
                else:
                  self.statusbar["text"]="There is an error"  
            else:
                speak('You have to select right file')
                self.statusbar["text"]='You have to select pre-trained model file'
        def All_images(self):
            try:
                self.f.write("speak(name[:6]+' processed')\n\tstatusbar['text']=name+' processed'\n\ttry:\n\t\tdata_mean=all_data_mean\n\texcept:\n\t\tHh=int(hypercube.shape[2]/2)\n\t\timg=hypercube[:,:,Hh]\n\t\tnon_zero=np.nonzero(img)\n\t\tmin_value=np.min(img[non_zero])\n\t\theight, width=np.where(img>min_value)\n\t\tdata_mean=np.asarray(np.mean(hypercube[height, width,:], 0)).reshape(1,-1)\n\t")
                self.f.write("speak('Spectral features have been extracted')\n\tstatusbar['text']=name+' spectral features calculated'\n\t")
                self.f.write("if Sc==1:\n\t\tspeak('Saving mat files')\n\t\tstatusbar['text']=name+'s mat files saving....'\n\t\tsave_mat_file((my_path+'/'+name+Type()), hypercube, my_wave, names, 1)\n\t\tstatusbar['text']=name+'s mat files saved'\n\t")
                self.f.write('return hypercube, data_mean, my_wave, names\n')
                self.f.close()
            except:
                pass
            try:
                self.root_imgprocess.destroy()
            except:
                pass
            try:
                self.preprocessing_button2.destroy()
            except:
                pass
            self.destroy_frames()
            my_time=time_convert(time.time()-self.time1)
            self.statusbar["text"]=('Single image analysis time:'+my_time)  
            try:
                self.canvas_frame.destroy()
            except:
                pass
            try:
                self.List_Frame.destroy()
            except:
                pass
            self.button_frame=tkinter.LabelFrame(window, bg='lightyellow', bd=1)
            self.button_frame.grid(row=2, column=3,rowspan=2,pady=5, padx=5, sticky='ne')
            self.check_frame=tkinter.LabelFrame(window, text='Select cube', bg='lightyellow', bd=1)
            self.check_frame.grid(row=2, column=1,columnspan=2, sticky='w')
            FS=tkinter.IntVar(window)
            BS=tkinter.IntVar(window)
            CS=tkinter.IntVar(window)
            Sb=tkinter.IntVar(window)
            vindex=tkinter.IntVar(window)
            Spc=tkinter.IntVar(window)
            Spb=tkinter.IntVar(window)
            Spz=tkinter.IntVar(window)
            D_aug=tkinter.IntVar(window)
            wc=tkinter.IntVar(window)
            def click():
                if FS.get()==1:
                    check2.config(state=tkinter.DISABLED)
                    check3.config(state=tkinter.DISABLED)
                    check4.config(state=tkinter.DISABLED)
                    self.start_button.config(state='active')
                    self.model_button.config(state='active')
                    self.prj_button.config(state='active')
                elif FS.get()==0:
                    self.start_button.config(state=tkinter.DISABLED)
                    self.model_button.config(state=tkinter.DISABLED)
                    self.prj_button.config(state=tkinter.DISABLED)
                    if self.Bin>1: 
                        check2.config(state='active')
                    if self.image2crop.shape[2]>1:
                        check3.config(state='active')
                    if self.img_selected.shape[2]>1:
                        check4.config(state='active')
            def click2():
                if BS.get()==1:
                    check.config(state=tkinter.DISABLED)
                    self.start_button.config(state='active')
                    self.model_button.config(state='active')
                    self.prj_button.config(state='active')
                elif BS.get()==0 and CS.get()==0 and Sb.get()==0:
                    self.start_button.config(state=tkinter.DISABLED)
                    self.model_button.config(state=tkinter.DISABLED)
                    self.prj_button.config(state=tkinter.DISABLED)
                    check.config(state='active')
            def click3():
                if CS.get()==1:
                    check.config(state=tkinter.DISABLED)
                    self.start_button.config(state='active')
                    self.model_button.config(state='active')
                    self.prj_button.config(state='active')
                elif BS.get()==0 and CS.get()==0 and Sb.get()==0:
                    self.start_button.config(state=tkinter.DISABLED)
                    self.model_button.config(state=tkinter.DISABLED)
                    self.prj_button.config(state=tkinter.DISABLED)
                    check.config(state='active')
            def click4():
                if Sb.get()==1:
                    check.config(state=tkinter.DISABLED)
                    self.start_button.config(state='active')
                    self.model_button.config(state='active')
                    self.prj_button.config(state='active')
                elif BS.get()==0 and CS.get()==0 and Sb.get()==0:
                    self.start_button.config(state=tkinter.DISABLED)
                    self.model_button.config(state=tkinter.DISABLED)
                    self.prj_button.config(state=tkinter.DISABLED)
                    check.config(state='active')
            wc_check=tkinter.Checkbutton(self.check_frame, text="Rad_calib",variable=wc, bg='lightyellow')
            wc_check.grid(row=0, column=0, sticky='w')
            wc_check.config(state=tkinter.DISABLED)
            if self.HSI_Img_calib.shape[2]>1:
                wc_check.config(state='active')
            check = tkinter.Checkbutton(self.check_frame, text="Full bands", command=click, variable=FS, bg='lightyellow')
            check.grid(row=0, column=1, sticky='w')
            check2 = tkinter.Checkbutton(self.check_frame, text="Binning spectral", command=click2, variable=BS, bg='lightyellow')
            check2.grid(row=1, column=0, sticky='w')
            if self.Bin<1:
                check2.config(state=tkinter.DISABLED)
            check3 = tkinter.Checkbutton(self.check_frame, text="Cropped spectral", command=click3, variable=CS, bg='lightyellow')
            check3.grid(row=1, column=1, sticky='w')
            if self.image2crop.shape[2]<2:
                check3.config(state=tkinter.DISABLED)
            check4 = tkinter.Checkbutton(self.check_frame, text="Selected bands", command=click4, variable=Sb, bg='lightyellow')
            check4.grid(row=1, column=2, sticky='w')
            if self.img_selected.shape[2]<2:
                check4.config(state=tkinter.DISABLED)
            check5 = tkinter.Checkbutton(self.check_frame, text="Spatial crop",  variable=Spc, bg='lightyellow')
            check5.grid(row=2, column=0, sticky='w')
            if self.hsi_croped_image.shape[0]<2:
                check5.config(state=tkinter.DISABLED)
            check6 = tkinter.Checkbutton(self.check_frame, text='Vegetation index',  variable=vindex, bg='lightyellow')
            check6.grid(row=0, column=2, sticky='w')
            if self.myvegetation.shape[1]<2:
                check6.config(state=tkinter.DISABLED)
            check_spat_bin = tkinter.Checkbutton(self.check_frame, text="Spatial binning",  variable=Spb, bg='lightyellow')
            check_spat_bin.grid(row=2, column=1, sticky='w')
            if self.spat_Bin<1:
                check_spat_bin.config(state=tkinter.DISABLED)
            check_spat_resize = tkinter.Checkbutton(self.check_frame, text="Spatial resize",  variable=Spz, bg='lightyellow')
            check_spat_resize.grid(row=2, column=2, sticky='w')
            if self.x_size<1 and self.y_size<1:
                check_spat_resize.config(state=tkinter.DISABLED)
            Sc=tkinter.IntVar(window)
            Ss=tkinter.IntVar(window)
            SR=tkinter.IntVar(window)
            TexFeat=tkinter.IntVar(window)
            Morph=tkinter.IntVar(window)
            SNVcheck=tkinter.IntVar(window)
            MSCcheck=tkinter.IntVar(window)
            SGD=tkinter.IntVar(window)
            self.output_frame=tkinter.LabelFrame(window, text='Out-put', bg='lightyellow', bd=1)
            self.output_frame.grid(row=3, column=1,columnspan=2, pady=2, sticky='w')
            SNV_check=tkinter.Checkbutton(self.output_frame, text='SNV',  variable=SNVcheck, bg='lightyellow') 
            SNV_check.grid(row=0, column=0, sticky='w')
            MSC_check=tkinter.Checkbutton(self.output_frame, text='MSC',  variable=MSCcheck, bg='lightyellow') 
            MSC_check.grid(row=0, column=1, sticky='w', ipadx=5)
            SGD_check=tkinter.Checkbutton(self.output_frame, text='SG_derv                ',  variable=SGD, bg='lightyellow')
            SGD_check.grid(row=0, column=2, sticky='w') 
            if self.Windowsd==0 and self.orderd==0 and self.Derv==0:
                SGD_check.config(state=tkinter.DISABLED)    
            spectrum_check=tkinter.Checkbutton(self.output_frame, text="Save spectrum", variable=Ss, bg='lightyellow')
            spectrum_check.grid(row=1, column=0, sticky='w')     
            tkinter.Checkbutton(self.output_frame, text="Save cube", variable=Sc, bg='lightyellow').grid(row=1, column=1, sticky='w', ipadx=5) 
            tkinter.Checkbutton(self.output_frame, text="Save RGB", variable=SR, bg='lightyellow').grid(row=1, column=2, sticky='w') 
            tkinter.Checkbutton(self.output_frame, text='Data_aug',  variable=D_aug, bg='lightyellow').grid(row=2, column=2, sticky='w') 
            text_checkbutton=tkinter.Checkbutton(self.output_frame, text='Textural features',  variable=TexFeat, bg='lightyellow')
            text_checkbutton.grid(row=2, column=1, sticky='w', ipadx=5)
            text_checkbutton.config(state=tkinter.DISABLED)
            morph_checkbutton=tkinter.Checkbutton(self.output_frame, text='Morph features',  variable=Morph, bg='lightyellow')
            morph_checkbutton.grid(row=2, column=0, sticky='w') 
            if len(self.angles)>0 and len(self.steps)>0:
                text_checkbutton.config(state='active')
            else:
                text_checkbutton.config(state=tkinter.DISABLED)  
            def analysis(Tbm):
                self.time2=time.time()
                speak('Wait for collect all image in The folder.')
                self.statusbar["text"]='Wait for collect all image in The folder........'
                MY_PATH=self.path.split('/')
                self.my_path='/'.join(MY_PATH[:-1])
                Path=self.my_path
                exec(open(self.my_path+'/HSI_PP prj.py').read())
                In_File=[]
                for File in os.listdir(Path):
                    if File.endswith(self.file_type):
                        Name, ext = os.path.splitext(File)
                        In_File.append(Name)
                if len(In_File)>1:
                    speak('Start to collect '+str(len(In_File))+' files')
                    self.statusbar["text"]='Start to collect '+str(len(In_File))+' files'
                    mean_all_image=[]
                    all_image_waves=[]
                    In_Files=[]
                    All_parameters=[]
                    All_Entropy=[]
                    All_Homogenity=[]
                    All_Correlation=[]
                    All_Contrast=[]
                    All_Energy=[]
                    name_texture=[]
                    all_snv=[]
                    all_msc=[]
                    all_derv=[]
                    name_morph=[]
                    All_size=[]
                    for infile in In_File:
                        if self.stop==False:
                            pass
                        if self.stop==True:
                            self.statusbar["text"]=('Software stopped')
                            break
                        speak('plaese wait for extract hyper spectral image from '+str(infile))
                        self.statusbar["text"]=infile+'....'
                        INFILE=(Path+'/'+infile+self.file_type)
                        image_size=os.stat(INFILE).st_size/10**9 # image size in GB
                        All_size.append(image_size)
                        try:
                            if self.file_type!='.mat':
                                a=HDR_test(INFILE)
                                if a==1:
                                    hypercube, data_mean, my_wave, names=analysis_img(INFILE, self.statusbar, wc.get(), SR.get(), BS.get(), CS.get(), Sb.get(), Spc.get(), Sc.get(), Spb.get(), Spz.get())
                                else:
                                    self.statusbar["text"]='Error! header file not available for '+infile
                                    pass
                            else:
                                hypercube, data_mean, my_wave, names=analysis_img(INFILE, self.statusbar, wc.get(), SR.get(), BS.get(), CS.get(), Sb.get(), Spc.get(), Sc.get(), Spb.get(), Spz.get())
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if Morph.get()==1:
                                speak('Calculate morphological features')
                                self.statusbar["text"]=infile+"'s morphological features calculating...."
                                img_binarries=cv2.imread(self.my_path+'/binarry/1.tiff', 1)
                                masked_img_green=cv2.imread(self.my_path+'/1.tiff', 1)
                                all_parameter=calculate_morphology(img_binarries, self.my_path, infile, masked_img_green, display=False)
                                if all_parameter.shape[0]>1:
                                    for l in range(all_parameter.shape[0]):
                                        All_parameters.append(all_parameter[l,:])
                                        name_morph.append(infile+'_'+str(l+1))
                                elif all_parameter.shape[0]==1:
                                    All_parameters.append(all_parameter[0])
                                    name_morph.append(infile)
                                speak('Morphological features have been calculted')
                                self.statusbar["text"]=infile+"'s morphological features calculated"
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if vindex.get()==1:
                                speak('Calculate Vegetation index')
                                self.statusbar["text"]=infile+"'s Vegetation index calculating...."
                                My_Vegetation=vegetation_index(hypercube, self.IVs, self.Vi)
                                if len(hypercube.shape)==3:
                                    My_Vegetation=vegetation_index(hypercube, self.IVs, self.Vi)
                                    My_Vegetation=np.asarray(My_Vegetation)
                                    name=infile+'_'+self.Values[self.Vi]
                                    save_mat_file((self.my_path+'/'+infile+self.file_type), My_Vegetation, self.veg_wave, name, 1)
                                elif len(hypercube.shape)==1 or len(hypercube.shape)==4:
                                    for i in range(hypercube.shape[0]):
                                        sub_image=hypercube[i]
                                        My_Vegetation=vegetation_index(sub_image, self.IVs, self.Vi)
                                        My_Vegetation=np.asarray(My_Vegetation)
                                        name=infile+'_'+self.Values[self.Vi]+str(i+1)
                                        save_mat_file((self.my_path+'/'+infile+self.file_type), My_Vegetation, self.veg_wave, name, 0)
                                    speak('The vegetation index have been saved')
                                speak('Vegetation index has been Calculated')
                                self.statusbar["text"]=infile+"'s Vegetation index calculate"
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if Ss.get()==1 or Tbm==1 and Ss.get()==1:
                                if Spc.get()==0:
                                    if len (data_mean.shape)==2:
                                        mean_all_image.append(data_mean[0])
                                    else:
                                        mean_all_image.append(data_mean)
                                elif Spc.get()==1:
                                    for iI in range(data_mean.shape[0]):
                                        mean_all_image.append(data_mean[iI])
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if SGD.get()==1 or Tbm==1 and SGD.get()==1:
                                speak('Calculate derivative image')
                                self.statusbar["text"]=infile+' Calculate derivative image'
                                img_derv_cube=sg(hypercube, self.Windowsd, self.orderd, self.Derv)[0]
                                img_derv=sg(hypercube, self.Windowsd, self.orderd, self.Derv)[1]
                                if Sc.get()==1:
                                    save_mat_file((self.my_path+'/'+infile+self.file_type), img_derv_cube, my_wave, names+'_derv', 1)
                                else:
                                    pass
                                if Spc.get()==0:
                                    all_derv.append(img_derv[0])
                                elif Spc.get()==1:
                                    for i in range(img_derv.shape[0]):
                                        all_derv.append(img_derv[i,:])
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if SNVcheck.get()==1 or Tbm==1 and SNVcheck.get()==1:
                                speak('Calculate SNV')
                                self.statusbar["text"]=infile+' Calculate SNV'
                                image_SNV=SNV_image(hypercube)[0]
                                image_snv_cube=SNV_image(hypercube)[1]
                                if Sc.get()==1:
                                    save_mat_file((self.my_path+'/'+infile+self.file_type), image_snv_cube, my_wave, names+'_SNV', 1)
                                else:
                                    pass
                                if Spc.get()==0:
                                   all_snv.append(image_SNV[0])
                                elif Spc.get()==1:
                                   for i in range(image_SNV.shape[0]):
                                        all_snv.append(image_SNV[i])
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if MSCcheck.get()==1 or Tbm==1 and MSCcheck.get()==1:
                                speak('Calculate MSC')
                                self.statusbar["text"]=infile+' Calculate MSC'
                                image_MSC=MSC_image(hypercube)[0]
                                image_msc_cube=MSC_image(hypercube)[1]
                                if Sc.get()==1:
                                    save_mat_file((self.my_path+'/'+infile+self.file_type), image_msc_cube, my_wave, names+'_MSC', 1)
                                else:
                                    pass
                                if Spc.get()==0:
                                    all_msc.append(image_MSC[0])
                                elif Spc.get()==1:
                                    for i in range(image_MSC.shape[0]):
                                        all_msc.append(image_MSC[i])
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if Ss.get()==1 or MSCcheck.get()==1 or SGD.get()==1 or SNVcheck.get()==1:
                                all_image_waves.append(my_wave)
                                if Spc.get()==0:
                                    In_Files.append(infile)
                                elif Spc.get()==1:
                                    for i in range(hypercube.shape[0]):
                                        infiles=infile+'_'+str(i+1)
                                        In_Files.append(infiles)
                            else:
                                pass
                            if TexFeat.get()==1:
                                speak('Calculate textural features')
                                self.statusbar["text"]=infile+"'s textural features calculating...."
                                Entropy, Homogenity, Correlation, Contrast, Energy=texture_features(hypercube,self.angles,self.steps)
                                if Homogenity.shape[0]>1:
                                    for l in range(Homogenity.shape[0]):
                                        All_Entropy.append(Entropy[l,:])
                                        All_Homogenity.append(Homogenity[l,:])
                                        All_Correlation.append(Correlation[l,:])
                                        All_Contrast.append(Contrast[l,:])
                                        All_Energy.append(Energy[l,:])
                                        name_texture.append(infile+'_'+str(l+1))
                                elif Homogenity.shape[0]==1:
                                    All_Entropy.append(Entropy)
                                    All_Homogenity.append(Homogenity[0,:])
                                    All_Correlation.append(Correlation[0,:])
                                    All_Contrast.append(Contrast[0,:])
                                    All_Energy.append(Energy[0,:])
                                    name_texture.append(infile)
                                speak('Textural features calculated')
                                self.statusbar["text"]=infile+"'s textural features calculated"
                            else:
                                pass
                            if self.stop==True:
                                self.statusbar["text"]=('Software stopped')
                                break
                            else:
                                pass
                            if D_aug.get()==1:
                                speak(infile+"'s augmenting....")
                                self.statusbar["text"]=infile+"'s augmenting...."
                                my_image_aug=Data_aug(hypercube)
                                save_mat_file((self.my_path+'/'+infile+self.file_type), my_image_aug, my_wave, '_DA', 1)
                                self.statusbar["text"]=infile+"'s augmented and saved"
                            else:
                                pass
                            speak(infile+" done")
                            self.statusbar["text"]=infile+" done"
                        except Exception as e:
                            self.statusbar["text"]=e
                            print(e)
                            pass
    #################output execel from HSI_PP
                    speak('Saving excel files')
                    self.statusbar["text"]=infile+"'s excel files saving...."
                    if TexFeat.get()==1 and len(All_Entropy)>1:
                        All_Entropy=np.asarray(All_Entropy)
                        All_Homogenity=np.asarray(All_Homogenity)
                        All_Correlation=np.asarray(All_Correlation)
                        All_Contrast=np.asarray(All_Contrast)
                        All_Energy=np.asarray(All_Energy)
                        try:
                            os.mkdir(Path+'/Excel files')
                            writer = pd.ExcelWriter(Path+'/Excel files/all_HSI_PP_Texture_features.xlsx', engine='xlsxwriter')
                        except:
                           writer = pd.ExcelWriter(Path+'/Excel files/all_HSI_PP_Texture_features.xlsx', engine='xlsxwriter')
                        writer.book.use_zip64()
                        name_texture=np.asarray(name_texture)
                        df_file_name=pd.DataFrame(name_texture)
                        df_All_Entropy=pd.DataFrame(All_Entropy, columns=all_image_waves[0])
                        df_All_Entropy.to_excel(writer, sheet_name='Entropy', index=False, startcol=1)
                        df_file_name.to_excel(writer, sheet_name='Entropy', index=False)
                        df_All_Homogenity=pd.DataFrame(All_Homogenity, columns=all_image_waves[0])
                        df_All_Homogenity.to_excel(writer, sheet_name='Homogenity', index=False, startcol=1)
                        df_file_name.to_excel(writer, sheet_name='Homogenity', index=False)
                        df_All_Correlation=pd.DataFrame(All_Correlation, columns=all_image_waves[0])
                        df_All_Correlation.to_excel(writer, sheet_name='Correlation', index=False, startcol=1)
                        df_file_name.to_excel(writer, sheet_name='Correlation', index=False)
                        df_All_Contrast=pd.DataFrame(All_Contrast, columns=all_image_waves[0])
                        df_All_Contrast.to_excel(writer, sheet_name='Contrast', index=False, startcol=1)
                        df_file_name.to_excel(writer, sheet_name='Contrast', index=False)
                        df_All_Energy=pd.DataFrame(All_Energy, columns=all_image_waves[0])
                        df_All_Energy.to_excel(writer, sheet_name='Energy', index=False, startcol=1)
                        df_file_name.to_excel(writer, sheet_name='Energy', index=False)                                   
                        writer.save()
                        speak('The texture features for all files in the folder have been saved')
                        self.statusbar["text"]=('The morphological features for all files in the folder have been saved')
                    if Morph.get()==1 and len(All_parameters)>1:
                        All_parameters=np.asarray(All_parameters)
                        colums=['Proj_area', 'plant_prem', 'convex_area', 'convex_pre', 'Major_axis', 'Minor_axis', 'circle_prem', 'Compactness', 'Stockiness']
                        df_All_parameters=pd.DataFrame(All_parameters,  columns=colums)
                        try:
                            os.mkdir(Path+'/Excel files')
                            writer = pd.ExcelWriter(Path+'/Excel files/all_HSI_PP_geometric.xlsx', engine='xlsxwriter')
                        except:
                           writer = pd.ExcelWriter(Path+'/Excel files/all_HSI_PP_geometric.xlsx', engine='xlsxwriter')
                        writer.book.use_zip64()
                        df_All_parameters.to_excel(writer, sheet_name='Geometric', index=False, startcol=1)
                        name_morph=np.asarray(name_morph)
                        df_file_name=pd.DataFrame(name_morph)
                        df_file_name.to_excel(writer, sheet_name='Geometric', index=False)
                        writer.save()
                        speak('The morphological features for all files in the folder have been saved')
                        self.statusbar["text"]=('The morphological features for all files in the folder have been saved')
                    if len(mean_all_image)>1 or len(all_snv)>1 or len(all_msc)>1 or len(all_derv)>1:
                        my_times=time_convert(time.time()-self.time2)
                        self.statusbar["text"]=('Collect time:'+my_times)
                        all_image_waves=np.asarray(all_image_waves)
                        In_Files=np.asarray(In_Files)
                        df_file_name=pd.DataFrame(In_Files)
                        try:
                            os.mkdir(Path+'/Excel files')
                            writer = pd.ExcelWriter(Path+'/Excel files/all_'+names+'_HSI_PP.xlsx', engine='xlsxwriter')
                        except: 
                            writer = pd.ExcelWriter(Path+'/Excel files/all_'+names+'_HSI_PP.xlsx', engine='xlsxwriter')
                        writer.book.use_zip64()
                        if Ss.get()==1:## save into excel
                            mean_all_image=np.asarray(mean_all_image)
                            df_mean_all_image=pd.DataFrame(mean_all_image, columns=all_image_waves[0])
                            df_mean_all_image.to_excel(writer, sheet_name='reflect', index=False, startcol=1)
                            df_file_name.to_excel(writer, sheet_name='reflect', index=False)
                        if SNVcheck.get()==1:
                            all_snv=np.asarray(all_snv)
                            df_mean_all_snv=pd.DataFrame(all_snv, columns=all_image_waves[0])
                            df_mean_all_snv.to_excel(writer, sheet_name='snv', index=False, startcol=1)
                            df_file_name.to_excel(writer, sheet_name='snv', index=False)
                            data_model=all_snv
                        if MSCcheck.get()==1:
                            all_msc=np.asarray(all_msc)
                            df_mean_all_msc=pd.DataFrame(all_msc, columns=all_image_waves[0])
                            df_mean_all_msc.to_excel(writer, sheet_name='msc', index=False, startcol=1)
                            df_file_name.to_excel(writer, sheet_name='msc', index=False)
                            data_model=all_msc
                        if SGD.get()==1:
                            all_derv=np.asarray(all_derv)
                            df_mean_all_derv=pd.DataFrame(all_derv, columns=all_image_waves[0])
                            if self.Derv==1:
                                name='First dervative'
                            else:
                                name='Second dervative'
                            df_mean_all_derv.to_excel(writer, sheet_name=name, index=False, startcol=1)
                            df_file_name.to_excel(writer, sheet_name=name, index=False)
                            data_model=all_derv
                        writer.save()
                        speak('The reflection for all files in the folder have been saved')
                        self.statusbar["text"]='The reflection for all files in the folder have been saved'
                        if Tbm==1:
                            data_model=np.asarray(mean_all_image)
                            if SNVcheck.get()==1:
                                data_model=np.asarray(all_snv)
                            if SGD.get()==1:
                                data_model=np.asarray(all_derv)
                            if MSCcheck.get()==1:
                                data_model=np.asarray(all_msc)
                            speak('plaese select model!')
                            self.path2 = select_infile(filt='.sav', title='Select model', name='Model')
                            self.input_text.set(self.path2[-79:])
                            self.loaded_model = pickle.load(open(self.path2, 'rb'))
                            try:
                                Y_test=self.loaded_model.predict(data_model)
                                Y_test=np.asarray(Y_test)
                                df_model_output=pd.DataFrame(Y_test)
                                In_Files=np.asarray(In_Files)
                                df_file_name=pd.DataFrame(In_Files)
                                try:
                                    os.mkdir(Path+'/Excel files')
                                    writer = pd.ExcelWriter(Path+'/Excel files/model_output_HSI_PP.xlsx', engine='xlsxwriter')
                                except: 
                                    writer = pd.ExcelWriter(Path+'/Excel files/model_output_HSI_PP.xlsx', engine='xlsxwriter')
                                writer.book.use_zip64()
                                df_model_output.to_excel(writer, sheet_name='output', index=False, startcol=1)
                                df_file_name.to_excel(writer, sheet_name='output', index=False)
                                speak('The model output saved')
                                self.statusbar['text']='The model output saved'
                                writer.save()
                            except Exception as e:
                                self.statusbar['text']=e
                    my_timess=time_convert(time.time()-self.time2)
                    speak('ALL images analyzed')
                    self.statusbar["text"]=('ALL images analyzed at:'+my_timess)
                    author="This program designed by: \n\t\t\t  (Ahmed Islam ElManawy) \nfor contact: \n\t   a.elmanawy_90@agr.suez.edu.eg\n"
                    MY_PATH=self.path.split('/')
                    my_path='/'.join(MY_PATH[:-1])
                    f=open(my_path+'/HSI_PP.txt', 'w') ##for only write some thing at the end of the file this is append mode
                    f.write(author)
                    images_number='Number of analyzed images are:\n\t\t'+str(len(All_size))+' images\n'
                    f.write(images_number)
                    Sum_all_size=round(np.sum(np.asarray(All_size)), 3)
                    images_size='The total size of all images in this folder is:\n\t\t'+str(Sum_all_size)+' GB\n'
                    f.write(images_size)
                    timess="ALL images analyzed at: \n\t\t"+my_timess
                    f.write(timess)
                    f.close()
            def start_collect():
                Tbm=0
                self.stop=False
                self.stop_button.config(state=tkinter.ACTIVE)
                self.start_button.config(state=tkinter.DISABLED)
                self.model_button.config(state=tkinter.DISABLED)
                self.prj_button.config(state=tkinter.DISABLED)
                t1 = threading.Thread(target=lambda:analysis(Tbm))
                t1.setDaemon(True)
                t1.start()
            def start_model():
                Tbm=1
                self.stop=False
                self.stop_button.config(state=tkinter.ACTIVE)
                self.start_button.config(state=tkinter.DISABLED)
                self.model_button.config(state=tkinter.DISABLED)
                self.prj_button.config(state=tkinter.DISABLED)
                t1 = threading.Thread(target=lambda:analysis(Tbm))
                t1.setDaemon(True)
                t1.start()
            def stops():
                self.stop_button.config(state=tkinter.DISABLED)
                self.start_button.config(state=tkinter.ACTIVE)
                self.model_button.config(state=tkinter.ACTIVE)
                self.prj_button.config(state=tkinter.ACTIVE)
                self.statusbar["text"]=('Stop software.....')
                self.stop=True
                self.statusbar["text"]=('Software stopped')
            def create_prj():
                f_modify=open(self.my_path+'/HSI_PP prj.py', 'r').read()
                if "def analysis_img" in f_modify:
                    FileSearch1=re.search("def analysis_img", f_modify)
                    first_part=f_modify[:FileSearch1.start()]
                    last_part=f_modify[FileSearch1.end():]
                    FileSearch1=re.search(":\n", last_part)
                    last_part=last_part[FileSearch1.end():]
                f=open(self.my_path+'/HSI_PP_prj.py', 'w') 
                f.write(first_part)
                middle_part="\ndef analysis_img(image_path, statusbar):\n\twc, SR, BS, CS, Sb, Spc, Sc, Spb, Spz=("+convert((wc.get(), SR.get(), BS.get(), CS.get(), Sb.get(), Spc.get(), Sc.get(), Spb.get(), Spz.get()),0)+")\n"
                f.write(middle_part)
                if 'return hypercube' in last_part:
                    FileSearch1=re.search('return hypercube', last_part)
                    last_part=last_part[:FileSearch1.start()]
                f.write(last_part)
                f.write("df = pd.DataFrame(data_mean, columns=my_wave)\n\twriter = pd.ExcelWriter(my_path+'/'+name+'.xlsx', engine='xlsxwriter')\n\twriter.book.use_zip64()\n\tdf.to_excel(writer, sheet_name='reflect', index=False, startcol=1)\n\t")
                if SGD.get()==1:
                    f.write("speak('Calculate derivative image')\n\timg_derv_cube=sg(hypercube,"+str(self.Windowsd)+','+str( self.orderd)+','+str( self.Derv)+")[0]\n\timg_derv=np.asarray(sg(hypercube,"+str(self.Windowsd)+','+str( self.orderd)+','+str( self.Derv)+")[1])\n\tData_mean_DV = pd.DataFrame(img_derv, columns=my_wave)\n\tData_mean_DV.to_excel(writer, sheet_name='DV', index=False, startcol=1)\n\tif Sc==1:\n\t\tsave_mat_file((my_path+'/'+name+Type()), img_derv_cube, my_wave, names+'_DV', 1)\n\t")
                if SNVcheck.get()==1:
                    f.write("speak('Calculate SNV')\n\timage_SNV=np.asarray(SNV_image(hypercube)[0])\n\timage_snv_cube=SNV_image(hypercube)[1]\n\tData_mean_SNV = pd.DataFrame(image_SNV, columns=my_wave)\n\tData_mean_SNV.to_excel(writer, sheet_name='SNV', index=False, startcol=1)\n\tif Sc==1:\n\t\tsave_mat_file((my_path+'/'+name+Type()), image_snv_cube, my_wave, names+'_SNV', 1)\n\t")
                if MSCcheck.get()==1:
                    f.write("speak('Calculate MSC')\n\timage_MSC=np.asarray(MSC_image(hypercube)[0])\n\timage_msc_cube=MSC_image(hypercube)[1]\n\tData_mean_MSC = pd.DataFrame(image_MSC, columns=my_wave)\n\tData_mean_MSC.to_excel(writer, sheet_name='MSC', index=False, startcol=1)\n\tif Sc==1:\n\t\tsave_mat_file((my_path+'/'+name+Type()), image_msc_cube, my_wave, names+'_MSC', 1)\n\t")
                if TexFeat.get()==1:
                    f.write("speak('Calculate textural features')\n\t")
                    f.write("Entropy, Homogenity, Correlation, Contrast, Energy=texture_features(hypercube,["+convert(self.angles, 0)+"],["+convert(self.steps, 0)+"])\n\ttry:\n\t\tEntropy = pd.DataFrame(Entropy, columns=my_wave)\n\texcept:\n\t\tEntropy = pd.DataFrame(Entropy)\n\tHomogenity = pd.DataFrame(Homogenity, columns=my_wave)\n\tCorrelation = pd.DataFrame(Correlation, columns=my_wave)\n\tContrast = pd.DataFrame(Contrast, columns=my_wave)\n\tEnergy = pd.DataFrame(Energy, columns=my_wave)\n\t")
                    f.write("Entropy.to_excel(writer, sheet_name='Entropy', index=False, startcol=1)\n\tHomogenity.to_excel(writer, sheet_name='Homogenity', index=False, startcol=1)\n\tCorrelation.to_excel(writer, sheet_name='Correlation', index=False, startcol=1)\n\tContrast.to_excel(writer, sheet_name='Contrast', index=False, startcol=1)\n\tEnergy.to_excel(writer, sheet_name='Energy', index=False, startcol=1)\n\t")
                if Morph.get()==1:
                    f.write("speak('Calculate morphological features')\n\timg_binarries=cv2.imread(my_path+'/binarry/1.tiff', 1)\n\tmasked_img_green=cv2.imread(my_path+'/1.tiff', 1)\n\t")
                    f.write("colums=['Proj_area', 'plant_prem', 'convex_area', 'convex_pre', 'Major_axis', 'Minor_axis', 'circle_prem', 'Compactness', 'Stockiness']\n\tall_parameter=calculate_morphology(img_binarries, my_path, 1, masked_img_green, display=False)\n\tall_parameter =pd.DataFrame(all_parameter, columns=colums)\n\t")
                    f.write("all_parameter.to_excel(writer, sheet_name='Morphological', index=False, startcol=1)\n\t")             
                if vindex.get()==1:
                    f.write("speak('Calculate Vegetation index')\n\t")
                    f.write("if len(hypercube.shape)==3:\n\t\tMy_Vegetation=vegetation_index(hypercube, ["+ convert(self.IVs, 0)+"]," +str(self.Vi)+")\n\t\tMy_Vegetation=np.asarray(My_Vegetation)\n\t\tnames=name+'_'+'"+self.Values[self.Vi]+"'\n\t\tsave_mat_file((my_path+'/'+name+Type()), My_Vegetation,["+ convert(self.veg_wave, 0)+"], names, 1)\n\t")
                    f.write("elif len(hypercube.shape)==1 or len(hypercube.shape)==4:\n\t\tfor i in range(hypercube.shape[0]):\n\t\t\tsub_image=hypercube[i]\n\t\t\tMy_Vegetation=vegetation_index(sub_image, ["+ convert(self.IVs, 0)+"]," +str(self.Vi)+")\n\t\t\tMy_Vegetation=np.asarray(My_Vegetation)\n\t\t\tnames=name+'_'+'"+self.Values[self.Vi]+"'+str(i+1)\n\t\t\tsave_mat_file((my_path+'/'+name+Type()), My_Vegetation, ["+ convert(self.veg_wave, 0)+"], names, 0)\n\t\tspeak('The vegetation index have been saved')\n\t")
                if D_aug.get()==1:
                    f.write("speak(name[:6]+'s augmenting....')\n\tmy_image_aug=Data_aug(hypercube)\n\tsave_mat_file((my_path+'/'+name+Type()), my_image_aug[I], my_wave, '_Da', 1)\n\tspeak('The hypercube has been augmented and saved')")
                if vindex.get()==1:
                    f.write("hypercube=My_Vegetation\n\t")
                if SGD.get()==1:
                    f.write("hypercube=img_derv_cube\n\t")
                if SNVcheck.get()==1:
                    f.write("hypercube=image_snv_cube\n\t")
                if MSCcheck.get()==1:
                    f.write("hypercube=image_msc_cube\n\t")
                f.write("speak('The image has been analyzed and data have been saved')\n\tstatusbar['text']=name+'has been analyzed and data have been saved'\n\t")
                f.write('writer.save()\n\tif Spc==1:\n\t\thypercube=hypercube[0]\n\treturn hypercube')
                f.close()
                speak('The project has been created')
            self.start_button=ttk.Button(self.button_frame, text = "Start", width=20, command=lambda:start_collect(), style='my.TButton')
            self.start_button.grid( row = 0, column = 0,  sticky='new')
            self.stop_button=ttk.Button(self.button_frame, text = "Stop", width=20, command=lambda:stops(), style='my.TButton')
            self.stop_button.grid( row = 3, column = 0,  sticky='new')
            self.prj_button=ttk.Button(self.button_frame, text = "Create project", width=20, command=lambda:create_prj(), style='my.TButton')
            self.prj_button.grid( row = 2, column = 0,  sticky='new')
            self.model_button=ttk.Button(self.button_frame, text = "Analysis by model", width=20, command=lambda:start_model(), style='my.TButton')
            self.model_button.grid( row = 1, column = 0,  sticky='new')
            self.start_button.config(state=tkinter.DISABLED)
            self.stop_button.config(state=tkinter.DISABLED)
            self.model_button.config(state=tkinter.DISABLED)
            self.prj_button.config(state=tkinter.DISABLED)
    window = tkinter.Tk()
    def remove_prj():
        try:
            F_file.close()
            os.remove(prj_path_creat)
        except Exception as e:
            print(e)
            pass
        window.destroy()
    gui = GUI(window)
    window.protocol('WM_DELETE_WINDOW', remove_prj)
    window.mainloop()
#%% Data analysis
def Data_analysis():
    class GUI:
        def __init__(self, Data_window):
            self.xl_path = select_infile(filt=['.xlsx', '.xls', '.csv'], title='Select excel file', name='Excel file')
            ttk.Button(Data_window, text = "Loading file", command = lambda: self.data_loading(), width = 15, style='my.TButton').grid(row=0, column=0)
            if len(self.xl_path)>0:
                Data_window.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
                s = ttk.Style(Data_window)
                s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
                style = ttk.Style(Data_window)
                style.configure("BW.TLabel", foreground="black", background="lightyellow")
                Data_window.wm_iconbitmap('DAAI logo.ico')
                Data_window.title("Data analysis")
                Data_window.resizable(0, 0)
                Data_window.deiconify()
                raise_above_all(Data_window)
                menubar = tkinter.Menu(Data_window, font=('Times New Roman', 15)) ## menu bar font
                Data_window.configure(menu=menubar)
                self.DataPreprocessing = tkinter.Menu(menubar, tearoff=0,font=('Times New Roman', 15))
                menubar.add_cascade(label="Data preprocessing", menu=self.DataPreprocessing, font=('Times New Roman', 15))
                self.reductionMenu = tkinter.Menu(menubar, tearoff=0,font=('Times New Roman', 15))
                menubar.add_cascade(label="Data reduction", menu=self.reductionMenu, font=('Times New Roman', 15))
                def plz_select():
                    speak('Please select and loading data')
                    self.statusbar["text"]=('Please select data columns and rows then press load data')
                for name in ("CFS","PCA", "SFS", "GA", 'VI select'):
                    self.reductionMenu.add_command(label=name, font=('Times New Roman', 15), command =plz_select)
                for name in ("Remove outliers","Correlation"):
                    self.DataPreprocessing.add_command(label=name, font=('Times New Roman', 15), command =plz_select)
                RegMenu = tkinter.Menu(menubar, font=('Times New Roman', 15)) ## menu bar font
                self.RegMenu = tkinter.Menu(RegMenu, tearoff=0,font=('Times New Roman', 15))
                menubar.add_cascade(label="Regression", menu=self.RegMenu, font=('Times New Roman', 15))
                for name in ("RF","PLSR", "SVM", "BPNN", 'MLR'):
                    self.RegMenu.add_command(label=name, font=('Times New Roman', 15), command =plz_select)
                classMenu = tkinter.Menu(menubar, font=('Times New Roman', 15)) ## menu bar font
                self.classMenu = tkinter.Menu(classMenu, tearoff=0,font=('Times New Roman', 15))
                menubar.add_cascade(label="Classification", menu=self.classMenu, font=('Times New Roman', 15))
                for name in ("RF", "KNN", "SVM", "BPNN", 'LDA'):
                    self.classMenu.add_command(label=name, font=('Times New Roman', 15), command =plz_select)
                self.statusbar = tkinter.Label(Data_window,text="Contact us: a.elmanawy_90@agr.suez.edu.eg",bd=1,relief=tkinter.SUNKEN,font='Tahoma 10 bold', bg='LightYellow2')
                self.statusbar.grid(row=7,column=0,columnspan=6, rowspan=2, sticky='ew')
                self.statusbar.config(width="100",anchor="w")           
                ttk.Label(Data_window, text=self.xl_path, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1, columnspan=4, ipadx=1, ipady=1, sticky='w')
                ttk.Label(Data_window, text='X-matrix', style="BW.TLabel", font=('Times New Roman', 15)).grid(row=2, column=1, columnspan=2, ipadx=5, ipady=5)
                ttk.Label(Data_window, text='Y-matrix', style="BW.TLabel", font=('Times New Roman', 15)).grid(row=2, column=3, columnspan=2, ipadx=5, ipady=5)
                ttk.Label(Data_window, text='Row range', style="BW.TLabel", font=('Times New Roman', 15)).grid(row=3, column=0,ipadx=5, ipady=5)
                ttk.Label(Data_window, text='Column range', style="BW.TLabel", font=('Times New Roman', 15)).grid(row=4, column=0,ipadx=5, ipady=5)
                rows_start=[]
                rows_end=[]
                col_start=[]
                col_end=[]
                if  self.xl_path.endswith('.xls') or self.xl_path.endswith('.xlsx'):
                    self.sh_names=ttk.Label(Data_window, text='Sheet name', style="BW.TLabel", font=('Times New Roman', 15))
                    self.sh_names.grid(row=1, column=0,ipadx=5, ipady=5)
                    self.workbook = xlrd.open_workbook(self.xl_path,"rb")
                    sheets=self.workbook.sheet_names()
                    self.sh_nam = ttk.Combobox(Data_window, values=sheets, width=15, font=('Times New Roman', 15))
                    self.sh_nam.set(sheets[0])
                    self.sh_nam.grid( row = 1, column = 1, sticky='ew', columnspan=2)
                    sh = self.workbook.sheet_by_name(sheets[0])
                    for i in range(sh.nrows):
                        rows_start.append(i+1)
                    for i in range(1, sh.nrows):
                        rows_end.append(i+1)
                    for i in range(sh.ncols):
                        col_start.append(i+1)
                    for i in range(1, sh.ncols):
                        col_end.append(i+1)
                if  self.xl_path.endswith('.csv') :
                    self.df = pd.read_csv(self.xl_path)
                    n,m = self.df.shape
                    for i in range(n):
                        rows_start.append(i+1)
                    for i in range(1, n):
                        rows_end.append(i+1)
                    for i in range(m):
                        col_start.append(i+1)
                    for i in range(1, m):
                        col_end.append(i+1)
                self.row_stx = ttk.Combobox(Data_window, values=rows_start, width=10, font=('Times New Roman', 15))
                self.row_stx.set('1')
                self.row_stx.grid( row = 3, column = 1,  sticky='w', ipadx=1, ipady=1)
                self.row_endx = ttk.Combobox(Data_window, values=rows_end, width=10, font=('Times New Roman', 15))
                self.row_endx.set(str(max(rows_end)))
                self.row_endx.grid( row = 3, column = 2,  sticky='w', ipadx=1, ipady=1)
                self.col_stx = ttk.Combobox(Data_window, values=col_start, width=10, font=('Times New Roman', 15))
                self.col_stx.set('1')
                self.col_stx.grid( row = 4, column = 1,  sticky='w', ipadx=1, ipady=1)
                self.col_endx = ttk.Combobox(Data_window, values=col_end, width=10, font=('Times New Roman', 15))
                self.col_endx.set(str(max(col_end)))
                self.col_endx.grid( row = 4, column = 2, sticky='w', ipadx=1, ipady=1)
                self.row_sty = ttk.Combobox(Data_window, values=rows_start, width=10, font=('Times New Roman', 15))
                self.row_sty.set('1')
                self.row_sty.grid( row = 3, column = 3,  sticky='w', ipadx=1, ipady=1)
                self.row_endy = ttk.Combobox(Data_window, values=rows_end, width=10, font=('Times New Roman', 15))
                self.row_endy.set(str(max(rows_end)))
                self.row_endy.grid( row = 3, column = 4,  sticky='w', ipadx=1, ipady=1)
                self.col_sty = ttk.Combobox(Data_window, values=col_start, width=10, font=('Times New Roman', 15))
                self.col_sty.set(str(max(col_end)))
                self.col_sty.grid( row = 4, column = 3,  sticky='w', ipadx=1, ipady=1)
                self.col_endy = ttk.Combobox(Data_window, values=col_end, width=10, font=('Times New Roman', 15))
                self.col_endy.set(str(max(col_end)))
                self.col_endy.grid( row = 4, column = 4, sticky='w', ipadx=1, ipady=1)
                ttk.Button(Data_window, text = "Load data", command = lambda:self.get_data(), style='my.TButton').grid(row = 5, column=0, ipadx=1, ipady=1, sticky='e') 
            else:
                Data_window.destroy()
        def data_loading(self):
            raise_above_all(Data_window)
            self.xl_path = select_infile(filt=['.xlsx', '.xls', 'csv'], title='Select excel file')
            if len(self.xl_path)>0:
                speak('please wait for loading excel file')
                ttk.Label(Data_window, text=self.xl_path, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1, columnspan=4, ipadx=1, ipady=1, sticky='w')
                rows_start=[]
                rows_end=[]
                col_start=[]
                col_end=[]
                if  self.xl_path.endswith('.xls') or self.xl_path.endswith('.xlsx'):
                    self.sh_names=ttk.Label(Data_window, text='Sheet name', style="BW.TLabel", font=('Times New Roman', 15))
                    self.sh_names.grid(row=1, column=0,ipadx=5, ipady=5)
                    self.workbook = xlrd.open_workbook(self.xl_path,"rb")
                    sheets=self.workbook.sheet_names()
                    self.sh_nam = ttk.Combobox(Data_window, values=sheets, width=15, font=('Times New Roman', 15))
                    self.sh_nam.set(sheets[0])
                    self.sh_nam.grid( row = 1, column = 1, sticky='ew', columnspan=2)
                    sh = self.workbook.sheet_by_name(sheets[0])
                    for i in range(sh.nrows):
                        rows_start.append(i+1)
                    for i in range(1, sh.nrows):
                        rows_end.append(i+1)
                    for i in range(sh.ncols):
                        col_start.append(i+1)
                    for i in range(1, sh.ncols):
                        col_end.append(i+1)
                if  self.xl_path.endswith('.csv') :
                    try:
                        self.sh_nam.destroy()
                    except:
                        pass
                    try:
                        self.sh_names.destroy()
                    except:
                        pass
                    self.df = pd.read_csv(self.xl_path)
                    n,m = self.df.shape
                    for i in range(n):
                        rows_start.append(i+1)
                    for i in range(1, n):
                        rows_end.append(i+1)
                    for i in range(m):
                        col_start.append(i+1)
                    for i in range(1, m):
                        col_end.append(i+1)
                self.row_stx = ttk.Combobox(Data_window, values=rows_start, width=10, font=('Times New Roman', 15))
                self.row_stx.set('1')
                self.row_stx.grid( row = 3, column = 1,  sticky='w', ipadx=1, ipady=1)
                self.row_endx = ttk.Combobox(Data_window, values=rows_end, width=10, font=('Times New Roman', 15))
                self.row_endx.set(str(max(rows_end)))
                self.row_endx.grid( row = 3, column = 2,  sticky='w', ipadx=1, ipady=1)
                self.col_stx = ttk.Combobox(Data_window, values=col_start, width=10, font=('Times New Roman', 15))
                self.col_stx.set('1')
                self.col_stx.grid( row = 4, column = 1,  sticky='w', ipadx=1, ipady=1)
                self.col_endx = ttk.Combobox(Data_window, values=col_end, width=10, font=('Times New Roman', 15))
                self.col_endx.set(str(max(col_end)))
                self.col_endx.grid( row = 4, column = 2, sticky='w', ipadx=1, ipady=1)
                self.row_sty = ttk.Combobox(Data_window, values=rows_start, width=10, font=('Times New Roman', 15))
                self.row_sty.set('1')
                self.row_sty.grid( row = 3, column = 3,  sticky='w', ipadx=1, ipady=1)
                self.row_endy = ttk.Combobox(Data_window, values=rows_end, width=10, font=('Times New Roman', 15))
                self.row_endy.set(str(max(rows_end)))
                self.row_endy.grid( row = 3, column = 4,  sticky='w', ipadx=1, ipady=1)
                self.col_sty = ttk.Combobox(Data_window, values=col_start, width=10, font=('Times New Roman', 15))
                self.col_sty.set(str(max(col_end)))
                self.col_sty.grid( row = 4, column = 3,  sticky='w', ipadx=1, ipady=1)
                self.col_endy = ttk.Combobox(Data_window, values=col_end, width=10, font=('Times New Roman', 15))
                self.col_endy.set(str(max(col_end)))
                self.col_endy.grid( row = 4, column = 4, sticky='w', ipadx=1, ipady=1)
                ttk.Button(Data_window, text = "Load data", command = lambda:self.get_data(), style='my.TButton').grid(row = 5, column=0, ipadx=1, ipady=1, sticky='e') 
        def get_data(self):
            self.statusbar['text']=('Loading data.....')
            if  self.xl_path.endswith('.xls') or self.xl_path.endswith('.xlsx'):
                sh = self.workbook.sheet_by_name(self.sh_nam.get())
                self.X_data = []
                rstx=int(self.row_stx.get())-1
                rex=int(self.row_endx.get())
                cstx=int(self.col_stx.get())-1
                cex=int(self.col_endx.get())
                if rstx>0:
                    self.y_label=sh.row_values(rstx-1)[cstx:cex]
                else:
                    self.y_label=[]
                if cstx>0:
                    self.x_label=sh.col_values(cstx-1)[rstx:rex]
                else:
                    self.x_label=[]
                for rownum in range(rstx,rex):
                    row_valaues = sh.row_values(rownum)
                    self.X_data.append(row_valaues[cstx:cex])
                self.X_data=np.asarray(self.X_data)
                self.Y_data = []
                rsty=int(self.row_sty.get())-1
                rey=int(self.row_endy.get())
                csty=int(self.col_sty.get())-1
                cey=int(self.col_endy.get())
                for rownum in range(rsty,rey):
                    row_valaues = sh.row_values(rownum)
                    self.Y_data.append(row_valaues[csty:cey])
                self.Y_data=np.asarray(self.Y_data)
            if  self.xl_path.endswith('.csv'):
                rstx=int(self.row_stx.get())-1
                rex=int(self.row_endx.get())
                cstx=int(self.col_stx.get())-1
                cex=int(self.col_endx.get())
                self.X_data =np.asarray(self.df.iloc[rstx:rex, cstx:cex])
                rsty=int(self.row_sty.get())-1
                rey=int(self.row_endy.get())
                csty=int(self.col_sty.get())-1
                cey=int(self.col_endy.get())
                self.Y_data =np.asarray(self.df.iloc[rsty:rey, csty:cey])
                self.y_label=self.df.columns[cstx:cex]
                self.x_label=self.df.iloc[rstx:rex, (cstx-1)]
            if self.X_data.shape[0]>1:
                for _ in range(5):
                    self.reductionMenu.delete(0)
                for _ in range(2):
                    self.DataPreprocessing.delete(0)
                self.reductionMenu.add_command(label="CFS", command = lambda:wavelength_CFS(self.xl_path, self.X_data, self.y_label, self.Y_data), font=('Times New Roman', 15))       
                self.reductionMenu.add_command(label="PCA", command = lambda:pca_cal(self.xl_path, self.X_data, self.Y_data, self.statusbar, self.sh_nam.get()), font=('Times New Roman', 15))       
                self.reductionMenu.add_command(label="SFS", command = lambda:sfs(self.xl_path, self.X_data, self.Y_data, self.statusbar, self.y_label, self.sh_nam.get()), font=('Times New Roman', 15))
                self.reductionMenu.add_command(label="GA", command = lambda:gen(self.xl_path, self.X_data, self.Y_data, self.statusbar, self.y_label, self.sh_nam.get()), font=('Times New Roman', 15))       
                self.reductionMenu.add_command(label="VI select", command = lambda:VI_bandselection(self.xl_path, self.X_data, self.y_label, self.Y_data, self.statusbar), font=('Times New Roman', 15))       
                self.DataPreprocessing.add_command(label="Remove outliers", command =lambda:self.outliers_remove(), font=('Times New Roman', 15)) 
                self.DataPreprocessing.add_command(label="Correlation", command = lambda:WavelengthCorr(self.xl_path, self.X_data, self.y_label, self.Y_data), font=('Times New Roman', 15))       
                split_perc=list(range(5, 55))
                self.Split_Perc = ttk.Combobox(Data_window, values=split_perc, width=10, font=('Times New Roman', 15))
                try:
                    self.Split_Perc.set(str(int(self.perc*100)))
                except:
                    self.Split_Perc.set('10')
                self.Split_Perc.grid( row = 5, column = 3,  sticky='w', ipadx=1, ipady=1)
                def data_normalized1(X_data):
                    self.X_data=StandardScaler().fit(X_data.T).transform(X_data.T).T
                    speak('The data have been Standardized')
                    self.statusbar['text']=('The data have been STD_normalized')
                def data_normalized2(X_data):
                    self.X_data=MinMaxScaler().fit(X_data.T).transform(X_data.T).T
                    speak('The data have been normalized')
                    self.statusbar['text']=('The data have been Min Max normalized')
                ttk.Button(Data_window, text = "Standardize", command = lambda:data_normalized1(self.X_data), style='my.TButton').grid(row = 6, column=0, ipadx=1, ipady=1, sticky='e') 
                ttk.Button(Data_window, text = "Normalize", command = lambda:data_normalized2(self.X_data), style='my.TButton').grid(row = 6, column=2, ipadx=1, ipady=1, sticky='w') 
                ttk.Button(Data_window, text = "Split data", command = lambda:self.Split_Data(), style='my.TButton').grid(row = 5, column=2, ipadx=1, ipady=1, sticky='w') 
                speak('The data have been loaded')
                self.statusbar['text']=('The data have been loaded')
                try:
                    check_classification_targets(self.Y_data) # for classification
                    labels=np.unique(self.Y_data)
                    LabelNames=[]
                    for L in labels:
                        h=np.where(self.Y_data==L)
                        h=np.asarray(h)
                        self.x_label=np.asarray(self.x_label)
                        Label_Names=np.unique(self.x_label[h[0].astype(int)])
                        for name in Label_Names:
                            LabelNames.append(name)
                    self.LabelNames=np.asarray(LabelNames)
                except:
                    self.LabelNames=[]
                    pass
        def outliers_remove(self):
            self.X_data,self.Y_data=Remove_Outliers(self.xl_path, self.X_data,self.Y_data, self.x_label, self.y_label, self.statusbar, self.sh_nam.get())            
        def Split_Data(self):
            self.statusbar['text']=('Splitting data.....')
            self.perc=int(self.Split_Perc.get())/100
            X_train, X_test,  Y_train, Y_test=split_data(self.X_data,self.Y_data,self.perc)
            y_train, y_test=Y_train.reshape(-1, 1), Y_test.reshape(-1, 1)
            if X_train.shape[0]>1:
                speak('The data have been splited')
                self.statusbar['text']=('The data have been splited')
                for _ in range(5):
                    self.classMenu.delete(0)
                for _ in range(5):
                    self.RegMenu.delete(0)
                self.classMenu.add_command(label='RF', command = lambda:RFC_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.LabelNames, self.sh_nam.get()), font=('Times New Roman', 15))
                self.classMenu.add_command(label='KNN', command = lambda:KNN_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.LabelNames, self.sh_nam.get()), font=('Times New Roman', 15))
                self.classMenu.add_command(label='SVM', command = lambda:SVMC_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.LabelNames, self.sh_nam.get()), font=('Times New Roman', 15))
                self.classMenu.add_command(label='LDA', command = lambda:LDA_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.LabelNames, self.sh_nam.get()), font=('Times New Roman', 15))
                self.classMenu.add_command(label='BPNN', command = lambda:BPNNC_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.LabelNames, self.sh_nam.get()), font=('Times New Roman', 15))
                self.RegMenu.add_command(label='RF', command = lambda:RFR_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.sh_nam.get()),  font=('Times New Roman', 15))
                self.RegMenu.add_command(label='PLSR', command = lambda:pls_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.sh_nam.get(), self.X_data, self.Y_data, self.y_label), font=('Times New Roman', 15))
                self.RegMenu.add_command(label='SVM', command = lambda:SVMR_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.sh_nam.get()), font=('Times New Roman', 15))
                self.RegMenu.add_command(label="BPNN", command = lambda:BPNNR_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.sh_nam.get()), font=('Times New Roman', 15))
                self.RegMenu.add_command(label="MLR", command = lambda:MLR_cal(self.xl_path, X_train, X_test,  y_train, y_test, self.statusbar, self.sh_nam.get()), font=('Times New Roman', 15))
            Data_window.mainloop()
    Data_window = tkinter.Tk()
    gui = GUI(Data_window)
    Data_window.mainloop()
#%% imported and run project
def run_prj():
    prj_window=tkinter.Tk()
    prj_window.configure(background='lightyellow', highlightthickness=3, highlightbackground="black")
    s = ttk.Style(prj_window)
    s.configure('my.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
    prj_window.wm_iconbitmap('DAAI logo.ico')
    prj_window.title("Run project")
    prj_window.resizable(0, 0)
    prj_window.deiconify()
    raise_above_all(prj_window)
    ttk.Entry(prj_window,  width = 70, font=("Tahoma bold", 10)).grid( row = 0, column = 1,  columnspan=3, padx=2, pady=2, sticky='ew') # this is placed in 0 1
    statusbar = tkinter.Label(prj_window,text="Contact us: a.elmanawy_90@agr.suez.edu.eg",bd=1,relief=tkinter.SUNKEN,font='Tahoma 10 bold', bg='LightYellow2')
    statusbar.grid(row=7,column=0,columnspan=6, rowspan=2, sticky='ew')
    statusbar.config(width="70",anchor="w")           
    def import_prj():
        prj_path=select_infile(filt=['.py'], title="Select the project's file")
        if prj_path.endswith('.py'):
            exec(open(prj_path).read())
            statusbar['text']='The project run'
            ttk.Label(prj_window, text=prj_path, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1,  columnspan=3, padx=2, pady=2, sticky='ew')
            def import_img():
                types=Type()
                img_path = select_infile(filt=[types], title='Select HSI file')
                ttk.Label(prj_window, text=img_path, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1,  columnspan=3, padx=2, pady=2, sticky='ew')
                hypercube=analysis_img(img_path, statusbar)
                my_path='/'.join(img_path.split('/')[:-1])
                img_rgb=cv2.imread(my_path+'/1.tiff', 1)
                canvas_frame=tkinter.LabelFrame(prj_window, bg='lightyellow', bd=0)
                canvas_frame.grid(row=5, column=0, columnspan=4, sticky='w')
                fig = matplotlib.figure.Figure(figsize=(3,2), tight_layout=True, dpi=300, facecolor='lightyellow')
                ax = fig.add_subplot(1,1,1)
                ax.imshow(img_rgb)
                ax.set_yticks([])
                ax.set_xticks([])
                ax.set_title('Color image' , fontsize=5)
                canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
                canvas.get_tk_widget().grid(row = 0, column=0)
                canvas.draw()
                def run_model():
                    path_model = select_infile(filt='.sav', title="Select model's file")
                    ttk.Label(prj_window, text=path_model, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1,  columnspan=3, padx=2, pady=2, sticky='ew')
                    loaded_model = pickle.load(open(path_model, 'rb'))
                    if len(hypercube.shape)>2:
                        Data_cube2D=hypercube.reshape((hypercube.shape[0]*hypercube.shape[1]),hypercube.shape[2])
                    elif len(hypercube.shape)>2:
                        Data_cube2D=hypercube.reshape((hypercube.shape[0]*hypercube.shape[1]),1)
                    try:
                        Results=loaded_model.predict(Data_cube2D)
                        Results=np.asarray(Results)
                        b=int(hypercube.shape[2]/2)
                        h,w=np.where(hypercube[:,:,b]==0)
                        result_2D=Results.reshape(hypercube.shape[0], hypercube.shape[1])
                        result_2D=remove_Outliers(result_2D, 2)
                        try:
                            check_classification_targets(Results)
                            result_2D[h,w]=-2
                            plot_contour(result_2D, -1, int(np.amax(result_2D)+1), canvas_frame, 'Classification result', img_path, 'class result', (2,2), 'lightyellow')
                        except:
                            result_2D[h,w]=0
                            plot_contour(result_2D, 0, 0, canvas_frame, 'Regression result', img_path, 'Reg result', (3,2), 'lightyellow')
                    except Exception as e:
                        statusbar['text']=e
                        print(e)
                ttk.Button(prj_window, text='Analysis by model', width=20,command=lambda:run_model(), style='my.TButton').grid( row = 1, column = 2, padx=5, pady=2, sticky='new')
            def batch_img():
                types=Type()
                img_path = select_infile(filt=[types], title='Select HSI file')
                ttk.Label(prj_window, text=img_path, width = 70, background='white', font=('Times New Roman', 15)).grid( row = 0, column = 1,  columnspan=3, padx=2, pady=2, sticky='ew')
                MY_PATH=img_path.split('/')
                Path='/'.join(MY_PATH[:-1])
                In_File=[]
                for File in os.listdir(Path):
                    if File.endswith(types):
                        Name, ext = os.path.splitext(File)
                        In_File.append(Name)
                for infile in In_File:
                    analysis_img((Path+'/'+infile+types), statusbar)
            def run_models():
                speak('First click Analysis single image button')
                statusbar['text']='Click "Analysis single image" button first'
            ttk.Button(prj_window, text='Analysis single image', width=20, command= lambda:import_img(), style='my.TButton').grid( row = 1, column = 1, padx=5, pady=2, sticky='new')
            ttk.Button(prj_window, text='Analysis batch of images', width=20, command= lambda:batch_img(), style='my.TButton').grid( row = 1, column = 3, padx=5, pady=2, sticky='new')
            ttk.Button(prj_window, text='Analysis by model',  width=20, command=lambda:run_models(), style='my.TButton').grid( row = 1, column = 2, padx=5, pady=2, sticky='new')
        else:
            speak('Cannot run this file')
    ttk.Button(prj_window, text='Import project', command=import_prj, style='my.TButton').grid( row = 0, column = 0, padx=5, pady=2, sticky='new')
    prj_window.mainloop()
#%% software main window
main_window=tkinter.Tk()
s = ttk.Style(main_window)
s.configure('BW.TButton', font=('Times New Roman', 15), bd=1, relief='raised')
greatMe()
main_window.configure(background='white', highlightthickness=3, highlightbackground="black")
main_window.wm_iconbitmap('DAAI logo.ico')
main_window.title("HSI_PP")
main_window.resizable(False, False) # this prevents from resizing the window
main_window.deiconify()
raise_above_all(main_window)
ttk.Button(main_window, text = "HSI analysis", width=20, command=HSI_analysis, style='BW.TButton').grid( row = 2, column = 0, padx=5, pady=2, sticky='new')
ttk.Button(main_window, text = "Data analysis", width=20, command=Data_analysis, style='BW.TButton').grid( row = 3, column = 0,  padx=5, pady=2, sticky='new')
ttk.Button(main_window, text = "Import project", width=20,  command=run_prj, style='BW.TButton').grid( row = 4, column = 0,  padx=5, pady=2, sticky='new')
root_gif=ttk.Frame(main_window)
root_gif.grid(row = 1, column=0)
open_gif(root_gif)
main_window.mainloop()
import PIL.ImageTk
import PIL.Image
from tkinter import *
from tkinter import messagebox
from playsound import playsound
import cv2 as cv 
import constants as c
import numpy as np
import time
import threading
import random

# IMPORTANT TO INSTALL SPECIFIC VERSION OF playsound
# pip install playsound==1.2.2

cap = cv.VideoCapture(0)
waterm = cv.imread(c.watermark)

#### FUNCTIONS ####

def adjust(x):
    pass

def play_audio(sound):
    threading.Thread(target=playsound, args=(sound,), daemon=True).start()

def start_counting_frames(seconds, frame_count, checking_for_motion, is_alive):
    if not is_alive:
        return np.nan, checking_for_motion
    frames_to_wait = seconds * c.frame_rate
    # print(frame_count, frames_to_wait)
    if frame_count > frames_to_wait:
        return 0, not checking_for_motion
    else:
        return frame_count + 1, checking_for_motion
    
def apply_watermark(original, waterm, frame):
    (img_height, img_width) = original.shape[:2]
    (w_height, w_width) = waterm.shape[:2]

    #base image
    h1 = img_height
    w1 = img_width
    #watermark image
    h2 = w_height
    w2 = w_width
    #base image midpoints
    h_mid = int(h1/2)
    w_mid = int(w1/2)
    #coordinates to place watermark in center
    px = w_mid-int(w2/2)
    py = h_mid-int(h2/2)
    # add a mr.increadible watermark
    watermark = np.zeros((img_height, img_width, 3), dtype='uint8')
    watermark[py:h2+py, px:w2+px] = waterm
    # Combining the two images
    return cv.addWeighted(frame, 0.5, watermark, 0.5, 0)

def play_game():
    window.destroy()

    # setup multiples array
    multiples_arr = []
    for i in range(c.frame_rate, (c.frame_rate * c.wait_seconds)+1, c.frame_rate):
        multiples_arr.append(i)
    # set initial variables
    is_alive = True
    is_checking_for_motion = False
    frames_counted = 1
    seconds_in_frame = 1
    font_color = c.green
    cont_area = c.start_area
    min_area = c.min_contour_area
    points = 0
    death_sound_played_once = False
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    iter = 0
    erode_count = 0
    _, frame = cap.read()

    while True:
        _, second = cap.read()
        original = second.copy()
        motion_frame = second.copy()

        # process frame difference until thresholding, contour detection only when checking for motion
        diff = cv.absdiff(second, frame)
        gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
        # can add trackbar to edit hardcoded 25
        _, th = cv.threshold(gray, 25, 255, cv.THRESH_BINARY)
        
        # recheck code below if we need second return value
        frames_counted, is_checking_for_motion = start_counting_frames(c.wait_seconds, frames_counted, is_checking_for_motion, is_alive)

        if frames_counted in multiples_arr:
            # change number printed in frame
            seconds_in_frame = int(frames_counted/c.frame_rate)
        if frames_counted == c.wait_seconds * c.frame_rate:
            # print('switching time')
            # change color of font
            if is_checking_for_motion:
                font_color = c.green
                points += 1
                # decrease area by half or stop at minimum allowable
                if int(cont_area/2) < min_area:
                    cont_area = min_area
                else:
                    cont_area = int(cont_area/2)
                print(f'Area is now {cont_area}')
                play_audio(c.point)
                
            else:
                font_color = c.red
                # play_audio(random.choice(c.red_arr))

        # perform contour detection only when you are checking for motion
        # print(is_checking_for_motion)
        # if is_checking_for_motion:
            # change playing audio
            # detect motion
        contours, heir = cv.findContours(th, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        for cont in contours:
            if cv.contourArea(cont) > cont_area:
                (x,y,w,h) = cv.boundingRect(cont)
                if is_checking_for_motion:
                    is_alive = False
                    if death_sound_played_once == False:
                        play_audio(c.sound)
                        death_sound_played_once = True
                cv.rectangle(motion_frame, (x,y),(x+w,y+h),font_color, 2)

        if not is_alive:
            original = apply_watermark(original, waterm, frame)
            gray_original = cv.cvtColor(original, cv.COLOR_BGR2GRAY)
            original = cv.merge((gray_original, gray_original, gray_original))
            original = cv.putText(original, c.dead, c.coordinates, c.font, c.font_scale, c.red, 2, cv.LINE_AA)
            # iter = cv.getTrackbarPos('iter', 'Trackbar')
            if erode_count < c.frame_rate:
                erode_count += 1
            else:
                erode_count = c.frame_rate

            if erode_count == 60:
                #start iterating through erosion after 1 second of frames
                if iter < c.iter_max:
                    iter += 1
                else:
                    iter = c.iter_max

            original = cv.dilate(original, kernel, iterations=iter)

        else:
            original = cv.putText(original, str(c.wait_seconds - seconds_in_frame), c.coordinates, c.font, c.font_scale, font_color, 2, cv.LINE_AA)
            if is_checking_for_motion:
                original = cv.putText(original, c.dont_move_text, c.dmt_coordinates, c.font, c.font_scale, font_color, 2, cv.LINE_AA)
            else:
                original = cv.putText(original, '', c.dmt_coordinates, c.font, c.font_scale, font_color, 2, cv.LINE_AA)

        all = np.hstack((original, motion_frame))
        cv.imshow('', all)

        frame = second.copy()

        if cv.waitKey(5) == ord("x"):
            break

    messagebox.showinfo(title="RIPP", message=f"Your Score is {points}")


###################

#### MAIN AND UI ####

window = Tk()
window.title('MOVEMENT DETECTION GAME')
window.config(padx=50, pady=50)
canvas = Canvas(height=200, width=200)
canvas.grid(row=2, column=0)
image = PIL.Image.open(c.window_img)
photo = PIL.ImageTk.PhotoImage(image)
label = Label(image = photo)
label.image = photo
label.grid(row=0, column=0)
go_button = Button(text="Go", command=play_game, width=20)
go_button.grid(row=1, column=0)
username_label = Label(text=
    "HOW TO PLAY:\n-can move when green\n-dont move when red\n-get points when you dont die...\n-allowable movement gets smaller per round :)\n-press 'X' in keyboard to leave game"
)
username_label.grid(row=2, column=0, columnspan=1)

window.mainloop()

cap.release()
cv.destroyAllWindows()

#####################

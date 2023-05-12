import cv2 as cv

red = (0,0,255)
green = (0,255,0)
dead = 'WASTED'
coordinates = (100,100)
font = cv.FONT_HERSHEY_COMPLEX
font_scale = 3
frame_rate = 60
wait_seconds = 5
watermark = 'mi.jpg'
window_img = 'tuco.jpg'
sound = 'gg.mp3'
point = 'point.mp3'
# red_arr = ['1.mp3', '2.mp3', '3.mp3', '4.mp3']
red_arr = ['1.mp3']
min_contour_area = 25
start_area = 800
iter_max = 30
dont_move_text = 'DONT MOVE!'
dmt_coordinates = (25,400)
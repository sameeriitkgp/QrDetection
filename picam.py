#!/usr/bin/python

from time import sleep
import picamera
import io
import cv2
import numpy as np
import zbar
from PIL import Image

def cam_setup():
    cam = picamera.PiCamera()
    cam.hflip = True
    cam.vflip = True
    cam.start_preview()
    cam.preview_fullscreen = True
    sleep(2) # Camera setup delay
    return cam

def process_stream(stream):
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY, dstCn=0)
    pil = Image.fromarray(gray)
    width, height = pil.size
    raw = pil.tostring()
    image = zbar.Image(width, height, 'Y800', raw)
    return image

def scan(camera, stream, scanner):
    camera.capture(stream, format='jpeg', use_video_port=True)
    image = process_stream(stream)
    scanner.scan(image)
    for symbol in image:
        if symbol.data != "None":
            print symbol.data # qr code data
            print symbol.location # pixel values of contour surrounding the qr code
    
    stream.seek(0)
    stream.truncate()

def main():
    stream = io.BytesIO()
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    camera = cam_setup()

    while(True):
        scan(camera, stream, scanner)

    camera.stop_preview()
    camera.close()

if __name__ == '__main__':
    main()

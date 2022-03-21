#!/usr/bin/env python3
import cv2
import numpy as np
from matplotlib import pyplot as plt

color = {
	'blanco': (255,255,255),
	'negro': (0,0,0),
	'gris': (127,127,127),
	'rojo': (0,0,255),
	'verde': (35,150,25)
}

def contornos(img, c = 130):
	'''Obtiene los contornos del diente'''
	# converting image into grayscale image
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# setting threshold of gray image
	_, threshold = cv2.threshold(gray, c, 255, cv2.THRESH_BINARY)
	# using a findContours() function
	contours, _ = cv2.findContours(threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
	return contours


def process_fill(original, img, relleno = 'negro'):
	'''Pinta todo el diente del color relleno'''
	# Usa src (imagen transparente) y escribe sobre img (fondo blanco)
	cv2.fillPoly(img, pts = contornos(original), color = color[relleno])
	return img

def read_transparent(src):
	# https://stackoverflow.com/a/41896175
	image_4channel = cv2.imread(src, cv2.IMREAD_UNCHANGED)
	alpha_channel = image_4channel[:,:,3]
	rgb_channels = image_4channel[:,:,:3]

	# White Background Image
	white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255

	# Alpha factor
	alpha_factor = alpha_channel[:,:,np.newaxis].astype(np.float32) / 255.0
	alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

	# Transparent image rendered on white background
	base = rgb_channels.astype(np.float32) * alpha_factor
	white = white_background_image.astype(np.float32) * (1 - alpha_factor)
	final_image = base + white
	return final_image.astype(np.uint8)
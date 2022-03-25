#!/usr/bin/env python3
import cv2
import numpy as np

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


def recta_to_curva(puntos):
	'''Suaviza las líneas para que los ángulos sean curvos'''
	tension = 1
	n = 512
	# Duplicate first and last points
	_pts = puntos.tolist()
	_pts = [_pts[0]] + _pts + [_pts[1]]
	# Create new list and append curve points
	res = []
	for i in range(1, len(_pts) - 2):
		for t in range(n):
			# Calc tension vectors
			t1x = (_pts[i][0] - _pts[i - 1][0]) * tension
			t2x = (_pts[i + 1][0] - _pts[i][0]) * tension

			t1y = (_pts[i][1] - _pts[i - 1][1]) * tension
			t2y = (_pts[i + 1][1] - _pts[i][1]) * tension

			# Calc step
			st = t / n

			# Calc cardinals
			c1 = 2 * (st ** 3) - 3 * (st ** 2) + 1
			c2 = -(2 * (st ** 3)) + 3 * (st ** 2)
			c3 = (st ** 3) - 2 * (st ** 2) + st
			c4 = (st ** 3) - (st ** 2)

			# Calc x and y cords with common control vectors
			x = c1 * _pts[i][0] + c2 * _pts[i + 1][0] + c3 * t1x + c4 * t2x
			y = c1 * _pts[i][1] + c2 * _pts[i + 1][1] + c3 * t1y + c4 * t2y

			res.append([x, y])

	return [np.array(res, np.int32)]

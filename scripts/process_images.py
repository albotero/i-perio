#!/usr/bin/env python3
import cv2
import numpy as np

# Manejo del base64
from PIL import Image
import io
import base64

color = {
	'amarillo': (1, 216, 255),
	'blanco': (255,255,255),
	'gris': (145,145,145),
	'negro': (0,0,0),
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


def recta_to_curva(_pts, tension = .5):
	'''Suaviza las líneas para que los ángulos sean curvos'''
	n = 512
	# Duplicate first and last points
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

def zoom(img, zoom_factor: float, interpolation=cv2.INTER_CUBIC):
	'''Cambia el tamaño de la imagen por el factor especificado'''
	return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)

def dibujar_curva(imagen, color_linea, puntos, tension = .5):
	'''Amplía la imagen, dibuja la curva, y luego vuelve la imagen al tamaño original'''
	# Si no hay puntos para graficar la curva no modifica la imagen
	if puntos is None:
		return imagen

	cv2.polylines(
		imagen, recta_to_curva(puntos.tolist(), tension),
		isClosed = False, color = color[color_linea],
		thickness = 2, lineType = cv2.LINE_AA)

	return imagen

def dibujar_flecha(img, coord_a, coord_b, color_linea, thickness = 4, tipLength = 0.5):
	return cv2.arrowedLine(img, coord_a, coord_b, color[color_linea],
		thickness, tipLength = tipLength)

def frame(arr: np.ndarray):
    '''Pasa imágenes a str base64'''
    # Reverse colors BGR to RGB
    arr = arr[:,:,::-1]
    # Gets base64
    mem_bytes = io.BytesIO()
    img = Image.fromarray(arr)
    img.save(mem_bytes, 'JPEG')
    mem_bytes.seek(0)
    img_base64 = base64.b64encode(mem_bytes.getvalue()).decode('ascii')
    mime = "image/jpeg"
    uri = "data:%s;base64,%s"%(mime, img_base64)
    return uri

def actualizar_imagenes(canvas):
	'''Obtiene el base64 de las 4 imágenes'''
	for key in canvas.keys():
		try:
			canvas[key] = frame(canvas[key])
		except Exception as ex:
			print(ex)
	return canvas

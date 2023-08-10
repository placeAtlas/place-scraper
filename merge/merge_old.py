import os
from PIL import Image
import numpy
import cv2

images = []

for file_name in os.listdir():
	if not file_name.endswith('.png'):
		continue
	if not '-' in file_name:
		continue
	images.append(file_name.split('-')[1])
images = list(dict.fromkeys(images))

for image_name in images:
	# print(image_name)
	y0 = None
	x = 0
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y0 == None:
			y0 = img
		else:
			y0 = numpy.hstack((y0, img))
	x = 1
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y0 == None:
			y0 = img
		else:
			y0 = numpy.hstack((y0, img))
	x = 2
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y0 == None:
			y0 = img
		else:
			y0 = numpy.hstack((y0, img))
	
	y1 = None
	x = 3
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y1 == None:
			y1 = img
		else:
			y1 = numpy.hstack((y0, img))
	x = 4
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y1 == None:
			y1 = img
		else:
			y1 = numpy.hstack((y0, img))
	x = 5
	if os.path.isfile(f'{x}-{image_name}'):
		img = cv2.imread(f'{x}-{image_name}')
		if y1 == None:
			y1 = img
		else:
			y1 = numpy.hstack((y0, img))
	final = numpy.vstack((y0, y1))

	# print(image_name)

	cv2.imwrite(image_name, final)
import os
from PIL import Image

images = []

for file_name in os.listdir():
	if not file_name.endswith('.png'):
		continue
	if not '-' in file_name:
		continue
	print(file_name)
	images.append(file_name.split('-')[1])
images = list(dict.fromkeys(images))

def paste(x, y, n, image_name, canvas: Image):
	path = f'{n}-{image_name}'
	if os.path.isfile(path):
		img = Image.open(path)
		canvas.paste(img, (x * 1000, y * 1000))

canvas_width, canvas_height = 3000, 2000

for image_name in images:

	canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

	# print(image_name)

	paste(0, 0, 0, image_name, canvas)
	paste(1, 0, 1, image_name, canvas)
	paste(2, 0, 2, image_name, canvas)
	paste(0, 1, 3, image_name, canvas)
	paste(1, 1, 4, image_name, canvas)
	paste(2, 1, 5, image_name, canvas)

	for x in range(0, canvas_width, 500):
		for y in range(0, canvas_height, 500):
			region = canvas.crop((x, y, x + 500, y + 500))
			if all(pixel == (255, 255, 255, 255) for pixel in region.getdata()):
				for i in range(500):
					for j in range(500):
						canvas.putpixel((x + i, y + j), (0, 0, 0, 0))


	canvas.save(image_name)

	print(image_name)


from PIL import Image

# Open the three images
image1 = Image.open("image1.png")
image2 = Image.open("image2.png")
image3 = Image.open("image3.png")

# Determine the size of the new image (for example, the max width and total height)
# This can be adjusted based on your specific requirements.
new_width = max(image1.width, image2.width, image3.width)
new_height = image1.height + image2.height + image3.height

# Create a new image with a transparent background
new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

# Paste the images into the new image
new_image.paste(image1, (0, 0), image1)
new_image.paste(image2, (0, image1.height), image2)
new_image.paste(image3, (0, image1.height + image2.height), image3)

# Save or display the result
new_image.save("combined_image.png")
new_image.show()


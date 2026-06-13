from PIL import Image
import os

gif_path = "assets/gifs/idle.gif"
im = Image.open(gif_path)
im.seek(0)
frame = im.copy().convert("RGBA")

# Make it square by padding
width, height = frame.size
max_dim = max(width, height)
square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))

# Center the image
offset = ((max_dim - width) // 2, (max_dim - height) // 2)
square_img.paste(frame, offset)

# Ensure dimensions are powers of 2 for ico
final_img = square_img.resize((256, 256), Image.Resampling.LANCZOS)

final_img.save("assets/icon.ico", format="ICO")
print("Saved assets/icon.ico")

from PIL import Image, ImageDraw
import os

img_path = "/Users/huihui/.gemini/antigravity-ide/brain/2534282d-3b83-4ff5-903d-bd1015c04f31/agypet_logo_antigravity_1781341442283.png"
im = Image.open(img_path).convert("RGBA")

width, height = im.size
margin = int(width * 0.1)
im = im.crop((margin, margin, width - margin, height - margin))
width, height = im.size

mask = Image.new("L", (width, height), 0)
draw = ImageDraw.Draw(mask)
radius = int(width * 0.225)
draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
im.putalpha(mask)

im_64 = im.resize((64, 64), Image.Resampling.LANCZOS)
im_64.save("assets/tray_icon.png", format="PNG")
print("Saved masked assets/tray_icon.png")

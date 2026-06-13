from PIL import Image, ImageDraw
import os

img_path = "/Users/huihui/.gemini/antigravity-ide/brain/2534282d-3b83-4ff5-903d-bd1015c04f31/agypet_logo_antigravity_1781341442283.png"
im = Image.open(img_path).convert("RGBA")

# The generated image has a background. The icon itself is around the center.
# Let's crop it tightly to the rounded square icon.
# Or better yet, since it's an AI generated image, the "icon" is probably centered.
# Let's just create a generic rounded rectangle mask for the whole image (or a bit cropped).
width, height = im.size

# Let's crop the center 80% to remove the background border.
margin = int(width * 0.1)
im = im.crop((margin, margin, width - margin, height - margin))
width, height = im.size

# Create squircle mask
mask = Image.new("L", (width, height), 0)
draw = ImageDraw.Draw(mask)
# Apple uses continuous curvature, but a rounded rectangle with radius 22.5% of width is close enough
radius = int(width * 0.225)
draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

# Apply mask
im.putalpha(mask)

# Resize to 512x512
im_512 = im.resize((512, 512), Image.Resampling.LANCZOS)
im_512.save("assets/icon.icns", format="ICNS")

# Resize to 256x256 for ICO
im_256 = im.resize((256, 256), Image.Resampling.LANCZOS)
im_256.save("assets/icon.ico", format="ICO")

print("Generated new HD icons!")

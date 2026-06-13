import os
from PIL import Image, ImageDraw

def create_pixel_cat(filename, color, action="idle"):
    frames = []
    width, height = 48, 48
    
    # Simple animation logic with 4 frames
    for i in range(4):
        # Create a transparent image
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Base face
        draw.rounded_rectangle([10, 20, 38, 40], radius=6, fill=color)
        
        # Ears (Twitch when thinking)
        if action == "thinking" and i % 2 == 1:
            draw.polygon([(10, 20), (14, 14), (18, 20)], fill=color)
            draw.polygon([(30, 20), (34, 14), (38, 20)], fill=color)
        else:
            draw.polygon([(10, 20), (10, 10), (18, 20)], fill=color)
            draw.polygon([(38, 20), (38, 10), (30, 20)], fill=color)
            
        # Eyes
        if action == "idle" and i == 3: # blink
            draw.line([(16, 28), (20, 28)], fill="#1E1E2E", width=2)
            draw.line([(28, 28), (32, 28)], fill="#1E1E2E", width=2)
        elif action == "error":
            draw.line([(16, 26), (20, 30)], fill="#1E1E2E", width=2)
            draw.line([(16, 30), (20, 26)], fill="#1E1E2E", width=2)
            draw.line([(28, 26), (32, 30)], fill="#1E1E2E", width=2)
            draw.line([(28, 30), (32, 26)], fill="#1E1E2E", width=2)
        else:
            draw.ellipse([16, 26, 20, 30], fill="#1E1E2E")
            draw.ellipse([28, 26, 32, 30], fill="#1E1E2E")
            
        # Nose
        draw.polygon([(23, 32), (25, 32), (24, 34)], fill="#F38BA8")
        
        # Waiting bounce
        if action == "waiting":
            offset = 4 if i % 2 == 0 else 0
            # translate image
            temp = Image.new("RGBA", (width, height), (0,0,0,0))
            temp.paste(img, (0, offset))
            img = temp
            
        frames.append(img)
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Save GIF with transparency and disposal=2 to prevent smearing
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=300, loop=0, transparency=0, disposal=2)

if __name__ == "__main__":
    create_pixel_cat("assets/gifs/idle.gif", "#A6DA95", "idle")
    create_pixel_cat("assets/gifs/thinking.gif", "#8AADF4", "thinking")
    create_pixel_cat("assets/gifs/waiting.gif", "#EED49F", "waiting")
    create_pixel_cat("assets/gifs/error.gif", "#ED8796", "error")
    print("Generated 4 default pet GIFs in assets/gifs/")

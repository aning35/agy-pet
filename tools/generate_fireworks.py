import math
import random
import os
from PIL import Image, ImageDraw

def generate_fireworks(filename, num_frames=45, width=800, height=600):
    frames = []
    
    # 5 fireworks bursts
    bursts = []
    colors = [
        (255, 100, 100), # Red
        (100, 255, 100), # Green
        (100, 100, 255), # Blue
        (255, 255, 100), # Yellow
        (255, 100, 255)  # Magenta
    ]
    
    for i in range(5):
        cx = random.randint(width//4, width*3//4)
        cy = random.randint(height//4, height//2)
        color = random.choice(colors)
        particles = []
        for _ in range(100): # 100 particles per burst
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 15)
            particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 255
            })
        bursts.append({"color": color, "particles": particles, "delay": random.randint(0, 15)})
        
    for frame_idx in range(num_frames):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        
        for burst in bursts:
            if frame_idx < burst["delay"]: continue
            
            color = burst["color"]
            for p in burst["particles"]:
                if p["life"] > 0:
                    # Draw trail or glowing dot
                    alpha = int(max(0, p["life"]))
                    c = color + (alpha,)
                    r = max(1, p["life"] / 60.0)
                    
                    # Core
                    d.ellipse((p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r), fill=c)
                    
                    # Update physics
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.5 # gravity
                    p["life"] -= random.uniform(5, 12) # fade out randomly
                    
        frames.append(img)
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    print(f"Fireworks GIF generated at {filename}")

if __name__ == "__main__":
    generate_fireworks("assets/gifs/fireworks.gif")

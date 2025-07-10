from PIL import Image, ImageDraw, ImageFont
import os
import math # Import the math module for cos() and sin()

def generate_icons():
    """
    Generates various image assets (PNGs) for the GUI application with enhanced 3D/realistic effects.
    """
    # Define colors for enhanced aesthetics
    primary_blue = (40, 110, 200)
    dark_blue = (20, 70, 150)
    light_blue = (80, 150, 255)

    primary_orange = (230, 126, 34)
    dark_orange = (180, 90, 20)
    light_orange = (255, 160, 60)

    primary_green = (40, 180, 99)
    dark_green = (20, 140, 70)
    light_green = (80, 220, 130)

    text_color_white = (255, 255, 255)
    shadow_color = (0, 0, 0, 80) # Semi-transparent black for shadows
    highlight_color = (255, 255, 255, 100) # Semi-transparent white for highlights
    border_color_dark = (50, 50, 50)

    # Try to load a bold font, fall back to default
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 70)
        font_medium = ImageFont.truetype("arialbd.ttf", 20)
        font_small = ImageFont.truetype("arialbd.ttf", 14)
    except IOError:
        try:
            font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
            font_medium = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
            font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
        except IOError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()


    # Helper to draw a rectangle with a simple gradient
    def draw_gradient_rect(draw, bbox, color1, color2, radius, direction='vertical'):
        x0, y0, x1, y1 = bbox
        for i in range(int(y0), int(y1)):
            ratio = (i - y0) / (y1 - y0)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x0, i), (x1, i)], fill=(r, g, b))
        draw.rounded_rectangle(bbox, radius=radius, outline=border_color_dark, width=2)


    # --- App Icon (128x128) ---
    size = (128, 128)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Base shape with gradient and shadow
    draw.rounded_rectangle((5, 5, 123, 123), radius=30, fill=shadow_color) # Shadow
    draw_gradient_rect(draw, (0, 0, 120, 120), light_blue, primary_blue, 25) # Main body
    
    # Text "C"
    text = "C"
    text_bbox = draw.textbbox((0,0), text, font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size[0] - text_width) / 2 - 5
    text_y = (size[1] - text_height) / 2 - 10
    draw.text((text_x, text_y), text, font=font_large, fill=text_color_white, stroke_width=2, stroke_fill=(0,0,0,150))

    # Gear (settings hint)
    gear_center = (size[0] - 30, size[1] - 30)
    gear_radius = 18
    draw.ellipse((gear_center[0] - gear_radius, gear_center[1] - gear_radius,
                  gear_center[0] + gear_radius, gear_center[1] + gear_radius),
                 fill=primary_green, outline=text_color_white, width=2)
    # Simple gear teeth
    for angle in range(0, 360, 45):
        x1 = gear_center[0] + (gear_radius + 5) * math.cos(math.radians(angle))
        y1 = gear_center[1] + (gear_radius + 5) * math.sin(math.radians(angle))
        x2 = gear_center[0] + (gear_radius) * math.cos(math.radians(angle + 20))
        y2 = gear_center[1] + (gear_radius) * math.sin(math.radians(angle + 20))
        x3 = gear_center[0] + (gear_radius) * math.cos(math.radians(angle - 20))
        y3 = gear_center[1] + (gear_radius) * math.sin(math.radians(angle - 20))
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=text_color_white)

    img.save(f"app_icon.png")
    print(f"Generated app_icon.png")

    # --- Folder Icon (48x48) ---
    size = (48, 48)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Shadow for depth
    draw.rounded_rectangle((5, 15, 45, 45), radius=8, fill=shadow_color)

    # Folder tab
    draw_gradient_rect(draw, (8, 10, 25, 20), (255, 240, 180), (255, 220, 100), 5)
    
    # Folder body
    draw_gradient_rect(draw, (5, 15, 43, 43), (255, 230, 150), (255, 200, 80), 8)
    
    # Opening line
    draw.line([(10, 20), (38, 20)], fill=(150, 100, 0), width=2)
    img.save("folder_icon.png")
    print(f"Generated folder_icon.png")

    # --- Convert Icon (48x48) ---
    size = (48, 48)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Base rectangle for arrows
    draw.rounded_rectangle((5, 15, 43, 33), radius=8, fill=(70, 70, 70), outline=(100,100,100), width=2)
    
    # Left arrow
    draw.polygon([(10, 24), (20, 18), (20, 30)], fill=light_green, outline=dark_green, width=1)
    
    # Right arrow
    draw.polygon([(38, 24), (28, 18), (28, 30)], fill=light_blue, outline=dark_blue, width=1)
    
    # Connecting line for a sense of transformation
    draw.line([(20, 24), (28, 24)], fill=(150, 150, 150), width=2)

    img.save("convert_icon.png")
    print(f"Generated convert_icon.png")

    # --- Settings Icon (48x48) ---
    size = (48, 48)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    center = (size[0] // 2, size[1] // 2)
    outer_radius = 18
    inner_radius = 9
    tooth_width = 6
    tooth_height = 6

    # Shadow
    draw.ellipse((center[0] - outer_radius + 2, center[1] - outer_radius + 2,
                  center[0] + outer_radius + 2, center[1] + outer_radius + 2), fill=shadow_color)

    # Main gear body with gradient
    draw_gradient_rect(draw, (center[0] - outer_radius, center[1] - outer_radius,
                              center[0] + outer_radius, center[1] + outer_radius),
                       (180, 180, 180), (100, 100, 100), outer_radius)
    
    # Inner circle
    draw.ellipse((center[0] - inner_radius, center[1] - inner_radius,
                  center[0] + inner_radius, center[1] + inner_radius),
                 fill=(0,0,0,0), outline=text_color_white, width=2)
    
    # Gear teeth with highlights
    for angle in range(0, 360, 30):
        x = center[0] + (outer_radius + tooth_height // 2) * math.cos(math.radians(angle))
        y = center[1] + (outer_radius + tooth_height // 2) * math.sin(math.radians(angle))
        draw.rounded_rectangle((x - tooth_width // 2, y - tooth_width // 2,
                                x + tooth_width // 2, y + tooth_width // 2), radius=2, fill=text_color_white)
    
    img.save("settings_icon.png")
    print(f"Generated settings_icon.png")

    # --- Image Mode Icon (64x64) ---
    size = (64, 64)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Frame with shadow
    draw.rounded_rectangle((8, 18, 60, 60), radius=10, fill=shadow_color)
    draw_gradient_rect(draw, (5, 15, 57, 57), (255, 255, 255), (200, 200, 200), 8) # White frame
    
    # Mountain with depth
    draw.polygon([(15, 45), (30, 20), (45, 45)], fill=primary_green, outline=dark_green, width=2)
    draw.polygon([(30, 45), (40, 30), (50, 45)], fill=light_green, outline=primary_green, width=1) # Second mountain
    
    # Sun with glow
    draw.ellipse((45, 8, 55, 18), fill="yellow", outline="orange", width=2)
    draw.ellipse((46, 9, 54, 17), fill=(255, 255, 0, 150)) # Inner glow
    
    img.save("image_mode_icon.png")
    print(f"Generated image_mode_icon.png")

    # --- Video Mode Icon (64x64) ---
    size = (64, 64)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Film reel shape with shadow
    draw.rounded_rectangle((8, 18, 60, 48), radius=10, fill=shadow_color)
    draw_gradient_rect(draw, (5, 15, 57, 45), (150, 150, 150), (80, 80, 80), 8) # Film strip body
    
    # Play button triangle
    draw.polygon([(25, 20), (25, 40), (45, 30)], fill=primary_orange, outline=dark_orange, width=2)
    
    # Small circles for film holes
    for i in range(4):
        draw.ellipse((8, 18 + i*7, 12, 22 + i*7), fill=(50,50,50))
        draw.ellipse((50, 18 + i*7, 54, 22 + i*7), fill=(50,50,50))

    img.save("video_mode_icon.png")
    print(f"Generated video_mode_icon.png")

    # --- Audio Mode Icon (64x64) ---
    size = (64, 64)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Music note with depth
    draw.ellipse((15, 40, 25, 50), fill=primary_blue, outline=dark_blue, width=2) # Bottom note
    draw.ellipse((30, 30, 40, 40), fill=primary_blue, outline=dark_blue, width=2) # Top note
    draw.line([(20, 40), (20, 10)], fill=dark_blue, width=3) # Stem 1
    draw.line([(35, 30), (35, 10)], fill=dark_blue, width=3) # Stem 2
    draw.line([(20, 10), (35, 10)], fill=dark_blue, width=3) # Bar
    
    # Add a subtle shadow to the notes
    draw.ellipse((17, 42, 27, 52), fill=shadow_color)
    draw.ellipse((32, 32, 42, 42), fill=shadow_color)

    img.save("audio_mode_icon.png")
    print(f"Generated audio_mode_icon.png")

    # --- Quality Icon (32x32) ---
    size = (32, 32)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Star with gradient and shadow
    center_x, center_y = size[0] // 2, size[1] // 2
    points = [
        (center_x, center_y - 12), # Top
        (center_x + 5, center_y - 5), # Top-right
        (center_x + 12, center_y), # Right
        (center_x + 5, center_y + 5), # Bottom-right
        (center_x, center_y + 12), # Bottom
        (center_x - 5, center_y + 5), # Bottom-left
        (center_x - 12, center_y), # Left
        (center_x - 5, center_y - 5) # Top-left
    ]
    draw.polygon(points, fill="gold", outline="darkgoldenrod", width=2)
    draw.polygon([(p[0]+1, p[1]+1) for p in points], fill=shadow_color) # Simple shadow

    img.save("quality_icon.png")
    print(f"Generated quality_icon.png")

    # --- Rescale Icon (32x32) ---
    size = (32, 32)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    arrow_color = (100, 180, 255) # Light blue
    dark_arrow_color = (50, 100, 180)

    # Top-left corner arrow pointing out
    draw.line([(5, 5), (12, 5)], fill=arrow_color, width=3)
    draw.line([(5, 5), (5, 12)], fill=arrow_color, width=3)
    draw.polygon([(12, 5), (15, 8), (12, 11)], fill=arrow_color, outline=dark_arrow_color, width=1) # Arrowhead right
    draw.polygon([(5, 12), (8, 15), (11, 12)], fill=arrow_color, outline=dark_arrow_color, width=1) # Arrowhead down

    # Bottom-right corner arrow pointing in
    draw.line([(27, 27), (20, 27)], fill=arrow_color, width=3)
    draw.line([(27, 27), (27, 20)], fill=arrow_color, width=3)
    draw.polygon([(20, 27), (17, 24), (20, 21)], fill=arrow_color, outline=dark_arrow_color, width=1) # Arrowhead left
    draw.polygon([(27, 20), (24, 17), (21, 20)], fill=arrow_color, outline=dark_arrow_color, width=1) # Arrowhead up

    img.save("rescale_icon.png")
    print(f"Generated rescale_icon.png")

    # --- Video Quality Icon (32x32) ---
    size = (32, 32)
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Film strip with a star
    draw.rounded_rectangle((4, 8, 28, 24), radius=4, fill=(100, 100, 100), outline=(50,50,50), width=2) # Film strip body
    
    # Perforation holes
    for i in range(3):
        draw.ellipse((6, 10 + i*5, 8, 12 + i*5), fill="black")
        draw.ellipse((24, 10 + i*5, 26, 12 + i*5), fill="black")
    
    # Small star for quality
    star_center_x, star_center_y = 16, 16
    star_points = [
        (star_center_x, star_center_y - 6),
        (star_center_x + 2.5, star_center_y - 2.5),
        (star_center_x + 6, star_center_y),
        (star_center_x + 2.5, star_center_y + 2.5),
        (star_center_x, star_center_y + 6),
        (star_center_x - 2.5, star_center_y + 2.5),
        (star_center_x - 6, star_center_y),
        (star_center_x - 2.5, star_center_y - 2.5)
    ]
    draw.polygon(star_points, fill="gold", outline="darkgoldenrod", width=1)
    
    img.save("video_quality_icon.png")
    print(f"Generated video_quality_icon.png")


    print("\nAll application assets generated successfully!")
    print("You can now run 'media_converter_app.py' to launch the GUI.")

if __name__ == "__main__":
    generate_icons()

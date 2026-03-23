import os
from PIL import Image, ImageDraw, ImageFont

def load_font(size, bold=False):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    font_folder = os.path.join(CURRENT_DIR, "fonts")
    font_name = "Georgia-Bold.ttf" if bold else "Georgia.ttf"
    path = os.path.join(font_folder, font_name)
    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines

def generate_card(name, message, photo_path, event_type):
    event_type = event_type.lower().strip()
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

    CONFIG = {
        "birthday": {
            "template": "templates/birthday_template.png",
            "circle_cy_pct": 0.50, "circle_r_pct": 0.24, "name_y_pct": 0.70,
            "msg_gap": 0.07, "name_color": "white", "msg_color": "white",
            "border_color": "white", "uppercase": True
        },
        "anniversary": {
            "template": "templates/anniversary_template.png",
            "circle_cy_pct": 0.44, "circle_r_pct": 0.18, "name_y_pct": 0.68,
            "msg_gap": 0.06, "name_color": "#FFD700", "msg_color": "white",
            "border_color": "#F3E48D", "uppercase": False
        }
    }

    cfg = CONFIG.get(event_type, CONFIG["birthday"])
    template_path = os.path.join(PROJECT_ROOT, cfg["template"])

    # Load and Normalize
    template = Image.open(template_path).convert("RGBA")
    with Image.open(photo_path) as img:
        img.load() 
        photo = img.convert("RGBA")

    width, height = template.size
    draw = ImageDraw.Draw(template)

    # Circle Crop
    cx, cy = width // 2, int(height * cfg["circle_cy_pct"])
    r, size = int(width * cfg["circle_r_pct"]), int(width * cfg["circle_r_pct"]) * 2
    w_p, h_p = photo.size
    m = min(w_p, h_p)
    photo = photo.crop(((w_p-m)//2, (h_p-m)//2, (w_p+m)//2, (h_p+m)//2)).resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    photo.putalpha(mask)
    template.paste(photo, (cx - r, cy - r), photo)
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=cfg["border_color"], width=3)

    # Text
    name_font = load_font(int(width * 0.085), bold=True)
    msg_font = load_font(int(width * 0.034))
    name_text = name.upper() if cfg["uppercase"] else name.title()
    ny = int(height * cfg["name_y_pct"])
    draw.text(((width - draw.textbbox((0, 0), name_text, font=name_font)[2])//2, ny), name_text, fill=cfg["name_color"], font=name_font)

    lines = wrap_text(draw, message, msg_font, int(width * 0.75))
    my = ny + int(height * cfg["msg_gap"])
    for line in lines:
        draw.text(((width - draw.textbbox((0, 0), line, font=msg_font)[2])//2, my), line, fill=cfg["msg_color"], font=msg_font)
        my += int(height * 0.04)

    out_path = os.path.join(PROJECT_ROOT, "generated_cards", f"{name.replace(' ', '_')}_{event_type}.png")
    template.save(out_path)
    return out_path


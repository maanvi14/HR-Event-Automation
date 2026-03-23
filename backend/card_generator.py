import os
from PIL import Image, ImageDraw, ImageFont

# ================= UTILS =================
def load_font(size, bold=False):
    # Path relative to this file: backend/fonts/
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    font_folder = os.path.join(CURRENT_DIR, "fonts")
    
    font_name = "Georgia-Bold.ttf" if bold else "Georgia.ttf"
    path = os.path.join(font_folder, font_name)

    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

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

# ================= GENERATOR =================
def generate_card(name, message, photo_path, event_type, years=None):
    event_type = event_type.lower().strip()
    
    # Path Setup
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

    if not os.path.exists(template_path):
        raise Exception(f"Template missing: {template_path}")

    # Load Images
    template = Image.open(template_path).convert("RGBA")
    photo = Image.open(photo_path).convert("RGBA")
    width, height = template.size
    draw = ImageDraw.Draw(template)

    # Fonts
    name_font = load_font(int(width * 0.085), bold=True)
    msg_font = load_font(int(width * 0.034))

    # Process Photo (Circle Crop)
    cx, cy = width // 2, int(height * cfg["circle_cy_pct"])
    r = int(width * cfg["circle_r_pct"])
    size = r * 2

    w, h = photo.size
    m = min(w, h)
    photo = photo.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))
    photo = photo.resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    photo.putalpha(mask)
    template.paste(photo, (cx - r, cy - r), photo)
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=cfg["border_color"], width=3)

    # Text: Name
    name_text = name.upper() if cfg["uppercase"] else name.title()
    nw = draw.textbbox((0, 0), name_text, font=name_font)[2]
    ny = int(height * cfg["name_y_pct"])
    draw.text(((width - nw)//2, ny), name_text, fill=cfg["name_color"], font=name_font)

    # Text: Message
    lines = wrap_text(draw, message, msg_font, int(width * 0.75))
    my = ny + int(height * cfg["msg_gap"])
    for line in lines:
        mw = draw.textbbox((0, 0), line, font=msg_font)[2]
        draw.text(((width - mw)//2, my), line, fill=cfg["msg_color"], font=msg_font)
        my += int(height * 0.04)

    # Final Save
    out_dir = os.path.join(PROJECT_ROOT, "generated_cards")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{name.replace(' ', '_')}_{event_type}.png")
    template.save(out_path)
    
    return out_path


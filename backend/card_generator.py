import os
from PIL import Image, ImageDraw, ImageFont

# ================= FONT LOADER =================
def load_font(size, bold=False):
    # Absolute pathing for Render: /opt/render/project/src/backend/fonts/
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    font_folder = os.path.join(CURRENT_DIR, "fonts")
    
    font_name = "Georgia-Bold.ttf" if bold else "Georgia.ttf"
    path = os.path.join(font_folder, font_name)

    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    
    print(f"⚠️ Font not found at {path}, using default")
    return ImageFont.load_default()

# ================= TEXT WRAPPING =================
def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        # Use textbbox for modern PIL compatibility
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# ================= MAIN GENERATOR =================
def generate_card(name, message, photo_path, event_type, years=None):
    event_type = event_type.lower().strip()
    
    # Setup Base Paths
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

    CONFIG = {
        "birthday": {
            "template": "templates/birthday_template.png",
            "circle_cy_pct": 0.50, 
            "circle_r_pct": 0.24, 
            "name_y_pct": 0.70,
            "msg_gap": 0.07, 
            "name_color": "white", 
            "msg_color": "white",
            "border_color": "white", 
            "uppercase": True
        },
        "anniversary": {
            "template": "templates/anniversary_template.png",
            "circle_cy_pct": 0.44, 
            "circle_r_pct": 0.18, 
            "name_y_pct": 0.68,
            "msg_gap": 0.06, 
            "name_color": "#FFD700", 
            "msg_color": "white",
            "border_color": "#F3E48D", 
            "uppercase": False
        }
    }

    # Fallback to birthday if event_type is messy
    cfg = CONFIG.get(event_type, CONFIG["birthday"])
    template_path = os.path.join(PROJECT_ROOT, cfg["template"])

    # 1. VALIDATION
    if not os.path.exists(template_path):
        raise Exception(f"Template missing: {template_path}")
    if not os.path.exists(photo_path):
        raise Exception(f"Photo missing: {photo_path}")

    try:
        # 2. LOAD IMAGES
        template = Image.open(template_path).convert("RGBA")
        photo = Image.open(photo_path).convert("RGBA")
    except Exception as e:
        raise Exception(f"PIL failed to load images: {str(e)}")

    width, height = template.size
    draw = ImageDraw.Draw(template)

    # 3. FONTS
    name_font = load_font(int(width * 0.085), bold=True)
    msg_font = load_font(int(width * 0.034))
    
    # 4. PHOTO PROCESSING (CIRCLE CROP)
    cx = width // 2
    cy = int(height * cfg["circle_cy_pct"])
    r = int(width * cfg["circle_r_pct"])
    size = r * 2

    # Square crop the photo
    w_p, h_p = photo.size
    m = min(w_p, h_p)
    photo = photo.crop(((w_p - m)//2, (h_p - m)//2, (w_p + m)//2, (h_p + m)//2))
    photo = photo.resize((size, size), Image.LANCZOS)

    # Apply circular mask
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    photo.putalpha(mask)
    
    # Paste photo onto template
    template.paste(photo, (cx - r, cy - r), photo)
    
    # Draw border around circle
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=cfg["border_color"], width=3)

    # 5. DRAW NAME
    name_text = name.upper() if cfg["uppercase"] else name.title()
    nw = draw.textbbox((0, 0), name_text, font=name_font)[2]
    ny = int(height * cfg["name_y_pct"])
    draw.text(((width - nw)//2, ny), name_text, fill=cfg["name_color"], font=name_font)

    # 6. DRAW MESSAGE
    lines = wrap_text(draw, message, msg_font, int(width * 0.75))
    my = ny + int(height * cfg["msg_gap"])
    for line in lines:
        mw = draw.textbbox((0, 0), line, font=msg_font)[2]
        draw.text(((width - mw)//2, my), line, fill=cfg["msg_color"], font=msg_font)
        my += int(height * 0.04)

    # 7. SAVE FINAL CARD
    out_dir = os.path.join(PROJECT_ROOT, "generated_cards")
    os.makedirs(out_dir, exist_ok=True)
    
    # Sanitize filename
    safe_name = name.replace(" ", "_")
    out_path = os.path.join(out_dir, f"{safe_name}_{event_type}.png")
    
    template.save(out_path)
    print(f"✅ Card Generated: {out_path}")
    
    return out_path




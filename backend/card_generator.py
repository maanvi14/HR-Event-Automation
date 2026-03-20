from PIL import Image, ImageDraw, ImageFont
import os


# ================= FONT LOADER =================
def load_font(size, bold=False):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    if bold:
        font_paths = [
            os.path.join(BASE_DIR, "fonts", "Georgia-Bold.ttf"),
            os.path.join(BASE_DIR, "fonts", "Times-Bold.ttf")
        ]
    else:
        font_paths = [
            os.path.join(BASE_DIR, "fonts", "Georgia.ttf"),
            os.path.join(BASE_DIR, "fonts", "Times.ttf")
        ]

    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    print("⚠️ Font not found, using default")
    return ImageFont.load_default()


# ================= TEXT WRAP =================
def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""

    for w in words:
        test = (current + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w

    if current:
        lines.append(current)

    return lines


# ================= MAIN FUNCTION =================
def generate_card(name, message, photo_path, event_type, years=None):

    event_type = event_type.lower().strip()

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
            "uppercase": True,
            "draw_title": False
        },
        "anniversary": {
            "template": "templates/anniversary_template.png",
            "circle_cy_pct": 0.44,
            "circle_r_pct": 0.18,
            "title_y_pct": 0.18,
            "name_y_pct": 0.68,
            "msg_gap": 0.06,
            "name_color": "#FFD700",
            "msg_color": "white",
            "border_color": "#F3E48D",
            "uppercase": False,
            "draw_title": True
        }
    }

    if event_type not in CONFIG:
        raise ValueError("Invalid event type")

    cfg = CONFIG[event_type]

    # ================= PATH FIX (CRITICAL 🔥) =================
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

    template_path = os.path.join(PROJECT_ROOT, cfg["template"])

    print("📂 TEMPLATE PATH:", template_path)
    print("📂 TEMPLATE EXISTS:", os.path.exists(template_path))
    print("📂 PHOTO PATH:", photo_path)
    print("📂 PHOTO EXISTS:", os.path.exists(photo_path))

    if not os.path.exists(template_path):
        raise Exception("Template not found")

    if not os.path.exists(photo_path):
        raise Exception("Photo not found")

    # ================= LOAD IMAGES =================
    template = Image.open(template_path).convert("RGBA")
    photo = Image.open(photo_path).convert("RGBA")

    width, height = template.size
    draw = ImageDraw.Draw(template)

    # ================= FONTS =================
    name_font = load_font(int(width * 0.085), bold=True)
    msg_font = load_font(int(width * 0.034))
    title_font = load_font(int(width * 0.055), bold=True)

    max_w = int(width * 0.75)

    # ================= TITLE (ANNIVERSARY) =================
    if cfg["draw_title"]:
        years_text = f"{years} Year" if years else ""

        title_lines = [
            f"Happy {years_text}",
            "Work Anniversary!"
        ]

        ty = int(height * cfg["title_y_pct"])

        for line in title_lines:
            w = draw.textbbox((0, 0), line, font=title_font)[2]
            draw.text(((width - w)//2, ty), line, fill="#FFD700", font=title_font)
            ty += int(height * 0.06)

    # ================= PHOTO =================
    cx = width // 2
    cy = int(height * cfg["circle_cy_pct"])
    r = int(width * cfg["circle_r_pct"])
    size = r * 2

    w, h = photo.size
    m = min(w, h)
    photo = photo.crop(((w - m)//2, (h - m)//2, (w + m)//2, (h + m)//2))
    photo = photo.resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    photo.putalpha(mask)

    x = cx - r
    y = cy - r
    template.paste(photo, (x, y), photo)

    draw.ellipse((x, y, x + size, y + size), outline=cfg["border_color"], width=2)

    # ================= NAME =================
    name_text = name.upper() if cfg["uppercase"] else name.title()
    nw = draw.textbbox((0, 0), name_text, font=name_font)[2]
    ny = int(height * cfg["name_y_pct"])

    draw.text(((width - nw)//2, ny), name_text, fill=cfg["name_color"], font=name_font)

    # ================= MESSAGE =================
    lines = wrap_text(draw, message, msg_font, max_w)
    my = ny + int(height * cfg["msg_gap"])

    for line in lines:
        mw = draw.textbbox((0, 0), line, font=msg_font)[2]
        draw.text(((width - mw)//2, my), line, fill=cfg["msg_color"], font=msg_font)
        my += int(height * 0.04)

    # ================= SAVE =================
    out_dir = os.path.join(PROJECT_ROOT, "generated_cards")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"{name.replace(' ', '_')}_{event_type}.png")

    template.save(path)

    print("✅ GENERATED:", path)

    return path


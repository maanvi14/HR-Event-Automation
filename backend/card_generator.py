import os
from PIL import Image, ImageDraw, ImageFont


# ================= FONT LOADER =================
def load_font(size, bold=False):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    font_folder = os.path.join(CURRENT_DIR, "fonts")

    font_name = "Georgia-Bold.ttf" if bold else "Georgia.ttf"
    path = os.path.join(font_folder, font_name)

    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()


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


# ================= SHADOW TEXT =================
def draw_text_with_shadow(draw, position, text, font, fill, shadow_color="black"):
    x, y = position
    draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


# ================= MAIN FUNCTION =================
def generate_card(data, photo_path):
    event_type = data["event_type"].lower().strip()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Render-safe temp folder
    output_dir = os.path.join(BASE_DIR, "temp_cards")
    os.makedirs(output_dir, exist_ok=True)

    # ================= CONFIG =================
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
            "default_msg": "Wishing you a fantastic birthday filled with joy and success!"
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
            "uppercase": False,
            "default_msg": "Celebrating your dedication and contribution. Happy Work Anniversary!"
        }
    }

    cfg = CONFIG.get(event_type, CONFIG["birthday"])
    template_path = os.path.join(BASE_DIR, cfg["template"])

    # ================= LOAD IMAGES =================
    template = Image.open(template_path).convert("RGBA")

    photo = None
    if photo_path and os.path.exists(photo_path):
        with Image.open(photo_path) as img:
            img.load()
            photo = img.convert("RGBA")

    width, height = template.size
    draw = ImageDraw.Draw(template)

    # ================= PHOTO CIRCLE =================
    if photo:
        cx = width // 2
        cy = int(height * cfg["circle_cy_pct"])
        r = int(width * cfg["circle_r_pct"])
        size = r * 2

        w_p, h_p = photo.size
        m = min(w_p, h_p)

        photo = photo.crop((
            (w_p - m) // 2,
            (h_p - m) // 2,
            (w_p + m) // 2,
            (h_p + m) // 2
        )).resize((size, size), Image.LANCZOS)

        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)

        photo.putalpha(mask)

        template.paste(photo, (cx - r, cy - r), photo)

        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            outline=cfg["border_color"],
            width=4
        )

    # ================= TEXT =================
    name_font = load_font(int(width * 0.095), bold=True)
    msg_font = load_font(int(width * 0.045))

    name_text = data["name"].upper() if cfg["uppercase"] else data["name"].title()
    message = data.get("message") or cfg["default_msg"]

    # NAME POSITION
    ny = int(height * cfg["name_y_pct"])
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    name_w = name_bbox[2]

    draw_text_with_shadow(
        draw,
        ((width - name_w) // 2, ny),
        name_text,
        name_font,
        cfg["name_color"]
    )

    # MESSAGE
    lines = wrap_text(draw, message, msg_font, int(width * 0.7))
    my = ny + int(height * cfg["msg_gap"])

    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=msg_font)
        line_w = line_bbox[2]

        draw_text_with_shadow(
            draw,
            ((width - line_w) // 2, my),
            line,
            msg_font,
            cfg["msg_color"]
        )

        my += int(height * 0.045)

    # ================= SAVE =================
    filename = f"{data['employee_id']}_{event_type}.png"
    out_path = os.path.join(output_dir, filename)

    template.save(out_path)

    return out_path
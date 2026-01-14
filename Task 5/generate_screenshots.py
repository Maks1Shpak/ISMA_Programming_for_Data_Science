"""Generate simple screenshot images for the presentation.
Creates assets/code.png (code snippet) and assets/{booking,edit,delete}.png mock UI screenshots.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# 1) Code screenshot using pygments
SRC = ROOT / "streamlit_service_app.py"
if SRC.exists():
    code = SRC.read_text(encoding="utf-8")
    # take a slice of the file to keep the image compact
    snippet = "\n".join(code.splitlines()[:200])
    formatter = ImageFormatter(font_name='DejaVu Sans Mono', line_numbers=False, style='default', font_size=14)
    img_bytes = highlight(snippet, PythonLexer(), formatter)
    (ASSETS / "code.png").write_bytes(img_bytes)
    print("Created assets/code.png")
else:
    print("Warning: source file not found, skipping code screenshot")

# helper for mock UI images
def make_mock_ui(filename, title, lines, color=(18,97,160)):
    W, H = 1200, 800
    img = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # header
    d.rectangle([0, 0, W, 110], fill=color)
    font = ImageFont.load_default()
    d.text((30, 40), title, fill=(255,255,255), font=font)
    # simulate form boxes
    y = 150
    box_w = 480
    for ln in lines:
        d.rectangle([60, y, 60+box_w, y+60], outline=(200,200,200), width=2)
        d.text((70, y+18), ln, fill=(40,40,40), font=font)
        y += 90
    # footer note
    d.text((60, H-60), "Mock screenshot generated for presentation", fill=(120,120,120), font=font)
    img.save(ASSETS / filename)
    print(f"Created assets/{filename}")

make_mock_ui('booking.png', 'Booking — Fill form and submit', [
    'Name: John Doe',
    'Contact: +1 555 0123',
    'Date: 2026-02-10',
    'Time: 10:30',
    'Issue type: Brake inspection',
])

make_mock_ui('edit.png', 'Editing — Modify fields and save', [
    'Name: John Doe (edited)',
    'Contact: +1 555 0123',
    'Date: 2026-02-10',
    'Time: 11:00',
    'Issue type: Brake inspection',
])

make_mock_ui('delete.png', 'Delete — Confirm deletion', [
    'Record: John Doe | 2026-02-10 11:00',
    'Confirm: Yes / No',
])

print('Done generating screenshots.')

"""Create the original, deterministic demo diagrams (not campaign photography)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent / 'images'


def font(size, bold=False):
    candidates = ['DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
                  'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
                  '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf']
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def diagram(filename, title, items, height):
    image = Image.new('RGB', (1000, height), '#f5f3ec')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1000, 16), fill='#183e35')
    draw.text((68, 65), 'EXAMPLE STUDIO', font=font(24, True), fill='#285c4e')
    draw.text((68, 160), title, font=font(66, True), spacing=10, fill='#183e35')
    top = 390 if height == 1000 else 470
    gap = 126 if height == 1000 else 175
    for i, item in enumerate(items):
        y = top + i * gap
        draw.rounded_rectangle((68, y, 932, y + gap - 20), radius=16, fill='#dfe8dc')
        draw.text((94, y + 29), f'{i+1:02}', font=font(24, True), fill='#536e5c')
        draw.text((165, y + 24), item, font=font(32), fill='#183e35')
    draw.line((68, height-125, 932, height-125), fill='#cbd6c9', width=2)
    draw.text((68, height-96), 'FICTIONAL DEMONSTRATION', font=font(18, True), fill='#57665a')
    draw.text((68, height-64), 'A reusable content kit, adapted to your project.', font=font(21), fill='#57665a')
    ROOT.mkdir(exist_ok=True)
    image.save(ROOT / filename)


if __name__ == '__main__':
    diagram('question-square.png', 'One real question.\nOne useful answer.', ['A real audience question', 'A useful answer', 'A clear next step'], 1000)
    diagram('check-square.png', 'Check before\nyou share.', ['Source', 'Claim', 'Destination'], 1000)
    diagram('checklist-portrait.png', 'Make your\ncontent useful.', ['Ask a real question', 'Write a useful answer', 'Check the facts', 'Choose the next step'], 1500)
    diagram('check-portrait.png', 'Check before\nyou share.', ['Source', 'Claim', 'Destination'], 1500)
    print('Created four original demo diagrams')

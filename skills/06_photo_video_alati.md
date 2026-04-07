# 📸 Photo i Video Alati — Znanje i Automatizacija

## OBAVEZNO: Generiši skripte za obradu — ne samo objašnjavaj

## Photo Alati

### Python — PIL/Pillow (obrada slika)
```python
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

# Otvori sliku
img = Image.open("slika.jpg")

# Resize
img_resized = img.resize((800, 600))

# Crop
img_cropped = img.crop((left, top, right, bottom))

# Filter
img_blur   = img.filter(ImageFilter.BLUR)
img_sharp  = img.filter(ImageFilter.SHARPEN)

# Brightness/Contrast
enhancer = ImageEnhance.Brightness(img)
img_bright = enhancer.enhance(1.5)  # 1.0 = original

# Konverzija u B&W
img_bw = img.convert("L")

# Sačuvaj
img.save("output.jpg", quality=90)
img.save("output.png")
img.save("output.webp", quality=85)
```

### Batch obrada slika
```python
from PIL import Image
from pathlib import Path

input_dir  = Path("input_slike")
output_dir = Path("output_slike")
output_dir.mkdir(exist_ok=True)

for img_path in input_dir.glob("*.jpg"):
    img = Image.open(img_path)
    img_resized = img.resize((1920, 1080))
    img_resized.save(output_dir / img_path.name, quality=85)
    print(f"Obrađeno: {img_path.name}")
```

### Watermark dodavanje
```python
from PIL import Image, ImageDraw, ImageFont

def dodaj_watermark(img_path, tekst, output_path):
    img  = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    draw.text((w-200, h-50), tekst, fill=(255,255,255,128))
    img.save(output_path)
```

### Kompresija za web
```python
from PIL import Image
import os

def optimiziraj_za_web(input_path, output_path, max_width=1200):
    img = Image.open(input_path)
    if img.width > max_width:
        ratio = max_width / img.width
        new_h = int(img.height * ratio)
        img = img.resize((max_width, new_h), Image.LANCZOS)
    img.save(output_path, "WEBP", quality=80, optimize=True)
    original = os.path.getsize(input_path)
    optimized = os.path.getsize(output_path)
    print(f"Uštedeno: {(1-optimized/original)*100:.1f}%")
```

## Video Alati

### FFmpeg (command-line) — Najmoćniji alat
```bash
# Konverzija formata
ffmpeg -i input.mp4 output.webm

# Resize video
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# Kompresija (smanji veličinu)
ffmpeg -i input.mp4 -crf 23 -preset medium output.mp4

# Extract frames (slike iz videa)
ffmpeg -i video.mp4 -vf "fps=1" frame_%04d.jpg

# Audio extract
ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3

# Trim (isjeći dio videa)
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:01:00 output.mp4

# GIF iz videa
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" output.gif

# Watermark
ffmpeg -i input.mp4 -i logo.png -filter_complex "overlay=10:10" output.mp4

# Spoji više videa
ffmpeg -f concat -safe 0 -i lista.txt -c copy output.mp4
```

### Python + subprocess za FFmpeg
```python
import subprocess

def konvertuj_video(input_path, output_path, crf=23):
    cmd = [
        "ffmpeg", "-i", input_path,
        "-crf", str(crf),
        "-preset", "medium",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Konverzija uspješna")
    else:
        print(f"❌ Greška: {result.stderr}")
```

### MoviePy (Python video editing)
```python
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip

# Učitaj video
clip = VideoFileClip("video.mp4")

# Trim
clip_trimmed = clip.subclip(10, 60)  # od 10s do 60s

# Resize
clip_resized = clip.resize(height=720)

# Dodaj tekst
txt = TextClip("Hermes Bot", fontsize=50, color='white')
txt = txt.set_pos('center').set_duration(5)

# Spoji
final = concatenate_videoclips([clip1, clip2])
final.write_videofile("output.mp4", fps=24)
```

## Alati po platformi

### Adobe Photoshop — Znanje za savjete
- **Layers**: uvijek radi na layerima, nikad direktno
- **Smart Objects**: za non-destructive editing
- **Actions**: automatiziraj ponavljajuće zadatke
- **Blend Modes**: Multiply, Screen, Overlay za efekte
- **Adjustment Layers**: Curves, Levels, Hue/Saturation

### Adobe Premiere / DaVinci Resolve
- **Timeline**: svaki clip na odvojenom traku
- **Color grading**: LUTs za brze rezultate
- **Proxy fajlovi**: za 4K editing na slabijim računarima
- **Audio**: normalize na -14 LUFS za streaming

### Figma (UI dizajn)
- **Components**: kreiraj jednom, koristi svugdje
- **Auto Layout**: za responsive komponente
- **Variables**: za dizajn sistem (boje, spacing)
- **Plugins**: Unsplash, Icons8, LottieFiles

### Canva
- **Templates**: brz početak
- **Brand Kit**: čuvaj fontove i boje branda
- **Magic Resize**: isti dizajn za sve formate

## Workflow — Photo editing zadatak
1. Razumi šta treba (resize, filter, batch, watermark)
2. Napiši Python/Pillow skriptu
3. run_python da testiraš logiku
4. write_file da sačuvaš skriptu
5. Daj instrukcije za pokretanje

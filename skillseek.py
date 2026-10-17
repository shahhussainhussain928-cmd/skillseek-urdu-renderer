
from pathlib import Path
import subprocess
import urllib.request

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "skillseek_output"
FRAMES = OUT / "frames"
FONT_DIR = OUT / "fonts"

WIDTH, HEIGHT = 1280, 720
FPS = 24
DURATION = 10

OUT.mkdir(exist_ok=True)
FRAMES.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

FONT = FONT_DIR / "urdu.ttf"
VIDEO = OUT / "skillseek-test.mp4"

FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/"
    "ofl/notonastaliqurdu/NotoNastaliqUrdu%5Bwght%5D.ttf"
)

SCENES = [
    ("سیکھو اسمارٹ، بڑھو آگے!", "اسکل سیک اردو"),
    ("مصنوعی ذہانت سے نئی مہارتیں سیکھیں", "SkillSeek Urdu"),
    ("آپ کا ڈیجیٹل سفر آج شروع ہوتا ہے", "آج ہی سیکھنا شروع کریں")
]


def urdu(text):
    return get_display(arabic_reshaper.reshape(text))


def main():
    print("Starting SkillSeek Urdu renderer...")

    if not FONT.exists():
        print("Downloading Urdu font...")
        urllib.request.urlretrieve(FONT_URL, FONT)

    if FONT.stat().st_size < 10000:
        raise RuntimeError("The Urdu font download appears incomplete.")

    heading_font = ImageFont.truetype(str(FONT), 58)
    sub_font = ImageFont.truetype(str(FONT), 34)

    for i, (heading, subtitle) in enumerate(SCENES):
        img = Image.new("RGB", (WIDTH, HEIGHT), "#0f172a")
        draw = ImageDraw.Draw(img)

        draw.rectangle((0, 0, WIDTH, 12), fill="#facc15")
        draw.rectangle(
            (0, HEIGHT - 12, WIDTH, HEIGHT),
            fill="#facc15"
        )

        draw.text(
            (WIDTH // 2, 270),
            urdu(heading),
            font=heading_font,
            fill="white",
            anchor="mm",
            direction="rtl"
        )

        draw.text(
            (WIDTH // 2, 370),
            urdu(subtitle),
            font=sub_font,
            fill="#facc15",
            anchor="mm",
            direction="rtl"
        )

        draw.text(
            (WIDTH // 2, 650),
            "SKILLSEEK URDU",
            font=ImageFont.truetype(str(FONT), 24),
            fill="#cbd5e1",
            anchor="mm"
        )

        img.save(FRAMES / f"frame_{i:03d}.png")
        print(f"Created scene {i + 1}/{len(SCENES)}")

    print("Rendering MP4...")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1",
            "-framerate", "1",
            "-i", str(FRAMES / "frame_000.png"),
            "-loop", "1",
            "-framerate", "1",
            "-i", str(FRAMES / "frame_001.png"),
            "-loop", "1",
            "-framerate", "1",
            "-i", str(FRAMES / "frame_002.png"),
            "-filter_complex",
            (
                "[0:v]trim=duration=3.34,setpts=PTS-STARTPTS[a];"
                "[1:v]trim=duration=3.33,setpts=PTS-STARTPTS[b];"
                "[2:v]trim=duration=3.33,setpts=PTS-STARTPTS[c];"
                "[a][b][c]concat=n=3:v=1:a=0,"
                f"fps={FPS},scale={WIDTH}:{HEIGHT},"
                "format=yuv420p[v]"
            ),
            "-map", "[v]",
            "-t", str(DURATION),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(VIDEO)
        ],
        check=True
    )

    print(f"SUCCESS: {VIDEO}")


if __name__ == "__main__":
    main()

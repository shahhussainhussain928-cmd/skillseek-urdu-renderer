
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
FONT = FONT_DIR / "NotoNastaliqUrdu-Regular.ttf"
VIDEO = OUT / "skillseek-test.mp4"

WIDTH, HEIGHT = 1280, 720
FPS = 24

OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)
FONT_DIR.mkdir(parents=True, exist_ok=True)

FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/"
    "ofl/notonastaliqurdu/NotoNastaliqUrdu%5Bwght%5D.ttf"
)

SCENES = [
    ("سیکھو اسمارٹ، بڑھو آگے!", "اسکل سیک اردو"),
    ("مصنوعی ذہانت سے نئی مہارتیں سیکھیں", "SkillSeek Urdu"),
    ("آپ کا ڈیجیٹل سفر آج شروع ہوتا ہے", "آج ہی سیکھنا شروع کریں"),
]


def shape_urdu(text):
    return get_display(arabic_reshaper.reshape(text))


def main():
    print("Downloading a fresh Urdu font...")
    request = urllib.request.Request(
        FONT_URL,
        headers={"User-Agent": "SkillSeekUrdu/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        FONT.write_bytes(response.read())

    if FONT.stat().st_size < 10000:
        raise RuntimeError("Font download is incomplete.")

    print(f"Font downloaded: {FONT.stat().st_size} bytes")

    # Verify that Pillow can open the font.
    heading_font = ImageFont.truetype(str(FONT), 58)
    subtitle_font = ImageFont.truetype(str(FONT), 36)
    brand_font = ImageFont.truetype(str(FONT), 24)

    for index, (heading, subtitle) in enumerate(SCENES):
        image = Image.new("RGB", (WIDTH, HEIGHT), "#0f172a")
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, WIDTH, 12), fill="#facc15")
        draw.rectangle((0, HEIGHT - 12, WIDTH, HEIGHT), fill="#facc15")

        draw.text(
            (WIDTH // 2, 270),
            shape_urdu(heading),
            font=heading_font,
            fill="#ffffff",
            anchor="mm",
            direction="rtl",
        )

        draw.text(
            (WIDTH // 2, 370),
            shape_urdu(subtitle),
            font=subtitle_font,
            fill="#facc15",
            anchor="mm",
            direction="rtl",
        )

        draw.text(
            (WIDTH // 2, 650),
            "SKILLSEEK URDU",
            font=brand_font,
            fill="#cbd5e1",
            anchor="mm",
        )

        image.save(FRAMES / f"frame_{index:03d}.png")
        print(f"Created scene {index + 1}")

    # Hold each scene for a few seconds, then join them.
    inputs = []
    filters = []

    durations = [3.34, 3.33, 3.33]

    for index, duration in enumerate(durations):
        inputs.extend([
            "-loop", "1",
            "-framerate", "1",
            "-t", str(duration),
            "-i", str(FRAMES / f"frame_{index:03d}.png"),
        ])
        filters.append(
            f"[{index}:v]fps={FPS},"
            f"trim=duration={duration},"
            f"setpts=PTS-STARTPTS,"
            f"scale={WIDTH}:{HEIGHT},format=yuv420p[v{index}]"
        )

    filters.append("[v0][v1][v2]concat=n=3:v=1:a=0[outv]")

    subprocess.run(
        [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", ";".join(filters),
            "-map", "[outv]",
            "-t", "10",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(VIDEO),
        ],
        check=True,
    )

    print(f"SUCCESS: {VIDEO}")


if __name__ == "__main__":
    main()

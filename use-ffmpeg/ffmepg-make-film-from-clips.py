import argparse
import subprocess
import csv
import re
from pathlib import Path
import shlex


# ============================================================
# SETTINGS
# ============================================================

FFMPEG_EXE = r"G:\Hetzner\OneDrive\Tools\ffmpeg\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# Folder containing the PNG images
INPUT_FOLDER = r"G:\Hetzner\Smalfilm enketlbilleder\Klip"

# Output folder where the films will be saved
OUTPUT_FOLDER = INPUT_FOLDER

# FFmpeg settings
FRAMERATE = 25
VIDEO_CODEC = "libx264"
CRF = 0
PIX_FMT = "yuv420p"


# ============================================================
# FUNCTIONS
# ============================================================

def parse_image_filename(filename: str) -> tuple[str, int, int]:
    """Parse a filename like '1967.aug.mp4-000020.png' into (prefix, frame_number, zero_pad_width)."""
    match = re.match(r'^(.+)-(\d+)\.png$', filename.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"Cannot parse frame number from filename: {filename}")
    prefix = match.group(1)
    frame_str = match.group(2)
    return prefix, int(frame_str), len(frame_str)


def read_csv(csv_file: str) -> list[tuple[str, str]]:
    clips = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            start, end = row[0].strip(), row[1].strip()
            # Skip header rows or empty rows
            if not start.lower().endswith('.png') or not end.lower().endswith('.png'):
                continue
            clips.append((start, end))
    return clips


def calculate_frame_count(first_frame: int, last_frame: int) -> int:
    return last_frame - first_frame + 1


def build_ffmpeg_command(
    input_pattern_full: str,
    first_frame: int,
    frame_count: int,
    output_file_full: str,
) -> list[str]:
    return [
        FFMPEG_EXE,
        "-framerate", str(FRAMERATE),
        "-start_number", str(first_frame),
        "-i", input_pattern_full,
        "-frames:v", str(frame_count),
        "-c:v", VIDEO_CODEC,
        "-crf", str(CRF),
        "-pix_fmt", PIX_FMT,
        output_file_full,
    ]


def process_clip(start_image: str, end_image: str) -> int:
    prefix_start, first_frame, padding = parse_image_filename(start_image)
    prefix_end, last_frame, _ = parse_image_filename(end_image)

    if prefix_start != prefix_end:
        raise ValueError(
            f"Start and end images have different prefixes: '{prefix_start}' vs '{prefix_end}'"
        )

    if last_frame < first_frame:
        raise ValueError(
            f"End frame ({last_frame}) must not be less than start frame ({first_frame})."
        )

    frame_count = calculate_frame_count(first_frame, last_frame)
    input_pattern = f"{prefix_start}-%0{padding}d.png"
    input_pattern_full = str(Path(INPUT_FOLDER) / input_pattern)
    output_filename = f"{prefix_start}-{first_frame:0{padding}d}-{last_frame:0{padding}d}_crf{CRF}.mp4"
    output_file_full = str(Path(OUTPUT_FOLDER) / output_filename)

    print(f"  Start image  : {start_image}")
    print(f"  End image    : {end_image}")
    print(f"  First frame  : {first_frame}")
    print(f"  Last frame   : {last_frame}")
    print(f"  Frame count  : {frame_count}")
    print(f"  Input pattern: {input_pattern_full}")
    print(f"  Output file  : {output_file_full}")
    print()

    cmd = build_ffmpeg_command(input_pattern_full, first_frame, frame_count, output_file_full)
    print("Command being run:")
    print(" ".join(shlex.quote(part) for part in cmd))
    print()

    return subprocess.run(cmd, check=False).returncode


def validate_paths(csv_file: str) -> None:
    if not Path(FFMPEG_EXE).is_file():
        raise FileNotFoundError(f"ffmpeg.exe not found:\n{FFMPEG_EXE}")
    if not Path(csv_file).is_file():
        raise FileNotFoundError(f"CSV file not found:\n{csv_file}")
    if not Path(INPUT_FOLDER).is_dir():
        raise FileNotFoundError(f"INPUT_FOLDER not found:\n{INPUT_FOLDER}")
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


def run_from_csv(csv_file: str) -> None:
    validate_paths(csv_file)

    clips = read_csv(csv_file)
    if not clips:
        raise ValueError("CSV file contains no valid rows.")

    print(f"Found {len(clips)} clip(s) in: {csv_file}")
    print(f"ffmpeg      : {FFMPEG_EXE}")
    print(f"Input folder: {INPUT_FOLDER}")
    print(f"Framerate   : {FRAMERATE}  Codec: {VIDEO_CODEC}  CRF: {CRF}  Pix fmt: {PIX_FMT}")
    print()

    results = []
    for i, (start_image, end_image) in enumerate(clips, start=1):
        print(f"--- Clip {i}/{len(clips)} ---")
        try:
            exit_code = process_clip(start_image, end_image)
            status = "OK" if exit_code == 0 else f"FAILED (exit code {exit_code})"
        except Exception as e:
            exit_code = -1
            status = f"ERROR: {e}"
        results.append((i, start_image, end_image, status))
        print(f"Result: {status}")
        print()

    print("=" * 60)
    print("Summary:")
    for i, start, end, status in results:
        print(f"  Clip {i}: {start} -> {end}  [{status}]")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create films from PNG clips using ffmpeg.")
    parser.add_argument("csv_file", help="Path to CSV file with start/end image columns")
    args = parser.parse_args()

    try:
        run_from_csv(args.csv_file)
    except Exception as e:
        print()
        print("Error:")
        print(e)

import subprocess
from pathlib import Path
import shlex


# ============================================================
# SETTINGS
# ============================================================

FFMPEG_EXE = r"G:\Hetzner\OneDrive\Tools\ffmpeg\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# Folder containing the PNG images
INPUT_FOLDER = r"G:\Hetzner\Smalfilm enketlbilleder\Klip\01-01-1967 aug.mp4"

# Filename pattern for images in INPUT_FOLDER
# Example filename:
# 1967.aug.mp4-000020.png
INPUT_PATTERN = "1967.aug.mp4-%06d.png"

# First and last frame number
FIRST_FRAME = 20
LAST_FRAME = 327

# Output folder where the film will be saved
# OUTPUT_FOLDER = r"G:\Hetzner\Smalfilm enketlbilleder\Klip\01-01-1967 aug.mp4"
OUTPUT_FOLDER = INPUT_FOLDER

# Name of the finished film
OUTPUT_FILENAME = "01-01-1967 aug_crf0.mp4"

# FFmpeg settings
FRAMERATE = 25
VIDEO_CODEC = "libx264"
CRF = 0
PIX_FMT = "yuv420p"


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_frames_v(first_frame: int, last_frame: int) -> int:
    return last_frame - first_frame + 1


def validate_settings() -> None:
    ffmpeg_path = Path(FFMPEG_EXE)
    input_folder = Path(INPUT_FOLDER)
    output_folder = Path(OUTPUT_FOLDER)

    if not ffmpeg_path.is_file():
        raise FileNotFoundError(f"ffmpeg.exe not found:\n{ffmpeg_path}")

    if not input_folder.is_dir():
        raise FileNotFoundError(f"INPUT_FOLDER not found:\n{input_folder}")

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    if FIRST_FRAME < 0:
        raise ValueError("FIRST_FRAME must not be negative.")

    if LAST_FRAME < FIRST_FRAME:
        raise ValueError("LAST_FRAME must not be less than FIRST_FRAME.")

    if FRAMERATE <= 0:
        raise ValueError("FRAMERATE must be greater than 0.")

    if CRF < 0:
        raise ValueError("CRF must not be negative.")

    if not INPUT_PATTERN.strip():
        raise ValueError("INPUT_PATTERN must not be empty.")

    if not OUTPUT_FILENAME.strip():
        raise ValueError("OUTPUT_FILENAME must not be empty.")


def build_paths() -> tuple[str, str]:
    input_pattern_full = str(Path(INPUT_FOLDER) / INPUT_PATTERN)
    output_file_full = str(Path(OUTPUT_FOLDER) / OUTPUT_FILENAME)
    return input_pattern_full, output_file_full


def build_ffmpeg_command() -> list[str]:
    frames_v = calculate_frames_v(FIRST_FRAME, LAST_FRAME)
    input_pattern_full, output_file_full = build_paths()

    return [
        FFMPEG_EXE,
        "-framerate", str(FRAMERATE),
        "-start_number", str(FIRST_FRAME),
        "-i", input_pattern_full,
        "-frames:v", str(frames_v),
        "-c:v", VIDEO_CODEC,
        "-crf", str(CRF),
        "-pix_fmt", PIX_FMT,
        output_file_full,
    ]


def print_summary() -> None:
    frames_v = calculate_frames_v(FIRST_FRAME, LAST_FRAME)
    input_pattern_full, output_file_full = build_paths()

    print("Settings:")
    print(f"  ffmpeg.exe   : {FFMPEG_EXE}")
    print(f"  Input folder : {INPUT_FOLDER}")
    print(f"  Input pattern: {INPUT_PATTERN}")
    print(f"  First frame  : {FIRST_FRAME}")
    print(f"  Last frame   : {LAST_FRAME}")
    print(f"  Frames total : {frames_v}")
    print(f"  Framerate    : {FRAMERATE}")
    print(f"  Codec        : {VIDEO_CODEC}")
    print(f"  CRF          : {CRF}")
    print(f"  Pix fmt      : {PIX_FMT}")
    print(f"  Output folder: {OUTPUT_FOLDER}")
    print(f"  Output file  : {output_file_full}")
    print(f"  Input full   : {input_pattern_full}")
    print()


def print_command(cmd: list[str]) -> None:
    print("Command being run:")
    print(" ".join(shlex.quote(part) for part in cmd))
    print()


def run_ffmpeg() -> int:
    validate_settings()
    print_summary()

    cmd = build_ffmpeg_command()
    print_command(cmd)

    process = subprocess.run(cmd, check=False)
    return process.returncode


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        exit_code = run_ffmpeg()
        print()
        print(f"FFmpeg finished with exit code: {exit_code}")

        if exit_code == 0:
            print("Video created successfully.")
        else:
            print("FFmpeg reported an error.")
    except Exception as e:
        print()
        print("Error:")
        print(e)

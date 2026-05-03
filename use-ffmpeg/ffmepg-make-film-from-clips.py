import subprocess
from pathlib import Path
import shlex


# ============================================================
# INDSTILLINGER
# ============================================================

FFMPEG_EXE = r"G:\Hetzner\OneDrive\Tools\ffmpeg\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# Mappen hvor PNG-billederne ligger
INPUT_FOLDER = r"G:\Hetzner\Smalfilm enketlbilleder\Klip\01-01-1967 aug.mp4"

# Filnavnsmønster for billederne i INPUT_FOLDER
# Eksempel på filnavn:
# 1967.aug.mp4-000020.png
INPUT_PATTERN = "1967.aug.mp4-%06d.png"

# Første og sidste frame-nummer
FIRST_FRAME = 20
LAST_FRAME = 327

# Output-mappe hvor filmen skal gemmes
# OUTPUT_FOLDER = r"G:\Hetzner\Smalfilm enketlbilleder\Klip\01-01-1967 aug.mp4"
OUTPUT_FOLDER = INPUT_FOLDER

# Navn på den færdige film
OUTPUT_FILENAME = "01-01-1967 aug_crf0.mp4"

# FFmpeg-indstillinger
FRAMERATE = 25
VIDEO_CODEC = "libx264"
CRF = 0
PIX_FMT = "yuv420p"


# ============================================================
# FUNKTIONER
# ============================================================

def calculate_frames_v(first_frame: int, last_frame: int) -> int:
    return last_frame - first_frame + 1


def validate_settings() -> None:
    ffmpeg_path = Path(FFMPEG_EXE)
    input_folder = Path(INPUT_FOLDER)
    output_folder = Path(OUTPUT_FOLDER)

    if not ffmpeg_path.is_file():
        raise FileNotFoundError(f"ffmpeg.exe blev ikke fundet:\n{ffmpeg_path}")

    if not input_folder.is_dir():
        raise FileNotFoundError(f"INPUT_FOLDER blev ikke fundet:\n{input_folder}")

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    if FIRST_FRAME < 0:
        raise ValueError("FIRST_FRAME må ikke være negativ.")

    if LAST_FRAME < FIRST_FRAME:
        raise ValueError("LAST_FRAME må ikke være mindre end FIRST_FRAME.")

    if FRAMERATE <= 0:
        raise ValueError("FRAMERATE skal være større end 0.")

    if CRF < 0:
        raise ValueError("CRF må ikke være negativ.")

    if not INPUT_PATTERN.strip():
        raise ValueError("INPUT_PATTERN må ikke være tom.")

    if not OUTPUT_FILENAME.strip():
        raise ValueError("OUTPUT_FILENAME må ikke være tom.")


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

    print("Indstillinger:")
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
    print("Kommando som køres:")
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
        print(f"FFmpeg afsluttede med exit code: {exit_code}")

        if exit_code == 0:
            print("Videoen blev oprettet uden fejl.")
        else:
            print("FFmpeg rapporterede en fejl.")
    except Exception as e:
        print()
        print("Fejl:")
        print(e)
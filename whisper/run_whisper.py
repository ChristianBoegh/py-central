"""
Run whisper sequentially on files listed in a config markdown file.
Usage: python run_whisper.py [config.md]
Default config file: whisper_config.md
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_config(md_path: Path) -> tuple[list[str], str, list[str]]:
    text = md_path.read_text(encoding="utf-8")
    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)

    input_files: list[str] = []
    output_folder: str = ""
    parameters: list[str] = []

    for section in sections:
        lines = section.strip().splitlines()
        if not lines:
            continue
        header = lines[0].strip().lower()

        if header == "input files":
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("-"):
                    path = line.lstrip("-").strip()
                    if path and not path.startswith("#"):
                        input_files.append(path)

        elif header == "output folder":
            for line in lines[1:]:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    output_folder = line
                    break

        elif header == "parameters":
            for line in lines[1:]:
                line = line.strip()
                if re.match(r"-\s*\[x\]", line, re.IGNORECASE):
                    param = re.sub(r"^-\s*\[x\]\s*", "", line, flags=re.IGNORECASE).strip()
                    if param:
                        parameters.extend(param.split())

    return input_files, output_folder, parameters


def format_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02}m {s:02}s"
    if m:
        return f"{m}m {s:02}s"
    return f"{s}s"


def rotate_log(log_path: Path) -> None:
    """Rotate existing log files: whisper_log.md -> whisper_log_1.md,
    whisper_log_1.md -> whisper_log_2.md, etc."""
    if not log_path.exists():
        return

    # Find the highest existing backup number
    n = 1
    while log_path.with_stem(f"whisper_log_{n}").exists():
        n += 1

    # Shift backups upward from highest to lowest
    for i in range(n, 1, -1):
        log_path.with_stem(f"whisper_log_{i - 1}").rename(
            log_path.with_stem(f"whisper_log_{i}")
        )

    # Move current log to _1
    log_path.rename(log_path.with_stem("whisper_log_1"))


def ts() -> str:
    """Current timestamp as a readable string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_whisper(config_path: Path) -> None:
    input_files, output_folder, parameters = parse_config(config_path)

    if not input_files:
        print("No input files found in config.")
        sys.exit(1)

    if not output_folder:
        print("No output folder specified in config.")
        sys.exit(1)

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    log_path = Path(output_folder) / "whisper_log.md"
    rotate_log(log_path)

    batch_start = datetime.now()

    with log_path.open("w", encoding="utf-8") as log:
        total = len(input_files)

        # Write header and planned file list up front so progress is visible
        log.write(f"# Whisper Log\n\n")
        log.write(f"**Started:** {ts()}  \n")
        log.write(f"**Config:** `{config_path}`  \n")
        log.write(f"**Parameters:** `{' '.join(parameters)}`  \n\n")
        log.write(f"## Queued ({total} files)\n\n")
        for i, file_path in enumerate(input_files, start=1):
            log.write(f"{i}. {file_path}\n")
        log.write("\n## Results\n\n")
        log.write("| # | Started | File | Status | Duration |\n")
        log.write("|---|---------|------|--------|----------|\n")
        log.flush()

        ok_count = 0

        for i, file_path in enumerate(input_files, start=1):
            t_start = datetime.now()
            started_at = t_start.strftime("%H:%M:%S")
            print(f"\n[{i}/{total}] {started_at} Processing: {file_path}")
            cmd = ["whisper", file_path, "--output_dir", output_folder] + parameters
            print("Command:", " ".join(f'"{c}"' if " " in c else c for c in cmd))

            result = subprocess.run(cmd)
            duration = (datetime.now() - t_start).total_seconds()

            if result.returncode == 0:
                status = "OK"
                ok_count += 1
            else:
                status = f"FAILED (exit {result.returncode})"
                print(f"  WARNING: whisper exited with code {result.returncode} for {file_path}")

            log.write(f"| {i} | {started_at} | {file_path} | {status} | {format_duration(duration)} |\n")
            log.flush()

        total_duration = (datetime.now() - batch_start).total_seconds()
        log.write(f"\n**Finished:** {ts()}  \n")
        log.write(f"**Total:** {ok_count}/{total} succeeded — {format_duration(total_duration)}\n")

    print(f"\nDone. Processed {total} file(s). Output in: {output_folder}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    config_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("whisper_config.md")
    if not config_file.exists():
        print(f"Config file not found: {config_file}")
        sys.exit(1)
    run_whisper(config_file)

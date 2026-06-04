"""
Run whisper sequentially on files listed in a config markdown file.
Usage: python run_whisper.py [config.md]
Default config file: whisper_config.md
"""

import re
import subprocess
import sys
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
            # Collect all checked parameters from sub-sections
            for line in lines[1:]:
                line = line.strip()
                if re.match(r"-\s*\[x\]", line, re.IGNORECASE):
                    param = re.sub(r"^-\s*\[x\]\s*", "", line, flags=re.IGNORECASE).strip()
                    if param:
                        parameters.extend(param.split())

    return input_files, output_folder, parameters


def run_whisper(config_path: Path) -> None:
    input_files, output_folder, parameters = parse_config(config_path)

    if not input_files:
        print("No input files found in config.")
        sys.exit(1)

    if not output_folder:
        print("No output folder specified in config.")
        sys.exit(1)

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    total = len(input_files)
    for i, file_path in enumerate(input_files, start=1):
        print(f"\n[{i}/{total}] Processing: {file_path}")
        cmd = ["whisper", file_path, "--output_dir", output_folder] + parameters
        print("Command:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"  WARNING: whisper exited with code {result.returncode} for {file_path}")

    print(f"\nDone. Processed {total} file(s). Output in: {output_folder}")


if __name__ == "__main__":
    config_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("whisper_config.md")
    if not config_file.exists():
        print(f"Config file not found: {config_file}")
        sys.exit(1)
    run_whisper(config_file)

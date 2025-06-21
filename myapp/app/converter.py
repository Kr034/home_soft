# app/converter.py
import os
import subprocess
from pathlib import Path
from datetime import datetime

def convert_md_to_pdf(input_path: str, output_path: str, log_path: str = "/data/logs/conversions.log") -> bool:
    try:
        subprocess.run([
            "pandoc", input_path,
            "-o", output_path,
            "--pdf-engine=xelatex"
        ], check=True)

        with open(log_path, "a") as log:
            log.write(f"[OK] {datetime.now()} Converted: {input_path} -> {output_path}\n")
        return True
    except subprocess.CalledProcessError:
        with open(log_path, "a") as log:
            log.write(f"[FAIL] {datetime.now()} Failed to convert: {input_path}\n")
        return False

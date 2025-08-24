import os
import subprocess
from setuptools import setup, find_packages

# -------------------- Optional Binary Check --------------------
def check_binaries():
    """Check if MAFFT and MUSCLE are installed; warn if MUSCLE <5."""
    missing_binaries = []
    for binary in ["mafft", "muscle"]:
        result = subprocess.run(["which", binary], capture_output=True, text=True)
        if result.returncode != 0:
            missing_binaries.append(binary)

    if missing_binaries:
        print(f"Warning: Missing binaries: {', '.join(missing_binaries)}")
        print("Please install them manually or run install_binaries.py if available.")
        return

    # Check versions
    try:
        mafft_version = subprocess.run(["mafft", "--version"], capture_output=True, text=True, check=True)
        mafft_ver_line = mafft_version.stdout.strip().splitlines()[0]
        print(f"MAFFT detected: {mafft_ver_line}")
    except Exception:
        print("Warning: Could not detect MAFFT version.")

    try:
        muscle_version = subprocess.run(["muscle", "-version"], capture_output=True, text=True, check=True)
        muscle_ver_line = muscle_version.stdout.strip().splitlines()[0]
        print(f"MUSCLE detected: {muscle_ver_line}")
        try:
            major_ver = int(muscle_ver_line.split()[1].split('.')[0])
            if major_ver < 5:
                print("Warning: MUSCLE version <5 detected. SwiftAlign requires MUSCLE 5.x for proper functionality.")
        except Exception:
            print("Warning: Could not parse MUSCLE version. Make sure MUSCLE 5.x is installed.")
    except Exception:
        print("Warning: Could not detect MUSCLE version.")

# Run binary check before installation
check_binaries()

# -------------------- Setup SwiftAlign --------------------
setup(
    name="SwiftAlign",
    version="1.0",
    author="Beckley Brown",
    author_email="brownbeckley94@gmail.com",
    description="Hybrid multiple sequence alignment tool combining MAFFT + MUSCLE",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "swiftalign=SwiftAlign.hybrid_msa:main",
        ],
    },
    python_requires=">=3.8",
)

#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import tarfile
import zipfile
import requests

BIN_DIR = os.path.join(os.getcwd(), "bin")
os.makedirs(BIN_DIR, exist_ok=True)

# -------------------- Helper Functions --------------------
def download_file(url, target_path):
    """Download a file from a URL."""
    print(f"Downloading {url} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def extract_archive(archive_path, extract_to):
    """Extract tar.gz or zip archives."""
    if archive_path.endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
    elif archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
    else:
        raise ValueError(f"Unknown archive format: {archive_path}")

def install_binary(name, urls):
    """Install a binary if missing."""
    if shutil.which(name):
        print(f"{name} already installed.")
        return

    system = platform.system()
    url = urls.get(system)
    if not url:
        print(f"No automatic installer for {name} on {system}. Please install manually.")
        return

    archive_name = os.path.join(BIN_DIR, os.path.basename(url))
    download_file(url, archive_name)
    extract_archive(archive_name, BIN_DIR)
    print(f"{name} installed in {BIN_DIR}")

# -------------------- Install MAFFT and MUSCLE --------------------
mafft_urls = {
    "Linux": "https://mafft.cbrc.jp/alignment/software/mafft-7.529-linux64.tgz",
    "Darwin": "https://mafft.cbrc.jp/alignment/software/mafft-7.529-mac.tgz",
    "Windows": "https://mafft.cbrc.jp/alignment/software/mafft-7.529-win64.zip"
}
muscle_urls = {
    "Linux": "https://www.drive5.com/muscle/muscle3.8.31_i86linux64.tar.gz",
    "Darwin": "https://www.drive5.com/muscle/muscle3.8.31_i86darwin64.tar.gz",
    "Windows": "https://www.drive5.com/muscle/muscle3.8.31_i86win64.zip"
}

install_binary("mafft", mafft_urls)
install_binary("muscle", muscle_urls)

# -------------------- Update PATH --------------------
def update_path():
    """Add BIN_DIR to PATH for current session and suggest permanent addition."""
    if BIN_DIR not in os.environ["PATH"]:
        os.environ["PATH"] = BIN_DIR + os.pathsep + os.environ["PATH"]
        print(f"Added {BIN_DIR} to PATH for this session.")
    shell_rc = os.path.expanduser("~/.bashrc")
    export_line = f'\n# Added by SwiftAlign installer\nexport PATH="{BIN_DIR}:$PATH"\n'
    with open(shell_rc, "a") as f:
        f.write(export_line)
    print(f"To make it permanent, PATH updated in {shell_rc} (applies to new terminals).")

update_path()
print("Installation complete! You can now run 'mafft' and 'muscle' from anywhere.")

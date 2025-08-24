import os
import subprocess
import pytest
from Bio import SeqIO

# -------------------- Directories --------------------
TESTS_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(TESTS_DIR, "test_sequences.fasta")
OUTPUT_DIR = os.path.join(TESTS_DIR, "test_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------- Helper Function --------------------
def run_swiftalign(input_file, output_file, extra_args=""):
    """Run SwiftAlign on given input and output with optional extra arguments."""
    cmd = f"python3 ../SwiftAlign/hybrid_msa.py -i {input_file} -o {output_file} {extra_args}"
    subprocess.run(cmd, shell=True, check=True)

# -------------------- Tests --------------------
def test_basic_alignment():
    output_fasta = os.path.join(OUTPUT_DIR, "aligned_basic.fasta")
    run_swiftalign(INPUT_FILE, output_fasta)
    
    assert os.path.exists(output_fasta)
    
    input_seqs = list(SeqIO.parse(INPUT_FILE, "fasta"))
    output_seqs = list(SeqIO.parse(output_fasta, "fasta"))
    assert len(input_seqs) == len(output_seqs)
    
    alignment_lengths = [len(seq.seq) for seq in output_seqs]
    assert all(l == alignment_lengths[0] for l in alignment_lengths)

def test_fast_mode():
    output_fasta = os.path.join(OUTPUT_DIR, "aligned_fast.fasta")
    run_swiftalign(INPUT_FILE, output_fasta, extra_args="--mode fast")
    assert os.path.exists(output_fasta)

def test_chunking():
    output_fasta = os.path.join(OUTPUT_DIR, "aligned_chunked.fasta")
    run_swiftalign(INPUT_FILE, output_fasta, extra_args="--chunk_size 1")
    assert os.path.exists(output_fasta)

def test_output_formats():
    for fmt in ["fasta", "clustal", "phylip"]:
        output_fasta = os.path.join(OUTPUT_DIR, f"aligned_{fmt}.{fmt}")
        run_swiftalign(INPUT_FILE, output_fasta, extra_args=f"--format {fmt}")
        assert os.path.exists(output_fasta)

def test_log_file_creation():
    output_fasta = os.path.join(OUTPUT_DIR, "aligned_with_log.fasta")
    log_file = os.path.join(OUTPUT_DIR, "test_run.log")
    
    run_swiftalign(INPUT_FILE, output_fasta, extra_args=f"--log_file {log_file}")
    assert os.path.exists(output_fasta)
    assert os.path.exists(log_file)
    
    with open(log_file, "r") as f:
        log_contents = f.read()
    assert "SwiftAlign" in log_contents
    assert "Hybrid MSA Summary Report" in log_contents

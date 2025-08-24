#!/usr/bin/env python3
"""
Test script for SwiftAlign — Hybrid MSA Tool
Ensures the pipeline runs end-to-end on a small example FASTA file.
"""

import os
import sys
import tempfile
from SwiftAlign.hybrid_msa import main as swiftalign_main

# -------------------- Create Temporary Test FASTA --------------------
test_fasta = tempfile.NamedTemporaryFile(delete=False, suffix=".fasta")
test_fasta.write(b""">seq1
ATGCTAGCTAGCTACGATCG
>seq2
ATGCTAGCTAGCTACGATCC
>seq3
ATGCTAGCTAGCTACGATGG
""")
test_fasta.close()

# Output file
test_output = tempfile.NamedTemporaryFile(delete=False, suffix=".fasta")
test_output.close()

# Log file
log_file = "test_swiftalign.log"

# -------------------- Run SwiftAlign --------------------
sys.argv = [
    "swiftalign",
    "-i", test_fasta.name,
    "-o", test_output.name,
    "--format", "fasta",
    "--chunk_size", "2",
    "--threads", "2",
    "--mode", "accurate",
    "--log_file", log_file
]

print(f"\nRunning SwiftAlign test with input: {test_fasta.name}")
print(f"Output will be saved to: {test_output.name}\n")

try:
    swiftalign_main()
    print(f"\nTest alignment complete. Check log: {log_file}")
except Exception as e:
    print(f"\nError running SwiftAlign test: {e}")

# -------------------- Cleanup --------------------
# Optional: remove temporary files after inspection
# os.unlink(test_fasta.name)
# os.unlink(test_output.name)

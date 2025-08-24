#!/bin/bash
# Run SwiftAlign example alignment using test_sequences.fasta
# This script assumes SwiftAlign is installed and hybrid_msa.py is executable

# Paths
SCRIPT_DIR=$(dirname "$0")
TEST_FASTA="../tests/test_sequences.fasta"
OUTPUT_DIR="${SCRIPT_DIR}/example_outputs"
mkdir -p "$OUTPUT_DIR"

# Run SwiftAlign in accurate mode
echo "Running SwiftAlign (Accurate Mode) on test_sequences.fasta..."
python3 ../SwiftAlign/hybrid_msa.py \
    -i "$TEST_FASTA" \
    -o "${OUTPUT_DIR}/aligned_accurate.fasta" \
    --mode accurate \
    --chunk_size 2 \
    --threads 2 \
    --log_file "${OUTPUT_DIR}/swiftalign.log"

echo "Alignment completed. Check the results in ${OUTPUT_DIR}/"

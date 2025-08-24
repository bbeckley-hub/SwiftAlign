#1. Accurate Mode (Default)

This mode prioritizes alignment quality, with divergence-aware MAFFT and MUSCLE parameters:


python3 hybrid_msa.py \
    -i input_sequences.fasta \
    -o aligned_output.fasta \
    --format fasta \
    --chunk_size 200 \
    --threads 8 \
    --mode accurate \
    --log_file swiftalign.log
#2. Fast Mode

This mode prioritizes speed over maximum accuracy:

python3 hybrid_msa.py \
    -i large_genomes.fasta \
    -o aligned_fast.fasta \
    --format fasta \
    --chunk_size 200 \
    --threads 8 \
    --mode fast \
    --log_file hybrid_fast.log
#3. Additional Options

Output format: Change --format to clustal or phylip for downstream tools:
--format clustal
--format phylip

Chunk size: Adjust --chunk_size to balance memory and parallel speed.

Threads: Increase --threads for more parallelism.

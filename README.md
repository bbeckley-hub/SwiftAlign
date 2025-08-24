# SwiftAlign — Hybrid Multiple Sequence Alignment Tool

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  
[![GitHub stars](https://img.shields.io/github/stars/bbeckley-hub/SwiftAlign?style=social)](https://github.com/bbeckley-hub/SwiftAlign/stargazers)

**SwiftAlign** is a **hybrid multiple sequence alignment (MSA) tool** that leverages the **speed of MAFFT** and the **accuracy of MUSCLE**. It is optimized for **large datasets (>100 genomes/sequences)**, features **automatic parameter tuning**, and offers flexible alignment modes to suit your research needs.

---

## Key Features

- Automatic detection of **DNA or protein sequences**  
- **Fast** and **Accurate** modes for different use-cases  
- Chunked MAFFT alignment for **large datasets**  
- Progressive merging of aligned chunks  
- MUSCLE refinement for **high-quality final alignment**  
- **Parallel processing** with multiple CPU threads  
- Logging, **ETA**, and summary report  
- Output formats: **FASTA**, **Clustal**, **PHYLIP**  

---

## Installation

Make sure the following are installed on your system:

- **Python 3.8+**  
- **Biopython** (`pip install biopython`)  
- **NumPy** (`pip install numpy`)  
- **MAFFT** (system-wide, accessible via PATH)  
- **MUSCLE** (system-wide, accessible via PATH)  

Clone the repository:

```bash
git clone https://github.com/bbeckley-hub/SwiftAlign.git
cd SwiftAlign
  INSTALLATION
#1️⃣ PyPI (pip)

User command to install:

pip install SwiftAlign

#2️⃣ Anaconda (conda)

User command to install:

conda install -c bbeckley-hub SwiftAlign

#3️⃣ Debian (APT)

sudo apt-get install  SwiftAlign

  #USAGE
1. Accurate Mode (Default)

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


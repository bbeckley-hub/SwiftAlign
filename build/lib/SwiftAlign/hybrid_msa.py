#!/usr/bin/env python3
"""
=== SwiftAlign — Hybrid MSA Tool v1.2 (2025-08-24) ===
Author: Beckley Brown <brownbeckley94@gmail.com>
GitHub: https://github.com/bbeckley-hub/SwiftAlign
University of Ghana / K.N.U.S.T
Department of Medical Biochemistry
"""

import argparse
import os
import subprocess
import time
from Bio import SeqIO, AlignIO
from multiprocessing import Pool, Manager
import numpy as np
import shutil
import sys

# -------------------- Logging --------------------
def log(message, log_file=None):
    print(message)
    if log_file:
        with open(log_file, "a") as f:
            f.write(message + "\n")

# -------------------- Header --------------------
def print_header():
    print("="*60)
    print("=== SwiftAlign — Hybrid MSA Tool v1.2 (2025-08-24) ===")
    print("Author: Beckley Brown <brownbeckley94@gmail.com>")
    print("GitHub: https://github.com/bbeckley-hub/SwiftAlign")
    print("University of Ghana / K.N.U.S.T")
    print("Department of Medical Biochemistry")
    print("="*60)

# -------------------- Footer --------------------
def print_footer():
    print("="*60)
    print("SwiftAlign run complete!")
    print("If you use SwiftAlign in your research, please cite:")
    print("Brown, B. (2025). SwiftAlign: Hybrid multiple sequence alignment combining MAFFT + MUSCLE.")
    print("GitHub: https://github.com/bbeckley-hub/SwiftAlign")
    print("="*60)

# -------------------- Find Binary --------------------
BIN_DIR = os.path.join(os.path.dirname(__file__), "..", "bin")

def find_binary(name):
    local_path = os.path.join(BIN_DIR, name)
    if os.path.exists(local_path):
        return local_path
    elif shutil.which(name):
        return shutil.which(name)
    else:
        raise FileNotFoundError(f"{name} not found in {BIN_DIR} or system PATH.")

# -------------------- Binary Version Detection --------------------
MUSCLE_VERSION = None

def log_binary_versions(log_file=None):
    global MUSCLE_VERSION
    binaries = ["mafft", "muscle"]
    for bin_name in binaries:
        try:
            bin_path = find_binary(bin_name)
            result = subprocess.run([bin_path, "--version"] if bin_name=="mafft" else [bin_path, "-version"], capture_output=True, text=True, check=True)
            output = result.stdout.strip() or result.stderr.strip()
            version_info = output.splitlines()[0] if output else "Unknown"
            log(f"{bin_name.upper()} version: {version_info}", log_file)
            if bin_name == "muscle":
                try:
                    MUSCLE_VERSION = int(version_info.split()[1].split('.')[0])
                except Exception:
                    MUSCLE_VERSION = None
        except Exception:
            log(f"Warning: Could not determine {bin_name} version.", log_file)

# -------------------- Sequence Type Detection --------------------
def detect_sequence_type(fasta_file, log_file=None):
    seqs = list(SeqIO.parse(fasta_file, "fasta"))
    dna_bases = set("ATGCNatgcn")
    total_bases = sum(len(seq.seq) for seq in seqs)
    dna_count = sum(sum(1 for b in seq.seq if b in dna_bases) for seq in seqs)
    seq_type = "dna" if total_bases == 0 or dna_count / total_bases > 0.85 else "protein"
    log(f"Sequence type detected: {seq_type.upper()}", log_file)
    return seq_type, seqs

# -------------------- Automatic Parameter Optimization --------------------
def auto_optimize_parameters(seqs, seq_type, mode="accurate", log_file=None):
    lengths = [len(seq.seq) for seq in seqs]
    mean_length = np.mean(lengths)
    std_length = np.std(lengths)
    divergence = std_length / mean_length if mean_length > 0 else 0

    if mode == "fast":
        mafft_method = "auto"
        gap_open = None
        gap_extend = None
        muscle_max_iter = 8
    else:
        if seq_type == "protein":
            mafft_method = "linsi" if divergence > 0.05 else "auto"
        else:
            mafft_method = "einsi" if divergence > 0.05 else "auto"
        gap_open = 1.5 if divergence > 0.1 else 1.0 if divergence > 0.05 else None
        gap_extend = 0.2 if divergence > 0.1 else 0.1 if divergence > 0.05 else None
        muscle_max_iter = 32 if divergence > 0.05 else 16

    log(f"Auto-optimized parameters for mode '{mode}':", log_file)
    log(f"  MAFFT method: {mafft_method}", log_file)
    log(f"  Gap open: {gap_open}, Gap extend: {gap_extend}", log_file)
    log(f"  MUSCLE max iterations: {muscle_max_iter}", log_file)
    return mafft_method, gap_open, gap_extend, muscle_max_iter

# -------------------- Chunking --------------------
def chunk_fasta(seqs, chunk_size, log_file=None):
    chunks = []
    for i in range(0, len(seqs), chunk_size):
        chunk_file = f"chunk_{i//chunk_size}.fasta"
        SeqIO.write(seqs[i:i+chunk_size], chunk_file, "fasta")
        chunks.append(chunk_file)
    log(f"Total chunks created: {len(chunks)}", log_file)
    return chunks

# -------------------- MAFFT with fallback --------------------
def run_mafft_with_fallback(mafft_cmd, output_file, chunk_file, log_file=None):
    try:
        subprocess.run(mafft_cmd, stdout=open(output_file, "w"), check=True)
        return True
    except subprocess.CalledProcessError:
        log(f"MAFFT failed on {chunk_file} with command: {' '.join(mafft_cmd)}", log_file)
        return False

def run_mafft_chunk(args):
    chunk_file, seq_type, mafft_method, gap_open, gap_extend, threads, idx, total_chunks, start_time, completed_counter, log_file = args
    output_file = f"{chunk_file}.aligned.fasta"

    seq_count = sum(1 for _ in SeqIO.parse(chunk_file, "fasta"))
    if seq_count <= 1:
        log(f"Skipping MAFFT for {chunk_file} (only {seq_count} sequence).", log_file)
        return chunk_file

    def build_cmd(method):
        cmd = [find_binary("mafft"), "--thread", str(threads)]
        if method == "linsi":
            cmd += ["--localpair", "--maxiterate", "1000"]
        elif method == "einsi":
            cmd += ["--genafpair", "--maxiterate", "1000"]
        elif method == "ginsi":
            cmd += ["--globalpair", "--maxiterate", "1000"]
        elif method == "auto":
            cmd.append("--auto")
        if gap_open is not None: cmd += ["--op", str(gap_open)]
        if gap_extend is not None: cmd += ["--ep", str(gap_extend)]
        cmd.append(chunk_file)
        return cmd

    methods_to_try = [mafft_method, "ginsi", "linsi", "auto"]
    tried = set()
    success = False
    for method in methods_to_try:
        if method in tried: 
            continue
        tried.add(method)
        cmd = build_cmd(method)
        log(f"Trying MAFFT method '{method}' on {chunk_file}...", log_file)
        if run_mafft_with_fallback(cmd, output_file, chunk_file, log_file):
            success = True
            break

    if not success:
        log(f"All MAFFT strategies failed for {chunk_file}. Exiting.", log_file)
        sys.exit(1)

    completed_counter.value += 1
    elapsed = time.time() - start_time
    avg_time = elapsed / completed_counter.value
    remaining = (total_chunks - completed_counter.value) * avg_time
    log(f"[{completed_counter.value}/{total_chunks}] Completed {chunk_file} in {elapsed:.2f} sec, ETA: {remaining:.2f} sec", log_file)
    return output_file

# -------------------- Progressive Merge --------------------
def progressive_merge(aligned_files, seq_type, mafft_method, gap_open, gap_extend, threads, log_file=None):
    step = 1
    while len(aligned_files) > 1:
        merged_files = []
        for i in range(0, len(aligned_files), 2):
            if i+1 < len(aligned_files):
                out_file = f"merged_{step}_{i//2}.fasta"

                def build_cmd(method):
                    cmd = [find_binary("mafft"), "--thread", str(threads), "--merge", aligned_files[i], aligned_files[i+1]]
                    if method == "linsi":
                        cmd.insert(1, "--localpair")
                        cmd.insert(2, "--maxiterate")
                        cmd.insert(3, "1000")
                    elif method == "einsi":
                        cmd.insert(1, "--genafpair")
                        cmd.insert(2, "--maxiterate")
                        cmd.insert(3, "1000")
                    elif method == "ginsi":
                        cmd.insert(1, "--globalpair")
                        cmd.insert(2, "--maxiterate")
                        cmd.insert(3, "1000")
                    elif method == "auto":
                        cmd.insert(1, "--auto")
                    if gap_open: cmd += ["--op", str(gap_open)]
                    if gap_extend: cmd += ["--ep", str(gap_extend)]
                    return cmd

                methods_to_try = [mafft_method, "ginsi", "linsi", "auto"]
                success = False
                for method in methods_to_try:
                    log(f"Trying MAFFT merge method '{method}' on {aligned_files[i]} + {aligned_files[i+1]}...", log_file)
                    cmd = build_cmd(method)
                    if run_mafft_with_fallback(cmd, out_file, f"{aligned_files[i]}+{aligned_files[i+1]}", log_file):
                        success = True
                        break
                if not success:
                    log(f"All MAFFT merge strategies failed. Exiting.", log_file)
                    sys.exit(1)

                merged_files.append(out_file)
                os.remove(aligned_files[i])
                os.remove(aligned_files[i+1])
            else:
                merged_files.append(aligned_files[i])
        aligned_files = merged_files
        log(f"Progressive merge step {step} complete. {len(aligned_files)} files remaining.", log_file)
        step += 1
    return aligned_files[0]

# -------------------- MUSCLE Refinement --------------------
def run_muscle(input_fasta, output_fasta, max_iter=16, log_file=None):
    start = time.time()
    muscle_path = find_binary("muscle")
    cmd = [muscle_path, "-in", input_fasta, "-out", output_fasta, "-maxiters", str(max_iter)]

    try:
        subprocess.run(cmd, check=True)
        elapsed = time.time() - start
        log(f"MUSCLE refinement completed in {elapsed:.2f} sec", log_file)
    except subprocess.CalledProcessError as e:
        log(f"Error running MUSCLE: {e}", log_file)
        sys.exit(1)

# -------------------- Convert Format --------------------
def convert_format(input_fasta, output_file, out_format, log_file=None):
    alignment = AlignIO.read(input_fasta, "fasta")
    AlignIO.write(alignment, output_file, out_format)
    log(f"Alignment saved in {out_format} format at: {output_file}", log_file)
    return alignment

# -------------------- Main Pipeline --------------------
def main():
    print_header()

    parser = argparse.ArgumentParser(description="SwiftAlign: Hybrid MSA with Auto-Parameter Optimization + MAFFT Fallbacks")
    parser.add_argument("-i", "--input", required=True, help="Input FASTA file")
    parser.add_argument("-o", "--output", required=True, help="Output alignment file")
    parser.add_argument("--format", default="fasta", choices=["fasta", "clustal", "phylip"])
    parser.add_argument("--chunk_size", type=int, default=200, help="Sequences per chunk")
    parser.add_argument("--threads", type=int, default=4, help="CPU threads for MAFFT")
    parser.add_argument("--mode", default="accurate", choices=["fast", "accurate"],
                        help="Alignment mode: 'fast' for speed, 'accurate' for quality")
    parser.add_argument("--log_file", default="swiftalign.log", help="Optional log file")
    args = parser.parse_args()

    log_file = args.log_file
    log(f"SwiftAlign pipeline started at {time.ctime()}", log_file)
    log_binary_versions(log_file)

    seq_type, seqs = detect_sequence_type(args.input, log_file)
    mafft_method, gap_open, gap_extend, muscle_max_iter = auto_optimize_parameters(seqs, seq_type, args.mode, log_file)
    chunks = chunk_fasta(seqs, args.chunk_size, log_file)

    manager = Manager()
    completed_counter = manager.Value('i', 0)
    start_time = time.time()

    pool = Pool(processes=args.threads)
    task_args = [(chunk, seq_type, mafft_method, gap_open, gap_extend, 1, idx+1, len(chunks), start_time, completed_counter, log_file)
                  for idx, chunk in enumerate(chunks)]
    results = [pool.apply_async(run_mafft_chunk, (ta,)) for ta in task_args]
    pool.close()
    pool.join()
    aligned_chunks = [r.get() for r in results]

    merged_file = progressive_merge(aligned_chunks, seq_type, mafft_method, gap_open, gap_extend, args.threads, log_file)

    temp_muscle = "muscle_final_temp.fasta"
    run_muscle(merged_file, temp_muscle, max_iter=muscle_max_iter, log_file=log_file)

    alignment = convert_format(temp_muscle, args.output, args.format, log_file)

    os.remove(merged_file)
    os.remove(temp_muscle)

    total_runtime = time.time() - start_time
    num_sequences = len(alignment)
    alignment_length = alignment.get_alignment_length()

    log("\n=== SwiftAlign Summary Report ===", log_file)
    log(f"Input sequences (approx.): {len(seqs)}", log_file)
    log(f"Total chunks processed: {len(chunks)}", log_file)
    log(f"Final number of sequences: {num_sequences}", log_file)
    log(f"Alignment length: {alignment_length} residues", log_file)
    log(f"Total runtime: {total_runtime:.2f} sec ({total_runtime/60:.2f} min)", log_file)
    log("================================", log_file)

    print_footer()

if __name__ == "__main__":
    main()

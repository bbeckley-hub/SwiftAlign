# SwiftAlign Parameters Reference

**Hybrid MSA Tool – MAFFT + MUSCLE**
Author: Beckley Brown `<brownbeckley94@gmail.com>`
GitHub: [bbeckley-hub/SwiftAlign](https://github.com/bbeckley-hub/SwiftAlign)

---

## 1. Input / Output

| Parameter        | Description                                          | Default  | Notes                                 |
| ---------------- | ---------------------------------------------------- | -------- | ------------------------------------- |
| `-i`, `--input`  | Input FASTA file containing DNA or protein sequences | Required | Supports `.fasta`, `.fa`              |
| `-o`, `--output` | Output file for aligned sequences                    | Required | Format depends on `--format`          |
| `--format`       | Output format                                        | `fasta`  | Options: `fasta`, `clustal`, `phylip` |

**Example:**

```bash
swiftalign -i examples/example_dna.fasta -o aligned_dna.fasta --format clustal
```

---

## 2. Alignment Modes

| Parameter | Description    | Default    | Notes                                                |
| --------- | -------------- | ---------- | ---------------------------------------------------- |
| `--mode`  | Alignment mode | `accurate` | Options: `fast` (speed) or `accurate` (high-quality) |

* `fast`: fewer iterations, lighter algorithms, optimized for large datasets.
* `accurate`: iterative refinement, optimized gap penalties, high-quality alignment.

**Example:**

```bash
swiftalign -i examples/example_protein.fasta -o aligned_protein.fasta --mode fast
```

---

## 3. MAFFT Parameters

| Parameter      | Description                         | Default | Notes                                                                                |
| -------------- | ----------------------------------- | ------- | ------------------------------------------------------------------------------------ |
| `mafft_method` | MAFFT algorithm method              | Auto    | Auto-selected based on mode and sequence divergence (e.g., `auto`, `linsi`, `einsi`) |
| `--chunk_size` | Number of sequences per MAFFT chunk | 200     | Useful for datasets >100 sequences                                                   |
| `gap_open`     | Gap opening penalty                 | Auto    | Set automatically based on divergence                                                |
| `gap_extend`   | Gap extension penalty               | Auto    | Set automatically based on divergence                                                |
| `--threads`    | Number of CPU threads               | 4       | Can increase speed on multi-core systems                                             |

**Example:**

```bash
swiftalign -i my_sequences.fasta -o aligned.fasta --chunk_size 500 --threads 8
```

---

## 4. MUSCLE Parameters

| Parameter    | Description                              | Default      | Notes                                           |
| ------------ | ---------------------------------------- | ------------ | ----------------------------------------------- |
| `max_iter`   | Maximum iterations for MUSCLE refinement | Auto (16–32) | Adjusted based on mode and sequence divergence  |
| `gap_open`   | Gap opening penalty                      | Auto         | Inherited from MAFFT optimization if applicable |
| `gap_extend` | Gap extension penalty                    | Auto         | Inherited from MAFFT optimization if applicable |

**Example:**

```bash
swiftalign -i large_dataset.fasta -o refined_alignment.fasta --mode accurate
```

---

## 5. Logging & Progress

| Parameter    | Description      | Default          | Notes                                           |
| ------------ | ---------------- | ---------------- | ----------------------------------------------- |
| `--log_file` | Path to log file | `hybrid_msa.log` | Logs progress, ETA, banners, and summary report |

**Example:**

```bash
swiftalign -i sequences.fasta -o aligned.fasta --log_file mylog.log
```

---

## Notes & Tips

* **Auto-Optimization:** SwiftAlign automatically tunes MAFFT and MUSCLE parameters based on sequence type (DNA/protein), divergence, and selected mode.
* **Chunking:** Large datasets are split into chunks for faster MAFFT alignment and merged progressively before MUSCLE refinement.
* **Modes:**

  * `fast`: prioritizes speed with lighter alignment strategies.
  * `accurate`: prioritizes alignment quality with iterative refinement.

**Recommended Workflow for Large Datasets (>500 sequences):**

1. Use `--mode fast` for initial testing and to check data.
2. Use `--mode accurate` for the final high-quality alignment.
3. Adjust `--chunk_size` and `--threads` according to available memory and CPU cores

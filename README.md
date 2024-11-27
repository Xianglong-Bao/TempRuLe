# Explainable Temporal Knowledge Graph Reasoning via Expressive Logic Rules

Hello :)

This is the anonymous code repository for the paper **"Explainable Temporal Knowledge Graph Reasoning via Expressive Logic Rules."** Below, you will find detailed instructions on how to set up the environment, run the code, and reproduce our experimental results.

---

## Table of Contents
- [Environment Configuration](#environment-configuration)
- [Possible Issues](#possible-issues)
- [Run](#run)
- [Experimental Results with Varying Seed Numbers](#experimental-results-with-varying-seed-numbers)

---

## Environment Configuration
We have bundled the environment requirements into `pyproject.toml`. To install the dependencies specified in `pyproject.toml`, run the following command:
 ```bash
 poetry install
 ```
Make sure to execute this command in the project directory. You can perform this step within a Conda virtual environment if desired.

If Poetry is not installed on your system, you can install it using:
 ```bash
 pip install poetry
 ```

---

## Possible Issues

### 1. Installation Error: `No file/folder found for package logical-tkgs`
   - Solution: Use the `--no-root` parameter during installation:
     ```bash
     poetry install --no-root
     ```

---

## Run

To reproduce our experiments, use the following commands for each dataset. Replace placeholders (`XXXXXX.json` and `YYYYYY.json`) with the appropriate file names generated during execution.

### ICEWS14 Dataset
1. **Temporal Rule Generation**:
   
   ```bash
   python learn.py -d icews14 -l 1 2 3 -n 2000 -p 20 -s 12
   ```
   This generates a file like `XXXXXX.json`.
   
2. **Apply the Rule**:
   
   ```bash
   python apply.py -d icews14 -r XXXXXX.json -l 1 2 3 -w 0 -p 20
   ```
   This generates a file like `YYYYYY.json`.
   
3. **Evaluate the Results**:
   
   ```bash
   python evaluate.py -d icews14 -c YYYYYY.json
   ```

### ICEWS18 Dataset
```bash
python learn.py -d icews18 -l 1 2 3 -n 2000 -p 20 -s 12
python apply.py -d icews18 -r XXXXXX.json -l 1 2 3 -w 200 -p 6
python evaluate.py -d icews18 -c YYYYYY.json
```

### ICEWS0515 Dataset
```bash
python learn.py -d icews0515 -l 1 2 3 -n 2000 -p 20 -s 12
python apply.py -d icews0515 -r XXXXXX.json -l 1 2 3 -w 500 -p 20
python evaluate.py -d icews0515 -c YYYYYY.json
```

---

## Experimental Results with Varying Seed Numbers

The following table summarizes the performance of our model on the ICEWS14 dataset using different seed numbers.


| Seed Number                   | MRR      | hit@1    | hit@3    | hit@10   |
|-------------------------------|----------|----------|----------|----------|
| 12 (The results in the paper) | 0.562006 | 0.525223 | 0.569127 | 0.638784 |
| 1                             | 0.562631 | 0.526017 | 0.569430 | 0.638973 |
| 2                             | 0.560175 | 0.523068 | 0.568106 | 0.636893 |
| 3                             | 0.567365 | 0.531992 | 0.574497 | 0.641885 |
| 4                             | 0.564409 | 0.527341 | 0.570754 | 0.640561 |
| 5                             | 0.565304 | 0.529912 | 0.571736 | 0.637914 |
| 6                             | 0.565455 | 0.529610 | 0.573438 | 0.637649 |
| 7                             | 0.555440 | 0.517584 | 0.562812 | 0.634662 |
| 8                             | 0.563587 | 0.527416 | 0.570602 | 0.637952 |
| 9                             | 0.560206 | 0.523710 | 0.567312 | 0.636704 |
| 10                            | 0.555619 | 0.518870 | 0.563115 | 0.632431 |
| 11                            | 0.559532 | 0.522538 | 0.566253 | 0.636553 |


---

If you have any questions or encounter issues, feel free to reach out!

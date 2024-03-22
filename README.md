# Explainable Temporal Knowledge Graph Reasoning via Expressive Logic Rules

Hello :)

This is the anonymous code repository for the paper 
`Explainable Temporal Knowledge Graph Reasoning via Expressive Logic Rules`
Next, I will guide you on how to run and reproduce our experimental results. Let's get started!

<h3> Environment Configuration </h3>

We have bundled the environment requirements into `pyproject.toml`. Please run the command `poetry install` to install the relevant dependencies specified in `pyproject.toml`. Please note that this command should be executed in the project directory. This step can be performed within a conda virtual environment. If you haven't installed poetry beforehand, execute the command `pip install poetry` to install poetry.

<h3> Possible Issues </h3>

If you encounter an error like `The current project could not be installed: No file/folder found for package logical-tkgs` during the`poetry install` process, don't worry. Simply add the parameter `--no-root` to the command.

<h3> Run </h3>

If you want to replicate our experiments, you can execute the following commands:
Please note that the `XXXXXX.json` file will be generated after the completion of the learn.py execution, and the `YYYYYY.json` file will be generated after the completion of the apply.py execution.

ICEWS14
`python learn.py -d icews14 -l 1 2 3 -n 2000 -p 20 -s 12`
`python apply.py -d icews14 -r XXXXXX.json -l 1 2 3 -w 0 -p 20`
`python evaluate.py -d icews14 -c yyyyyy.json`

ICEWS18
`python learn.py -d icews18 -l 1 2 3 -n 2000 -p 20 -s 12`
`python apply.py -d icews18 -r XXXXXX.json -l 1 2 3 -w 200 -p 6`
`python evaluate.py -d icews18 -c yyyyyy.json`

ICEWS0515
`python learn.py -d icews0515 -l 1 2 3 -n 2000 -p 20 -s 12`
`python apply.py -d icews0515 -r XXXXXX.json -l 1 2 3 -w 500 -p 20`
`python evaluate.py -d icews0515 -c yyyyyy.json`

<h3> Experimental results on the ICEWS14 with varying seed numbers </h3>

| Seed Number                   | hit@1    | hit@3    | hit@10   | MRR      |
|-------------------------------|----------|----------|----------|----------|
| 12 (The results in the paper) | 0.525223 | 0.569127 | 0.638784 | 0.562006 |
| 1                             | 0.526017 | 0.569430 | 0.638973 | 0.562631 |
| 2                             | 0.523068 | 0.568106 | 0.636893 | 0.560175 |
| 3                             | 0.531992 | 0.574497 | 0.641885 | 0.567365 |
| 4                             | 0.527341 | 0.570754 | 0.640561 | 0.564409 |
| 5                             | 0.529912 | 0.571736 | 0.637914 | 0.565304 |
| 6                             | 0.529610 | 0.573438 | 0.637649 | 0.565455 |
| 7                             | 0.517584 | 0.562812 | 0.634662 | 0.555440 |
| 8                             | 0.527416 | 0.570602 | 0.637952 | 0.563587 |
| 9                             | 0.523710 | 0.567312 | 0.636704 | 0.560206 |
| 10                            | 0.518870 | 0.563115 | 0.632431 | 0.555619 |

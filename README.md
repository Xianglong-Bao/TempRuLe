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

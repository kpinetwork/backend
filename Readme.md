## KPINetwork Backend

This is the repository for the backend services and their common codebase

# Getting started

Follow the next instructions to get the project ready to use.

## Requirements:

- [Python version 3](https://www.python.org/download/releases/3.0/) (recommended 3.8 or less) in your path. It will install
  automatically [pip](https://pip.pypa.io/en/stable/) as well.
- A virtual environment, namely [.venv](https://docs.python.org/3/library/venv.html).

### Create a virtual environment

Execute the next command at the root of the project:

```shell
python -m venv .venv
```

**Activate the environment**

Windows:
```shell
.venv\Scripts\activate.bat
```

In Unix based operative systems:

```shell
source .venv/bin/activate
```

## Dependencies:

The dependencies are defined inside requirements' folder, here you can 
define your dependencies to production(prod.txt) or development(dev.txt)
environment, in prod.txt are defined all required dependencies to project
can execute, meanwhile in dev.txt are defined dependencies to test 
or validate the code for example pre-commit package. 

### Installation

#### Dependencies

Execute the next command once you have created the venv:

```shell
pip install -r requirements/envs/dev.txt
```

#### Pre-commits hooks

The library will take configuration from `.pre-commit-config.yaml` and will set up the hooks by us.

If pre-commits event doesn't validates nothing before a commit has been done,
you need run the next:

```shell
pre-commit install
pre-commit install --hook-type commit-msg 
```

```shell
Note: In first commit the event is slow, because preparate the hooks and the environment to run the validations.  
```

### Talisman
The project uses [talisman](https://github.com/thoughtworks/talisman) to avoid credentials 
in code, to use this library in a pre-commit hook is necessary the installation of golang, 
you can use this page https://golang.org/doc/install to install it according to your OS.

## Test
This project uses [pytest](https://docs.pytest.org/en/6.2.x/) to execute unit tests, you can run the tests with the following command:

```shell
python -m pytest src/tests/*
```

In case you get some errors when removing or adding a file, please use these flags:

```shell
python -m pytest  --cache-clear src/tests/* --collect-only
```

## Branch names format

For example if your task in Jira is **KPI-48 implement semantic versioning** your branch name is:

```shell
KPI-48-implement-semantic-versioning
```

## Semantic versioning

The project use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) as the
standard commit message style.

### Commit message style

Use the following commit message style. e.g:

```shell
'feat: KPI-123 Applying some changes'
'fix: KPI-321 Fixing something broken'
'feat(config): KPI-00 Fix something in config files'
```

The value `KPI-###` refers to the Jira issue that is being solved. Use KPI-00 if the commit does not refer to any issue.

If you need check the commit message before make a real 
commit, you can use this command:

```shell
cz check -m "fix: KPI-00 check commit message" 
```

## Docker file
Lambdas aws environment can be tested with docker image, use the following Dockerfile

```
FROM amazon/aws-lambda-python:3.6
ENV VAR=<value>                                                                                                                      

COPY dist/<handler>.zip ./
RUN unzip <handler>.zip

COPY requirements/docker/requirements.txt  ./
RUN  pip3 install -r requirements.txt
CMD [ "<handler>.handler" ]

```

## Code Style

The project use [PEP 8](https://www.python.org/dev/peps/pep-0008/) as the
standard code style.

### Validating code style

In pre-commit event the code style is validated, but you can use the following command to validate the style:

```shell
flake8 src/*
```

Additionally, you can run the next command to set the correct format in your code,

```shell
black {source_file_or_directory}
```

## Git hooks

We use [pre-commit](https://pre-commit.com/) library to manage local git hooks.

This library allows you to execute validations right before the commit, for example:
- Check if the commit contains the correct formatting.
- Execute unit tests.
- Format modified files based on a Style Guide such as PEP 8, etc.
- Prevent credentials in code


## Built with

- [Python version 3](https://www.python.org/download/releases/3.0/) as backend programming language. Strong typing for
  the win.
- [Coverage](https://coverage.readthedocs.io/en/coverage-4.5.4/) for code coverage.
- [Black](https://pypi.org/project/black/) to format the code.
- [Flake8](https://pypi.org/project/flake8/) to validate the code style.
- [Pre-commit](https://pre-commit.com) to execute GitHub hooks before a commit.
- [Commitizen](https://github.com/commitizen-tools/commitizen) to define a standard way of committing rules.
- [Talisman](https://github.com/thoughtworks/talisman) to ensure that potential secrets or sensitive information do not leave the developer's workstation.
- [Terraform](https://www.terraform.io) to define the infrastructure as code
- [Juniper](https://github.com/eabglobal/juniper) to stream and standardize the creation of a zip artifact for a set of AWS Lambda functions.

## License

Copyright 2021 ioet Inc. All Rights Reserved.

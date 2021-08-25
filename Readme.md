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

##Dependencies:

The dependencies are defined inside requirements' folder, here you can 
define your dependencies to production(prod.txt) or development(dev.txt)
environment, in prod.txt are defined all required dependencies to project
can execute, meanwhile in dev.txt are defined dependencies to test 
or validate the code for example pre-commit package. 

###Installation

Execute the next command once you have created the venv:

```shell
pip install -r requirements/dev.txt
```

##Branch names format

For example if your task in Jira is **KPI-48 implement semantic versioning** your branch name is:

```shell
KPI-48-implement-semantic-versioning
```

## Semantic versioning
We use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) as the
standard commit message style.
###Commit message style

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

##Git hooks

We use [pre-commit](https://pre-commit.com/) library to manage local git hooks.

This library allows you to execute validations right before the commit, for example:
- Check if the commit contains the correct formatting.
- Execute unit tests.
- Format modified files based on a Style Guide such as PEP 8, etc.

With this command the library will take configuration from `.pre-commit-config.yaml` and will set up the hooks by us.

## Built with

- [Python version 3](https://www.python.org/download/releases/3.0/) as backend programming language. Strong typing for
  the win.
- [Coverage](https://coverage.readthedocs.io/en/coverage-4.5.4/) for coverage.
  
## License

Copyright 2021 ioet Inc. All Rights Reserved.

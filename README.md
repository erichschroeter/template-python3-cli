# FIXME Development Environment Setup
A template repository for jump-starting creating a Python 3 CLI program.

This guide will help you set up the development environment for the FIXME project.
The project uses Python 3.10 and manages dependencies using Pipenv.

## Prerequisites
- Python 3.10 or higher
- Pipenv (install using `pip install pipenv`)

## Getting Started

1. Clone the repository and change to the project directory:
   ```bash
   git clone https://github.com/fixme/fixme.git
   cd fixme
   ```
2. Install project dependencies:
   ```bash
   pipenv install --dev
   ```

## Available Commands

To run the project or execute various tasks, you can use the following commands:

- Run the program:
  ```bash
  python -m fixme --help
  ```

- Run tests with code coverage:
  ```bash
  pipenv run pytest --cov=fixme
  ```

- Perform static code analysis using Flake8 (should match _"Lint with Flake8"_ step in `.github/workflows/python-app.yml`):
  ```bash
  # stop the build if there are Python syntax errors or undefined names
  pipenv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
  # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
  pipenv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
  ```


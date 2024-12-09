# Python LLM task
Repository with source code to simulate integration with an LLM to summarize each section of a regulatory text file.

## Assumptions

It is assumed that each new section starts with 'Section N' where N is an integer and all text until the next word 'Section' (or EOF) belongs to the current section.

In this example LLM integration is simulated by the following transformation of original section text:
 - text is normalized by removing all special symbols, new lines and extra spaces;
 - all words from normalized section text are returned in the reversed order.

## Project structure

```bash
├───extract_requirements.py      # Source code
├───extracted_requirements.json  # Script output
├───README.md                    # Project description
├───regulations.txt              # Sample regulations text file 
├───requirements.txt             # Python version control file
```

## Setup

#### Setup virtual environment

```bash
>> python -m venv .venv
>> source .venv/bin/activate
>> pip install -r requirements.txt
```

### How to run the script

#### With default parameters

```bash
>> source .venv/bin/activate
>> python extract_requirements.py
```

#### With user input

Typer library is used here to provide user input. To see input options, type

```bash
>> python extract_requirements.py --help
```

To change input filename, for example, type:

```bash
>> python extract_requirements.py --input-filename regulations.txt
```

To change output filename, for example, type:

```bash
>> python extract_requirements.py --output-filename output.csv
```
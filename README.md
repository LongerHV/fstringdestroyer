# Fstring destroyer

Quick and dirty script to replace python f-string interpolation with literal values.

## Usage

```bash
# clone the repo
git clone https://github.com/LongerHV/fstringdestroyer
cd fstringdestroyer

# venv
python -m venv .venv
. .venv
python -m pip install -r requirements.txt

# Dry run
python main.py /path/to/your/file.py

# Update file in place (MAKE SURE TO MAKE A BACKUP!!!)
python main.py --inplace /path/to/your/file.py

# Or many files
python main.py --inplace /path/to/your/directory/*.py
```

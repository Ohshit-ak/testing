# Combined Workspace README

This workspace contains three testing-focused areas:

- blackbox: Black-box API tests and bug report for QuickCart
- integration : StreetRace Manager integration code and tests
- whitebox: Moneypoly game implementation and tests

## Prerequisites

- Linux (or any OS with Python 3.10+)
- Python virtual environment available at .venv (already present in this workspace)

## Setup

From the workspace root:

```bash
cd 
```

## Run Code

### Integration system (StreetRace Manager)

```bash
cd integration /code
python main.py
```

### Moneypoly game

```bash
cd whitebox/moneypoly
python main.py
```

### Blackbox area

```bash
cd blackbox
docker load -i quickcart_image.tar
docker run -p 8080:8080 quickcart
```

## Run Tests

Run from workspace root:



### Integration tests

```bash
cd integration
cd tests
pytest -v 
```

### Blackbox tests

```bash
cd blackbox
cd tests
pytest -v
or 
pytest {file_name} -v ("for better results")
```

### Moneypoly tests

```bash
cd whitebox
cd tests
pytest -v
```

## Reports

- blackbox report: blackbox/report.pdf
- integration report: integration /report.pdf
- moneypoly report: moneypoly/report.pdf

## Placeholder Links

- GitHub: [https://github.com/Ohshit-ak/testing]


# Combined Workspace README

This workspace contains three testing-focused areas:

- blackbox: Black-box API tests and bug report for QuickCart
- integration : StreetRace Manager integration code and tests
- moneypoly: Moneypoly game implementation and tests

## Prerequisites

- Linux (or any OS with Python 3.10+)
- Python virtual environment available at .venv (already present in this workspace)

## Setup

From the workspace root:

```bash
cd /home/akshith-kandagtla/Desktop/testing
source .venv/bin/activate
```

## Run Code

### Integration system (StreetRace Manager)

```bash
cd '/home/akshith-kandagtla/Desktop/testing/integration /code'
python main.py
```

### Moneypoly game

```bash
cd /home/akshith-kandagtla/Desktop/testing/moneypoly/moneypoly
python main.py
```

### Blackbox area

The blackbox folder contains tests/reporting assets and no local application entrypoint script in this workspace.

## Run Tests

Run from workspace root:

```bash
cd /home/akshith-kandagtla/Desktop/testing
source .venv/bin/activate
```

### Integration tests

```bash
python -m pytest 'integration /tests' -v
```

### Blackbox tests

```bash
python -m pytest blackbox/tests -v
```

### Moneypoly tests

```bash
python -m pytest moneypoly/moneypoly/test -v
```

### Run all tests in one command

```bash
python -m pytest 'integration /tests' blackbox/tests moneypoly/moneypoly/test -v
```

## Reports

- blackbox report: blackbox/report.md
- integration report: integration /report.md
- moneypoly report: moneypoly/report.md

## Placeholder Links

- Project documentation link: [ADD_LINK_HERE]
- Demo/video link: [ADD_LINK_HERE]
- API/base URL link: [ADD_LINK_HERE]

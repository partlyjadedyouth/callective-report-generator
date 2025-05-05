# How to run this script

## Step 1. Install uv

uv를 사용해보신 적이 없다면 설치해주세요.

```bash
# MacOS
brew install uv
```

## Step 2. Clone git repository

이 repository를 clone해주세요.

```bash
cd ~/

git clone https://github.com/partlyjadedyouth/callective-report-generator
```

## Step 3. uv init

```bash
cd ~/callective-report-generator

uv add -r requirements.txt
```

## Step 4. Run

```bash
uv run src/main.py --sheet_key=[SHEET_KEY] --week=[WEEK_NUMBER]
```

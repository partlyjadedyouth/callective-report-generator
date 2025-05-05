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
```

```bash
git clone https://github.com/partlyjadedyouth/callective-report-generator
```

## Step 3. uv init

```bash
cd ~/callective-report-generator
```

```bash
uv add -r requirements.txt
```

## Step 4. Run

```bash
uv run src/main.py --sheet_key=[SHEET_KEY] --week=[WEEK_NUMBER]
```

SHEET_KEY는 구글 스프레드시트 URL에서 `/d/` 와 `/edit?gid=...` 사이에 있는 부분입니다.
`https://docs.google.com/spreadsheets/d/[SHEET_KEY]/edit?gid=247967581#gid=247967581`

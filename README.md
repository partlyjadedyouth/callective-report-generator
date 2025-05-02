# Survey Results Analyzer

This project fetches survey data from Google Sheets, processes it, and generates analysis reports.

## Features

- Fetches data from Google Spreadsheets
- Processes survey responses
- Calculates per-participant averages for BAT_primary, BAT_secondary, emotional_labor, and stress
- Generates per-participant type-specific averages within each category
- Organizes analysis results by participant with all weeks' data in a single file

## Running the code

```bash
python src/main.py --sheet_key=YOUR_SHEET_KEY --week=WEEK_NUMBER
```

Where:

- `YOUR_SHEET_KEY` is the Google Sheet key/ID
- `WEEK_NUMBER` is the week number (e.g., 0 for "0주차")

## Output

The code generates the following outputs:

- CSV data in `data/csv/`
- Survey results in `data/results/` (e.g., `0주차.json`)
- Participant analysis in `data/analysis/participant_analysis.json`

The analysis results are structured with a participant-oriented approach:

```json
[
  {
    "name": "참여자 이름",
    "team": "소속 팀",
    "role": "직무",
    "analysis": {
      "0주차": {
        "category_averages": { ... },
        "type_averages": { ... }
      },
      "2주차": {
        "category_averages": { ... },
        "type_averages": { ... }
      }
    }
  },
  ...
]
```

This allows comparing a participant's responses across different weeks.

```bash
uv sync
```

```bash
uv pip install -r requirements.txt
```

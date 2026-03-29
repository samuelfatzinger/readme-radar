# readme-radar

CLI tool that finds GitHub repositories with weak or missing README files to identify documentation contribution opportunities.

## Overview

readme-radar searches GitHub repositories, analyzes README quality, and ranks projects that could benefit from documentation improvements. It is designed for technical writers and contributors looking for meaningful documentation work.

## Features

- GitHub repository search
- README quality scoring
- Missing section detection
- Candidate labeling
- Ranked results (worst first)
- Compact output mode
- JSON export
- Top issue summary

## Setup

- Python 3.10+
- GitHub Personal Access Token

Create a `.env` file: 

```env
GITHUB_TOKEN=your_token_here
```

Install dependencies:

```bash
pip install requests python-dotenv
```

## Usage

Search with default settings:

```bash
python readme_radar.py
```

Search with query:

```bash
python readme_radar.py "python cli"
```

Limit results:

```bash
python readme_radar.py "python cli" 25
```

Compact mode:

```bash
python readme_radar.py "python cli" --compact
```

Show only top results:

```bash
python readme_radar.py "python cli" --show 5
```

Export JSON:

```bash
python readme_radar.py "python cli" --json
```

Save JSON:

```bash
python readme_radar.py "python cli" --json results.json
```

### Pagination

You can start scanning from a later GitHub results page:

```bash
python readme_radar.py "python cli" 100 --start-page 3
```

## Options

`--show N`  
Limit the number of displayed results.

`--compact`  
Show condensed output.

`--json`  
Output results as JSON.

`--json filename.json`  
Save results to a JSON file.

`--start-page N`  
Begin GitHub search from a specific results page.

## Example

compact output recommended:

```bash
python readme_radar.py "python cli" 100 --start-page 3 --compact --show 1
```

```
readme-radar
============
Query: python cli
Fetched: 100
Skipped: 19
Analyzed: 81
Flagged: 75
Shown: 1
Start page: 3
Strong candidates: 1
Good candidates: 0

Top issues:
2 - README under 100 words
1 - Missing README

1. STRONG CANDIDATE | user/repo | stars: 12 | score: 92 | README under 100 words
   https://github.com/user/repo
   other issues:
   - Missing Installation section
   - Missing Usage section
```

## Why This Exists

Many open source projects lack clear README documentation. readme-radar helps surface repositories where documentation improvements can have the most impact.

## License

MIT License. See LICENSE file for details.

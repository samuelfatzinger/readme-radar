# Changelog

All notable changes to readme-radar will be documented in this file.

## v0.1.2

### Added
- GitHub search pagination to fetch multiple result pages instead of only the first page.
- `--start-page` option to begin scanning from a specified GitHub search results page.
- Summary header metrics:
  - Fetched
  - Skipped
  - Analyzed
  - Flagged
  - Shown
  - Start page

### Changed
- Increased fetch depth so the tool can analyze more repositories before applying display limits.
- Changed summary label from `Scanned` to `Analyzed` for clarity.
- Updated flagged count logic so `Flagged` reflects actual candidate repos rather than total analyzed repos.
- Improved search workflow so repeated runs can explore beyond the same initial GitHub results.

### Fixed
- Fixed search behavior that previously capped results too early.
- Fixed lack of pagination that caused the tool to repeatedly return the same early results.
- Fixed duplicate processing by deduplicating exact repositories by full repo name.
- Fixed inclusion of archived and disabled repositories in analysis results.
- Fixed summary/count mismatches caused by earlier search-limit behavior.

## v0.1.1 - UX polish

### Changed
- Normalized compact and full output layout
- Removed redundant "README missing" status line
- Added spacing between summary and results
- Removed experimental language detection
- Updated README to match current functionality

## v0.1

### Initial release of readme-radar CLI tool.

Features:
- GitHub repository search
- README quality scoring
- Missing section detection
- Candidate labeling
- Ranked results (worst first)
- Compact output mode
- JSON output
- JSON file export
- Top issue summary
- Non-English README deprioritization

Notes:
- Designed for technical writers seeking documentation contributions
- Focus on identifying weak or missing README files
- CLI-first workflow

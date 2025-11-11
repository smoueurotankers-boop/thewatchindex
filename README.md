# The Watch Index v2

This repository contains the source for a fully static but automated version of **The Watch Index**, an anonymous fatigue reporting initiative for seafarers.

## Features

- **Modern dark UI** with red accents and responsive design.
- Anonymous submission form that never sends data to a server; instead it generates a JSON file for you to transmit via a secure channel of your choosing.
- **Dashboard** that displays current totals and averages, with charts by ship type and region. It reads from `data/data.json`.
- **GitHub Action** (`update-data.yml`) that aggregates CSV submission files placed in the `submissions` folder into `data/data.json` automatically whenever new submissions are committed. No manual script execution required.

## How it works

1. **Anonymous submissions**: Navigate to `submit.html`, fill in your fatigue data and click *Generate report file*. A `.json` file will download to your device. Share this file via a secure anonymous channel (e.g. Tor, secure email) with the operators of the Watch Index.

2. **Collect submissions**: Store collected JSON or CSV submissions in the `submissions/` directory of this repository. (For convenience, you can convert JSON reports to CSV with a spreadsheet tool; see below for the required headers.)

3. **Automatic aggregation**: When you push new submission files to `submissions/` on the `main` branch, GitHub Actions runs `scripts/aggregate.py` to recompute totals, averages and counts, writing the results to `data/data.json`. It then commits that file back to the repository. The dashboard will show the updated numbers after the GitHub Pages site rebuilds.

4. **View dashboard**: Visit `dashboard.html` to see the current aggregated metrics and charts.

## Submission CSV format

The aggregator expects CSV files with the following header row:

```
ship_type,region,sleep_hours,rest_violations,called_during_rest,port_intensity
```

Example row:

```
Tanker,Middle East,5,2,yes,high
```

No personal identifiers should be included in the CSV. The `called_during_rest` and `port_intensity` columns are currently ignored by the aggregator but retained for future analysis.

## Local development

```bash
npm install            # if you choose to use a dev server; not required for static HTML
# serve the site locally using Python
python3 -m http.server 8000 -d new_watch_index
```

Run the aggregator manually:

```bash
python scripts/aggregate.py
```

## Deployment

1. Create a new GitHub repository and push the contents of this folder to the `main` branch.
2. Enable **GitHub Pages** for the repository (from the `Settings` → `Pages` menu) and set the source to the root of the `main` branch.
3. Configure your custom domain (e.g. `thewatchindex.org`) to point to GitHub Pages.
4. Ensure the `update-data.yml` workflow is enabled under `Actions`. It will run automatically when new submission CSVs are added.

## License

This project is provided without warranty. You may modify and redistribute it under the MIT license.
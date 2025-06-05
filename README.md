# jira-cli
CLI wrapper for Jira

## Extract Jira Issues to JSON

You can use `jira_cli.py` to extract issues from your Jira project and save them as a JSON file:

1. Set the required environment variables:
   - `JIRA_BASE_URL` (e.g., https://yourcompany.atlassian.net)
   - `JIRA_EMAIL` (your Jira email)
   - `JIRA_API_TOKEN` (your Jira API token)
   - `JIRA_PROJECT_KEY` (your Jira project key, or use --project option)

2. Extract issues to a file (e.g., `issues.json`):

```bash
python3 jira_cli.py extract --output issues.json
```

You can limit the number of issues with `--max`:

```bash
python3 jira_cli.py extract --output issues.json --max 100
```

## Convert Jira JSON to CSV for CRM Import

This project includes a script to convert Jira issue JSON exports to a CSV format suitable for CRM import.

### Usage

1. Place your Jira JSON export file as `issues.json` in the project directory (or use the file generated above).
2. Run the conversion script:

```bash
python3 json_to_csv.py
```

3. The script will generate `output.csv` with the following columns:
   - Name
   - Email
   - Phone
   - Status
   - Created Date
   - Reporter Name
   - Reporter Email

You can then import `output.csv` into your CRM.

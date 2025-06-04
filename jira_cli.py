import os
import sys
import requests
import click

JIRA_BASE = os.environ.get("JIRA_BASE_URL")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_API_TOKEN")


def jira_auth():
    if not all([JIRA_BASE, JIRA_EMAIL, JIRA_TOKEN]):
        click.echo("JIRA configuration is missing. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN.", err=True)
        sys.exit(1)
    return (JIRA_EMAIL, JIRA_TOKEN)


def create_jira_issue(summary: str, description: str, project: str) -> dict:
    url = f"{JIRA_BASE}/rest/api/3/issue"
    data = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": description}
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"},
        }
    }
    resp = requests.post(url, json=data, auth=jira_auth())
    resp.raise_for_status()
    return resp.json()


def list_jira_issues(project: str, max_results=None):
    url = f"{JIRA_BASE}/rest/api/3/search"
    jql = f"project={project} ORDER BY created DESC"
    issues = []
    start_at = 0
    page_size = 100
    total = None
    while True:
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": page_size if max_results is None else min(page_size, max_results - len(issues)),
        }
        resp = requests.get(url, params=params, auth=jira_auth())
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("issues", [])
        issues.extend(batch)
        if total is None:
            total = data.get("total", 0)
        if max_results is not None and len(issues) >= max_results:
            return issues[:max_results]
        if len(issues) >= total or not batch:
            break
        start_at += len(batch)
    return issues


@click.group()
@click.option('--project', default=None, help='JIRA project key (overrides JIRA_PROJECT_KEY env var).')
@click.pass_context
def cli(ctx, project):
    """JIRA CLI tool to list and create issues."""
    ctx.ensure_object(dict)
    ctx.obj['PROJECT'] = project or os.environ.get("JIRA_PROJECT_KEY")
    if not ctx.obj['PROJECT']:
        click.echo("JIRA project key not specified. Use --project or set JIRA_PROJECT_KEY.", err=True)
        sys.exit(1)


@cli.command()
@click.option("--max", "max_results", default=None, type=int, help="Max issues to list. If not set, lists all issues.")
@click.pass_context
def list(ctx, max_results):
    """List issues in the JIRA project."""
    project = ctx.obj['PROJECT']
    try:
        issues = list_jira_issues(project, max_results)
        for issue in issues:
            key = issue.get("key")
            summary = issue.get("fields", {}).get("summary", "")
            status = issue.get("fields", {}).get("status", {}).get("name", "")
            print(f"{key}: {summary} [Status: {status}]")
    except Exception as e:
        click.echo(f"Error listing issues: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--summary", prompt=True, help="Summary for the new issue.")
@click.option("--description", prompt=True, help="Description for the new issue.")
@click.pass_context
def create(ctx, summary, description):
    """Create a new JIRA issue."""
    project = ctx.obj['PROJECT']
    try:
        issue = create_jira_issue(summary, description, project)
        key = issue.get("key")
        url = f"{JIRA_BASE}/browse/{key}" if key else ""
        print(f"Created issue {key}: {url}")
    except Exception as e:
        click.echo(f"Error creating issue: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli(obj={}) 

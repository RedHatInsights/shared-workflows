"""Send an SC Environment Impact Assessment notification to Slack."""

import json
import os
import sys
import urllib.request

EMOJI = {
    "critical": ":red_circle:",
    "high": ":large_orange_circle:",
    "medium": ":large_yellow_circle:",
    "low": ":large_green_circle:",
}

# PR statuses that should not trigger Slack notifications.
# Possible values: draft, open, closed, merged
SKIP_PR_STATUSES = {"draft"}


def build_payload(repo, pr_number, pr_url, impact):
    emoji = EMOJI.get(impact, ":white_circle:")
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "SC Environment Impact Assessment",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Repository:*\n{repo}"},
                    {"type": "mrkdwn", "text": f"*Pull Request:*\n<{pr_url}|#{pr_number}>"},
                    {"type": "mrkdwn", "text": f"*Overall Impact:*\n{emoji} {impact.upper()}"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Pull Request"},
                        "url": pr_url,
                    }
                ],
            },
        ]
    }


def main():
    webhook_url = os.environ.get("SC_ASSESSOR_SLACK_URL")
    if not webhook_url:
        print("SC_ASSESSOR_SLACK_URL not set — skipping", file=sys.stderr)
        sys.exit(0)

    pr_status = os.environ.get("PR_STATUS", "").strip()
    if pr_status in SKIP_PR_STATUSES:
        print(f"PR status is '{pr_status}' — skipping Slack notification")
        sys.exit(0)

    repo = os.environ["GITHUB_REPOSITORY"]
    server_url = os.environ["GITHUB_SERVER_URL"]
    pr_number = os.environ["PR_NUMBER"]
    impact = os.environ["OVERALL_IMPACT"]

    pr_url = f"{server_url}/{repo}/pull/{pr_number}"
    payload = build_payload(repo, pr_number, pr_url, impact)

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)
    print(f"Slack notification sent (impact: {impact})")


if __name__ == "__main__":
    main()

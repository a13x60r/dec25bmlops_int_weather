import logging

import requests
from airflow.models import Variable


def send_slack_alert(context):
    """
    Sends a Slack notification on task failure using Bot User OAuth Token.
    """
    token = Variable.get("SLACK_BOT_TOKEN", default_var=None)
    channel = Variable.get("SLACK_CHANNEL", default_var="#general")

    if not token:
        logging.warning("SLACK_BOT_TOKEN variable not set. Skipping notification.")
        return

    task_id = context.get("task_instance").task_id
    dag_id = context.get("task_instance").dag_id
    execution_date = context.get("execution_date")
    exception = context.get("exception")
    log_url = context.get("task_instance").log_url

    # Slack Block Kit Layout
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🔴 Airflow Task Failed", "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*DAG:*\n{dag_id}"},
                {"type": "mrkdwn", "text": f"*Task:*\n{task_id}"},
                {"type": "mrkdwn", "text": f"*Time:*\n{execution_date}"},
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Exception:*\n```{str(exception)[:500]}...```",  # Truncate long errors
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Logs"},
                    "url": log_url,
                    "style": "danger",
                }
            ],
        },
    ]

    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": channel,
                "blocks": blocks,
                # Fallback text for notifications
                "text": f"Task Failed: {dag_id}.{task_id}",
            },
        )
        data = response.json()

        if not data.get("ok"):
            logging.error(f"Slack API Error: {data.get('error')}")
        else:
            logging.info("Slack notification sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send Slack notification: {e}")

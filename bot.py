import os
from pathlib import Path

import slack
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
from flask import Flask, Response, request

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

bot_token = os.environ["SLACK_BOT_TOKEN"]
signing_secret = os.environ["SIGNING_SECRET"]

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(signing_secret, "/slack/events", app)

client = slack.WebClient(token=bot_token)
bot_id = client.api_call("auth.test")["user_id"]

client.chat_postMessage(channel="#test-twt", text="Hello, World!")


# Implement echo bot
@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    if user_id != bot_id:
        client.chat_postMessage(
            channel=channel_id, text=f"{text} back to you, {user_id}!"
        )


# Implement /echo slash commend
@app.route("/echo", methods=["POST"])
def message_count():
    data = request.form
    text = data.get("text")
    if text == "":
        text = "Say something!"
    channel_id = data.get("channel_id")
    client.chat_postMessage(channel=channel_id, text=text)
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)

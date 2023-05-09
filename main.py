import json
from flask import Flask, request
import boto3
from apscheduler.schedulers.background import BackgroundScheduler
import pymsteams

app = Flask(__name__)
def createMessage(messageDict):
    teamsMessage = pymsteams.connectorcard(
        "https://softwareinstitute.webhook.office.com/webhookb2/6af7ae5d-12ad-4126-8d1d-5c234ab49642@14e1d7e2-2c30-4e78-8b82-5fb14801c021/IncomingWebhook/0ff4bc98f9cf45e6a478ddbefac3a5e6/4ff6d443-43ce-497c-8ee8-338d52a4176b")
    teamsMessage.title("ALERT: A NEW HIGH PRIORITY BUG HAS BEEN FOUND!")
    teamsMessage.text("Calling all DevOps Engineers!!")
    messageSection = pymsteams.cardsection()
    messageSection.title(f"Title: {messageDict['name']}")
    messageSection.text(f"Description: {messageDict['description']}")
    teamsMessage.addSection(messageSection)
    teamsMessage.send()


@app.route("/message", methods=['POST'])
def consumeMessages():
        sqs = boto3.resource('sqs')
        # Get the queue
        queue = sqs.get_queue_by_name(QueueName='HighPriority')
        # Process messages by printing out body and optional author name
        for message in queue.receive_messages():
            print(message.body)
            createMessage(json.loads(message.body))
            message.delete()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=consumeMessages, trigger="interval", seconds=10)
    scheduler.start()
    app.run()
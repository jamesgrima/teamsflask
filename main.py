import json
from flask import Flask, request
import boto3
from apscheduler.schedulers.background import BackgroundScheduler
import pymsteams

app = Flask(__name__)
def createMessage(messageDict):
    teamsMessage = pymsteams.connectorcard(
        "https://softwareinstitute.webhook.office.com/webhookb2/6af7ae5d-12ad-4126-8d1d-5c234ab49642@14e1d7e2-2c30-4e78-8b82-5fb14801c021/IncomingWebhook/23ca62eceea74196a793e5630ff7a278/4ff6d443-43ce-497c-8ee8-338d52a4176b")
    teamsMessage.title("Test")
    teamsMessage.text("Calling all DevOps Engineers!!")
    messageSection = pymsteams.cardsection()
    messageSection.title(f"Title: {messageDict['name']}")
    messageSection.text(f"Description: {messageDict['description']}")
    # messageSection.addImage(
    #     "https://w7.pngwing.com/pngs/1006/882/png-transparent-insect-bed-bug-software-bug-computer-icons-insect"
    #     "-animals-computer-black-thumbnail.png")
    teamsMessage.addSection(messageSection)
    teamsMessage.send()


@app.route("/message", methods=['POST'])
def consumeMessages():
        sqs = boto3.resource('sqs')
        # Get the queue
        queue = sqs.get_queue_by_name(QueueName='DLQ')
        # Process messages by printing out body and optional author name
        for message in queue.receive_messages():
            print(message.body)
            createMessage(json.loads(message.body))
            #message.delete()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=consumeMessages, trigger="interval", seconds=10)
    scheduler.start()
    app.run()
import json
from flask import Flask
import boto3
from botocore.exceptions import ClientError
from apscheduler.schedulers.background import BackgroundScheduler
import pymsteams

app = Flask(__name__)


def get_secret():
    secret_name = "awsaccesskeys"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    secretdict = json.loads(secret)
    print(secretdict)

    return secretdict


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
    secretdict = get_secret()
    accesskey = secretdict.get('access')
    secretkey = secretdict.get('secretaccess')
    sqs = boto3.resource('sqs', region_name='eu-west-2', aws_access_key_id=accesskey, aws_secret_access_key=secretkey)
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

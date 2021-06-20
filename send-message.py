from boto3.session import Session

QUEUE_NAME = "tst-dva-queue.fifo"


class SQSClient:
    def __init__(self):
        self.sqs = Session(profile_name="kameda").client("sqs")
        self.account_id = (
            Session(profile_name="kameda")
            .client("sts")
            .get_caller_identity()["Account"]
        )

    def send_message(self, message):
        response = self.sqs.send_message(
            QueueUrl=f"https://sqs.ap-northeast-1.amazonaws.com/{self.account_id}/{QUEUE_NAME}",
            MessageBody=message,
            MessageGroupId="messageGroup1",
        )
        return response


if __name__ == "__main__":
    message = "Hello, SQS!"
    response = SQSClient().send_message(message)
    print(response)
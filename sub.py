
import argparse
import time
# [START pubsub_quickstart_sub_deps]
from google.cloud import pubsub_v1
# [END pubsub_quickstart_sub_deps]


def sub(project_id, subscription_name):
    """Receives messages from a Pub/Sub subscription."""
    # [START pubsub_quickstart_sub_client]
    # Initialize a Subscriber client
    client = pubsub_v1.SubscriberClient()
    # [END pubsub_quickstart_sub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = client.subscription_path(
        project_id, subscription_name)

    def callback(message):
        print('Received message {} of message ID {}'.format(
            message, message.message_id))
        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()
        print('Acknowledged message of message ID {}\n'.format(
            message.message_id))

    client.subscribe(subscription_path, callback=callback)
    print('Listening for messages on {}..\n'.format(subscription_path))

    # Keep the main thread from exiting so the subscriber can
    # process messages in the background.
    while True:
        time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_id', help='Google Cloud project ID')
    parser.add_argument('subscription_name', help='Pub/Sub subscription name')

    args = parser.parse_args()

    sub(args.project_id, args.subscription_name)
# [END pubsub_quickstart_sub_all]

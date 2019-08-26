#!/usr/bin/env python

import argparse
import time
# [START pubsub_quickstart_pub_deps]
from google.cloud import pubsub_v1
# [END pubsub_quickstart_pub_deps]


def get_callback(api_future, data):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            print("Published message {} now has message ID {}".format(
                data, api_future.result()))
        except Exception:
            print("A problem occurred when publishing {}: {}\n".format(
                data, api_future.exception()))
            raise
    return callback


def pub(project_id, topic_name):
    """Publishes a message to a Pub/Sub topic."""
    # [START pubsub_quickstart_pub_client]
    # Initialize a Publisher client
    client = pubsub_v1.PublisherClient()
    # [END pubsub_quickstart_pub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path(project_id, topic_name)

    # Data sent to Cloud Pub/Sub must be a bytestring
    data = b"Hello, World!"

    # When you publish a message, the client returns a future.
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_id', help='Google Cloud project ID')
    parser.add_argument('topic_name', help='Pub/Sub topic name')

    args = parser.parse_args()

    pub(args.project_id, args.topic_name)
# [END pubsub_quickstart_pub_all]

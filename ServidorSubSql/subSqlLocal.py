

import time
import datetime
# [START pubsub_quickstart_sub_deps]
from google.cloud import pubsub_v1
# [END pubsub_quickstart_sub_deps]

import os
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://alvarov:lata5comprar@127.0.0.1:3306/prueba_appengine', echo=True)
metadata = MetaData()
users = Table('datosConsumo', metadata,
   Column('id', Integer, primary_key=True),
   Column('dispositivo', String(250)),
   Column('valor', String(50)),
   Column('fecha',String(100)),
   Column('fechanow',sqlalchemy.types.DateTime(timezone=True),default=datetime.datetime.utcnow)
)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
#variables

proyecto='asistente-180018'
topico='casa1-consumo-sub1'


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
        #print(message['PublishTime'])
        print('Received message {} of message ID {}'.format(
            message, message.message_id))

        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()

        print('Acknowledged message of message ID {}\n'.format(
            message.message_id))

        ins = users.insert().values(valor=str(message.data),fecha=str(message.publish_time))
        conn = engine.connect()
        result = conn.execute(ins)

    client.subscribe(subscription_path, callback=callback)
    print('Listening for messages on {}..\n'.format(subscription_path))

    while True:
        time.sleep(60)

if __name__ == '__main__':
    sub(proyecto, topico)
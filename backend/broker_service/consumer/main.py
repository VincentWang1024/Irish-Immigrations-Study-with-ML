
from confluent_kafka import Consumer
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
# bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS")
# security_protocol = os.getenv("SECURITY_PROTOCOL")
# sasl_mechanisms = os.getenv("SASL_MECHANISMS")
# sasl_username = os.getenv("SASL_USERNAME")
# sasl_password = os.getenv("SASL_PASSWORD")

bootstrap_servers = 'pkc-z9doz.eu-west-1.aws.confluent.cloud:9092'
security_protocol = 'SASL_SSL'
sasl_mechanisms = 'PLAIN'
sasl_username = 'PR6L4XJHNR3TI33I'
sasl_password = 'xs38vTm+VwsTO9/VZwmHh4DQgyORiVx5K7LlkGDqLy02llk4mrWpvqdRF5+BZOJc'

# Create a Kafka producer configuration
conf = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanisms': sasl_mechanisms,
    'sasl.username': sasl_username,
    'sasl.password': sasl_password,
}

# Create consumer
props = conf
props["group.id"] = "python-group-1"
props["auto.offset.reset"] = "earliest"

c = Consumer(props)

c.subscribe(['nlp-workflow'])

try:
    while True:
        msg = c.poll(0.1)  # Wait for message or event/error
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to `session.timeout.ms` for
            #   the group to rebalance and start consuming.
            continue
        if msg.error():
            # Errors are typically temporary, print error and continue.
            print('Consumer error: {}'.format(msg.error()))
            continue

        print('Consumed: {}'.format(msg.value()))

except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    c.close()
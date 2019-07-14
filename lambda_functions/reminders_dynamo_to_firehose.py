"""Logs reminders to firehose"""
import json
import logging.config
import os

import boto3
from boto3.dynamodb.types import TypeDeserializer

DESERIALIZER = TypeDeserializer()
FIREHOSE_CLIENT = boto3.client('firehose')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
REMINDERS_FIREHOSE = os.environ['REMINDERS_FIREHOSE_STREAM_NAME']


def handler(event, context):
    """handler function works as controller function"""
    firehose_records = list()
    for record in event['Records']:
        firehose_records.append(build_firehose_record(record))

    put_records_on_firehose(firehose_records)
    LOGGER.debug('Time left to execute %s ms', context.get_remaining_time_in_millis())
    return {'Complete': True}


def build_firehose_record(record):
    """builds firehose record based on event type"""
    if record['eventName'] == 'REMOVE':
        image = {k: DESERIALIZER.deserialize(
            v) for k, v in record['dynamodb']['OldImage'].items()}
    else:
        image = {k: DESERIALIZER.deserialize(
            v) for k, v in record['dynamodb']['NewImage'].items()}

    image.update({'event': record['eventName']})
    return json.dumps(image, separators=(',', ':'), sort_keys=True) + '\n'


def put_records_on_firehose(firehose_records):
    """Break list of firehose records into lists of 500 and put on firehose"""
    firehose_record_chunks = [firehose_records[i:i + 500] for i in range(0, len(firehose_records), 500)]

    for chunk in firehose_record_chunks:
        FIREHOSE_CLIENT.put_record_batch(
            DeliveryStreamName=REMINDERS_FIREHOSE,
            Records=chunk
        )

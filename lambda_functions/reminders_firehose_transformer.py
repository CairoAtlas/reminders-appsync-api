"""This lambda function adds workflowId and transaction times to the firehose record"""

import base64
import json
import logging.config
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
REMINDER_KEYS = os.environ['REMINDER_KEYS'].split(',')
""" 'title',
    'createdTimestamp',
    'notes',
    'dueTimestamp',
    'location',
    'remindTimestamp',
    'priority'
"""


def handler(event, context):
    """handler function, manages transaction transformation"""
    records = list()
    for record in event['records']:
        new_record = {
            'recordId': record['recordId'],
            'result': 'Ok'
        }

        reminder = json.loads(base64.b64decode(record['data']))
        reminder.update(**get_missing_keys(reminder))

        reminder_str = json.dumps(reminder, separators=(',', ':'), sort_keys=True) + '\n'
        data = base64.b64encode(reminder_str.encode())
        new_record.update({'data': data.decode()})
        records.append(new_record)

    LOGGER.debug('Time left to execute %s ms', context.get_remaining_time_in_millis())

    return {
        'records': records
    }


def get_missing_keys(reminder):
    """Ensures reminder has all necessary data even if it is just an empty string"""
    missing_keys = dict()
    for key in REMINDER_KEYS:
        if key not in reminder:
            missing_keys.update({key: ''})

    return missing_keys

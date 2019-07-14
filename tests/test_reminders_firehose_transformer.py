import base64
import json
import os

from lambda_functions import reminders_firehose_transformer as function_code
from tests.mocks import context_mock as context

DATA_AS_JSON = {
    'title': 'Test Get Missing Keys',
    'createdTimestamp': 1563146089
}

EXPECTED_RECORD_AS_JSON = {
    'title': 'Test Get Missing Keys',
    'createdTimestamp': 1563146089,
    'notes': '',
    'dueTimestamp': '',
    'location': '',
    'remindTimestamp': '',
    'priority': ''
}

FIREHOSE_EVENT = {
  'invocationId': 'invocationIdExample',
  'deliveryStreamArn': 'arn:aws:kinesis:EXAMPLE',
  'region': 'us-east-1',
  'records': [
    {
      'recordId': '49546986683135544286507457936321625675700192471156785154',
      'approximateArrivalTimestamp': 1563146089,
      'data': 'changeme'
    }
  ]
}


def test_get_missing_keys():
    reminder_keys = os.environ['REMINDER_KEYS'].split(',')
    missing_data = function_code.get_missing_keys(DATA_AS_JSON)
    assert len(missing_data.keys()) == 5
    for key, value in missing_data.items():
        if key in reminder_keys:
            assert not value
    assert 'title' not in missing_data
    assert 'createdTimestamp' not in missing_data


def test_handler():
    event = FIREHOSE_EVENT.copy()
    data = base64.b64encode(json.dumps(DATA_AS_JSON, separators=(',', ':'), sort_keys=True).encode()).decode()
    event['records'][0]['data'] = data
    expected_data_str = json.dumps(EXPECTED_RECORD_AS_JSON, separators=(',', ':'), sort_keys=True) + '\n'
    expected_data = base64.b64encode(expected_data_str.encode()).decode()

    response = function_code.handler(event, context.Context(20))
    assert response['records'][0]['data'] == expected_data

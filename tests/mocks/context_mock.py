from datetime import datetime
from datetime import timedelta
import uuid


class Context(object):
    def __init__(self, timeout_in_seconds,
                 aws_request_id=uuid.uuid4(),
                 function_name="process-accident-file",
                 function_version="$LATEST",
                 log_group_name="undefined",
                 log_stream_name="undefined",
                 invoked_function_arn="process-accident-file",
                 memory_limit_in_mb='0',
                 client_context=None,
                 identity=None):
        self.function_name = function_name
        self.function_version = function_version
        self.invoked_function_arn = invoked_function_arn
        self.memory_limit_in_mb = memory_limit_in_mb
        self.aws_request_id = aws_request_id
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.identity = identity
        self.client_context = client_context

        self._timeout_in_seconds = timeout_in_seconds
        self._duration = timedelta(seconds=timeout_in_seconds)
        self._activate()

    def get_remaining_time_in_millis(self):
        if self._timelimit is None:
            raise Exception("Context not activated.")
        return millis_interval(datetime.now(), self._timelimit)

    def log(self, msg):
        print(msg)

    def _activate(self):
        self._timelimit = datetime.now() + self._duration
        return self


def millis_interval(start, end):
    """start and end are datetime instances"""
    diff = end - start
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis
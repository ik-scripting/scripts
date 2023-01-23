#!/usr/bin/env python

from datetime import datetime
from datetime import timedelta


def show_events(environment, seconds, eventtype, eb_context):
    time = datetime.now() - timedelta(seconds=seconds)
    start_time = datetime(year=time.year, month=time.month, day=time.day, hour=time.hour, minute=time.minute,
                          second=time.second)

    response = eb_context.eb_client.describe_events(
        ApplicationName=eb_context.application,
        EnvironmentName=environment,
        Severity=eventtype,
        MaxRecords=5,
        StartTime=start_time,
    )

    events = response['Events']
    if events:
        print "\n Events"
        for data in events:
            print "  -Severity- {}.\n  -Message- {}".format(data['Severity'], data['Message'])
        print "\n"

# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""This module provides the LogEntryObserver which implements the Observer pattern.

The scheduler notifies about log entries, so this class is used to catch these
updates and log them into a file
"""

# standard libraries
from datetime import datetime
import logging
from typing import Any

# local sources
from pfdl_scheduler.api.observer_api import NotificationType
from pfdl_scheduler.api.observer_api import Observer

# do not log requests entries if it is lesser than a warning
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# constants
LOG_FILE_LOCATION = "temp/"
LOG_FILE_FORMAT = ".log"
LOG_FILE_ENCODING = "utf-8"
LOG_FILE_FILEMODE = "w"


class LogEntryObserver(Observer):
    """LogEntryObserver for receiving logging information from the Scheduler.

    LogLevels are based of https://docs.python.org/3/library/logging.html#logging-levels
    """

    def __init__(self, scheduler_id: str):
        logging.basicConfig(
            filename=LOG_FILE_LOCATION + scheduler_id + LOG_FILE_FORMAT,
            encoding=LOG_FILE_ENCODING,
            level=logging.DEBUG,
            filemode=LOG_FILE_FILEMODE,
        )

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.LOG_EVENT:
            log_level = data[1]
            log_date = str(datetime.now())
            log_entry = log_date + ": " + data[0]
            logging.log(log_level, log_entry)

# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""This class contains classes to enable the Observer pattern.

The `NotificationTye` class is an enum class which is used for setting the
type of the notification.

The abstract `Observer` class represents the observers in the pattern and requires
an `update` method which is called by a `Subject` object. Here, the type of the notification
and the corresponding data is required.

The abstract `Subject` class represents the subjects in the observer pattern.
It provides methods to attach or detach observers and to notify them.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class NotificationType(Enum):
    """Declares the type of Notification in the observer pattern."""

    PETRI_NET = 1
    LOG_EVENT = 2
    SCHEDULER = 3


class Observer(ABC):
    """The Observer interface declares the update method, used by subjects."""

    @abstractmethod
    def update(self, notification_type: NotificationType, data: Any) -> None:
        """Receive update from subject."""
        pass


class Subject(ABC):
    """The Subject interface declares a set of methods for managing subscribers."""

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self, notification_type: NotificationType, data: Any) -> None:
        """Notify all observers about an event."""
        pass

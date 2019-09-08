""" Module which is capable of proxying requests via tor. """
from typing import Generator, Any, List, Optional
from enum import Enum

import socket
import time
import socks
from stem.control import Controller
from stem import Signal
import requests


class StepResult(Enum):
    """ Enum which shows result of the iteration step. """

    # Step succeed
    OK = 0
    # Error occured during request, need to retry
    ERROR = 1


def run_with_proxy(gen: Generator[Any, Optional[StepResult], None]) -> List[Any]:
    """
    Runs the given generator with the use of tor.
    On each step a value is retrieved from the generator, and StepResult is sent to it.
    StepResult is OK if no HTTP errors occured and ERROR otherwise.
    """
    err = 0
    values: List[Any] = []
    with Controller.from_port(port=9151) as controller:
        controller.authenticate()
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)

        setattr(socket, "socket", socks.socksocket)

        result = None

        # Go through every value in generator.
        while True:
            try:
                value = gen.send(result)
                values.append(value)

                result = StepResult.OK

                # Pylint doesn't see member of enum
                # pylint: disable=no-member
                controller.signal(Signal.NEWNYM)
                time.sleep(controller.get_newnym_wait())
            except requests.HTTPError:
                print("Could not reach URL")
                result = StepResult.ERROR
                err = err + 1
            except StopIteration:
                break
    print("Got " + str(err) + " errors")

    return values

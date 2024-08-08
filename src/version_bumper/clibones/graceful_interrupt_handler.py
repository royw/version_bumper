# SPDX-FileCopyrightText: 2024 Roy Wright
#
# SPDX-License-Identifier: MIT

"""
Graceful Interrupt Handler as a context manager.

Can be nested.

From:

* https://stackoverflow.com/a/10972804
* https://gist.github.com/nonZero/2907502
"""

from __future__ import annotations

import signal
from collections.abc import Callable
from types import FrameType
from typing import Any, Self


class GracefulInterruptHandler:
    """
    Example Usage::

        with GracefulInterruptHandler() as h1:
            while True:
                print("(1)...")
                time.sleep(1)
                with GracefulInterruptHandler() as h2:
                    while True:
                        print("\t(2)...")
                        time.sleep(1)
                        if h2.interrupted:
                            print("\t(2) interrupted!")
                            time.sleep(2)
                            break
                if h1.interrupted:
                    print("(1) interrupted!")
                    time.sleep(2)
                    break
    """

    def __init__(self, sig: int = signal.SIGINT):
        self.sig: int = sig
        self.interrupted: bool = False
        self.released: bool = False
        self.original_handler: Callable[[int, FrameType | None], Any] | int | None = None

    def __enter__(self) -> Self:
        return self.capture()

    def release(self) -> bool:
        """release the signal handler"""
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True

    def capture(self) -> Self:
        """
        Capture the signal.  Useful when not using the "with GracefulInterruptHandler" syntax.
        :return: current GracefulInterruptHandler instance
        :rtype: GracefulInterruptHandler
        """
        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        # noinspection PyUnusedLocal
        def handler(signum: int, frame: FrameType | None) -> None:  # NOQA: ARG001
            """
            signal that an interrupt has occurred.

            :param signum: the signal number
            :param frame: unused
            """
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    # noinspection PyUnusedLocal,PyShadowingBuiltins
    def __exit__(self, *exc: Any) -> None:
        self.release()

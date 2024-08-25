"""Custom override for class Signal and shutdown func in aioshutdown."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from signal import Signals
from typing import Any

import inject
from aioshutdown import Signal
from aioshutdown._shutdown import cancel

log = logging.getLogger(__name__)

_HandlerType = Callable[[asyncio.AbstractEventLoop, Signals, asyncio.Event], Coroutine[Any, Any, None]]


class _Signal(Signal):
    def __init__(self, signal: Signals, event: asyncio.Event) -> None:
        super().__init__(signal)
        self.signal: Signals = signal
        self._signals: set[Signals] = set()
        self.event: asyncio.Event = event

    def _add_signal_handler(
        self,
        handler: _HandlerType,
        signal: Signals,
    ) -> None:
        self.loop.add_signal_handler(
            signal,
            lambda s=signal: asyncio.create_task(handler(self.loop, s, self.event)),
        )

    def __enter__(self) -> asyncio.AbstractEventLoop:
        super().__enter__()
        self._signals.add(self.signal)

        self.loop = asyncio.events.new_event_loop()

        for s in self._signals:
            self._add_signal_handler(app_shutdown, s)

        return self.loop


@inject.autoparams()
async def app_shutdown(
    loop: asyncio.AbstractEventLoop,
    signal: Signals,
    event: asyncio.Event,
    background_tasks: set[asyncio.Task],
) -> None:
    """Cleanup tasks tied to the service's shutdown.

    Args:
        loop: Event loop.
        signal: OS signal. Defaults to None.
        event: asyncio.Event to set.
        background_tasks: Background AsyncIO tasks storage.
    """
    event.set()

    log.info("Received exit signal {}...", signal.name)
    background_tasks.clear()
    # Get the list of all tasks except the current one.
    tasks, consumers = [], []
    for t in asyncio.all_tasks(loop):
        if t is asyncio.current_task(loop=loop):
            continue
        if not t.get_name().startswith("consumer"):
            tasks.append(t)
        else:
            consumers.append(t)

    # Request for cancellation of all outstanding tasks.
    for task in tasks:
        cancel(task, signal)

    log.info("Cancelling {} outstanding tasks", len(tasks))

    # Concurrently wait for all tasks to be cancelled.
    await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )
    log.info("Stopping event loop")

    loop.stop()

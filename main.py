import signal
import asyncio
import logging

import click
import inject
from aioshutdown import Signal

from src.settings import ApplicationSettings
from src.logging import configure_logging
from src.worker import worker


@click.group()
@inject.autoparams()
def cli(app_settings: ApplicationSettings) -> None:
    """Base cli."""
    configure_logging(app_settings.settings)
    logging.info("Load the following application settings: {}", app_settings)
    logging.configure(
        extra={
            "api-key": app_settings.segment_path,
        }
    )


@cli.command(help="Run segment collector.")
def run_aggregator(event: asyncio.Event = asyncio.Event()) -> None:
    """Run segment collector service."""
    logging.info("Aggregator startup")

    with Signal(signal.SIGINT) | Signal(signal.SIGTERM) | Signal(signal.SIGHUP) as loop:
        loop.create_task(worker())
        loop.run_forever()


if __name__ == "__main__":
    cli()

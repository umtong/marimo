# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

import asyncio
import sys
from contextlib import suppress
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Coroutine

T = TypeVar("T")


async def run_browser_task(coro: Coroutine[Any, Any, T]) -> T:
    if sys.platform != "win32":
        return await coro

    def run() -> T:
        # Sessions need a Selector loop, but Playwright requires subprocesses.
        with asyncio.Runner(
            loop_factory=asyncio.ProactorEventLoop,  # type: ignore[attr-defined]
        ) as runner:
            return runner.run(coro)

    task = asyncio.create_task(asyncio.to_thread(run))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        # Keep the asset server and staging files alive until the browser exits.
        with suppress(Exception):
            await asyncio.shield(task)
        raise

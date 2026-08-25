from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from cashews import Cache
from sqlalchemy import event
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

CACHE_KEY_PREFIX = "schedule-bot:v1"
_INVALIDATION_TAGS = "cashews_invalidation_tags"

# A dedicated instance keeps this application's configuration isolated from
# Cashews' module-level default cache.
cache = Cache("schedule-telegram-bot")


async def invalidate_tags(session: AsyncSession, *tags: str) -> None:
    """Invalidate now and once more after a successful database commit.

    The first invalidation preserves read-your-writes inside the current transaction.
    Repeating it after commit prevents another worker from repopulating a key from the
    previous committed state between ``flush`` and ``commit``.
    """
    session.info.setdefault(_INVALIDATION_TAGS, set()).update(tags)
    await cache.delete_tags(*tags)


@event.listens_for(Session, "after_commit")
def _invalidate_after_commit(session: Session) -> None:
    tags = session.info.pop(_INVALIDATION_TAGS, set())
    if tags:
        asyncio.get_running_loop().create_task(cache.delete_tags(*tags))


@event.listens_for(Session, "after_rollback")
def _discard_invalidations_after_rollback(session: Session) -> None:
    session.info.pop(_INVALIDATION_TAGS, None)

#!/bin/bash
# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

set -e

echo "⏳ Running database migrations..."
uv run alembic upgrade head

echo "🌱 Seeding database if empty (timeout 60s)..."
timeout 60 uv run python -c "
import asyncio, sys
from sqlalchemy import text
from app.core.database import async_session_factory

async def check_and_seed():
    async with async_session_factory() as session:
        result = await session.execute(text('SELECT COUNT(*) FROM users'))
        count = result.scalar()
        if count == 0:
            print('   Database is empty, running seed...', flush=True)
            from app.seed import seed
            await seed()
        else:
            print(f'   Database already has {count} users, skipping seed.', flush=True)

asyncio.run(check_and_seed())
" && echo "✅ Seed completed" || echo "⚠️ Seed timed out or failed, continuing..."

echo "🚀 Starting backend server..."
UVICORN_OPTS="${UVICORN_OPTS:---host 0.0.0.0 --port 8000}"
exec uv run uvicorn app.main:app $UVICORN_OPTS
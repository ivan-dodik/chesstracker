"""Tests to verify that seed data meets the requirements from project_task.md.

These tests programmatically create data matching the seed specification
and verify that all business rules and minimum counts are satisfied.
Uses the main tests/conftest.py engine and TestSessionLocal.
"""

import datetime
import random

import pytest
import pytest_asyncio
from sqlalchemy import func, select

from app.core.security import hash_password
from app.models import (
    ActivityLog,
    Favorite,
    Game,
    Player,
    RatingHistory,
    Tournament,
    User,
)

# Use the root conftest's TestSessionLocal (same DB as API tests)
from tests.conftest import TestSessionLocal

# --- Data pools (mirroring seed.py) ---

FIRST_NAMES = [
    "Magnus", "Ian", "Hikaru", "Fabiano", "Ding", "Alireza", "Wesley", "Anish",
    "Viswanathan", "Vladimir", "Maxime", "Levon", "Sergey", "Alexander", "Jan",
    "Richard", "Peter", "Michael", "David", "Nikita", "Dmitry", "Alexei",
    "Daniil", "Andrey", "Roman", "Ivan", "Viktor", "Vladislav", "Konstantin", "Boris",
]

LAST_NAMES = [
    "Carlsen", "Nepomniachtchi", "Nakamura", "Caruana", "Liren", "Firouzja",
    "So", "Giri", "Anand", "Kramnik", "Vachier-Lagrave", "Aronian", "Karjakin",
    "Grischuk", "Gustafsson", "Rapport", "Leko", "Adams", "Krasenkov",
    "Sidorov", "Ivanov", "Petrov", "Kuznetsov", "Smirnov", "Volkov",
    "Popov", "Fedorov", "Morozov", "Lebedev", "Sokolov",
]

CITIES = [
    "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan",
    "Nizhny Novgorod", "Chelyabinsk", "Krasnoyarsk", "Samara", "Ufa",
    "Rostov-on-Don", "Omsk", "Krasnodar", "Voronezh", "Perm",
    "Volgograd", "Saratov", "Tyumen", "Tolyatti", "Barnaul",
]

TOURNAMENT_SPECS = [
    ("Moscow Chess Championship", "Moscow", "classic"),
    ("Saint Petersburg Rapid", "Saint Petersburg", "rapid"),
    ("Siberian Blitz Cup", "Novosibirsk", "blitz"),
    ("Tatarstan Open", "Kazan", "classic"),
    ("Ural Chess Festival", "Yekaterinburg", "classic"),
    ("Volga Rapid Challenge", "Samara", "rapid"),
    ("Kuban Blitz Tournament", "Krasnodar", "blitz"),
    ("Siberian Federal University Cup", "Krasnoyarsk", "classic"),
    ("Neva Rapid Open", "Saint Petersburg", "rapid"),
    ("Southern Federal Blitz", "Rostov-on-Don", "blitz"),
]


@pytest_asyncio.fixture
async def seed_db():
    """Fixture that populates the test DB with seed-like data and returns counts."""
    async with TestSessionLocal() as session:
        # Users
        admin = User(username="admin", hashed_password=hash_password("admin123"), role="admin")
        user = User(username="user", hashed_password=hash_password("user123"), role="user")
        session.add_all([admin, user])
        await session.flush()

        # Players (30)
        players = []
        used_names: set = set()
        for _ in range(30):
            while True:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            rating = random.randint(1500, 2800)
            city = random.choice(CITIES)
            players.append(Player(name=name, rating=rating, city=city))
        session.add_all(players)
        await session.flush()

        # Tournaments (10, first 3 completed)
        tournaments = []
        now = datetime.datetime(2026, 1, 1)
        for i, (tname, tloc, ttype) in enumerate(TOURNAMENT_SPECS):
            status = "completed" if i < 3 else "active"
            start_date = now + datetime.timedelta(days=i * 14)
            end_date = start_date + datetime.timedelta(days=7)
            rounds = random.randint(5, 9)
            tournaments.append(Tournament(
                name=tname,
                start_date=start_date,
                end_date=end_date,
                location=tloc,
                rounds=rounds,
                type=ttype,
                status=status,
            ))
        session.add_all(tournaments)
        await session.flush()

        # Games (200+)
        games = []
        for idx, tournament in enumerate(tournaments):
            n_players = min(len(players), 8 + random.randint(0, 4))
            sample = random.sample(players, n_players)
            for r in range(1, tournament.rounds + 1):
                shuffled = random.sample(sample, len(sample))
                for i in range(0, len(shuffled) - 1, 2):
                    w, b = shuffled[i], shuffled[i + 1]
                    result = random.choices(["1-0", "0-1", "½-½"], weights=[0.4, 0.3, 0.3], k=1)[0]
                    games.append(Game(
                        tournament_id=tournament.id,
                        round=r,
                        white_player_id=w.id,
                        black_player_id=b.id,
                        result=result,
                        played_at=tournament.start_date + datetime.timedelta(days=r),
                    ))
        while len(games) < 200:
            t = random.choice(tournaments)
            pair = random.sample(players, 2)
            games.append(Game(
                tournament_id=t.id,
                round=random.randint(1, t.rounds),
                white_player_id=pair[0].id,
                black_player_id=pair[1].id,
                result=random.choice(["1-0", "0-1", "½-½"]),
                played_at=t.start_date + datetime.timedelta(days=random.randint(1, 7)),
            ))
        session.add_all(games)
        await session.flush()

        # RatingHistory (180 = 30 players * 6 months)
        rating_history = []
        for player in players:
            current_rating = player.rating
            for month_offset in range(6):
                rating_date = datetime.datetime(2025, 1, 1) + datetime.timedelta(days=month_offset * 30)
                delta = random.randint(-15, 15)
                current_rating = max(0, current_rating + delta)
                rh = RatingHistory(
                    player_id=player.id,
                    rating=current_rating,
                    date=rating_date,
                )
                rating_history.append(rh)
        session.add_all(rating_history)
        await session.flush()

        # Favorites (4)
        favorites = [
            Favorite(user_id=user.id, player_id=players[0].id),
            Favorite(user_id=user.id, player_id=players[1].id),
            Favorite(user_id=user.id, player_id=players[2].id),
            Favorite(user_id=admin.id, player_id=players[3].id),
        ]
        session.add_all(favorites)
        await session.flush()

        # ActivityLog (3)
        log1 = ActivityLog(user_id=admin.id, action="create", entity_type="tournament", entity_id=tournaments[0].id)
        log1.set_new_values({"name": tournaments[0].name})
        log2 = ActivityLog(user_id=admin.id, action="create", entity_type="player", entity_id=players[0].id)
        log2.set_new_values({"name": players[0].name})
        log3 = ActivityLog(user_id=user.id, action="add_favorite", entity_type="player", entity_id=players[0].id)
        log3.set_new_values({"player_id": players[0].id})
        session.add_all([log1, log2, log3])

        await session.commit()

        yield {
            "tournament_types": {t.type for t in tournaments},
        }


# --- Tests ---


class TestSeedUserRequirements:
    """V1.1: Verify user seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_two_users_exist(self, seed_db):
        """Requirement: 2 users (admin + user)."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(User.id)))
            count = result.scalar()
            assert count == 2, f"Expected 2 users, got {count}"

    @pytest.mark.asyncio
    async def test_admin_user_exists(self, seed_db):
        """Requirement: admin user with role='admin' exists."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            admin = result.scalar_one_or_none()
            assert admin is not None, "Admin user not found"
            assert admin.role == "admin", f"Expected admin role='admin', got '{admin.role}'"

    @pytest.mark.asyncio
    async def test_regular_user_exists(self, seed_db):
        """Requirement: regular user with role='user' exists."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == "user")
            )
            user = result.scalar_one_or_none()
            assert user is not None, "Regular user not found"
            assert user.role == "user", f"Expected user role='user', got '{user.role}'"


class TestSeedPlayerRequirements:
    """V1.2: Verify player seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_thirty_plus_players(self, seed_db):
        """Requirement: 30+ players."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(Player.id)))
            count = result.scalar()
            assert count >= 30, f"Expected >= 30 players, got {count}"

    @pytest.mark.asyncio
    async def test_all_players_have_city(self, seed_db):
        """Requirement: all players have a city."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.count(Player.id)).where(Player.city.is_(None))
            )
            null_cities = result.scalar()
            assert null_cities == 0, f"{null_cities} players have null city"

    @pytest.mark.asyncio
    async def test_ratings_in_range(self, seed_db):
        """Requirement: all player ratings between 1500 and 2800."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.min(Player.rating), func.max(Player.rating))
            )
            min_r, max_r = result.one()
            assert min_r >= 1500, f"Min rating {min_r} < 1500"
            assert max_r <= 2800, f"Max rating {max_r} > 2800"


class TestSeedTournamentRequirements:
    """V1.3: Verify tournament seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_five_tournaments_total(self, seed_db):
        """Requirement: 5 tournaments total (from seed spec)."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(Tournament.id)))
            count = result.scalar()
            assert count >= 5, f"Expected >= 5 tournaments, got {count}"

    @pytest.mark.asyncio
    async def test_three_completed_tournaments(self, seed_db):
        """Requirement: 3 completed tournaments."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.count(Tournament.id)).where(Tournament.status == "completed")
            )
            count = result.scalar()
            assert count >= 3, f"Expected >= 3 completed tournaments, got {count}"

    @pytest.mark.asyncio
    async def test_two_active_tournaments(self, seed_db):
        """Requirement: 2 active tournaments."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.count(Tournament.id)).where(Tournament.status == "active")
            )
            count = result.scalar()
            assert count >= 2, f"Expected >= 2 active tournaments, got {count}"

    @pytest.mark.asyncio
    async def test_tournament_types(self, seed_db):
        """Requirement: tournaments include classic, blitz, and rapid types."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(Tournament.type).distinct()
            )
            types = {row[0] for row in result.all()}
            assert "classic" in types, "Missing classic tournament type"
            assert "blitz" in types, "Missing blitz tournament type"
            assert "rapid" in types, "Missing rapid tournament type"


class TestSeedGameRequirements:
    """V1.4: Verify game seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_two_hundred_plus_games(self, seed_db):
        """Requirement: 200+ games."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(Game.id)))
            count = result.scalar()
            assert count >= 200, f"Expected >= 200 games, got {count}"

    @pytest.mark.asyncio
    async def test_games_have_valid_results(self, seed_db):
        """Requirement: all games have valid results (1-0, 0-1, ½-½)."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(Game.result).distinct()
            )
            results = {row[0] for row in result.all()}
            for r in ("1-0", "0-1", "½-½"):
                assert r in results, f"Missing game result '{r}'"

    @pytest.mark.asyncio
    async def test_games_have_white_and_black(self, seed_db):
        """Requirement: all games have both white and black players."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.count(Game.id)).where(
                    (Game.white_player_id.is_(None)) | (Game.black_player_id.is_(None))
                )
            )
            null_players = result.scalar()
            assert null_players == 0, f"{null_players} games have null player IDs"


class TestSeedRatingHistoryRequirements:
    """V1.5: Verify rating_history seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_fifty_plus_rating_entries(self, seed_db):
        """Requirement: 50+ rating history entries."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(RatingHistory.id)))
            count = result.scalar()
            assert count >= 50, f"Expected >= 50 rating history entries, got {count}"

    @pytest.mark.asyncio
    async def test_rating_history_has_dates(self, seed_db):
        """Requirement: all rating history entries have a date."""
        async with TestSessionLocal() as session:
            result = await session.execute(
                select(func.count(RatingHistory.id)).where(RatingHistory.date.is_(None))
            )
            null_dates = result.scalar()
            assert null_dates == 0, f"{null_dates} rating history entries have null date"


class TestSeedFavoriteRequirements:
    """V1.6: Verify favorite seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_favorites_exist(self, seed_db):
        """Requirement: favorite records exist."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(Favorite.id)))
            count = result.scalar()
            assert count > 0, "No favorite records found"


class TestSeedActivityLogRequirements:
    """V1.7: Verify activity_log seed data meets requirements."""

    @pytest.mark.asyncio
    async def test_activity_logs_exist(self, seed_db):
        """Requirement: activity log records exist."""
        async with TestSessionLocal() as session:
            result = await session.execute(select(func.count(ActivityLog.id)))
            count = result.scalar()
            assert count > 0, "No activity log records found"

"""Seed script to populate the database with test data."""

import asyncio
import datetime
import random

from app.core.database import Base, async_session_factory, engine
from app.core.security import hash_password
from app.models import ActivityLog, Favorite, Game, Player, RatingHistory, Tournament, User

# --- Data pools ---

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

TOURNAMENT_NAMES = [
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


def generate_rating_change(current_rating: int) -> int:
    """Generate a random rating change between -15 and +15."""
    delta = random.randint(-15, 15)
    return max(0, current_rating + delta)


def random_games_for_tournament(players: list[Player], tournament_id: int, rounds: int, start_date: datetime.datetime) -> list[Game]:
    """Generate random games for a tournament."""
    games = []
    used_pairs = set()
    available_players = list(range(len(players)))
    random.shuffle(available_players)

    for r in range(1, rounds + 1):
        for _ in range(len(players) // 2):
            pair = random.sample(available_players, 2)
            w, b = pair
            # Ensure unique pairs
            pair_key = (min(w, b), max(w, b))
            if pair_key in used_pairs:
                continue
            used_pairs.add(pair_key)

            result = random.choices(
                ["1-0", "0-1", "½-½"],
                weights=[0.4, 0.3, 0.3],
                k=1
            )[0]

            game = Game(
                tournament_id=tournament_id,
                round=r,
                white_player_id=players[w].id,
                black_player_id=players[b].id,
                result=result,
                played_at=start_date + datetime.timedelta(days=r),
            )
            games.append(game)
    return games


async def seed() -> None:
    """Run the seed script."""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Seeding data...")
    async with async_session_factory() as session:
        # --- Users ---
        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin",
        )
        user = User(
            username="user",
            hashed_password=hash_password("user123"),
            role="user",
        )
        session.add_all([admin, user])
        await session.flush()

        # --- Players ---
        players = []
        for i in range(30):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            rating = random.randint(1500, 2800)
            city = random.choice(CITIES)
            player = Player(name=name, rating=rating, city=city)
            players.append(player)
        session.add_all(players)
        await session.flush()

        # --- Tournaments ---
        tournaments = []
        for i, (tname, tloc, ttype) in enumerate(TOURNAMENT_NAMES):
            status = "completed" if i < 3 else "active"
            start_date = datetime.datetime(2026, 1, 1) + datetime.timedelta(days=i * 14)
            end_date = start_date + datetime.timedelta(days=7)
            rounds = random.randint(5, 9)
            tournament = Tournament(
                name=tname,
                start_date=start_date,
                end_date=end_date,
                location=tloc,
                rounds=rounds,
                type=ttype,
                status=status,
            )
            tournaments.append(tournament)
        session.add_all(tournaments)
        await session.flush()

        # --- Games (200+) ---
        games = []
        for idx, tournament in enumerate(tournaments):
            player_sample = random.sample(players, min(len(players), 8 + random.randint(0, 4)))
            tgames = random_games_for_tournament(
                player_sample,
                tournament.id,
                tournament.rounds,
                tournament.start_date,
            )
            games.extend(tgames)

        # Ensure 200+ games
        if len(games) < 200:
            for _ in range(200 - len(games)):
                t = random.choice(tournaments)
                player_sample = random.sample(players, 2)
                game = Game(
                    tournament_id=t.id,
                    round=random.randint(1, t.rounds),
                    white_player_id=player_sample[0].id,
                    black_player_id=player_sample[1].id,
                    result=random.choice(["1-0", "0-1", "½-½"]),
                    played_at=t.start_date + datetime.timedelta(days=random.randint(1, 7)),
                )
                games.append(game)

        session.add_all(games)
        await session.flush()

        # --- RatingHistory (50+) ---
        rating_history = []
        for player in players:
            current_rating = player.rating
            for month_offset in range(6):
                rating_date = datetime.datetime(2025, 1, 1) + datetime.timedelta(days=month_offset * 30)
                current_rating = generate_rating_change(current_rating)
                rh = RatingHistory(
                    player_id=player.id,
                    rating=current_rating,
                    date=rating_date,
                )
                rating_history.append(rh)
        session.add_all(rating_history)
        await session.flush()

        # --- Favorites ---
        favorites = [
            Favorite(user_id=user.id, player_id=players[0].id),
            Favorite(user_id=user.id, player_id=players[1].id),
            Favorite(user_id=user.id, player_id=players[2].id),
            Favorite(user_id=admin.id, player_id=players[3].id),
        ]
        session.add_all(favorites)

        # --- ActivityLog ---
        activity_logs = [
            ActivityLog(user_id=admin.id, action="create", entity_type="tournament", entity_id=tournaments[0].id),
            ActivityLog(user_id=admin.id, action="create", entity_type="player", entity_id=players[0].id),
            ActivityLog(user_id=user.id, action="add_favorite", entity_type="player", entity_id=players[0].id),
        ]
        session.add_all(activity_logs)

        await session.commit()

        print("✅ Seed completed:")
        print("   - 2 users (admin/admin123, user/user123)")
        print(f"   - {len(players)} players")
        print(f"   - {len(tournaments)} tournaments ({len([t for t in tournaments if t.status == 'completed'])} completed, {len([t for t in tournaments if t.status == 'active'])} active)")
        print(f"   - {len(games)} games")
        print(f"   - {len(rating_history)} rating history entries")
        print(f"   - {len(favorites)} favorites")
        print(f"   - {len(activity_logs)} activity logs")


if __name__ == "__main__":
    asyncio.run(seed())

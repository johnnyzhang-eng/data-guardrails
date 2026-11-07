"""Create a repeatable SQLite demo, replacing its three demo tables only."""
import argparse
import random
import sqlite3
from pathlib import Path

SEED = 16
AS_OF = "2025-01-12T00:00:00+00:00"
CHECK_DAY = "2025-01-07"


def populate(connection: sqlite3.Connection, seed: int = SEED) -> None:
    """Rebuilding gives identical logical rows, rather than appending duplicates.

    Raw orders deliberately have no key or reference constraints so bad rows
    can be inspected. Dimension tables do have primary keys. Amount is in
    integer demo currency units. All timestamps are UTC.
    """
    rng = random.Random(seed)
    with connection:
        for table in ("orders", "merchants", "users"):
            connection.execute(f"DROP TABLE IF EXISTS {table}")
        connection.execute("CREATE TABLE merchants (merchant_id INTEGER PRIMARY KEY, city TEXT, category TEXT)")
        connection.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, city TEXT, register_date TEXT)")
        connection.execute("""CREATE TABLE orders (
            order_id INTEGER, user_id INTEGER, merchant_id INTEGER,
            order_time TEXT, amount INTEGER, status TEXT)""")
        connection.executemany("INSERT INTO merchants VALUES (?, ?, ?)", [
            (1, "Lake City", "noodles"), (2, "Hill City", "rice"), (3, "Lake City", "pizza")])
        connection.executemany("INSERT INTO users VALUES (?, ?, ?)", [
            (i, "Lake City" if i % 2 else "Hill City", "2024-12-01") for i in range(1, 11)])
        rows = []
        for day in range(1, 9):
            for _ in range(4 if day == 7 else 20):
                rows.append((len(rows) + 1, rng.randint(1, 10), rng.randint(1, 3),
                             f"2025-01-{day:02d}T12:00:00+00:00", rng.randint(10, 90),
                             "cancelled" if rng.randrange(5) == 0 else "delivered"))
        rows[1] = (*rows[1][:4], 0, rows[1][5])  # zero is known, unlike NULL
        rows[20] = (*rows[20][:4], None, rows[20][5])
        rows[40] = (*rows[40][:2], 9999, *rows[40][3:])
        rows.append(rows[-1])  # one exact duplicate on the final day
        connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("artifacts/delivery.sqlite3"))
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.db) as connection:
        populate(connection)
        count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"Created synthetic data: {count} order rows; seed={SEED}")


if __name__ == "__main__":
    main()

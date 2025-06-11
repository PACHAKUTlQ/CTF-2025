import os
import sqlite3
import sys

conn = sqlite3.connect("db.sqlite", check_same_thread=False)


class Model:
    @classmethod
    def one(self, conditions, ordering="id"):
        where = " AND ".join([f"{k} = '{v}'" for k, v in conditions.items()])
        # --- DEBUG PRINT ---
        sql = f"SELECT * FROM {self.__name__.lower()} WHERE {where} ORDER BY {
            ordering
        } LIMIT 1"
        print(f"[*] db.py - one() - SQL: {sql}", flush=True)
        # --- END DEBUG ---
        c = conn.cursor()
        c.execute(sql)
        r = c.fetchone()
        if r:
            # --- DEBUG PRINT ---
            print(f"[*] db.py - one() - Result: {r}", flush=True)
            # --- END DEBUG ---
            return self(*r)
        # --- DEBUG PRINT ---
        print(f"[*] db.py - one() - No result", flush=True)
        # --- END DEBUG ---
        return None

    @classmethod
    def scalar(self, conditions, field):
        # --- DEBUG PRINT ---
        print(
            f"[*] db.py - scalar() - Conditions: {conditions}, Field: {field}",
            flush=True,
        )
        # --- END DEBUG ---
        one = self.one(conditions, field)
        if one:
            # --- DEBUG PRINT ---
            result = getattr(one, field)
            print(f"[*] db.py - scalar() - Returning: {result}", flush=True)
            # --- END DEBUG ---
            return result
        # --- DEBUG PRINT ---
        print(f"[*] db.py - scalar() - Returning None", flush=True)
        # --- END DEBUG ---
        return None

    @classmethod
    def update(self, conditions, updates):
        where = " AND ".join([f"{k} = '{v}'" for k, v in conditions.items()])
        set_clause = ", ".join(
            [f"{k} = '{v}'" for k, v in updates.items()]
        )  # Renamed 'set' -> 'set_clause'
        # --- DEBUG PRINT ---
        sql = f"UPDATE {self.__name__.lower()} SET {set_clause} WHERE {where}"
        print(f"[*] db.py - update() - SQL: {sql}", flush=True)
        # --- END DEBUG ---
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        # --- DEBUG PRINT ---
        print(f"[*] db.py - update() - Committed", flush=True)
        # --- END DEBUG ---


class Users(Model):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


class Credentials(Model):
    def __init__(self, id, user_id, credential_id, public_key, sign_count):
        self.id = id
        self.user_id = user_id
        self.credential_id = credential_id
        self.public_key = public_key
        self.sign_count = sign_count


def init_db():
    c = conn.cursor()
    c.execute(
        """
        DROP TABLE IF EXISTS users;
        """
    )
    c.execute(
        """
        DROP TABLE IF EXISTS credentials;
        """
    )
    c.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL
        );
        """
    )
    c.execute(
        """
        CREATE TABLE credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            credential_id TEXT NOT NULL,
            public_key TEXT NOT NULL,
            sign_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    conn.commit()


def create_user(username, role, credential_id, public_key):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO users (username, role)
        VALUES (?, ?);
        """,
        (username, role),
    )
    c.execute(
        """
        INSERT INTO credentials (user_id, credential_id, public_key)
        VALUES (
            (SELECT id FROM users WHERE username = ?),
            ?,
            ?
        );
        """,
        (username, credential_id, public_key),
    )
    conn.commit()


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "init":
    init_db()
    # --- DEBUG PRINT ---
    print("[*] db.py - Initializing DB and creating admin user", flush=True)
    # --- END DEBUG ---
    create_user(
        "admin",
        "admin",
        os.environ.get("ADMIN_CREDENTIAL_ID", "whatever"),
        os.environ.get("ADMIN_PUBLIC_KEY", "whatever"),
    )
    conn.close()
    print("[*] db.py - Initialization complete", flush=True)

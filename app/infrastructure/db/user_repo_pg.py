from psycopg import Connection
from psycopg.errors import UniqueViolation
from app.domain.entities.user import User
from app.domain.interfaces.user_repo import UserRepo
from app.core.exceptions import UserAlreadyExists


class PostgresUserRepo(UserRepo):
    def __init__(self, conn: Connection):
        self.conn = conn

    def create(self, email: str, password_hash: str) -> int:
        try:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (email, password_hash, is_active)
                        VALUES (%s, %s, false)
                        RETURNING id
                        """,
                        (email, password_hash),
                    )
                    return cur.fetchone()["id"]
        except UniqueViolation:
            # Map infra error → domain exception
            raise UserAlreadyExists()

    def get_by_email(self, email: str):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return User(**row) if row else None

    def get_by_id(self, user_id: int):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return User(**row) if row else None

    def activate(self, user_id: int) -> bool:
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_active = true WHERE id = %s RETURNING id",
                    (user_id,),
                )
                return cur.fetchone() is not None

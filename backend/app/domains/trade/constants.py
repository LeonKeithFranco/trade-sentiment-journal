from asyncpg.compat import StrEnum


class Direction(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"

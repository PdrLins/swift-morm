import enum


class KeyProvider(enum.Enum):
    POSTGRES = 1,
    MYSQL = 2,
    SQLSERVER = 3,
    ORACLE = 4

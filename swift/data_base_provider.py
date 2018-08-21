import psycopg2
import pyodbc
from swift.swift import KeyProvider


class InstanceProvide(object):
    __key: None

    def __init__(self, connectionString: str, provider: any):
        self.connectionString = connectionString
        self.provider = provider
        self.__defineKey()

    def getKey(self):
        return self.__key

    def __defineKey(self):
        """
            Define what is the key of the provide
        """
        if self.provider is PostgresSqlProvider:
            self.__key = KeyProvider.POSTGRES
        elif self.provider is MySqlProvider:
            self.__key = KeyProvider.MYSQL
        elif self.provider is OracleSqlProvider:
            self.__key = KeyProvider.ORACLE
        elif self.provider is SqlServerProvider:
            self.__key = KeyProvider.SQLSERVER
        else:
            raise Exception("SwiftError(100): Provider unknown to the swift.")


class PostgresSqlProvider:
    pass


class MySqlProvider:
    # raise Exception("Swift does not support MySql Database yet.")
    pass


class OracleSqlProvider:
    # raise Exception("Swift does not support Oracle Database yet.")
    pass


class SqlServerProvider:
    # raise Exception("Swift does not support SqlServer Database yet.")
    pass

from enum import Enum
from typing import TypeVar, Type
from swift.data_base_provider import *  # ficar esperto porque tem aqui coisa do provedor db que ta errado no cursor

T = TypeVar('T')


class RowType(Enum):
    Multiple = 1,
    Single = 2,
    SingleOrDefault = 3


class SwiftSqlMapper(object):
    __poolConnection: [] #avaliar como resolver o problema de privacidade desse atributo
    __initialized = None
    __providers = []

    @classmethod
    def __ensureInitialization(cls):
        if not cls.__initialized:
            cls.__poolConnection = cls.__createConnections()
            cls.__initialized = True

    @classmethod
    def __createConnections(cls) -> object:
        for pr in cls.__providers:
            yield {pr.getKey(): SwiftSqlMapper.connect(pr.connectionString, pr.provider)}

    @classmethod
    def __getConnection(cls, keyProvider):
        __connection = None
        for c in cls.__poolConnection:
            if c.get(keyProvider) is not None:
                __connection = c.get(keyProvider)
                break

        if __connection is None:
            raise Exception("SwiftError(106): The %s connection tha was passed was not found." % keyProvider)

        return __connection

    @classmethod
    def __ImplementExecute(cls, providerKey: KeyProvider, commandText: str, parameters: object = None, doCommit: bool = True)-> int:
        __connection = cls.__getConnection(providerKey)
        cursor = __connection.cursor()
        try:
            if parameters is None:
                cursor.execute(commandText)
            else:
                cursor.execute(commandText, parameters)
            _id = cursor.fetchone()[0]

        except ValueError as e:
            raise Exception('SwiftError(107): A error occurred during try to execute the cursor. (%s)' % e)
        finally:
            cursor.close()
            if doCommit:
                __connection.commit()

            if __connection is not None:
                __connection.close()

        return _id

    # ajeitar os parametros para que avalie se ta ok ou não
    @classmethod
    def __ImplementQuery(cls, providerKey: KeyProvider, commandText: str, buffered: bool = False, parameters: object = None,  classType: Type[T] = None) -> [T]:
        __connection = cls.__getConnection(providerKey)
        cursor = __connection.cursor()
        cls.__r = []
        cls.__dictList = []

        try:
            if parameters is None:
                cursor.execute(commandText)
            else:
                cursor.execute(commandText, parameters)

            _row = cursor.fetchone()
            while _row:
                _dict = {}
                for idx, col in enumerate(cursor.description):
                    _dict[col[0].lower()] = _row[idx].strip() if type(_row[idx]) is str is not None else _row[idx]

                cls.__dictList.append(_dict)
                _row = cursor.fetchone()

            if classType is None and cls.__dictList:
                return cls.__dictList
            elif cls.__dictList:
                _objAttr = []
                for attr in vars(classType()):
                    _objAttr.append(attr)

                for current in cls.__dictList:
                    _record = classType()
                    for column in _objAttr:
                        if column.lower() in current:
                            _record.__setattr__(column, current[column.lower()])

                    cls.__r.append(_record)

        except ValueError as e:
            raise Exception('SwiftError(107): A error occurred during try to execute the cursor. (%s)' % e)

        finally:
            cursor.close()
            __connection.close()

        return cls.__r

    @classmethod
    def __prepareCommandDefinition(cls, commandText: str) -> str:
        return commandText

    @classmethod
    def __processQuery(cls, commandText: str, providerKey: KeyProvider, parameters: object = None, classType: Type[T] = None):
        global data
        try:
            cls.__ensureInitialization()
            # cuidar do command sql, parametros e algo mais depois
            command = cls.__prepareCommandDefinition(commandText)
            data = cls.__ImplementQuery(providerKey, command, False, parameters, classType)
        except ValueError as e:
            raise Exception('SwiftError(105): Error during try execute query. (%s)' % e)
        return data

    @classmethod
    def __processExecute(cls, commandText: str, providerKey: KeyProvider, parameters: object = None):
        global data
        try:
            cls.__ensureInitialization()
            # cuidar do command sql, parametros e algo mais depois
            command = cls.__prepareCommandDefinition(commandText)
            data = cls.__ImplementExecute(providerKey, command, parameters, True)
        except ValueError as e:
            raise Exception('SwiftError(111): Error during try execute query. (%s)' % e)
        return data

    @classmethod
    def Query(cls, commandText: str, providerKey: KeyProvider, parameters: object = None, classType: Type[T] = None) -> [T]:
        """
            Method responsible to execute queries in database that do not change data. For instance: Selects
            :param providerKey: key of provider that the swift will use the db connection'
            :param parameters: Parameters
            :param classType: Generic T (Type of object that will result),
            :param commandText: str (Sql statement to execute in DataBase)
            :return [T]: return a list of T (A generic object, based on the
        """
        __rowTye = RowType.Multiple;
        return cls.__processQuery(commandText, providerKey, parameters, classType)

    @classmethod
    def Single(cls, commandText: str, providerKey: KeyProvider, parameters: object = None, classType: Type[T] = None) -> T:
        """
            Method responsible to execute queries in database that do not change data. For instance: Selects
            :param providerKey: key of provider that the swift will use the db connection'
            :param parameters: Parameters
            :param classType: Generic T (Type of object that will result),
            :param commandText: str (Sql statement to execute in DataBase)
            :return [T]: return a list of T (A generic object, based on the
        """
        __rowType = RowType.Single
        __result = cls.__processQuery(commandText, providerKey, parameters, classType)

        if len(__result) > 1 or len(__result) == 0:
            raise Exception("SwiftError(109): You tried to execute Single Query. The query returns more than one element or none.")

        return __result[0]

    @classmethod
    def SingleOrDefault(cls, commandText: str, providerKey: KeyProvider, parameters: object = None, classType: Type[T] = None) -> [T]:
        """
            Method responsible to execute queries in database but just return only one item or nothing. For instance: Selects
            :param providerKey: key of provider that the swift will use the db connection'
            :param parameters: Parameters
            :param classType: Generic T (Type of object that will result),
            :param commandText: str (Sql statement to execute in DataBase)
            :return [T]: return a list of T (A generic object, based on the
        """
        __rowType = RowType.SingleOrDefault
        __result = cls.__processQuery(commandText, providerKey, parameters, classType)

        if len(__result) > 1:
            raise Exception("SwiftError(108): The query returns more than one element.")

        return __result[0] if len(__result) == 1 else None

    @classmethod
    def Execute(cls, commandText: str, providerKey: KeyProvider, parameters: object):
        """ Method responsible to execute queries in database that do not change data. For instance: Selects
           :param providerKey:
           :param parameters: Parameters
           :param commandText: str (Sql statement to execute in DataBase
        """
        pass

    @classmethod
    def ExecuteScalar(cls, commandText: str, providerKey: KeyProvider, parameters: object =None)-> int:
        """ Method responsible to execute queries in database that do not change data. For instance: Selects
           :param providerKey:
           :param parameters: Parameters
           :param commandText: str (Sql statement to execute in DataBase)
           :return return the id that was inserted
        """
        return cls.__processExecute(commandText, providerKey, parameters)

    @staticmethod
    def connect(connString: str, provider: object) -> object:
        """
            Method responsible to connect in Database depending on the provider passed by parameter.
            :param connString: string connection to connect in database depending on the provider passed by parameter.
            :param provider: Parameters to execute the query passed by parameter.
            :return cursor from the connection
        """
        __connection = None

        try:
            if provider is PostgresSqlProvider:
                __connection = psycopg2.connect(connString, connection_factory=PostgresSqlProvider)
            elif provider is MySqlProvider:
                pass

            elif provider is OracleSqlProvider:
                pass

            elif provider is SqlServerProvider:
                __connection = pyodbc.connect(connString)
        except ValueError as e:
            raise Exception('SwiftError(103): Unable to connect to the database. Please, try again %s' % e)
        finally:
            return __connection

    @classmethod
    def setProviders(cls, dbProviders: []):
        for new_provide in dbProviders:
            if len(cls.__providers) == 0:
                cls.__providers.append(new_provide)
            else:
                for existent_provide in cls.__providers:
                    if new_provide.getKey() not in vars(existent_provide).values():
                        cls.__providers.append(new_provide)
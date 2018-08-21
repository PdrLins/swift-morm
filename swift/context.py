from flask import current_app
from .sql_mapper import *


class Context(SwiftSqlMapper):
    __providers_keys = []

    def __init__(self, providers: []):
        self.setProviders(providers)

    @staticmethod
    def get_context():
        post_connString = current_app.config.get('POSTGRESQL_DATABASE_URI')  # need to define the connection string
        sqlServer_connString = current_app.config.get('SQLSERVER_DATABASE_URI') # need to define the connection string
        ins_Post = InstanceProvide(post_connString, PostgresSqlProvider)
        ins_sqlServer = InstanceProvide(sqlServer_connString, SqlServerProvider)
        context = Context([ins_Post, ins_sqlServer])
        return context

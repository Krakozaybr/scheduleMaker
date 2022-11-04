import sqlite3
import os
from scheduler.config import STORE_DIR, MAIN_DB_NAME
import scheduler.data.database_interaction.sql_commands as sql_commands
import glob


class DatabaseAlreadyExistsException(Exception):
    pass


class DatabaseDoesNotExist(Exception):
    pass


def _get_db_filename(name):
    filename = os.path.join(STORE_DIR, name)
    if not filename.endswith('.sqlite'):
        filename += '.sqlite'
    return filename


def _create(commands, filename):
    with sqlite3.connect(filename) as con:
        cur = con.cursor()
        for command in commands:
            cur.execute(command)


def db_exists(name: str):
    return os.path.exists(_get_db_filename(name))


def check_db_exists(func):
    """
    Decorator. Checks whether database with name = {name} exists
    """
    def wrapper(name, *args, **kwargs):
        if not db_exists(name):
            raise DatabaseDoesNotExist
        return func(_get_db_filename(name), *args, **kwargs)
    return wrapper


def create_db_with_models(name: str, *models):
    """
    Creates database with schedule structure
    :param name: DB name
    :raises TableAlreadyExistsException if table with such name already exists
    """

    if db_exists(name):
        raise DatabaseAlreadyExistsException

    filename = _get_db_filename(name)
    create_commands = []
    for model in models:
        command = sql_commands.CREATE_DB_TABLE % (
            model.get_table_name(),
            model.to_sql()
        )
        create_commands.append(command)
    _create(create_commands, filename)


@check_db_exists
def delete_db(name):
    """
    Deletes database with name = {name}
    :param name: DB name
    :raises: TableDoesNotExist
    """

    filename = _get_db_filename(name)
    os.remove(filename)


def get_dbs():
    result = []
    for filename in glob.glob(os.path.join(STORE_DIR, '*.sqlite')):
        name = os.path.splitext(os.path.basename(filename))[0]
        result.append(name)
    return result

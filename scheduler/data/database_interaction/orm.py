import sqlite3
from .db_utils import check_db_exists
from .sql_commands import SELECT_ALL, UPDATE_BY_ID, INSERT, DELETE_BY_ID


@check_db_exists
def get(db_name: str, table: str, fields='*'):
    """
    Takes all values from *fields and returns them
    :param db_name: name of the database
    :param table: name of the table in the db
    :param fields: values of these fields will be returned
                   in the same order
    :return: values of the fields
    """
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        command = SELECT_ALL % (', '.join(fields), table)
        return cur.execute(command).fetchall()


@check_db_exists
def update_by_ids(db_name: str, table: str, element_id: int,
                  fields: tuple[str], values_sets: tuple[tuple[str]]):
    """
    Sets field values of the table in the db with name = {db_name}
    to *values
    :param db_name: name of the database
    :param table: name of the table in the db
    :param element_id: id of the element in the table
    :param fields: all fields of the table
    :param values_sets: values sets for fields
    """
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        for values in values_sets:
            new_vals = []
            for key, val in zip(fields, values):
                if isinstance(val, int):
                    new_vals.append(f'{key} = {val}')
                else:
                    new_vals.append(f'{key} = "{val}"')
            command = UPDATE_BY_ID % (table, ', '.join(new_vals), element_id)
            cur.execute(command)


@check_db_exists
def update_by_id(db_name: str, table: str, element_id: int, fields: tuple[str], values: tuple[str]):
    """
    Sets field values of the table in the db with name = {db_name}
    to *values
    :param db_name: name of the database
    :param table: name of the table in the db
    :param element_id: id of the element in the table
    :param fields: all fields of the table
    :param values: values for fields
    """
    update_by_ids(db_name, table, element_id, fields, (values,))


@check_db_exists
def insert_many(db_name: str, table: str, fields: tuple[str], values_sets: tuple[tuple[str]]):
    """
    Inserts into table of the database with name = {db_name}
    *fields and set them *values
    :param db_name: name of the database
    :param table: name of the table in the db
    :param fields: all fields of the table
    :param values_sets: values sets for fields
    """
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        for values in values_sets:
            new_vals = []
            for val in values:
                if isinstance(val, int):
                    new_vals.append(str(val))
                else:
                    new_vals.append(f'"{val}"')
            command = INSERT % (table, ', '.join(fields), ', '.join(new_vals))
            cur.execute(command)


@check_db_exists
def insert(db_name: str, table: str, fields: tuple[str], values: tuple[str]):
    """
    Inserts into table of the database with name = {db_name}
    *fields and set them *values
    :param db_name: name of the database
    :param table: name of the table in the db
    :param fields: all fields of the table
    :param values: values for fields
    """
    insert_many(db_name, table, fields, (values,))


@check_db_exists
def delete_by_ids(db_name: str, table: str, ids: tuple[int]):
    """
    Deletes elements with ids from table
    of the database with name = {db_name}
    :param db_name: name of the database
    :param table: name of the table in the db
    :param ids: ids of elements in the table
    """
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        for element_id in ids:
            command = DELETE_BY_ID % (table, element_id)
            cur.execute(command)


@check_db_exists
def delete_by_id(db_name: str, table: str, element_id: int):
    """
    Deletes element with id = {element_id} from table
    of the database with name = {db_name}
    :param db_name: name of the database
    :param table: name of the table in the db
    :param element_id: id of the element in the table
    """
    delete_by_ids(db_name, table, (element_id,))

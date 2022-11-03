import scheduler.config as config

groups = config.groups_table_name
teachers = config.teachers_table_name
classrooms = config.classrooms_table_name
lessons = config.lessons_table_name
days = config.days_table_name
weeks = config.weeks_table_name

CREATE_MAIN_DB_TABLES = (
    f"CREATE TABLE IF NOT EXISTS {groups}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   name TEXT"
    f");",
    f"CREATE TABLE IF NOT EXISTS {teachers}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   name TEXT,"
    f"   image TEXT DEFAULT 'default.png'"
    f");",
    f"CREATE TABLE IF NOT EXISTS {classrooms}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   name TEXT"
    f");",
    f"CREATE TABLE IF NOT EXISTS {lessons}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   teacher_id INTEGER,"
    f"   name TEXT"
    f");"
)
CREATE_SCHEDULE_TABLES = (
    f"CREATE TABLE IF NOT EXISTS {days}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   lessons TEXT,"
    f"   group_id TEXT,"
    f"   day_order INTEGER"
    f");"
    f"",
    f"CREATE TABLE IF NOT EXISTS {weeks}("
    f"   id INTEGER PRIMARY KEY AUTOINCREMENT,"
    f"   days TEXT,"
    f"   group_id INTEGER"
    f");"
)
SELECT_ALL = 'SELECT %s FROM %s'
UPDATE_BY_ID = 'UPDATE %s SET %s WHERE id = %s;'
INSERT = 'INSERT INTO %s(%s) VALUES(%s)'
DELETE_BY_ID = 'DELETE from %s where id = %s;'

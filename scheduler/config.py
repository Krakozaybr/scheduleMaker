import os

CURRENT_DIR = os.path.dirname(__file__)
STORE_DIR = os.path.join(CURRENT_DIR, 'data/store')
IMAGES_DIR = os.path.join(STORE_DIR, 'images/')
MAIN_DB_NAME = 'main_db'

STANDARD_IMAGE_SIZE = 200, 200

groups_table_name = 'groups'
teachers_table_name = 'teachers'
classrooms_table_name = 'classrooms'
lessons_table_name = 'lessons'
days_table_name = 'days'
weeks_table_name = 'weeks'

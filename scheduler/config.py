import os

CURRENT_DIR = os.path.dirname(__file__)
STORE_DIR = os.path.join(CURRENT_DIR, 'data/store')
IMAGES_DIR = os.path.join(STORE_DIR, 'images/')
MAIN_DB_NAME = 'main_db'
DEFAULT_TEACHER_IMG = 'default.png'
EDIT_IMG = 'edit.png'
DELETE_IMG = 'delete.png'
UPLIFT_IMG = 'uplift.png'
DOWNLIFT_IMG = 'downlift.png'

STANDARD_IMAGE_SIZE = 200, 200

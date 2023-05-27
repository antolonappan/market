import os
from utils import hash_password

DATABASE_CONFIG = {
    'database': "/home/anto/scratch/mystocks.db",
    'username': os.environ.get('STOCKUSER'),
    'password': os.environ.get('STOCKPASS')
}
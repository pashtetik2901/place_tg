from database.models import get_place_from_db, ModelWrite
from database.config_reader import config
import redis

try:
    data = get_place_from_db('962582174')
    print(data[0].title)
except:
    print('Error')



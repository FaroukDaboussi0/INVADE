import pytest
from mongoengine import connect, disconnect, get_connection
from config import Config 

@pytest.fixture(scope='session', autouse=True)
def init_db():

    connect("test", host=Config.MONGODB_SETTINGS['host'], port=Config.MONGODB_SETTINGS['port'])

    yield 


    disconnect()

@pytest.fixture(autouse=True)
def clear_db():

    db_connection = get_connection() 
    db_connection.drop_database('test') 
    db_connection.client.admin.command('createDatabase', 'test')

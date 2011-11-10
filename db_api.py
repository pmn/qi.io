# db interactions
import logging
import pymongo
import settings

MONGODB_CONNECTION = pymongo.connection.Connection(host=settings.MONGODB_HOST)

class QiDB(object):
    def __init__(self, db_name='qi'):
        self.db = MONGODB_CONNECTION(db_name)
        logging.debug('Connected to database: {}'.format(db_name))

    def get_entry(self, entryid):
        logging.debug('Fetching entry: {}'.format(entryid))

    def save_entry(self, entry):
        logging.info('Saving entry: {}'.format(repr(entry)))

    def get_user(self, userid):
        logging.debug('Fetching user: {}'.format(userid))

    def save_user(self, user):
        logging.info('Saving user: {}'.format(repr(user)))

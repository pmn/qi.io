# db interactions
import logging
import pymongo
import settings

MONGODB_CONNECTION = pymongo.connection.Connection(host=settings.MONGODB_HOST)

class QiDB(object):
    def __init__(self, db_name='qi'):
        """Set up the database"""
        self.db = MONGODB_CONNECTION[db_name]
        logging.debug('Connected to database: {}'.format(db_name))

    def get_entry(self, entryid):
        """Get a single entry from the database"""
        logging.debug('Fetching entry: {}'.format(entryid))
        return self.db.entries.find_one({"id": entryid})

    def get_entries_for_user(self, username):
        """Get all the entries for a specific user"""
        logging.debug('Fetching entries for user: {}'.format(username))
        return self.db.entries.find({'created_by': username})

    def get_current_entry_for_user(self, username):
        """Get the user's current entry"""
        logging.debug('Fetching current entry for user: {}'.format(username))
        return self.db.entries.find({'created_by': username,
                                     'current': true})

    def save_entry(self, entry):
        """Save an entry into the database"""
        logging.info('Saving entry: {}'.format(repr(entry)))

        # Insert the new entry
        self.db.entries.update({'id': entry.id},
                               {'$set': {'id': entry.id,
                                         'raw_body': entry.raw_body,
                                         'tags': entry.tags,
                                         'created_by': entry.created_by,
                                         'created_at': entry.created_at,
                                         'parsed': False}},
                               upsert=True)



    def get_user(self, username):
        """Fetch a user record"""
        logging.debug('Fetching user: {}'.format(username))
        return self.db.users.find_one({"username": username})

    def save_user(self, user):
        """Save a user record"""
        logging.info('Saving user: {}'.format(repr(user)))
        self.db.users.insert({'username': user.username,
                              'password': user.password,
                              'email': user.email})

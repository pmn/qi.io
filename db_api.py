# db interactions
from bson.code import Code
from datetime import datetime
import logging
import pymongo
import settings

MONGODB_CONNECTION = pymongo.connection.Connection(host=settings.MONGODB_HOST)

class QiDB(object):
    def __init__(self, db_name='app1875861'):
        """Set up the database"""
        self.db = MONGODB_CONNECTION[db_name]
        logging.debug('Connected to database: {}'.format(db_name))

    def get_entry(self, entryid, created_by):
        """Get a single entry from the database"""
        logging.debug('Fetching entry: {}'.format(entryid))
        return self.db.entries.find_one({'id': entryid,
                                         'created_by': created_by})

    def get_all_entries(self):
        """Return all entries from the database.
        This should only be used for administrative functions."""
        logging.info("Fetching all entries from the database.")
        return self.db.entries.find()

    def get_entries_for_user(self, username, page=0, numperpage=settings.ITEMS_PER_PAGE):
        """Get all the entries for a specific user"""
        logging.debug('Fetching entries for user: {}'.format(username))
        return self.db.entries.find({'created_by': username,
                                     'id': {'$ne': 'scratchpad'}
                                     }).sort('id',pymongo.DESCENDING
                                             ).skip((page * numperpage)).limit(numperpage)

    def get_entry_count_for_user(self, username):
        """Get a count of all the user's records"""
        logging.debug('Fetching the entry count for user: {}'.format(username))
        return self.db.entries.find({'created_by': username,
                                     'id': {'$ne': 'scratchpad'}}).count()

    def get_current_entry_for_user(self, username):
        """Get the user's current entry"""
        logging.debug('Fetching current entry for user: {}'.format(username))
        current_entry = self.db.entries.find({'created_by': username,
                                              'id': {'$ne': 'scratchpad'}}
                                             ).sort('id', pymongo.DESCENDING).limit(1)
        if current_entry and current_entry.count() > 0:
            return current_entry[0]
        else:
            return None

    def get_user_tags(self, username):
        """Get a listing of tags with counts for this user."""
        mapfn = Code("function () {"
                     "  this.tags.forEach(function(z) {"
                     "    emit(z, 1);"
                     "  });"
                     "}")

        reducefn = Code("function (key, values) {"
                        "  var total = 0;"
                        "  for (var i = 0; i < values.length; i++) {"
                        "    total += values[i];"
                        "}"
                        "  return total;"
                        "}")

        return self.db.entries.map_reduce(mapfn,
                                     reducefn,
                                     "taglist",
                                     query={"created_by":username })

    def get_tagged_entries(self, username, tag):
        """Get entries for user with <username> tagged with <tag>"""
        logging.debug('Fetching {}\'s entries tagged with {}'.format(username, tag))
        return self.db.entries.find({'created_by': username,
                                     'id': {'$ne': 'scratchpad'},
                                     'tags': tag}).sort('id', pymongo.DESCENDING)

    def search_user_entries(self, username, searchterm):
        """Get entries for <username> containing <searchterm>"""
        logging.debug("Searching {}'s entries for term {}".format(username, searchterm))
        return self.db.entries.find({'created_by': username,
                                     'id': {'$ne': 'scratchpad'},
                                     '_keywords': searchterm}).sort('id', pymongo.DESCENDING)

    def save_entry(self, entry):
        """Save an entry into the database"""
        logging.info('Saving entry: {}'.format(repr(entry)))

        # Insert the new entry
        self.db.entries.update({'id': entry.id,
                                'created_by': entry.created_by},
                               {'$set': {'id': entry.id,
                                         'body': entry.body,
                                         'raw_body': entry.raw_body,
                                         'todos': entry.todos,
                                         'tags': entry.tags,
                                         '_keywords': entry.keywords,
                                         'created_by': entry.created_by,
                                         'created_at': entry.created_at,
                                         'updated_by': entry.updated_by,
                                         'updated_at': entry.updated_at,
                                         'parsed': False}},
                               upsert=True)

    def delete_entry(self, entry):
        """'Delete' an entry from the database"""
        logging.info('Deleting entry: {}'.format(repr(entry)))

        # Insert a backup into the deleted items collection
        self.db.deleted_entries.update({'id': entry.id,
                                        'created_by': entry.created_by},
                                       {'$set': {'id': entry.id,
                                                 'body': entry.body,
                                                 'raw_body': entry.raw_body,
                                                 'todos': entry.todos,
                                                 'tags': entry.tags,
                                                 '_keywords': entry.keywords,
                                                 'created_by': entry.created_by,
                                                 'created_at': entry.created_at,
                                                 'updated_by': entry.updated_by,
                                                 'updated_at': entry.updated_at,
                                                 'deleted_at': datetime.now()}},
                                       upsert=True)

        # Delete the old item
        self.db.entries.remove({'id': entry.id,
                                'created_by': entry.created_by},
                               multi=True)


    def get_scratchpad_for_user(self, username):
        """Get the user's scratchpad"""
        logging.debug('Fetching scratchpad for user: {}'.format(username))
        return self.db.entries.find_one({'id': 'scratchpad',
                                         'created_by': username})

    def get_user(self, username):
        """Fetch a user record"""
        logging.debug('Fetching user: {}'.format(username))
        return self.db.users.find_one({"username": username})

    def get_user_list(self):
        """Get a list of all the users. For administrative use only."""
        logging.info('Getting a list of all the users')
        return self.db.users.find().sort('username', pymongo.ASCENDING)

    def save_user(self, user):
        """Save a user record"""
        logging.info('Saving user: {}'.format(repr(user)))
        self.db.users.update({'username': user.username},
                             {'$set': {'username': user.username,
                                       'password': user.password,
                                       'email': user.email,
                                       'created_at': user.created_at,
                                       'updated_at': user.updated_at}},
                             upsert=True)

    def add_resetpw_token(self, token, username):
        """Add a token to denote a user has requested a password reset."""
        logging.info('Adding a password reset token "{}" for user "{}"'.format(token, username))
        # There should be a maximum of 1 token active at a time to prevent
        # old emails from being allowed to reset a password.
        self.db.reset_tokens.update({'username': username},
                                    {'$set': {'is_valid': False }},
                                    multi=True)

        self.db.reset_tokens.insert({'username': username,
                                     'token': token,
                                     'created_at': datetime.now(),
                                     'is_valid': True,
                                     'claimed_at': None,
                                     'requester-ip': None})

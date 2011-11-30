from datetime import datetime

import bcrypt
import db_api
import utils
import settings

db = db_api.QiDB()

class User(object):
    def __init__(self, username=None):
        if username:
            record = db.get_user(username)
            if record:
                self.username = record.get('username')
                self.password = record.get('password')
                self.email = record.get('email')
                self.invitation_code = record.get('invitation_code')
                self.created_at = record.get('created_at')
                self.updated_at = record.get('updated_at')
            else:
                # This could be a new user
                self.username = username
                self.email = None
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
        else:
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

    def __repr__(self):
        return "<User {}>".format(self.username)

    def authenticate(self, password):
        if hasattr(self, 'password'):
            return bcrypt.hashpw(password, self.password) == self.password
        else:
            return False

    def set_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt(settings.BCRYPT_WORK_FACTOR))

    def entries(self):
        """All the entries belonging to the user"""
        return db.get_entries_for_user(self.username)

    def current_entry(self):
        """Return the most current entry for the user"""
        record = db.get_current_entry_for_user(self.username)
        if record:
            entry = Entry(record.get('id'), self.username)
        else:
            # Create an entry if there aren't any yet
            entry = Entry(None, self.username)
            entry.raw_body = 'Click here and start typing!'
            entry.save()
        return entry

    def scratchpad(self):
        """Return the user's scratchpad"""
        scratchpad = Entry('scratchpad', self.username)
        if scratchpad:
            return scratchpad
        else:
            # Every user should have a scratchpad
            scratchpad = Entry(None, self.username)
            scratchpad.id = 'scratchpad'
            scratchpad.save()
            return scratchpad

    def save(self):
        """Save the user in the db"""
        return db.save_user(self)


class Entry(object):
    def __init__(self, id=None, created_by=None):
        record = None
        if id and created_by:
            record = db.get_entry(id, created_by)
        
        if record:
            self.id = id
            self.created_by = created_by
            self.raw_body = record.get('raw_body')
            self.tags = record.get('tags')
            self.created_at = record.get('created_at')
            self.updated_by = record.get('updated_by')
            self.updated_at = record.get('updated_at')
        else:
            # Create a new entry
            self.raw_body = ''
            self.tags = []
            self.created_by = created_by
            self.updated_by = created_by
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

            # ids depend on pre-existing ids
            if id:
                self.id = id
            else:
                current_entry = db.get_current_entry_for_user(created_by)
                if current_entry:
                    self.id = utils.nextid(current_entry.get('id'))
                else:
                    self.id = utils.nextid()

    def __repr__(self):
        return "<Entry {} created by {}>".format(self.id, self.created_by)

    def save(self):
        """Save the entry in the db"""
        return db.save_entry(self)

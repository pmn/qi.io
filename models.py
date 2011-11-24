from datetime import datetime

import db_api
import utils

db = db_api.QiDB()

class User(object):
    def __init__(self, username, password=None, email=None, created_at=None, invitation_code=None):
        self.username = username
        self.password = password
        self.email = email
        self.invitation_code = invitation_code
        if created_at == None:
            self.created_at = datetime.now()

    def __repr__(self):
        return "<User {}>".format(self.username)

    def entries(self):
        """All the entries belonging to the user"""
        return db.get_entries_for_user(self.username)

    def current_entry(self):
        """Return the most current entry for the user"""
        record = db.get_current_entry_for_user(self.username)
        if record:
            entry = Entry(raw_body=record['raw_body'],
                          created_by=record['created_by'],
                          id=record['id'],
                          tags=record['tags'],
                          created_at=record['created_at'])
        else:
            entry = None
        return entry

    def scratchpad(self):
        """Return the user's scratchpad"""
        return db.get_scratchpad_for_user(self.username)


class Entry(object):
    def __init__(self, raw_body, created_by, id=None, tags=[], created_at=None):
        self.raw_body = raw_body
        self.tags = tags
        self.created_by = created_by
        
        if id == None:
            # ids depend on pre-existing ids. 
            current_entry = db.get_current_entry_for_user(created_by)
            if current_entry == None:
                self.id = utils.nextid()
            else:
                self.id = utils.nextid(current_entry['id'])
        else:
            self.id = id
 
        if created_at == None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return "<Entry {} created by {}>".format(self.id, self.created_by)

    def save(self):
        """Save the entry in the db"""
        return db.save_entry(self)

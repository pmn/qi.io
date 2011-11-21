from datetime import datetime
import db_api

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
        return db.get_current_entry_for_user(self.username)


class Entry(object):
    def __init__(self, raw_body, created_by, id=None, tags=[], created_at=None):
        self.raw_body = raw_body
        self.tags = tags
        self.created_by = created_by
        
        if id == None:
            self.id = datetime.now().strftime("%Y%m%d.01")
        else:
            self.id = id
 
        if created_at == None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return "<Entry {} created by {}>".format(self.id, self.created_by)

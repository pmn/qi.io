from datetime import datetime
import json
import re
import bcrypt
import db_api
import utils
import settings
import markdown
import urlize
import wordlists
from itertools import groupby

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
        return list(db.get_entries_for_user(self.username))

    def current_entry(self):
        """Return the most current entry for the user"""
        record = db.get_current_entry_for_user(self.username)
        if record:
            entry = Entry(record.get('id'), self.username)
        else:
            # Create an entry if there aren't any yet
            entry = Entry(None, self.username)
            entry.raw_body = 'Double-click here and start typing!'
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

    def tags(self):
        """Return a list of user's tags"""
        taglist = db.get_user_tags(self.username)
        return [{'tag': tag.get('_id'), 'count': int(tag.get('value'))}
                for tag in taglist.find()]

    def is_admin(self):
        """Return true if the user is an admin"""
        return self.username in settings.ADMIN_USERS

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
            self.body = record.get('body')
            self.raw_body = record.get('raw_body')
            self.tags = record.get('tags')
            self.keywords = record.get('_keywords')
            self.created_at = record.get('created_at')
            self.updated_by = record.get('updated_by')
            self.updated_at = record.get('updated_at')
        else:
            # Create a new entry
            self.body = ''
            self.raw_body = ''
            self.tags = []
            self.keywords = []
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


    def to_json(self):
        """Return a json representation of the object"""
        obj = {'id': self.id,
               'created_by': self.created_by,
               'body':self.body,
               'raw_body':self.raw_body,
               'tags':self.tags,
               }

        return json.dumps(obj)

    def delete(self):
        """Delete the entry from the db"""
        db.delete_entry(self)

    def save(self):
        """Save the entry in the db"""
        # Insert a space in the beginning of any line that starts with "#"
        if self.raw_body.startswith("#"):
            self.raw_body = " " + self.raw_body

        self.raw_body = self.raw_body.replace("\n#","\n #")

        # First update the tags
        taglist = [utils.strip_punctuation(tag) for tag in re.findall(r"#(\S+)", self.raw_body)]
        self.tags = taglist

        # Populate a wordlist for searching
        wordlist = [utils.strip_punctuation(word) for word in set(self.raw_body.split())
                    if word not in wordlists.STOP_WORDS]
        self.keywords = wordlist

        # Translate the raw body to the markdownified body
        urlize_ext = urlize.UrlizeExtension()
        md = markdown.Markdown(extensions=[urlize_ext,
                                           'nl2br'])

        self.body = md.convert(self.raw_body)

        db.save_entry(self)
        return self

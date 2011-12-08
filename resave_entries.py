# Get all of the entries out of the database and re-save them.
# This forces all pre-save modifications to occur

import settings
import db_api
import logging
from models import Entry

db = db_api.QiDB()

def resave_entries():
    """ Fetch and re-save all entries """
    entries = db.get_all_entries()
    for item in entries:
        print("Updating entry {} from user {}".format(item.get('id'), item.get('created_by')))
        entry = Entry(id=item.get('id'), created_by=item.get('created_by'))
        entry.save()

if __name__ == "__main__":
    resave_entries()

#!/usr/bin/env python
# Remember to:
# export FLASK_APP=hello.py (this file name)
# To make server externally visible use: --host=0.0.0.0 (flask run --host=0.0.0.0)
# Card ID is 81:00:74:08
# Beacon ID is 19:90:59:D3

from __future__ import print_function
from flask import Flask


import mongo.databases.local as internal_db
import mongo.databases.external as external_db

app = Flask(__name__)


@app.route('/check_user_id/<user_id>', methods=['GET'])
def external_check_user_id(user_id):
    """Check if a userID exists in external database

    :return
    - True: if the userID has access
    - False: if the userID has not access
    """

    db = external_db.Database(user_id)
    response = db.get_response()  # contains a dict
    local_db = internal_db.Database(user_id)

    if response['status'] == 'connected':
        print('(info) - connected to external database, checking userID')

        if response['response'] != 'null':
            # (userID exists in external database): update local database with the user (if any)
            local_db.insert_or_update_user_id(response['response'])

            return response['response']
    else:
        print('(warning) - could not connected to external database, checking userID from internal database')

        # Check if the user exists and is authorized in local database
        if local_db.check_user_id() and local_db.is_authorized():
            return 'true'
        elif local_db.check_user_id() and not local_db.is_authorized():
            return 'false'
        elif not local_db.check_user_id():
            print('(info) - userID: ({}): does not has any record in local database'.format(user_id))
            print('(info) - TIP: the next time that connected to external database (if the userID exists) it will '
                  'be insert in local database to consult it')
            return 'false'


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)


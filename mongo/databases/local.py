"""Services to handle a local mongodb connection"""

import pymongo


class Database(object):

    INTERNAL_URI = 'mongodb://localhost:27017'
    MAX_SER_SEL_DELAY = 3  # connection delay in milliseconds

    def __init__(self, user_id):
        """Perform the connection to local database

        Once this class is instanciate the connection will perform to be use in the class functions

        :param user_id: the user id to check
        """
        self.user_id = user_id

        try:
            self.client = pymongo.MongoClient(Database.INTERNAL_URI, Database.MAX_SER_SEL_DELAY)
            self.client.server_info()  # force the connection request
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print('could not connected to local db because: {}'.format(err))

        self.db = self.client['aquatica']
        self.collection = self.db['users']

    def check_user_id(self):
        """Check an user id

        Perform a query into a specific collection returning specific fields

        :return:
        - True: If the userID exists
        - False: if the userID does not exists
        """
        user_id = self.collection.find_one({'userID': self.user_id}, {'userID': 1})  # returns the userID (if any)
        user_exist = True if user_id else False

        return user_exist

    def is_authorized(self):
        """Check if and user id is authorized to access

        Perform a query into a specific collection returning specific fields

        :return:
        - True: If the userID is authorized to access
        - False: if the userID is not authorized to access
        """
        authorize = self.collection.find_one({'userID': self.user_id}, {'authorized': 1})  # returns authorize dict
        return True if authorize['authorized'] == 'true' else False

    def insert_or_update_user_id(self, authorized):
        """Insert or update an userID

        If the user does not exists this will insert a new record, otherwise if the user exists this will check
        if there is some new value and it will be updated.

        Note: this function has concurrency allowing to update one by one the existing records in the local database
              avoiding duplicates
        """
        _id = self.collection.find_one({'userID': self.user_id}, {'_id': 1})  # returns the _id (if any)
        data_to_insert = {'userID': self.user_id, 'authorized': authorized}  # data example

        if not _id:
            # the record does not exists in db
            self.collection.insert_one(data_to_insert)
            print('(info) - record successfully inserted: {}'.format(data_to_insert))
        else:
            # the record already exists in db
            update = self.collection.update_one(_id, {'$set': data_to_insert}, upsert=True)
            if update.modified_count > 0:
                print('(info) - the record: ({}) was successfully updated'.format(data_to_insert))
            else:
                print('(info) - the record: ({}) was not changed'.format(data_to_insert))


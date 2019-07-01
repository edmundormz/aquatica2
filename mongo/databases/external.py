"""Services to handle a external database connection"""

from __future__ import print_function

import requests


class Database(object):

    def __init__(self, user_id):
        """Set the api-endpoint

        :param user_id: the userID to check in the external database
        """
        # api-endpoint
        self.api_endpoint = 'http://142.93.93.25/api/Students/canPass?nfcId={}'.format(user_id)

    def get_response(self):
        """Get response from external server

        The external server can returns the following values:
        - String:true: => when a userID exists in the database and has access
        - String:false => when a userID exists in the database and has not access
        - String:No    => when a userID is not in database

        :return:
            - a dictionary that contains if the connection was established or not and the response received from
              the external server
        """
        timeout = 1  # timeout to close connection with the database (unit:seconds)

        try:
            # sending get request and saving the response as response object
            response = requests.get(url=self.api_endpoint, timeout=timeout, verify=False)
            if response.status_code == 200:
                if response.text == 'true':
                    data = {'status': 'connected', 'response': 'true'}
                    return data
                elif response.text == 'false':
                    data = {'status': 'connected', 'response': 'false'}
                    return data
            else:
                data = {'status': 'disconnected', 'response': 'null'}
                return data

        except requests.ConnectTimeout as err:
            print('(error) - failed to connect to external database due to: {}'.format(err))
            pass
        finally:
            return {'status': 'disconnected', 'response': "null"}


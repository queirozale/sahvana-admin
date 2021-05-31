import json, requests
from requests.exceptions import RequestException, HTTPError, URLRequired

class Auth0User:
    def __init__(self, config):
        # Configuration Values
        self.domain = config["AUTH0_DOMAIN"]
        self.audience = f'https://{self.domain}/api/v2/'
        self.client_id = config["AUTH0_CLIENT_ID"]
        self.client_secret = config["AUTH0_CLIENT_SECRET"]
        self.grant_type = "client_credentials" # OAuth 2.0 flow to use
        self.base_url = f"https://{self.domain}"


    def get_access_token(self):
        # Get an Access Token from Auth0
        payload =  { 
        'grant_type': self.grant_type,
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'audience': self.audience
        }
        response = requests.post(f'{self.base_url}/oauth/token', data=payload)
        oauth = response.json()
        access_token = oauth.get('access_token')

        return access_token


    def find_all(self):
        access_token = self.get_access_token()

        # Add the token to the Authorization header of the request
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
        }

        # Get all Applications using the token
        try:
            res = requests.get(f'{self.base_url}/api/v2/users', headers=headers)
            data = res.json()
            if res.status_code == 201:
                print("Users readed!")
            return data
        except HTTPError as e:
            print(f'HTTPError: {str(e.code)} {str(e.reason)}')
        except URLRequired as e:
            print(f'URLRequired: {str(e.reason)}')
        except RequestException as e:
            print(f'RequestException: {e}')
        except Exception as e:
            print(f'Generic Exception: {e}')


    def find(self, access_token, user_id):
        # Add the token to the Authorization header of the request
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
        }

        # Get all Applications using the token
        try:
            res = requests.get(f'{self.base_url}/api/v2/users/{user_id}', headers=headers)
            data = res.json()
            if res.status_code == 204:
                print("Users found!")
            return data
        except HTTPError as e:
            print(f'HTTPError: {str(e.code)} {str(e.reason)}')
        except URLRequired as e:
            print(f'URLRequired: {str(e.reason)}')
        except RequestException as e:
            print(f'RequestException: {e}')
        except Exception as e:
            print(f'Generic Exception: {e}')


    def create(self, user_data):
        access_token = self.get_access_token()

        # Add the token to the Authorization header of the request
        headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
        }

        # Get all Applications using the token
        try:
            res = requests.post(f'{self.base_url}/api/v2/users', headers=headers, json=user_data)
            data = res.json()
            if res.status_code == 201:
                print("Users created!")
            return data
        except HTTPError as e:
            print(f'HTTPError: {str(e.code)} {str(e.reason)}')
        except URLRequired as e:
            print(f'URLRequired: {str(e.reason)}')
        except RequestException as e:
            print(f'RequestException: {e}')
        except Exception as e:
            print(f'Generic Exception: {e}')


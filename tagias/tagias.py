import requests
from datetime import datetime

# Enum for project types
class TagiasTypes:
  BoundingBoxes = 'BoundingBoxes'
  Polygons = 'Polygons'
  Keypoints = 'Keypoints'
  ClassificationSingle = 'ClassificationSingle'
  ClassificationMultiple = 'ClassificationMultiple'
  Lines = 'Lines'


# Enum for project statuses
class TagiasStatuses:
  ACTIVE = 'ACTIVE'
  STOPPED = 'STOPPED'
  SUSPENDED = 'SUSPENDED'
  FINISHED = 'FINISHED'


# Enum for TAGIAS error codes
class TagiasErrors:
    NONAME = 'NONAME'
    NOPICTURES = 'NOPICTURES'
    NOLABELS = 'NOLABELS'
    BADCALLBACK = 'BADCALLBACK'
    BADBASEURL = 'BADBASEURL'
    BADTYPE = 'BADTYPE'
    BADSTATUS = 'BADSTATUS'
    NOTFOUND = 'NOTFOUND'
    INTERNAL = 'INTERNAL'
    NOAPIKEY = 'NOAPIKEY'
    UNAUTHORIZED = 'UNAUTHORIZED'
    UNKNOWN = 'UNKNOWN'


# TAGIAS error class that contains a code and a message for the thrown error
class TagiasError(Exception):
    # Constructor for the TAGIAS error
    def __init__(self, code):
        self.code = code
        self.message = self.translateErrorCode(code)

    # Translates the provided TAGIAS error code to a string message
    def translateErrorCode(self, code):
        if code==TagiasErrors.NONAME: 
            return 'The package name is missing'
        elif code==TagiasErrors.NOPICTURES: 
            return 'The pictures array is empty or missing'
        elif code==TagiasErrors.NOLABELS: 
            return 'The labels array for the classification task is missing (or there are less than 2 items in the array)'
        elif code==TagiasErrors.BADCALLBACK: 
            return 'The callback URL is malformed'
        elif code==TagiasErrors.BADBASEURL: 
            return 'The baseurl URL is malformed'
        elif code==TagiasErrors.BADTYPE: 
            return 'The type value is not one of the allowed values'
        elif code==TagiasErrors.BADSTATUS: 
            return 'The status value is not one of the allowed values or this kind of change is not allowed'
        elif code==TagiasErrors.NOTFOUND: 
            return 'The specified object does not exist'
        elif code==TagiasErrors.INTERNAL: 
            return 'An internal error has occurred'
        elif code==TagiasErrors.NOAPIKEY: 
            return 'TAGIAS API Key is not provided'
        elif code==TagiasErrors.UNAUTHORIZED: 
            return 'TAGIAS API Key is incorrect'
        elif code==TagiasErrors.UNKNOWN: 
            return 'Unknown response received'
        else: 
            return 'HTTP error code returned'


# TAGIAS helper class
class TagiasHelper:
    # URL for the TAGIAS external API endpoint
    _TAGIAS_URL = 'https://p.tagias.com/api/v1/tagias'

    # Saves the provided API key for using it in subsequent method calls
    def __init__(self, apiKey):
        if not apiKey:
            raise TagiasError(TagiasErrors.NOAPIKEY)

        self.apiKey = apiKey
        self.headers = {'Content-Type': 'application/json', 'Authorization': 'Api-Key ' + self.apiKey}

    # Verifies the returned status code and status attribute; raises a TagiasError exception in case of error
    def _handle_response(self, resp):
        if resp.status_code==200:
            json = resp.json()
            if json['status'] == 'ok':
                return json
            else:
                raise TagiasError(json['error'])
        elif resp.status_code==401:
            raise TagiasError(TagiasErrors.UNAUTHORIZED)
        else:
            raise TagiasError(str(resp.status_code))

    # Converts the string in ISO format to datetime
    def _to_datetime(self, s):
        if s is None:
            return None
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Converts the 'created' attribute to datetime
    def _created_to_datetime(self, package):
        package['created'] = self._to_datetime(package['created'])
        return package

    # Converts the 'date' attribute to datetime
    def _date_to_datetime(self, op):
        op['date'] = self._to_datetime(op['date'])
        return op

    # Returns the array of created packages
    def get_packages(self):
        resp = requests.get(self._TAGIAS_URL + '/packages', headers=self.headers)
        json = self._handle_response(resp)
        packages = map(self._created_to_datetime, json['packages'])
        return packages

    # Creates a new TAGIAS package for annotation
    def create_package(self, name, type, descr, labels, callback, baseurl, pictures):
        data = {
            'name': name,
            'type': type,
            'descr': descr,
            'labels': labels,
            'callback': callback,
            'baseurl': baseurl,
            'pictures': pictures
        }
        resp = requests.post(self._TAGIAS_URL + '/packages', json = data, headers=self.headers)
        json = self._handle_response(resp)

        return { 'id': json['id'], 'pictures_num': json['pictures_num'] }

    # Modifies the TAGIAS package's status
    def set_package_status(self, id, status):
        resp = requests.patch(self._TAGIAS_URL + '/packages/' + id, json = { 'status': status }, headers=self.headers)
        self._handle_response(resp)
        return

    # Reads the TAGIAS package's properties
    def get_package(self, id):
        resp = requests.get(self._TAGIAS_URL + '/packages/' + id, headers=self.headers)
        json = self._handle_response(resp)
        package = json['package']
        package['created'] = self._to_datetime(package['created'])
        package['started'] = self._to_datetime(package['started'])
        package['stopped'] = self._to_datetime(package['stopped'])
        package['finished'] = self._to_datetime(package['finished'])
        package['updated'] = self._to_datetime(package['updated'])
        package['delivered'] = self._to_datetime(package['delivered'])
        return package

    # Requests the tagias.com server to send currently available annotations for all completed images from the specified package to the package's callback endpoint
    def request_result(self, id):
        resp = requests.post(self._TAGIAS_URL + '/packages/result/' + id, headers=self.headers)
        self._handle_response(resp)
        return

    # Reads the currently available annotations for all completed images from the specified package
    def get_result(self, id):
        resp = requests.get(self._TAGIAS_URL + '/packages/result/' + id, headers=self.headers)
        json = self._handle_response(resp)
        json['finished'] = self._to_datetime(json['finished'])
        json.pop('status', None)
        return json

    # Reads the current balance amount and the list of all operations
    def get_balance(self):
        resp = requests.get(self._TAGIAS_URL + '/balance', headers=self.headers)
        json = self._handle_response(resp)
        json['operations'] = map(self._date_to_datetime, json['operations'])
        json.pop('status', None)
        return json

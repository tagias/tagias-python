import requests
import datetime


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
    BADPICTURES = 'BADPICTURES'
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
    BADRESULTTYPE = 'BADRESULTTYPE'


# TAGIAS error class that contains a code and a message for the thrown error
class TagiasError(Exception):
    # Constructor for the TAGIAS error
    def __init__(self, code):
        self.code = code
        self.message = self.translateErrorCode(code)

    # Translates the provided TAGIAS error code to a string message
    def translateErrorCode(self, code):
        if code == TagiasErrors.NONAME:
            return 'The package name is missing'
        elif code == TagiasErrors.NOPICTURES:
            return 'The pictures array is empty or missing'
        elif code == TagiasErrors.BADPICTURES:
            return 'Some of the provided pictures could not be accessed or their URLs are malformed'
        elif code == TagiasErrors.NOLABELS:
            return 'The labels array for the classification task is missing (or there are less than 2 items in the array)'
        elif code == TagiasErrors.BADCALLBACK:
            return 'The callback URL is malformed'
        elif code == TagiasErrors.BADBASEURL:
            return 'The baseurl URL is malformed'
        elif code == TagiasErrors.BADTYPE:
            return 'The type value is not one of the allowed values'
        elif code == TagiasErrors.BADSTATUS:
            return 'The status value is not one of the allowed values or this kind of change is not allowed'
        elif code == TagiasErrors.NOTFOUND:
            return 'The specified object does not exist'
        elif code == TagiasErrors.INTERNAL:
            return 'An internal error has occurred'
        elif code == TagiasErrors.NOAPIKEY:
            return 'TAGIAS API Key is not provided'
        elif code == TagiasErrors.UNAUTHORIZED:
            return 'TAGIAS API Key is incorrect'
        elif code == TagiasErrors.UNKNOWN:
            return 'Unknown response received'
        else:
            return 'HTTP error code returned'


# TAGIAS helper class
class TagiasHelper:
    # URL for the TAGIAS external API endpoint
    _TAGIAS_URL = 'https://p.tagias.com/api/v2/tagias'

    # Saves the provided API key for using it in subsequent method calls
    def __init__(self, apiKey):
        if not apiKey:
            raise TagiasError(TagiasErrors.NOAPIKEY)

        self.apiKey = apiKey
        self.headers = {'Content-Type': 'application/json', 'Authorization': 'Api-Key ' + self.apiKey}

    # Verifies the returned status code and status attribute; raises a TagiasError exception in case of error
    def _handle_response(self, resp):
        if resp.status_code == 200:
            json = resp.json()
            if json['status'] == 'ok':
                return json
            else:
                raise TagiasError(json['error'])
        elif resp.status_code == 401:
            raise TagiasError(TagiasErrors.UNAUTHORIZED)
        else:
            raise TagiasError(str(resp.status_code))

    # Converts the string in ISO format to datetime
    def _to_datetime(self, s):
        if s is None:
            return None
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')

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
        packages = list(map(self._created_to_datetime, json['packages']))
        return packages

    # Creates a new TAGIAS package for annotation
    def create_package(self, name, type, descr, labels, callback, baseurl, pictures, labels_required = None):
        data = {
            'name': name,
            'type': type,
            'descr': descr,
            'labels': labels,
            'callback': callback,
            'baseurl': baseurl,
            'pictures': pictures,
            'labels_required': labels_required
        }
        resp = requests.post(self._TAGIAS_URL + '/packages', json=data, headers=self.headers)
        json = self._handle_response(resp)

        return {'id': json['id'], 'pictures_num': json['pictures_num']}

    # Modifies the TAGIAS package's status
    def set_package_status(self, id, status):
        resp = requests.patch(self._TAGIAS_URL + '/packages/' + id, json={'status': status}, headers=self.headers)
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
        json['operations'] = list(map(self._date_to_datetime, json['operations']))
        json.pop('status', None)
        return json


# TAGIAS Package class
class TagiasPackage:
    def __init__(self, package):
        self.id = package.get('id')
        self.name = package.get('name')
        self.type = package.get('type')
        self.status = package.get('status')
        self.created = package.get('created')
        self.amount = package.get('amount')
        self.pictures_num = package.get('pictures_num')
        self.completed_num = package.get('completed_num')


# TAGIAS NewPackage class
class TagiasNewPackage:
    def __init__(self, package):
        self.id = package.get('id')
        self.pictures_num = package.get('pictures_num')


# TAGIAS FullPackage class
class TagiasFullPackage:
    def __init__(self, package):
        self.id = package.get('id')
        self.name = package.get('name')
        self.type = package.get('type')
        self.status = package.get('status')
        self.descr = package.get('descr')
        self.labels = package.get('labels')
        self.labels_required = package.get('labels_required')
        self.callback = package.get('callback')
        self.created = package.get('created')
        self.started = package.get('started')
        self.stopped = package.get('stopped')
        self.finished = package.get('finished')
        self.updated = package.get('updated')
        self.delivered = package.get('delivered')
        self.baseurl = package.get('baseurl')
        self.amount = package.get('amount')
        self.pictures_num = package.get('pictures_num')
        self.completed_num = package.get('completed_num')


# TAGIAS BoundingBox class
class TagiasBoundingBox:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.BoundingBoxes:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.label = data.get('label')
        if 'x' in data:
            self.x = data.get('x')
            self.y = data.get('y')
            self.width = data.get('width')
            self.height = data.get('height')
        elif 'x1' in data:
            self.x1 = data.get('x1')
            self.y1 = data.get('y1')
            self.x2 = data.get('x2')
            self.y2 = data.get('y2')

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS Point class
class TagiasPoint:
    def __init__(self, data):
        self.x = data.get('x')
        self.y = data.get('y')

    def __repr__(self):
        return ("{}({{ 'x':{}, 'y':{} }})".format(self.__class__.__name__, self.x, self.y))

    def __str__(self):
        return ("({}, {})".format(self.x, self.y))


# TAGIAS Line class
class TagiasLine:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.Lines:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.label = data.get('label')
        self.points = list(map(lambda x: TagiasPoint(x), data.get('points')))

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS Poligon class
class TagiasPoligon:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.Polygons:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.label = data.get('label')
        self.points = list(map(lambda x: TagiasPoint(x), data.get('points')))

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS Keypoints class
class TagiasKeypoint:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.Keypoints:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.label = data.get('label')
        self.x = data.get('x')
        self.y = data.get('y')

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS ClassificationSingle class
class TagiasClassificationSingle:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.ClassificationSingle:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.label = data.get('label')

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS ClassificationMultiple class
class TagiasClassificationMultiple:
    def __init__(self, data):
        if data.get('type') != TagiasTypes.ClassificationMultiple:
            raise TagiasError(TagiasErrors.BADRESULTTYPE)
        self._data = data
        self.labels = data.get('labels')

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._data))

    def __str__(self):
        return str(self._data)


# TAGIAS ResultError class
class TagiasResultError:
    def __init__(self, data):
        self.error = data.get('error')

    def __repr__(self):
        return ("{}({{ 'error':{} }})".format(self.__class__.__name__, self.error))

    def __str__(self):
        return ("ERROR {}".format(self.error))


# TAGIAS PictureResult class
class TagiasPictureResult:
    def __init__(self, picture):
        self._picture = picture
        self.name = picture.get('name')
        self.result = picture.get('result')
        if isinstance(self.result, list):
            self.datalist = list(map(self._convert_to_datalist, self.result))
        else:
            self.data = self._convert_to_data(self.result)

    def _convert_to_datalist(self, result):
        resulttype = result.get('type')
        if resulttype == TagiasTypes.BoundingBoxes:
            return TagiasBoundingBox(result)
        elif resulttype == TagiasTypes.Lines:
            return TagiasLine(result)
        elif resulttype == TagiasTypes.Polygons:
            return TagiasPoligon(result)
        elif resulttype == TagiasTypes.Keypoints:
            return TagiasKeypoint(result)
        else:
            return None

    def _convert_to_data(self, result):
        resulttype = result.get('type')
        if resulttype == TagiasTypes.ClassificationSingle:
            return TagiasClassificationSingle(result)
        elif resulttype == TagiasTypes.ClassificationMultiple:
            return TagiasClassificationMultiple(result)
        elif 'error' in result:
            return TagiasResultError(result)
        else:
            return None

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._picture))

    def __str__(self):
        return str(self._picture)


# TAGIAS Result class
class TagiasResult:
    def __init__(self, result):
        self._result = result
        self.id = result.get('id')
        self.finished = result.get('finished')
        self.baseurl = result.get('baseurl')
        self.pictures = list(map(lambda x: TagiasPictureResult(x), result.get('pictures')))

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._result))

    def __str__(self):
        return str(self._result)


# TAGIAS Operation class
class TagiasOperation:
    def __init__(self, operation):
        self._operation = operation
        self.date = operation.get('date')
        self.amount = operation.get('amount')
        self.note = operation.get('note')

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._operation))

    def __str__(self):
        return str(self._operation)


# TAGIAS Balance class
class TagiasBalance:
    def __init__(self, balance):
        self._balance = balance
        self.balance = balance.get('balance')
        self.operations = list(map(lambda x: TagiasOperation(x), balance.get('operations')))

    def __repr__(self):
        return ("{}({!r})".format(self.__class__.__name__, self._balance))

    def __str__(self):
        return str(self._balance)


# TAGIAS helper class
class TagiasHelper2:
    # Saves an instance of the TagiasHelper class
    def __init__(self, apiKey):
        self.helper = TagiasHelper(apiKey)

    # Returns the array of created packages
    def get_packages(self):
        packages = self.helper.get_packages()
        return list(map(lambda x: TagiasPackage(x), packages))

    # Creates a new TAGIAS package for annotation
    def create_package(self, name, type, descr, labels, callback, baseurl, pictures):
        package = self.helper.create_package(name, type, descr, labels, callback, baseurl, pictures)
        return TagiasNewPackage(package)

    # Modifies the TAGIAS package's status
    def set_package_status(self, id, status):
        self.helper.set_package_status(id, status)
        return

    # Reads the TAGIAS package's properties
    def get_package(self, id):
        package = self.helper.get_package(id)
        return TagiasFullPackage(package)

    # Requests the tagias.com server to send currently available annotations for all completed images from the specified package to the package's callback endpoint
    def request_result(self, id):
        self.helper.request_result(id)
        return

    # Reads the currently available annotations for all completed images from the specified package
    def get_result(self, id):
        result = self.helper.get_result(id)
        return TagiasResult(result)

    # Reads the current balance amount and the list of all operations
    def get_balance(self):
        balance = self.helper.get_balance()
        return TagiasBalance(balance)

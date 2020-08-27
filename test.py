# import the tagias api helper classes
from tagias.tagias import TagiasHelper, TagiasHelper2, TagiasError, TagiasTypes, TagiasStatuses, TagiasOperation

# Replace the test API key with your own private API key
apiKey = 'test'


# Testing the TAGIAS external API methods using TagiasHelper class
def test(apiKey):
    try:
        print('Test Start')

        # create tagias helper object
        helper = TagiasHelper(apiKey)

        # create a new package
        newPackage = helper.create_package('Test package', TagiasTypes.Keypoints,
                                           'Put one point only in the center of the image', None, None,
                                           'https://p.tagias.com/samples/', ['dog.8001.jpg', 'dog.8002.jpg', 'dog.8003.jpg'])

        print('Package {} was created with {} image(s)'.format(newPackage['id'], newPackage['pictures_num']))

        try:
            # modify the package's status
            helper.set_package_status(newPackage['id'], TagiasStatuses.STOPPED)
        except TagiasError as e:
            # handle a TagiasError exception
            print('{} package\'s status was NOT modified: {}'.format(newPackage['id'], e.message))

        # get the package's properties
        package = helper.get_package(newPackage['id'])
        print('New package properties:')
        for prop in package:
            print(' * {}: {}'.format(prop, package[prop]))

        # get the list of all your packages
        packages = helper.get_packages()
        print('Packages:')
        for package in packages:
            print(' * {} {} {} {}'.format(package['id'], package['name'], package['status'], package['created']))
            if package['status'] == TagiasStatuses.FINISHED:
                # get the package's result if it's already finished
                result = helper.get_result(package['id'])
                print(' Result: {}'.format(result))

                try:
                    # request the package's result to be send to the callback endpoint
                    helper.request_result(package['id'])
                except TagiasError as e:
                    # handle a TagiasError exception
                    print('{} package\'s result was NOT requested: {}'.format(package['id'], e.message))

        # get current balance and financial operations
        balance = helper.get_balance()
        print('Current balance: {} USD'.format(balance['balance']))
        print('Operations:')
        for op in balance['operations']:
            print(' * {}: {} USD, {}'.format(op['date'], op['amount'], op['note']))

        print('Test End')
    except TagiasError as e:
        # handle a TagiasError exception
        print('TagiasError: {} ({})'.format(e.message, e.code))


# Testing the TAGIAS external API methods using TagiasHelper2 class
def test2(apiKey):
    try:
        print('Test2 Start')

        # create tagias helper object
        helper = TagiasHelper2(apiKey)

        # create a new package
        newPackage = helper.create_package('Test package', TagiasTypes.Keypoints,
                                           'Put one point only in the center of the image', None, None,
                                           'https://p.tagias.com/samples/', ['dog.8001.jpg', 'dog.8002.jpg', 'dog.8003.jpg'])

        print('Package {} was created with {} image(s)'.format(newPackage.id, newPackage.pictures_num))

        try:
            # modify the package's status
            helper.set_package_status(newPackage.id, TagiasStatuses.STOPPED)
        except TagiasError as e:
            # handle a TagiasError exception
            print('{} package\'s status was NOT modified: {}'.format(newPackage.id, e.message))

        # get the package's properties
        package = helper.get_package(newPackage.id)
        print('New package properties:')
        for prop in dir(package):
            if not prop.startswith('_'):
                print(' * {}: {}'.format(prop, getattr(package, prop)))

        # get the list of all your packages
        packages = helper.get_packages()
        print('Packages:')
        for package in packages:
            print(' * {} {} {} {}'.format(package.id, package.name, package.status, package.created))
            if package.status == TagiasStatuses.FINISHED:
                # get the package's result if it's already finished
                result = helper.get_result(package.id)
                print(result)

                try:
                    # request the package's result to be send to the callback endpoint
                    helper.request_result(package.id)
                except TagiasError as e:
                    # handle a TagiasError exception
                    print('{} package\'s result was NOT requested: {}'.format(package.id, e.message))

        # get current balance and financial operations
        balance = helper.get_balance()
        print('Current balance: {} USD'.format(balance.balance))
        print('Operations:')
        for op in balance.operations:
            print(' * {}: {} USD, {}'.format(op.date, op.amount, op.note))

        print('Test2 End')
    except TagiasError as e:
        # handle a TagiasError exception
        print('TagiasError: {} ({})'.format(e.message, e.code))


# test with TagiasHelper class
# test(apiKey)

# test with TagiasHelper2 class
test2(apiKey)

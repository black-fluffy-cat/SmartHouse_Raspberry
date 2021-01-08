from scripts import DataSender


def sendAddressesToServerUntilSuccess():
    from scripts.startServer import app
    with app.test_request_context():
        sentSuccessfully = False
        while not sentSuccessfully: # Maybe some additional stop condition?
            sentSuccessfully = DataSender.makeNgrokAddressesCall()

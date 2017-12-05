# -*- coding: utf-8 -*-
"""
ePages provisioning service

Uses the following wsdl files from ePages

http://tatu05.sml18.vilkas.pri/WebRoot/WSDL/SimpleProvisioningService6.wsdl

"""
import logging
from urllib.parse import urlparse
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

logger = logging.getLogger(__name__)


class BaseProvisioningService(object):
    """
    Base for provisioning services
    """
    def __init__(self, endpoint="", provider="", username="", password=""):
        super().__init__()
        self.endpoint = endpoint
        self.username = username
        self.password = password


class SimpleProvisioningService(BaseProvisioningService):
    """
    Simple provisioning, handles creating updating and deleting shops in ePages
    environment.
    """
    def __init__(self, endpoint="", provider="", username="", password="", wsdl=""):
        super().__init__(
            endpoint=endpoint,
            provider=provider,
            username=username,
            password=password
            )
        # build url for the wsdl from the endpoint information
        parsed = urlparse(endpoint)
        wsdlurl = '{uri.scheme}://{uri.netloc}/WebRoot/WSDL/SimpleProvisioningService6.wsdl'.format(uri=parsed)
        logger.info('Built wsdl url from endpoint: {}'.format(wsdlurl))
        self.wsdl = wsdlurl

        # the username must be in ePages format (but we want to hide this fact from the user)
        user = "/Providers/{}/Users/{}".format(provider, username)

        # initialize our client using basic auth and with the wsdl file
        session = Session()
        session.auth = HTTPBasicAuth(user, password)
        client = Client(
            wsdl=self.wsdl,
            transport=Transport(session=session)
        )
        self.client = client

        # the wsdl always points to localhost, change to our endpoint instead
        # TODO: There must be a better way

        # figure out our binding name
        qname = str(client.service._binding.name)
        # and create new service with the name pointing to our endpoint
        service2 = client.create_service(qname, endpoint)
        self.service2 = service2

        logger.info('Initialized new client: {}'.format(self.client))

    def create(self, data):
        """
        Creates new shop

        input:
            TODO

        returns:
            TODO


        """
        return self.service2.create(data)

    def exists(self):
        raise NotImplementedError

    def getInfo(self):
        raise NotImplementedError

    def markForDeletion(self, data):
        return self.service2.markForDeletion(data)

    def rename(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

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
        self.provider = provider
        self.username = username
        self.password = password


class SimpleProvisioningService(BaseProvisioningService):
    """
    Simple provisioning, handles creating updating and deleting shops in ePages
    environment.
    """

    def __init__(self,
                 endpoint="",
                 provider="",
                 username="",
                 password="",
                 version="6"):
        super().__init__(
            endpoint=endpoint,
            provider=provider,
            username=username,
            password=password
        )

        self.version = version
        self.wsdl = self.__build_wsdl_url_from_endpoint()
        self.userpath = self.__build_full_username()

        # initialize our client using basic auth and with the wsdl file
        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)
        client = Client(
            wsdl=self.wsdl,
            strict=False,  # ePages wsdl files are full of errors...
            transport=Transport(session=session)
        )
        self.client = client

        # the wsdl always points to localhost, change to our endpoint instead

        # figure out our binding name TODO: There must be a better way
        qname = str(client.service._binding.name)
        # and create new service with the name pointing to our endpoint
        service2 = client.create_service(qname, endpoint)
        self.service2 = service2

        logger.debug('Initialized new client: %s', self.client)

    def __build_full_username(self):
        """ build the username as a path """
        return "/Providers/{}/Users/{}".format(self.provider, self.username)

    def __build_wsdl_url_from_endpoint(self):
        """ Builds url to the wsdl from endpoint and version number """
        parsed = urlparse(self.endpoint)
        wsdlurl = '{uri.scheme}://{uri.netloc}/WebRoot/WSDL/SimpleProvisioningService{version}.wsdl'.format(
            uri=parsed, version=self.version)
        logger.debug('Built wsdl url from endpoint: %s', wsdlurl)
        return wsdlurl

    def create(self, data):
        """
        Creates new shop

        input:
            TODO

        returns:
            TODO
        """
        logger.info('Creating new shop with data: %s', data)
        return self.service2.create(data)

    def exists(self, data):
        """
        Check if shop exists

        input:
            TODO

        returns:
            TODO

        """
        return self.service2.exists(data)

    def get_info(self, data):
        """
        Get shop information

        input:
            TODO

        returns:
            TODO
        """
        return self.service2.getInfo(data)

    def mark_for_deletion(self, data):
        """
        Mark the shop for deletion, it will be deleted by ePages after some
        time (default 30 days)

        Does a extra exists call before marking for deletion because
        ePages service always returns None for this call

        input:
            TODO

        returns:
            None if everything is ok, False if shop is not found

        raises:
        """
        if self.service2.exists(data):
            return self.service2.markForDeletion(data)
        else:
            return False

    def rename(self):
        """
        Rename shop

        Warning: this might change some urls in the shop and confuse
        search engines etc.
        """
        raise NotImplementedError

    def update(self):
        """
        Update shop information
        """

        raise NotImplementedError

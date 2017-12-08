# -*- coding: utf-8 -*-
"""
ePages provisioning service

"""
import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

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
        super(BaseProvisioningService, self).__init__()
        self.endpoint = endpoint
        self.provider = provider
        self.username = username
        self.password = password


class SimpleProvisioningService(BaseProvisioningService):
    """
    Simple provisioning, handles creating updating and deleting shops in ePages
    environment.

    By default uses the following wsdl file from ePages:

    https://example.com/WebRoot/WSDL/SimpleProvisioningService6.wsdl

    You can also define the version to get other versions of the wsdl.

    The wsdl location is built from endpoint information.
    """

    def __init__(self,
                 endpoint="",
                 provider="",
                 username="",
                 password="",
                 version="6"):
        super(SimpleProvisioningService, self).__init__(
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
        wsdlurl = '{uri.scheme}://{uri.netloc}/WebRoot/WSDL/'\
                  'SimpleProvisioningService{version}.wsdl'.format(
                      uri=parsed, version=self.version
                  )
        logger.debug('Built wsdl url from endpoint: %s', wsdlurl)
        return wsdlurl

    def get_createshop_type(self):
        """ get the create type """
        return self.client.get_type('ns0:TCreateShop')

    def get_createshop_obj(self, data={}):
        """ get shop object for creation """
        return self.get_createshop_type()(**data)

    def get_shopref_type(self):
        """ get shopref factory """
        return self.client.get_type('ns0:TShopRef')

    def get_shopref_obj(self, data={}):
        """ get shop object for exists, getinfo and markfor deletion calls """
        return self.get_shopref_type()(**data)

    def get_updateshop_type(self):
        """ get updateshop factory """
        return self.client.get_type('ns0:TUpdateShop')

    def get_updateshop_obj(self, data={}):
        """ get shop object for update call """
        return self.get_updateshop_type()(**data)

    def get_rename_type(self):
        """ get rename type factory """
        return self.client.get_type('ns0:TRename_Input')

    def get_rename_obj(self, data={}):
        """ get rename object """
        return self.get_rename_type()(**data)

    def create(self, shop):
        """
        Creates new shop

        sp = provisioning.SimpleProvisioningService(...)
        shop = sp.factory_createshop_obj()
        shop.Alias = "TestShop"
        shop.ShopType = "MinDemo"
        sp.create(shop)

        returns None when everything is ok.
        """
        if not isinstance(shop, type(self.get_createshop_obj())):
            raise TypeError(
                "Get shop from get_createshop_obj and call with that")

        logger.info('Creating new shop with data: %s', shop)
        return self.service2.create(shop)

    def exists(self, shop):
        """
        Check if shop exists

        shopref = sp.get_shopref_obj()
        shopref.Alias = "ExistingShop"
        exists = sp.get_info(shopref)

        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError("Get shop from get_shopref_obj and call with that")

        return self.service2.exists(shop)

    def get_info(self, shop):
        """
        Get shop information

        shopref = sp.get_shopref_obj()
        shopref.Alias = "ExistingShop"
        info = sp.get_info(shopref)

        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        return self.service2.getInfo(shop)

    def mark_for_deletion(self, shop):
        """
        Mark the shop for deletion, it will be deleted by ePages after some
        time (default 30 days)

        Does a extra exists call before marking for deletion because
        ePages service always returns None for this call

        deleteshop = sp.get_shopref_obj()
        deleteshop.Alias = "ExistingShop"
        sp.delete(deleteshop)

        returns None if the operation was successfull
        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        if self.service2.exists(shop):
            return self.service2.markForDeletion(shop)
        else:
            return False

    def rename(self, shop):
        """
        Rename shop

        Warning: this might change some urls in the shop and confuse
        search engines etc.

        renameshop = sp.get_rename_obj()
        renameshop.Alias = "ExistingAlias"
        renameshop.NewAlias = "NewAlias"
        sp.rename(renamshop)

        returns None if the operation was successfull
        """
        if not isinstance(shop, type(self.get_rename_obj())):
            raise TypeError(
                "Get shop from get_rename_obj and call with that")

        return self.service2.rename(shop)

    def update(self, shop):
        """
        Update shop information.

        updateshop = sp.get_updateshop_obj()
        updateshop.Alias = "ExistingAlias"
        updateshop.IsClosed = 1
        sp.update(updateshop)

        returns None if the operation was successfull
        """
        if not isinstance(shop, type(self.get_updateshop_obj())):
            raise TypeError(
                "Get shop from get_updateshop_obj and call with that")

        return self.service2.update(shop)

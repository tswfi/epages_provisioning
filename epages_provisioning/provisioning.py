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
    """ Base for provisioning services

    :param endpoint: server to use e.g. https://example.com/
    :param provider: provider name
    :param username: username
    :param password: password
    :param version: wsdl version number, defaults to latest version available
    """
    def __init__(
            self,
            server="",
            provider="",
            username="",
            password="",
            version=""):

        for key, value in locals().items():
            if value is "":
                raise ValueError('Argument %s required', key)

        super(BaseProvisioningService, self).__init__()

        self.server = server

        self.provider = provider
        self.username = username
        self.password = password
        self.version = version

        self.endpoint = self._build_endpoint_from_server()
        self.wsdl = self._build_wsdl_url_from_endpoint()
        self.userpath = self._build_full_username()

        # initialize our client using basic auth and with the wsdl file
        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)
        client = Client(
            wsdl=self.wsdl,
            strict=False,  # ePages wsdl files are full of errors...
            transport=Transport(session=session)
        )
        self.client = client

        # get the binding name, there is only one so this should be ok
        qname = next(iter(client.wsdl.bindings))

        # and create new service with the name pointing to our endpoint
        self.service2 = client.create_service(qname, self.endpoint)
        logger.debug('Initialized new client: %s', self.client)

    def _build_endpoint_from_server(self):
        """ Build endpoint url from server """
        return "{}/epages/Site.soap".format(self.server)

    def _build_wsdl_url_from_endpoint(self):
        """ you need to implement this method in subclasses, each service has
        different wsdl file locations """
        raise NotImplementedError

    def _build_full_username(self):
        """ build the username as a path """
        return "/Providers/{}/Users/{}".format(self.provider, self.username)


class ShopConfigService(BaseProvisioningService):
    """
    ShopConfig service, handles more than simple provisioning service
    """

    def __init__(self,
                 server="",
                 provider="",
                 username="",
                 password="",
                 version="11"):  # TODO: 12 after ePages fixes AD-8535
        super(ShopConfigService, self).__init__(
            server=server,
            provider=provider,
            username=username,
            password=password,
            version=version,
        )

    def _build_wsdl_url_from_endpoint(self):
        """ Builds url to the wsdl from endpoint and version number """
        parsed = urlparse(self.endpoint)
        wsdlurl = '{uri.scheme}://{uri.netloc}/WebRoot/WSDL/'\
                  'ShopConfigService{version}.wsdl'.format(
                      uri=parsed, version=self.version
                  )
        logger.debug('Built wsdl url from endpoint: %s', wsdlurl)
        return wsdlurl

    def get_infoshop_obj(self, data=None):
        """ infoshop object, used with get_info """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TInfoShop_Input')(**data)

    def get_shopref_obj(self, data=None):
        """ returns a shopref object
        use this when calling exists, delete etc. """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TShopRef')(**data)

    def get_all_info(self):
        """ Get info about all shops """
        return self.service2.getAllInfo()

    def get_createshop_obj(self, data=None):
        """ createshop obj
        use this when calling create """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TCreateShop')(**data)

    def get_updateshop_obj(self, data=None):
        """ createshop obj
        use this when calling create """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TUpdateShop')(**data)

    def get_secondarydomains_obj(self, domains):
        """ get secondarydomains obj, used with set_secondary_domains """
        if not isinstance(domains, list):
            raise TypeError(
                "domains should be a list of domains"
            )
        return self.client.get_type('ns0:TSecondaryDomains')(domains)

    def get_info(self, shop):
        """ get information about one shop

        sc.get_info(sc.get_infoshop_obj({'Alias': 'DemoShop'}))
        """
        if not isinstance(shop, type(self.get_infoshop_obj())):
            raise TypeError(
                "Get shop from get_infoshop_obj and call with that")

        return self.service2.getInfo(shop)

    def exists(self, shop):
        """ Check if a shop exists

        sc.exists(sc.get_shopref_obj({'Alias': 'DemoShop'}))
        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        return self.service2.exists(shop)

    def create(self, shop):
        """ create new shop

        shop = sc.get_createshop_obj()
        shop.Alias = "Test"
        shop.ShopType = "MinDemo"
        sc.create(shop)
        """
        if not isinstance(shop, type(self.get_createshop_obj())):
            raise TypeError(
                "Get shop from get_createshop_obj and call with that")

        return self.service2.create(shop)

    def update(self, shop):
        """ update shop

        shop = sc.get_updateshop_obj()
        shop.Alias = "Test"
        shop.IsTrial = False
        sc.update(shop)
        """
        if not isinstance(shop, type(self.get_updateshop_obj())):
            raise TypeError(
                "Get shop from get_updateshop_obj and call with that")

        return self.service2.update(shop)

    def set_secondary_domains(self, shop, domains):
        """ set secondary domains for the shop

        shopref = sc.get_shopref_obj()
        shopref.Alias = 'DemoShop'
        domains = sc.get_secondarydomains_obj(['test.fi', 'test2.fi'])
        sc.set_secondary_domains(shopref, domains)
        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")
        if not isinstance(domains, type(self.get_secondarydomains_obj())):
            raise TypeError(
                "Get shop from get_secondarydomains_obj and call with that")

        return self.service2.setSecondaryDomains(shop, domains)

    def delete(self, shop):
        """ delete a shop

        sc.delete(sc.get_shopref_obj({'Alias': 'DemoShop'}))
        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        return self.service2.delete(shop)

    def delete_shopref(self, shop):
        """ delete a shop

        sc.delete_shopref(sc.get_shopref_obj({'Alias': 'DemoShop'}))
        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        return self.service2.deleteShopRef(shop)


class SimpleProvisioningService(BaseProvisioningService):
    """ Simple provisioning

    handles creating updating and deleting shops in ePages environment.

    By default uses the following wsdl file from ePages:

    https://example.com/WebRoot/WSDL/SimpleProvisioningService6.wsdl

    You can also define the version to get other versions of the wsdl.

    The wsdl location is built from endpoint information.
    """

    def __init__(self,
                 server="",
                 provider="",
                 username="",
                 password="",
                 version="6"):
        super(SimpleProvisioningService, self).__init__(
            server=server,
            provider=provider,
            username=username,
            password=password,
            version=version
        )

    def _build_wsdl_url_from_endpoint(self):
        """ Builds url to the wsdl from endpoint and version number """
        parsed = urlparse(self.endpoint)
        wsdlurl = '{uri.scheme}://{uri.netloc}/WebRoot/WSDL/'\
                  'SimpleProvisioningService{version}.wsdl'.format(
                      uri=parsed, version=self.version
                  )
        logger.debug('Built wsdl url from endpoint: %s', wsdlurl)
        return wsdlurl

    def get_createshop_obj(self, data=None):
        """ get shop object for creation """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TCreateShop')(**data)

    def get_shopref_obj(self, data=None):
        """ get shop object for exists, getinfo and markfor deletion calls """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TShopRef')(**data)

    def get_updateshop_obj(self, data=None):
        """ get shop object for update call """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TUpdateShop')(**data)

    def get_rename_obj(self, data=None):
        """ get rename object """
        if data is None:
            data = {}
        return self.client.get_type('ns0:TRename_Input')(**data)

    def create(self, shop):
        """ Creates new shop

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
        """ Check if shop exists

        shopref = sp.get_shopref_obj()
        shopref.Alias = "ExistingShop"
        exists = sp.get_info(shopref)

        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError("Get shop from get_shopref_obj and call with that")

        return self.service2.exists(shop)

    def get_info(self, shop):
        """ Get shop information

        shopref = sp.get_shopref_obj()
        shopref.Alias = "ExistingShop"
        info = sp.get_info(shopref)

        """
        if not isinstance(shop, type(self.get_shopref_obj())):
            raise TypeError(
                "Get shop from get_shopref_obj and call with that")

        return self.service2.getInfo(shop)

    def mark_for_deletion(self, shop):
        """ Mark the shop for deletion

        The shop will be deleted by ePages after some time (default 30 days)

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
        """ Rename shop

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
        """ Update shop information.

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

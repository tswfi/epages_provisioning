#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `epages_provisioning` package."""

import os
import unittest
from datetime import datetime

import logging
import http.client as http_client

from epages_provisioning import provisioning

# activate full logging to see what is on the wire
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class TestSimpleProvisioning(unittest.TestCase):
    """ Tests for `epages_provisioning` package.
    All tests require that the environment variables:

        EP_ENDPOINT
        EP_PROVIDER
        EP_USERNAME
        EP_PASSWORD

    are set

    For example:

        export EP_ENDPOINT=http://tatu05.sml18.vilkas.pri/epages/Site.soap
        export EP_PROVIDER=Distributor
        export EP_USERNAME=admin
        export EP_PASSWORD=admin
        make test

    These tests also assume that the ePages service is a default installation
    with default shoptypes etc.
    """

    @classmethod
    def setUpClass(cls):
        """ set up our client for the tests """
        cls._sp = provisioning.SimpleProvisioningService(
            endpoint=os.environ['EP_ENDPOINT'],
            provider=os.environ['EP_PROVIDER'],
            username=os.environ['EP_USERNAME'],
            password=os.environ['EP_PASSWORD'],
            )
        # used as alias for these tests
        cls._nowstr = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cls._shopalias = 'test-{}'.format(cls._nowstr)

    def test_000_create(self):
        """ test creating new shop """
        data = {
            'Alias': self._shopalias,
            'ShopType': 'MinDemo',
        }
        self.assertIsNone(self._sp.create(data))
        self.assertTrue(self._sp.get_info(data))

    def test_001_exists(self):
        """ test exists method, assumes that shop with alias "NotExistingAlias
        does not exists in the ePages system """
        data = {
            'Alias': self._shopalias
        }
        self.assertTrue(self._sp.exists(data))

        data = {
            'Alias': 'NotExistingAlias'
        }
        self.assertFalse(self._sp.exists(data))

    def test_002_get_info(self):
        """ test getinfo """
        data = {
            'Alias': self._shopalias
        }
        info = self._sp.get_info(data)
        self.assertTrue(self._sp.get_info(data))
        print(info)

    def test_999_mark_for_delete(self):
        """ test shop deletion, assumes that create was successfull """
        data = {
            'Alias': self._shopalias,
        }
        self._sp.mark_for_deletion(data)

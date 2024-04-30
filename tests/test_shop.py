#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `epages_provisioning` package."""

import os
import unittest
from datetime import datetime

from epages_provisioning.provisioning import ShopConfigService
from epages_provisioning.shop import Shop

# check for our environment variables
envcheck = unittest.skipUnless(
    os.environ.get('EP_SERVER', False) and
    os.environ.get('EP_PROVIDER', False) and
    os.environ.get('EP_PASSWORD', False) and
    os.environ.get('EP_USERNAME', False), 'Environment variables not set'
)


@envcheck
class TestShop(unittest.TestCase):
    """ Tests for `epages_provisioning` shop Class.
    All tests require that the environment variables:

        EP_SERVER
        EP_PROVIDER
        EP_USERNAME
        EP_PASSWORD

    are set

    For example:

        export EP_SERVER=http://example.com/
        export EP_PROVIDER=Distributor
        export EP_USERNAME=admin
        export EP_PASSWORD=admin
        make test

    These tests also assume that the ePages service is a default installation
    with default shoptypes etc.

    Also if you want to see a full message trace say:

        export EP_TRACE=1

    And you can define the shoptype to use with

        export EP_SHOPTYPE=MinDemo

    MinDemo is the default value if not set

    and then run your tests

    Warning: these will take a while to run.
    """
    @classmethod
    def setUpClass(cls):
        """
        set up our client for the tests
        """
        cls._sc = ShopConfigService(
            server=os.environ['EP_SERVER'],
            provider=os.environ['EP_PROVIDER'],
            username=os.environ['EP_USERNAME'],
            password=os.environ['EP_PASSWORD'],
        )
        # used as alias for these tests
        cls._nowstr = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cls._alias = 'test-{}-min'.format(cls._nowstr)
        cls._shoptype = os.environ.get('EP_SHOPTYPE', 'MinDemo')
        print("Using shopalias: {} for testing".format(cls._alias))

    def setUp(self):
        """ get a shop to play with """
        self.s = Shop(Alias=self._alias, provisioning=self._sc)

    def test_001_start(self):
        """ sanity check """
        self.assertTrue(self.s)

    def test_010_create(self):
        """ set the shop type and create the shop """
        self.s.ShopType = self._shoptype
        self.assertIsNone(self.s.create())
        self.assertEqual(self.s.Alias, self._alias)

        self.assertFalse(self.s.IsTrialShop)
        self.assertFalse(self.s.IsClosed)
        self.assertFalse(self.s.IsClosedTemporarily)

    def test_020_update(self):
        """ update shop attribute """
        self.s.IsTrialShop = True
        self.assertIsNone(self.s.apply())
        self.assertTrue(self.s.IsTrialShop)

    def test_030_secondarydomains(self):
        """ assign extra domains to the shop """
        domains = [
            "test1"+self._alias+".com",
            "test2"+self._alias+".com",
            ]
        self.s.SecondaryDomains = domains
        self.assertIsNone(self.s.apply())

        self.assertEqual(self.s.SecondaryDomains, domains)

    def test_040_set_extra_attribute(self):
        self.assertIsNone(self.s.set_shop_attribute('GrantServiceAccessUntil',
                                                    '2100-01-01'))

    def test_050_get_extra_attribute(self):
        """ get one extra attribute from shop """
        self.assertTrue(self.s.get_shop_attribute('Path'))
        self.assertTrue(self.s.get_shop_attribute('CreationDate'))
        # this was set in a previous test
        service_access = self.s.get_shop_attribute('GrantServiceAccessUntil')
        self.assertEqual(service_access[0:10], '2100-01-01')
        with self.assertRaises(Exception) as e:
            self.s.get_shop_attribute('NotExistingAttributeName')

    def test_900_mark_deletion(self):
        """ mark the shop for deletion """
        self.assertIsNone(self.s.mark_for_delete())
        self.assertTrue(self.s.MarkedForDelOn)

    def test_999_delete(self):
        """ delete the shop completely """
        self.assertIsNone(self.s.delete(shopref=True))
        self.assertFalse(self.s.exists)

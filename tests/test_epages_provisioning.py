#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `epages_provisioning` package."""

import os
import unittest
from datetime import datetime

# import logging
# import http.client as http_client

from zeep.exceptions import ValidationError
from epages_provisioning import provisioning

# activate full logging to see what is on the wire
# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


class TestSimpleProvisioning(unittest.TestCase):
    """ Tests for `epages_provisioning` package.
    All tests require that the environment variables:

        EP_ENDPOINT
        EP_PROVIDER
        EP_USERNAME
        EP_PASSWORD

    are set

    For example:

        export EP_ENDPOINT=http://example.com/epages/Site.soap
        export EP_PROVIDER=Distributor
        export EP_USERNAME=admin
        export EP_PASSWORD=admin
        make test

    These tests also assume that the ePages service is a default installation
    with default shoptypes etc.

    Warning: these will take a while to run.
    """

    @classmethod
    def setUpClass(cls):
        """
        set up our client for the tests
        """
        cls._sp = provisioning.SimpleProvisioningService(
            endpoint=os.environ['EP_ENDPOINT'],
            provider=os.environ['EP_PROVIDER'],
            username=os.environ['EP_USERNAME'],
            password=os.environ['EP_PASSWORD'],
        )
        # used as alias for these tests
        cls._nowstr = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cls._shopalias_min = 'test-{}-min'.format(cls._nowstr)
        cls._shopalias_min_tmp = 'test-{}-min_tmp'.format(cls._nowstr)
        cls._shopalias_add = 'test-{}-add'.format(cls._nowstr)

    def test_000_create_mindata(self):
        """
        test creating new shop with minimal data
        """
        shop = self._sp.get_createshop_obj(
            {
                'Alias': self._shopalias_min,
                'ShopType': 'MinDemo',
            }
        )
        self.assertIsNone(self._sp.create(shop))

    def test_001_create_missingdata(self):
        """
        test creating with missing data
        """
        # ShopType is mandatory
        shop = self._sp.get_createshop_obj(
            {
                'Alias': self._shopalias_min,
            }
        )
        with self.assertRaises(ValidationError) as e:
            self._sp.create(shop)

        self.assertEqual(e.exception.message, "Missing element ShopType")

    def test_002_create_with_additional(self):
        shop = self._sp.get_createshop_obj(
            {
                'Alias': self._shopalias_add,
                'ShopType': 'MinDemo',
                'IsClosed': 1,
                'IsTrialShop': 1,
                'IsInternalTestShop': 1,
                # 'HasSSLCertificate': 0,
                'MerchantLogin': 'test',
                'MerchantPassword': '123456',
                'MerchantEMail': 'test@example.com',
                'Name': 'TestShop',
                'AdditionalAttributes': [
                    {
                        'Name': 'Channel',
                            'Type': 'String',
                            'Value': 'TestScript'
                    },
                    {
                        'Name': 'Likeability',
                        'Type': 'Integer',
                        'Value': '1'
                    },
                ],
            }
        )
        # TODO this fails, ePages does not understand the AdditionalAttributes
#        self.assertIsNone(self._sp.create(shop))
#        shop = self._sp.get_shopref_obj(
#            {
#                'Alias': self._shopalias_add,
#            }
#        )
#        self.assertTrue(self._sp.get_info(shop))
        # TODO check that the additionalattributes are there
#        self.assertDictContainsSubset(
#            {
#                'Alias': self._shopalias_min,
#                'AdditionalAttributes'
#            },
#            info)

    def test_010_exists(self):
        """
        test exists method, assumes that shop with alias "NotExistingAlias
        does not exists in the ePages system
        """
        shop = self._sp.get_shopref_obj(
            {
                'Alias': self._shopalias_min,
            }
        )

        self.assertTrue(self._sp.exists(shop))

        shop = self._sp.get_shopref_obj(
            {
                'Alias': 'NotExistingAlias',
            }
        )
        self.assertFalse(self._sp.exists(shop))

    def test_020_get_info(self):
        """
        test getinfo
        """
        shop = self._sp.get_shopref_obj(
            {
                'Alias': self._shopalias_min,
            }
        )

        info = self._sp.get_info(shop)
        self.assertTrue(info)
        self.assertDictContainsSubset(
            {
                'Alias': self._shopalias_min,
                'MerchantLogin': None,
                'IsClosed': False,
            },
            info
        )

    def test_030_update(self):
        """
        Test updating shop data
        """
        update = self._sp.get_updateshop_obj(
            {
                'Alias': self._shopalias_min,
                'IsClosed': 1,
                'Name': "Test shop updated"
            }
        )
        self.assertIsNone(self._sp.update(update))

    def test_040_rename(self):
        """
        test rename operation (twice to get the name back to what it was)
        """
        rename = self._sp.get_rename_obj(
            {
                'Alias': self._shopalias_min,
                'NewAlias': self._shopalias_min_tmp,
            }
        )
        self.assertIsNone(self._sp.rename(rename))

        # and rename back for others
        rename = self._sp.get_rename_obj(
            {
                'Alias': self._shopalias_min_tmp,
                'NewAlias': self._shopalias_min,
            }
        )
        self.assertIsNone(self._sp.rename(rename))

    def test_900_mark_for_delete_not(self):
        """
        test shop deletion with non existing shop
        """
        shop = self._sp.get_shopref_obj(
            {
                'Alias': 'NotExistingAlias',
            }
        )
        self.assertFalse(self._sp.mark_for_deletion(shop))

    def test_901_mark_for_delete(self):
        """
        test shop deletion, assumes that creates were successfull
        """
        shop = self._sp.get_shopref_obj(
            {
                'Alias': self._shopalias_min,
            }
        )
        self.assertIsNone(self._sp.mark_for_deletion(shop))
        # TODO: add back after additional creation works
#        shop = self._sp.get_shopref_obj(
#            {
#                'Alias': self._shopalias_add,
#            }
#        )
#        self.assertIsNone(self._sp.mark_for_deletion(shop))

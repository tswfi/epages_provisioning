#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `epages_provisioning` package."""

import os
import unittest
from datetime import datetime

from epages_provisioning import provisioning


class TestSimpleProvisioning(unittest.TestCase):
    """ Tests for `epages_provisioning` package.
    All tests require that the environment variables:

        EP_ENDPOINT
        EP_PROVIDER
        EP_USERNAME
        EP_PASSWORD

    are set

    For example:

        EP_ENDPOINT=http://tatu05.sml18.vilkas.pri/epages/Site.soap EP_PROVIDER=Distributor EP_USERNAME=admin EP_PASSWORD=admin make test

    These tests also assume that the ePages service is a default installation with default shoptypes etc.
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

    def test_000_create(self):
        """ test creating new shop """
        data = {
            'Alias': 'test-{}'.format(self._nowstr),
            'ShopType': 'MinDemo',
        }
        shopinfo = self._sp.create(data)

    def test_001_delete(self):
        data = {
            'Alias': 'test-{}'.format(self._nowstr),
        }
        self._sp.markForDeletion(data)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `epages_provisioning` package."""

import os
import unittest

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

    def test_000_create(self):
        """ test creating new shop """
        data = {
            'Alias': 'foobar',
            'ShopType': 'MinDemo',
        }
        self._sp.create(data)

    def test_001_delete(self):
        data = {
            'Alias': 'foobar',
        }
        self._sp.markForDeletion(data)

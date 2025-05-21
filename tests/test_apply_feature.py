import os
import unittest
import logging

from epages_provisioning import features

logger = logging.getLogger(__name__)

class TestFeaturePackService(unittest.TestCase):

    @unittest.skipUnless(
        all(os.environ.get(var) for var in ['EP_SERVER', 'EP_PROVIDER', 'EP_USERNAME', 'EP_PASSWORD']),
        "Environment variables not set"
    )
    def test_list_feature_packs(self):
        fps = features.FeaturePackService(
            server=os.environ['EP_SERVER'],
            provider=os.environ['EP_PROVIDER'],
            username=os.environ['EP_USERNAME'],
            password=os.environ['EP_PASSWORD'],
        )


        applyShop = fps.applyToShop('demo', 'DemoShop2')
        logger.debug(f"Apply to shop: {applyShop}")

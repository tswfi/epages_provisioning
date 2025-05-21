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


        applyShop = fps.applyToShop('demo2', 'demo2')
        logger.debug(f"Apply to shop: {applyShop}")
        # this might fail, because the feature is already assigned

        removeShop = fps.removeFromShop('demo2', 'demo2')
        logger.debug(f"Remove from shop: {removeShop}")
        assert removeShop.Error == None
        assert removeShop.removed == True

        applyShop = fps.applyToShop('demo2', 'demo2')
        logger.debug(f"Apply to shop: {applyShop}")
        assert applyShop.Error == None
        assert applyShop.applied == True

        invalid = fps.applyToShop('demo', 'invalid')
        logger.debug(f"Apply to invalid shop: {invalid}")
        assert invalid.Error.Message == 'Object with path /Providers/Distributor/ShopRefs/invalid was not found.'

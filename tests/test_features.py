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


        error = fps.getInfo('invalid');
        logger.debug(f"feature pack not found error: {error}")
        assert error.Error.Message == 'Object with path /Providers/Distributor/FeaturePacks/invalid was not found.'

        feature = fps.getInfo('demo')

        logger.debug(f"Feature: {feature}")
        assert feature.Error == None
        assert feature.IsActive == True
        assert feature.Attributes[0].Value == 'demo'

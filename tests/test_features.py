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


        error = fps.getInfo('invalid'); # This returns an error, which is valid.
        logger.debug(f"invalid feature response. feature pack not found: {error}")
        assert error[0].Error.Message == 'Object with path /Providers/Distributor/FeaturePacks/invalid was not found.'

        # But if you fetch a valid feature pack, it returns the information in invalid form...
        #feature = fps.getInfo('demo') # so this needs to be fixes in ingress.

        #logger.error(f"Feature: {feature}")
        #print(feature)

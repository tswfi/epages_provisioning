import logging
from zeep import Client, Settings
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from requests import Session

from .zeep_utils import BooleanFixer, ArrayFixer, LocalSchemaTransport

logger = logging.getLogger(__name__)

class FeaturePackService:
    def __init__(self, server, provider, username, password):
        wsdl_url = f"{server}/WebRoot/WSDL/FeaturePackService.wsdl"
        if not wsdl_url.startswith("http"):
            wsdl_url = "https://" + wsdl_url
        self.provider = provider
        self.username = username
        self.password = password
        self.userpath = self._build_full_username()
        self.server = server
        self.endpoint = self._build_endpoint_from_server()
        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)

        settings = Settings(
            strict=False,
        )
        # Plugins instances
        arrayfixer = ArrayFixer()
        booleanfixer = BooleanFixer()

        self.client = Client(
            wsdl=wsdl_url,
            settings=settings,
            transport=LocalSchemaTransport(session=session),
            plugins=[arrayfixer, booleanfixer]
        )
        qname = next(iter(self.client.wsdl.bindings))
        logger.debug(f"Binding: {qname}")
        self.service2 = self.client.create_service(qname, self.endpoint)

    def _build_endpoint_from_server(self):
        """ Build endpoint url from server """
        return "{}/epages/Site.soap".format(self.server)

    def _build_full_username(self):
        return f"/Providers/{self.provider}/Users/{self.username}"

    def getInfo(self, feature: str, language: str | list[str] = "en"):
        """ Get information about a feature pack. Stuff like isActive or ShopCount """
        return self.getInfoMultiple([feature], language)[0]

    def getInfoMultiple(self, features: list[str], language: str | list[str] = ["en"]):
        """ Get information about multiple feature packs. Note that it still requires the aliases """
        getinfo_type = self.client.get_type("ns0:type_GetInfo_In")
        path = [f"/Providers/{self.provider}/FeaturePacks/{feature}" for feature in features]
        getinfo = getinfo_type(path)
        attributenames_type = self.client.get_type("ns0:type_AttributeNames_In")

        # Can fetch more attributes, that ePages doesn't return by default.
        # By default it doesn't return the alias, so let's at least return that.
        attributenames = attributenames_type(['Alias'])

        language_code_type = self.client.get_type("ns0:type_LanguageCodes_In")
        language_code = language_code_type([language] if isinstance(language, str) else language)
        feature = self.service2.getInfo(getinfo, attributenames, language_code)
        return feature

    def applyToShop(self, feature: str, shop: str):
        """ Apply a feature pack to a specific shop. """
        input_type = self.client.get_type("ns1:TApplyToShop_Input")
        feature_path = f"/Providers/{self.provider}/FeaturePacks/{feature}"
        shop_path = f"/Providers/{self.provider}/ShopRefs/{shop}"
        pair = input_type(feature_path, shop_path)
        result = self.service2.applyToShop(pair)
        return result[0]

    def removeFromShop(self, feature: str, shop: str):
        """ Remove a feature pack from a specific shop. """
        input_type = self.client.get_type("ns1:TRemoveFromShop_Input")
        feature_path = f"/Providers/{self.provider}/FeaturePacks/{feature}"
        shop_path = f"/Providers/{self.provider}/ShopRefs/{shop}"
        pair = input_type(feature_path, shop_path)
        result = self.service2.removeFromShop(pair)
        return result[0]

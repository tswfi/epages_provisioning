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
        self.provider = provider
        self.username = username
        self.password = password
        self.userpath = self._build_full_username()
        self.server = server
        self.endpoint = self._build_endpoint_from_server()
        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)

        settings = Settings(
            strict=True,  # For now, seems to work. But toggle back if something comes up again...
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
        logger.error(f"Binding: {qname}")
        self.service2 = self.client.create_service(qname, self.endpoint)

    def _build_endpoint_from_server(self):
        """ Build endpoint url from server """
        return "{}/epages/Site.soap".format(self.server)

    def _build_full_username(self):
        return f"/Providers/{self.provider}/Users/{self.username}"

    def list_feature_packs(self):
        getinfo_type = self.client.get_type("ns0:type_GetInfo_In")
        getinfo = getinfo_type(['/Providers/Distributor/FeaturePacks/demo']) # I have no idea what this parameter is. MinOcr 1...
        attributenames_type = self.client.get_type("ns0:type_AttributeNames_In")
        attributenames = attributenames_type(['Alias', 'test']) # I'm guessing this is what attributes we want to receive? IDK
        language_code_type = self.client.get_type("ns0:type_LanguageCodes_In")
        language_code = language_code_type(['en', 'fi'])
        return self.service2.getInfo(getinfo, attributenames, language_code)
        # Now it sends the request, but cannot parse the response...


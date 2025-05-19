import logging
from zeep import Client
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
        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)

        # Plugins instances
        arrayfixer = ArrayFixer()
        booleanfixer = BooleanFixer()

        self.client = Client(
            wsdl=wsdl_url,
            transport=LocalSchemaTransport(session=session),
            plugins=[arrayfixer, booleanfixer]
        )

    def _build_full_username(self):
        return f"/Providers/{self.provider}/Users/{self.username}"

    def list_feature_packs(self):
        # todo remove this. just for logging
        for service in self.client.wsdl.services.values():
            for port in service.ports.values():
                logger.error(f"Port: {port.name}")
                logger.error("Operations:")
                for op in port.binding._operations.values():
                    logger.error(f" - {op.name}")
                    logger.error(op.input)
                    logger.error(op.input.signature())
                    logger.error(op.input.body)
                    logger.error(op.input.body.type)


        # This needs some parameter... it's not working as is
        return self.client.service.getInfo(self.provider)


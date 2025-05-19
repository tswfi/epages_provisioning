import logging
import os
from urllib.parse import urlparse
from lxml import etree

from zeep import Plugin
from zeep.transports import Transport

logger = logging.getLogger(__name__)

class LocalSchemaTransport(Transport):
    """
    Overrides Transport to accommodate local version of schema for http://schemas.xmlsoap.org/soap/encoding/

    Thanks: https://github.com/mvantellingen/python-zeep/issues/1417

    If zeep starts to do this natively this can be removed
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, url):
        """Load the content from the given URL"""
        if not url:
            raise ValueError("No url given to load")
        logger.error(f"Loading {url}")
        scheme = urlparse(url).scheme
        if scheme in ("http", "https", "file"):

            if self.cache:
                response = self.cache.get(url)
                if response:
                    return bytes(response)

            # fix feature namespaces
            # TODO, maybe just do the same fix as the others, and fix the xml file
            if url.endswith("FeaturePackService.wsdl"):
                logger.error(f"Patching WSDL {url}")
                parser = etree.XMLParser(ns_clean=True, recover=True)
                content = super().load(url)
                doc = etree.fromstring(content, parser=parser)

                # Fix the import namespace in WSDL to match the XSD targetNamespace exactly
                for imp in doc.xpath("//xsd:import", namespaces={'xsd': 'http://www.w3.org/2001/XMLSchema'}):
                    imp.attrib['namespace'] = "urn://epages.de/WebService/FeaturePackTypes/2005/03"


                return etree.tostring(doc)

            elif url.endswith("FeaturePackTypes.xsd"):
                logger.error(f"Patching XSD {url}")
                parser = etree.XMLParser(ns_clean=True, recover=True)
                content = super().load(url)
                doc = etree.fromstring(content, parser=parser)

                expected_ns = "urn://epages.de/WebService/FeaturePackTypes/2005/03"
                current_ns = doc.attrib.get('targetNamespace', '')
                if current_ns != expected_ns:
                    doc.attrib['targetNamespace'] = expected_ns
                return etree.tostring(doc)

            # this url was causing some issues (404 errors); it is now saved locally for fast retrieval when needed
            if url == 'http://schemas.xmlsoap.org/soap/encoding/':
                DIR_ABS_PATH = os.path.dirname(__file__)
                soap_encodings_file = os.path.join(DIR_ABS_PATH, 'data', 'soap-encodings.xml')
                with open(soap_encodings_file, 'rb') as fh:
                    return fh.read()

            content = self._load_remote_data(url)

            if self.cache:
                self.cache.add(url, content)

            return content
        else:
            with open(os.path.expanduser(url), "rb") as fh:
                return fh.read()


class BooleanFixer(Plugin):
    """ ePages does not like boolean values as being "false"

    change them to 0

    TODO: There must be a better way
    """

    elements = (
        'IsClosed',
        'IsClosedTemporarily',
        'IsTrialShop',
        'IsInternalTestShop',
        'MarkedForDelete',
        'IsInternalTestShop',
        'HasSSLCertificate',
    )

    def ingress(self, envelope, http_headers, operation):
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):

        for elementkey in self.elements:
            element = envelope.find(".//"+elementkey)
            if element is not None and element.text == "false":
                element.text = "0"

        return envelope, http_headers


class ArrayFixer(Plugin):
    """ try to fix the soap arrays for Soap::Lite

    see https://github.com/mvantellingen/python-zeep/issues/521

    TODO: There must be a better way. yeah, this needs a rewrite...
    """

    def ingress(self, envelope, http_headers, operation):
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        """ force array type to SecondaryDomains, AdditionalAttributes
        Attributes and Languages elements. And remove xsitype from items """

        # for future reference on how to look inside the envelope
        # from xml.etree import ElementTree
        # print(ElementTree.tostring(envelope, encoding='utf8', method='xml'))

        secondarydomains = envelope.find(".//SecondaryDomains")
        if secondarydomains is not None:
            logger.debug("Mangling SecondaryDomains element, to arraytype")
            length = len(secondarydomains)
            secondarydomains.attrib[
                "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
            ] = "ns1:string[{}]".format(length)
            for item in secondarydomains.getchildren():
                item.attrib.clear()

        additional = envelope.find(".//AdditionalAttributes")
        if additional is not None:
            logger.debug("Mangling AdditionalAttributes element, to arraytype")
            length = len(additional)
            additional.attrib[
                "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
            ] = "ns1:anyType[{}]".format(length)
            for item in additional.getchildren():
                item.attrib.clear()

        # getinfo and update want different types...
        attributes = envelope.find(".//Attributes")
        if attributes is not None:
            # if TAttribute elements exists the attributes is probably
            # for update not for get...
            action = envelope.find(".//TAttribute")
            if action is not None:
                logger.debug("Mangling Attributes element, to arraytype")
                length = len(attributes)
                attributes.attrib[
                    "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
                ] = "ns1:Tattribute[{}]".format(length)
                for item in attributes.getchildren():
                    item.attrib.clear()
            else:
                logger.debug("Mangling Attributes element, to arraytype")
                length = len(attributes)
                attributes.attrib[
                    "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
                ] = "ns1:string[{}]".format(length)
                for item in attributes.getchildren():
                    item.attrib.clear()

        languages = envelope.find(".//Languages")
        if languages is not None:
            logger.debug("Mangling Languages element, to arraytype")
            length = len(languages)
            languages.attrib[
                "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
            ] = "ns2:string[{}]".format(length)
            for item in languages.getchildren():
                item.attrib.clear()

        return envelope, http_headers

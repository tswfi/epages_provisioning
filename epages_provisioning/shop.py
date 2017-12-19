"""
ePages shop
"""
import logging

logger = logging.getLogger(__name__)


class ShopError(Exception):
    pass


class ShopExistsError(ShopError):
    pass


class ShopDisappearedError(ShopError):
    pass


class Shop(object):
    """ wrapper for shopconfig service to get it more pythonic """

    # shop keys
    shopkeys = (
        'Alias',
        'ShopType',
        'Database',
        'Provider',
        'IsClosed',
        'IsClosedTemporarily',
        'IsDeleted',
        'MarkedForDelOn',
        'IsTrialShop',
        'IsInternalTestShop',
        'DomainName',
        'HasSSLCertificate',
        'WebServerScriptNamePart',
        'MerchantLogin',
        'MerchantEMail',
        'SecondaryDomains',
        'Attributes',
    )

    def __init__(
            self,
            Alias=None,
            provisioning=None,
    ):
        """ ePages shop object """
        # default to None
        for key in self.shopkeys:
            setattr(self, key, None)

        # set alias from parameters
        self.Alias = Alias

        # set shoptype to None
        self.ShopType = None

        self.sc = provisioning

        self.shoprefobj = self.sc.get_shopref_obj({'Alias': self.Alias})
        self.infoshopobj = self.sc.get_infoshop_obj({'Alias': self.Alias})

        # check if the shop has been created
        self.exists = self.sc.exists(self.shoprefobj)

        # refresh data if the shop already exists
        if self.exists:
            self.refresh()

    def _to_dict(self):
        """ helper method for getting the shop attributes to a dict """
        data = {}
        for key in self.shopkeys:
            data[key] = getattr(self, key)

        # set secondary domains to empty array if it is none
        if data['SecondaryDomains'] is None:
            data['SecondaryDomains'] = []

        # set attributes as array if it is None
        if data['Attributes'] is None:
            data['Attributes'] = []

        return data

    def _from_dict(self, data=None):
        """ helper method for updating the shop attributes from a dict """
        for key in self.shopkeys:
            setattr(self, key, getattr(data, key))

    def refresh(self):
        """ refresh the internal state from the server """
        # exists state
        self.shoprefobj = self.sc.get_shopref_obj({'Alias': self.Alias})
        self.exists = self.sc.exists(self.shoprefobj)

        if not self.exists:
            raise ShopDisappearedError("Could not find the shop anymore!")

        # data from the server
        self.infoshopobj = self.sc.get_infoshop_obj({'Alias': self.Alias})
        self.shopinfo = self.sc.get_info(self.infoshopobj)

        self._from_dict(self.shopinfo)

    def create(self):
        """ creates the shop on the server """

        # refresh the exists information
        self.shoprefobj = self.sc.get_shopref_obj({'Alias': self.Alias})
        self.exists = self.sc.exists(self.shoprefobj)

        if self.exists:
            raise ShopExistsError("Shop already exists")

        if not self.ShopType:
            raise ValueError("Shoptype must be defined")

        data = self._to_dict()
        # create requires ShopAlias also
        data['ShopAlias'] = data['Alias']
        # also set the webserverscriptname part to be the same as the alias
        # by default
        if data['WebServerScriptNamePart'] is None:
            data['WebServerScriptNamePart'] = data['Alias']

        shopcreateobj = self.sc.get_createshop_obj(
            {k: v for k, v in data.items() if v})
        self.sc.create(shopcreateobj)

        # refresh the data
        self.refresh()

    def apply(self):
        """ apply the changes to the server """

        data = self._to_dict()

        # read only attributes
        del(data['Provider'])
        del(data['MarkedForDelOn'])
        del(data['IsDeleted'])
        del(data['Database'])

        print(data)

        data = {k: v for k, v in data.items() if v is not None}

        # remove empty arrays
        if len(data['Attributes']) == 0:
            del(data['Attributes'])

        if len(data['SecondaryDomains']) == 0:
            del(data['SecondaryDomains'])

        del(data['HasSSLCertificate'])

        print(data)

        updateshopobj = self.sc.get_updateshop_obj(data)

        self.sc.update(updateshopobj)

        self.refresh()

    def reset_merchant_pass(self, newpass):
        """ reset the merchant password

        Note: does not apply other values and will refresh the state from
        server """
        self.refresh()
        if not newpass:
            raise ValueError("Password must be defined")

        updateshopobj = self.sc.get_updateshop_obj(
            {
                'Alias': self.Alias,
                'MerchantPassword': newpass,
            }
        )
        self.sc.update(updateshopobj)
        self.refresh()

    def rename(self, newalias):
        """ rename the shop

        Note: does not apply other values and will refresh the state from
        server """
        self.refresh()
        if not newalias:
            raise ValueError("New alias must be defined")

        updateshopobj = self.sc.get_updateshop_obj(
            {
                'Alias': self.Alias,
                'NewAlias': newalias,
                'WebServerScriptNamePart': newalias,
            }
        )
        self.sc.update(updateshopobj)

        # update our internal alias so that refresh can find
        # the correct shop
        self.Alias = newalias
        self.refresh()

    def mark_for_delete(self, mark=True):
        """ mark the shop for deletion

        If mark is false will revert the deletion if the shop still exists

        Scheduled script will handle the deletion sometime in the future.

        Note: This will not open the shop
        """
        updateshopobj = self.sc.get_updateshop_obj(
            {
                'Alias': self.Alias,
                'MarkedForDelete': mark,
            }
        )
        self.sc.update(updateshopobj)
        self.refresh()

    def delete(self, shopref=False):
        """ delete the shop

        if shopref is True will also delete the shopref """
        self.refresh()

        if shopref:
            self.sc.delete(self.shoprefobj)
        else:
            self.sc.delete(self.shoprefobj)

        self.exists = False

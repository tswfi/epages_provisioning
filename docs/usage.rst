=====
Usage
=====

There are three different ways to use this module.

* SimpleProvisioningService
   * Simple soap service for handling the shop data
   * does not support Attributes but can handle most of the required stuff
* ShopConfigService
   * bit more complete service that can add extra attributes to the shop
* Shop
   * pythonic way of calling ShopConfigService


Shop
----

Shop uses the ShopConfigService as a "transport" layer.

Create new shop
~~~~~~~~~~~~~~~

.. code-block:: python

    from epages_provisioning.provisioning import ShopConfigService
    from epages_provisioning.shop import Shop
    sc = ShopConfigService(
        server = "example.com",
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )

    # this wont create the shop yet
    shop = Shop(Alias="MyTestShop", provisioning=sc)
    # shop type is mandatory
    shop.ShopType="MinDemo"
    # create the shop
    shop.create()
    # access the shop attributes, and change them as required
    shop.IsTrialShop = False
    # apply the changes to the server
    shop.apply()
    # get one attribute from shop (particulary useful if you can also extend
    # the ePages end, for example add attribute SSO_URL to shop ;)
    shop.get_shop_attribute('CreationDate')
    # or set a attribute
    shop.set_shop_attribute('GrantServiceAccessUntil', '2100-01-01')


Get shop attribute
~~~~~~~~~~~~~~~~~~

Pretty much the same as above, but instead use an alias of an existing shop

.. code-block:: python
    from epages_provisioning.provisioning import ShopConfigService
    from epages_provisioning.shop import Shop
    sc = ShopConfigService(
        server = "example.com",
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )

    # this wont create the shop yet
    shop = Shop('ExsitingShopAlias', sc)
    shop.get_shop_attribute('GBaseActiveFeatureList') # This is not implemented yet



Mark the shop for deletion
~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark the shop for delete, ePages will periodically check for shops that have
been marked for deletion for long enough and will delete them

.. code-block:: python

    # this will call apply automatically
    # WARNING: this will also do a refresh from the server, you should call
    # apply before to prevent losing information in our shop object
    shop.mark_for_delete()
    # and reverse delete
    shop.mark_for_delete(mark=False)

Reset merchants password
~~~~~~~~~~~~~~~~~~~~~~~~

Only the super merchant password can be resetted.

.. code-block:: python

    # this will call apply automatically
    # WARNING: this will also do a refresh from the server, you should call
    # apply before to prevent losing information in our shop object
    shop.reset_merchant_pass(newpass="hunter2")

Rename shop
~~~~~~~~~~~

This will change the shops alias and thus all the url structures, not really
recommended for a live shop.

.. code-block:: python

    # this will call apply automatically
    # WARNING: this will also do a refresh from the server, you should call
    # apply before to prevent losing information in our shop object
    shop.rename("MyOtherTestShop")


Delete shop
~~~~~~~~~~~

Totally remove the shop

.. code-block:: python

    shop.delete(shopref=True)


SimpleProvisioningService
-------------------------

Create new shop
~~~~~~~~~~~~~~~

.. code-block:: python

    from epages_provisioning import provisioning
    sp = provisioning.SimpleProvisioningService(
        server = "example.com",
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )
    shop = sp.get_createshop_obj(
        {
            'Alias': 'TestShop1',
            'ShopType': 'MinDemo',
        }
    )
    sp.create(shop)


Get shop info
~~~~~~~~~~~~~

.. code-block:: python

    from epages_provisioning import provisioning
    sp = provisioning.SimpleProvisioningService(
        server = "example.com",
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )
    shop = sp.get_shopref_obj(
        {
            'Alias': 'TestShop1',
        }
    )
    shopinfo = sp.get_info(shop)


ShopConfigService
-----------------

Create new shop
~~~~~~~~~~~~~~~

.. code-block:: python

    from epages_provisioning import provisioning
    sc = provisioning.ShopConfigService(
        server = "example.com",
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )
    shop = sc.get_createshop_obj(
        {
            'Alias': 'TestShop1',
            'ShopType': 'MinDemo',
        }
    )
    sc.create(shop)


Features
~~~~~~~~

.. code-block:: python

    from epages_provisioning import features
    feature_service = features.FeaturePackService(
        server = "example.com", # for testing, you can force http, but by default it addres https://
        provider = "Distributor",
        username = "admin",
        password = "admin",
    )

    ## first let's get a feature pack.
    ## There is not method for fetching all, so you need to know the "Alias" of the feature pack.
    feature_pack = feature_service.getInfo('RateCompass')
    if(feature_pack.Error == None):
         print(feature_pack.IsActive)
         for attr in feature_pack.Attributes:
             print(f"name {attr.Name} value is {attr.Value}") # for now it only has alias
         print(feature_pack.ShopCount) # This increases on every assign, and doesn't subtract removes
         print(feature_pack.ActiveShopCount) # This it what you probably actually want


    ## or fetch multiple features with one request. Still requires the aliases...
    feature_packs = feature_service.getInfoMultiple(['RateCompass', 'BaseDesign', 'invalid'])
    # Note that you can use this to check which feature_packs are available. Even though
    # one parameter is invalid, it returns 3 items, one with an error and IsActive false


    ## Language support. by default en/de are supported, but not fi
    feature_service.getInfo('RateCompass', 'en')
    feature_service.getInfo('RateCompass', ['en', 'de'])
    feature_service.getInfoMultiple(['a', 'b'], 'en')
    feature_service.getInfoMultiple(['a','b'], ['en', 'de'])

    ## Next assign shop to the feature pack.
    res = feature_service.applyToShop('RateCompass', 'DemoShop')
    if(res.applied):
        print('OK')
    else:
        print(res.Error.Message)

    ## And remove the feature pack from the shop
    res = feature_service.removeFromShop('RateCompass', 'DemoShop');
    if(res.removed):
        print('OK')
    else:
        print(res.Error.Message)

    # error handling
    # Response should always be same, errors are displayed in `Error.Message`. So if `Error` is undef, it should be fine.
    non_existing_feature_pack = feature_service.getInfo('does_not_exist');
    if(non_existing_feature_pack.Error):
         print(non_existing_feature_pack.Error.Message)
         # In this case it's that it doesn't exists.



To check if feature pack is already active for the shop, check the new shop attribute GBaseActiveFeatureList


* Make sure to check that the feature pack is active in general, before using it.
* Make sure that the feature pack is active **for the specific shop type** before trying to activate it for a shop.
* You can't check if the shop is eligible for the feature. You just need to assign it and see if it complains about it (TODO)


* TOOD: Check if there is a way of checking if shop is eligible for a specific feature pack, before doing an assign.
* TODO: Check if there is a way of getting list of **all** feature packs.

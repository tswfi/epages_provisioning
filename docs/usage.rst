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

Mark the shop for deletion
~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark the shop for delete, ePages will periodically check for shops that have
been marked for deletion for long enough and will delete them

.. code-block:: python

    # this will call apply automatically
    # WARNING: this will also do a refresh from the server, you should call
    # apply before to prevent losing information in our shop object
    shop.mark_for_deletion()
    # and reverse delete
    shop.mark_for_deletion(mark=False)

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

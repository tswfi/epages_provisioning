=====
Usage
=====

To use ePages provisioning in a project:

Create shop
-----------

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
-------------

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


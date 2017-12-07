=====
Usage
=====

To use ePages provisioning in a project:

.. code-block:: python

   from epages_provisioning import provisioning
   sp = provisioning.SimpleProvisioningService(
   endpoint = "https://example.com/epages/Site.soap,
   provider = "Distributor",
   username = "admin",
   password = "admin",
   )
   shopdata = {
   'Alias': 'MyShop',
   'ShopType': 'MinDemo',
   }
   sp.create(shopdata)
   shopinfo = sp.getinfo(shopdata)


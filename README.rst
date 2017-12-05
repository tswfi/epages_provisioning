===================
ePages provisioning
===================


.. image:: https://img.shields.io/pypi/v/epages_provisioning.svg
        :target: https://pypi.python.org/pypi/epages_provisioning

.. image:: https://img.shields.io/travis/tswfi/epages_provisioning.svg
        :target: https://travis-ci.org/tswfi/epages_provisioning

.. image:: https://readthedocs.org/projects/epages-provisioning/badge/?version=latest
        :target: https://epages-provisioning.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/tswfi/epages_provisioning/shield.svg
     :target: https://pyup.io/repos/github/tswfi/epages_provisioning/
     :alt: Updates


Python library for calling ePages provisioning services

* Free software: MIT license
* Documentation: https://epages-provisioning.readthedocs.io.

Usage
-----

Initialize the service and call it.

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
    shopinfo = sp.create(shopdata)

Features
--------

* ePages SimpleProvisioningService for easy shop creation, modifying and deletion

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

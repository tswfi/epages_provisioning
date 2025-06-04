=======
History
=======

1.1.3 (2025-06-04)
------------------
* add feature pack services
* update zeep to 4.3.1

1.1.2 (2024-04-30)
------------------
* add the xml file to release..

1.1.1 (2024-04-30)
------------------
* bump version to get a proper release done after fixing publish workflow

1.1.0 (2024-04-30)
------------------

* Sync all zeep requirements to 4.2.1
* Fix `test_010_create_mindata` to send `WebServerScriptNamePart` which is required now
* Allow defining shoptype as env variable for tests
* up Pipenv python version to 3.8
* refactor zeep utils to own file
* use local copy of soap-encodings as the server is not stable
  * see: https://github.com/mvantellingen/python-zeep/issues/1417

1.0.2 (2021-01-04)
------------------

* remove last remrants of travis from docs
* fix readme in built package
* retest deploy process

1.0.1 (2021-01-04)
------------------

* drop travis and switch to github actions for pypi publish
* fix pypi and docs build

1.0.0 (2021-01-04)
------------------

* drop support for python 2.7
* update zeep to 4.0.0

0.5.0 (2018-10-02)
------------------

* added two new methods get_shop_attribute and set_shop_attribute to shop class
* fixed some documentation typos
* fixed some code comments
* updated dev requirements via pyup

0.4.0 (2018-09-10)
------------------

* update zeep to 3.1.0
* added coveralls to testsuite
* ShopAddress attributes to shop class
* update to ShopConfigService12, getAllInfo is now fixed

0.3.0 (2017-12-22)
------------------

* added "shop" class which is a pythonic wrapper over the shopconfigservice

0.2.1 (2017-12-19)
------------------

* fixed AddtionalAttributes and SecondaryDomains
* restructuring

0.2.0 (2017-12-08)
------------------

* First "working" release

0.1.2 through 0.1.7 (2017-12-08)
--------------------------------

* Travis deployment tests

0.1.0 (2017-12-05)
------------------

* First release on PyPI.

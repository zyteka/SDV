.. raw:: html

   <p align="left">
   <img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt="DAI-Lab" />
   <i>An open source project from Data to AI Lab at MIT.</i>
   </p>

|Development Status| |PyPi Shield| |Travis CI Shield| |Coverage Status|
|Downloads| |Binder| |Slack|

SDV - The Synthetic Data Vault
==============================

**Date**: |today| **Version**: |version|

-  License: `MIT <https://github.com/sdv-dev/SDV/blob/master/LICENSE>`__
-  Development Status:
   `Pre-Alpha <https://pypi.org/search/?c=Development+Status+%3A%3A+2+-+Pre-Alpha>`__
-  Documentation: https://sdv-dev.github.io/SDV
-  Homepage: https://github.com/sdv-dev/SDV

Overview
--------

The **Synthetic Data Vault (SDV)** is a **Synthetic Data Generation**
ecosystem of libraries that allows users to easily learn :ref:`single-table
<single_table>`, :ref:`multi-table <relational>` and :ref:`timeseries <timeseries>`
datasets to later on generate new **Synthetic Data** that has the **same format and
statistical properties** as the original dataset.

Synthetic data can then be used to supplement, augment and in some cases
replace real data when training Machine Learning models. Additionally,
it enables the testing of Machine Learning or other data dependent
software systems without the risk of exposure that comes with data
disclosure.

Underneath the hood it uses several probabilistic graphical modeling and
deep learning based techniques. To enable a variety of data storage
structures, we employ unique hierarchical generative modeling and
recursive sampling techniques.

Current functionality and features:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Synthetic data generators for `single tables <single_table>` with the following features:

   -  Using `Copulas <gaussian_copula>` and `Deep Learning <ctgan>` based models.
   -  Handling of multiple data types and missing data with minimum user input.
   -  Support for `pre-defined and custom constraints <constraints>` and data validation.

-  Synthetic data generators for `complex multi-table, relational datasets <relational>`
   with the following features:

   -  Definition of entire `multi-table datasets metadata <relational_metadata>` with a custom
      and flexible `JSON schema <metadata_schema>`.
   -  Using Copulas and recursive modeling techniques.

Coming soon:
~~~~~~~~~~~~

-  Synthetic data generators for **timeseries** with the following
   features:

   -  Using statistical, Autoregressive and Deep Learning models.
   -  Handling context.

Try it out now!
---------------

If you want to quickly discover **SDV**, simply click the button below
and follow the tutorials!

|Binder|

Join our Slack Workspace
------------------------

If you want to be part of the SDV community to receive announcements of the latest releases,
ask questions, suggest new features or participate in the development meetings, please join
our Slack Workspace!

|Slack|

Explore SDV
-----------

* `Getting Started <getting_started/index.html>`_
* `User Guides <user_guides/index.html>`_
* `API Reference <api_reference/index.html>`_
* `Developer Guides <developer_guides/index.html>`_
* `Release Notes <history.html>`_

--------------

.. |Development Status| image:: https://img.shields.io/badge/Development%20Status-2%20--%20Pre--Alpha-yellow
   :target: https://pypi.org/search/?c=Development+Status+%3A%3A+2+-+Pre-Alpha
.. |PyPi Shield| image:: https://img.shields.io/pypi/v/SDV.svg
   :target: https://pypi.python.org/pypi/SDV
.. |Travis CI Shield| image:: https://travis-ci.org/sdv-dev/SDV.svg?branch=master
   :target: https://travis-ci.org/sdv-dev/SDV
.. |Coverage Status| image:: https://codecov.io/gh/sdv-dev/SDV/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/sdv-dev/SDV
.. |Downloads| image:: https://pepy.tech/badge/sdv
   :target: https://pepy.tech/project/sdv
.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/sdv-dev/SDV/master?filepath=tutorials
.. |Slack| image:: https://img.shields.io/badge/Slack%20Workspace-Join%20now!-36C5F0?logo=slack
   :target: https://join.slack.com/t/sdv-space/shared_invite/zt-gdsfcb5w-0QQpFMVoyB2Yd6SRiMplcw


.. toctree::
    :maxdepth: 3
    :hidden:
    :titlesonly:

    getting_started/index
    user_guides/index
    api_reference/index
    developer_guides/index
    Release Notes <history>

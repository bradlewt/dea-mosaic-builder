DEA Mosaic Builder
==================

Introduction
------------

Official documentation to setup and run the **DEA Mosaic builder**. `Github Home`_

The `DEA Analysis Sandbox`_ is a ``Jupyter Lab`` instance maintained and served by `Digital Earth Africa`_. A number of click-to-run jupyter notebooks are available in the ``sandbox`` that are capable of fetching a range of ``Sentinel-1`` satellite data for a single location. For this purpose the sanbox's memory and storage resources are more than sufficient. 

However, the ``sandbox`` memory and storage will fail if entire ``AMD0`` level data needs to be fetched and stored. The Mosaic Builder extends the capabilities of the **DEA Analysis Sandbox** in order to generate and store ``ADM0`` level data while working within the ``sandbox's`` memory and storage limitations.

.. _Github Home: https://github.com/rhinejoel/dea-mosaic-builder/tree/main
.. _DEA Analysis Sandbox: http://sandbox.digitalearth.africa
.. _Digital Earth Africa: https://www.digitalearthafrica.org 

.. toctree::
   :caption: Setup
   :hidden:

   setup/gcs
   setup/local
   setup/sandbox

.. toctree::
   :caption: Run
   :hidden:

   run/genthreshold
   run/genaoicounts
   run/genfloodraster

----

This documentation provides a **step-by-step guide** to setup and run each of these components and in-turn automate the entire process for any ``ADM0`` country in **Africa**.

----

Setup
-----

The first part of this documentation deals with all the necessary steps required to set this automated pipeline up and the second part gives an understanding of how to run the pipeline.

.. image:: _static/index/id-1.png
   :align: center

There are three main components to setup the **Mosaic Builder**:

* **Google Drive API** via ``GCS`` to store the data.
* **Local Processing** to generate ``GCS`` ``credentials`` and merge the files.
* **DEA Analysis Sandbox** to run the application.

Each component requires setup and is covered in this documentation in detail.

Run
---

And as of now, there are three notebooks to run the pipeline.

.. image:: _static/index/id-2.png
   :align: center

* **Generate AOI Thresholds** - ``1. aoi-threshold.ipynb`` Generates a threshold report based on a sample area covering land and water.
* **Calculate Dataset Water Values** - ``2. aoi-cell-count.ipynb`` Generates a table of count of ``wet pixels`` each month for a 12 month period.
* **Generate Raster Data** - ``3. gen-flood-raster.ipynb`` Generates the actual raster data and uploads it to **Google Drive** for the entire ``ADM0`` boundary.
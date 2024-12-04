Local Environment
=================

We need to replicate the Sandbox envireonment locally for two reasons - to generate the GCS credentials which will be used in the sandbox and to create a merged .vrt (virtual) raster file. Create a new project directory and open VS code in that directory. 

.. note:: You are free to use whatever IDE you like. For the purposes of this guide, we will use VS Code. If you do not have VS Code installed, download and install it from `VS Code`_.

.. _VS Code: https://code.visualstudio.com

.. image:: ../_static/lc/lc-1.png
    :align: center

Clone Repository
----------------

Open VS Code terminal and run

.. code::

    git clone https://github.com/rhinejoel/dea-mosaic-builder.git

    cd dea-mosaic-builder

Your VS code Explorer should look like this

.. image:: ../_static/lc/lc-2.png
    :align: center

Create Micromamba Environment
-----------------------------

Micromama is a faster version of conda. If you do not have micromamba installed install it from `Micromamba's Installation Docs`_

.. _Micromamba's Installation Docs: https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html

.. note:: It is recommended to use micromamba. conda/miniconda will still work, but substantially slowly as compared to micromamba. Just switch the command from micromamba to conda to use conda.

From the current folder run

.. important:: Ensure that you are in the dea-mosaic-builder folder or else micromamba/conda will not be able to find the environment.yml file.

.. code:: 

    micromamba create -f environment.yml -y

    micromamba activate dea-env

This will create a new micromamba environment with the name "dea-env". The second command activats the "dea-env" environment

Test Environment 
----------------

.. important:: Ensure that the newly created environment is activated. If it is you should see the name of the environment instead of (base).

Run the deps.py file to test if all dependencies are imported successfully. You should get a message that says "Dependencies Import Successful".

.. image:: ../_static/lc/lc-3.png
    :align: center

Get GDrive Creds
----------------

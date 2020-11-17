CPBlob
======

To use this, first set the ``AZURE_CONNECTION_STRING`` environment
variable to something valid. Then, to download::

  cpblob container:remotepath localpath

Or to upload::

  cpblob [-f] localpath container:remotepath

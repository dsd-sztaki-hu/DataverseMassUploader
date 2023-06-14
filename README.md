# DataverseMassUploader

This is a Python script to mass-upload files and directories to Harvard dataverse (dataverse.org) 
repositories. It is based on the pyDataverse library.

# Installation

## Prerequisites

* python3
* python3-pip
* curl (optional)
* pyDataverse

## Installation instructions

[Detailed installation instructions are available for several platforms in INSTALL.md](INSTALL.md)

# Example

    ## Show help for command line options
    python3 uploadFilesToExistingDataset.py --help
    
    ## Upload README.md to dataverse.org into a dataset with PID "hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID"
    python3 uploadFilesToExistingDataset.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE README.md
    
    ## Upload all files from current directory and all files from subdirectories 1 level deep
    python3 uploadFilesToExistingDataset.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE * */*

    ## Download all files from a dataset
    python3 downloadDatasetFiles.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE

# Further configuration

## enviroment variables

* DataverseMassUploaderCurlUseThreshold: The threshold in bytes over which curl is used. 2^25 by default, as python upload uses filesize*3 RAM.
* DataverseApiKey: You can define the API key/token in this environment variable.
* DataverseMassUploaderMaximumRetryCount: In case of an upload failure, the program retries the upload after some waiting. This specifies the maximum retry count.
* DataverseMassUploaderMaximumWaitBetweenRetries: In case of an upload failure, the program waits between uploads in exponential increments. This sets the upper limit in seconds.

# Issues


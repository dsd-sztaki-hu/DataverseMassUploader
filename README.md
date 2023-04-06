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

# Issues


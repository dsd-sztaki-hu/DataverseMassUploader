# DataverseMassUploader
Scripts to mass-upload files and directories to Harvard dataverse (dataverse.org) repositories, using pyDataverse

# Prerequisites

* install python3
* install python3-pip
* install curl (optional)
* install pyDataverse
  * `pip3 install pydataverse`

# Example

    ## Show help for command line options
    python3 uploadFilesToExistingDataset.py --help
    
    ## Upload README.md to dataverse.org into a dataset with PID "hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID"
    python3 uploadFilesToExistingDataset.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE README.md
    
    ## Upload all files from current directory and all files from subdirectories 1 level deep
    python3 uploadFilesToExistingDataset.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE * */*

# Issues

* Directory names are not included in uploaded file names
  * All will be uploaded into the root directory of the dataset
  * Directory structure is not preserved

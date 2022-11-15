# DataverseMassUploader
Scripts to mass-upload files and directories to Harvard dataverse (dataverse.org) repositories, using pyDataverse

# Prerequisites

* install python3
* install pyDataverse
  * `pip3 install pydataverse`

# Example

    python3 uploadFilesToExistingDataset.py --help
    python3 uploadFilesToExistingDataset.py -u https://dataverse.org -d hdl:HANDLEID/EXAMPLE_SHOULDER/EXAMPLE_ID -k API-KEY-HERE README.md

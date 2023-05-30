# DataverseMassUploader Installation instructions

## Installing prerequisites

### Debian / Ubuntu Linux

    apt install python3 python3-pip curl
    # after cloning the repository, go there and run
    pip3 install -r requirements.txt

### Synology DSM

* add SynoCommunity to package sources:
  * package manager -> settings -> package sources -> add
  * name: SynoCommunity
  * location: https://packages.synocommunity.com/
* install prerequisites in the package manager
  * python3
  * git
* install pip using the command line (log in using ssh)
```
python3 -m ensurepip
python3 -m pip install --upgrade pip
# after cloning the repository, go there and run
python3 -m pip install -r requirements.txt
```

## Download DataverseMassUploader using git

    git clone https://github.com/dsd-sztaki-hu/DataverseMassUploader


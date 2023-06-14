#!/usr/bin/python3

import os
import json
import time
import shutil
import argparse
import subprocess
from pyDataverse.api import NativeApi, DataAccessApi, SearchApi
from pyDataverse.models import Dataverse, Dataset
from var_dump import var_dump

argparser = argparse.ArgumentParser(description ='Download files from existing dataset', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', required=True,
                       help='dataset pid to download from')
argparser.add_argument('-u', '--dataverseBaseUrl', dest ='baseUrl', required=True,
                       help='dataverse base URL')
argparser.add_argument('-k', '--apiKey', dest ='apiKey', default=os.environ.get('DataverseApiKey'),
                       help='Dataverse API key/token; you can also specify the DataverseApiKey environment variable instead.')
argparser.add_argument('-o', '--overwrite-existing', dest='overwrite', action=argparse.BooleanOptionalAction, default=False,
                       help='overwrite existing files')
#argparser.add_argument("filePattern", nargs='*', help='the name of the file(s) to download')
args = argparser.parse_args()
#var_dump(args)

curlAvailable=subprocess.run(["curl --version"], shell=True, capture_output=True).returncode == 0

if not args.apiKey:
	print("ERROR: API key/token must be defined either on the command line or in an environment variable.")
	exit(argparser.print_usage())
api = NativeApi(args.baseUrl,args.apiKey)
data_api = DataAccessApi(args.baseUrl)

dataset = api.get_dataset(args.dataset)

def downloadFile(file_id,filename):
	response = data_api.get_datafile(file_id)
	with open(filename, "wb") as f:
		f.write(response.content)

def downloadFileCurl(file_id,filename):
#	print("Size of %s is too big (%d bytes), downloading with curl."%(filename,filesize))
	response=subprocess.run(
			'curl -H "X-Dataverse-key:%s" -o "%s" "%s/api/access/datafile/%s"'%(
				args.apiKey,filename,args.baseUrl,file_id),
			shell=True, capture_output=True)
	if response.returncode != 0:
		print("Error downloading %s"%filename)
		print("  Response message was: '%s'"%response.stdout)
	else:
		print("Successful download: %s"%filename)

files_list = dataset.json()['data']['latestVersion']['files']
for file in files_list:
	filename = file["dataFile"]["filename"]
	file_id = file["dataFile"]["id"]
	file_size = file["dataFile"]["filesize"]
#	var_dump(file)
	print("File name {}, id {}, size {}".format(filename, file_id, file_size))
	try:
		filestat = os.stat(filename)
		if filestat.st_size<file_size:
			if args.overwrite:
				print("File with same name exists, but file on disk smaller. Re-downloading.")
			else:
				print("File with same name exists, but file on disk smaller and overwrite disabled. Skipping.")
				continue
		elif filestat.st_size>file_size:
			print("File with same name exists, but file on disk bigger. Skipping.")
			continue
		else:
			print("File with same name and size exists, skipping")
			continue
	except Exception as e:
#		print(e)
		pass
	
	if file_size>2**3:
		downloadFileCurl(file_id,filename)
	else:
		downloadFile(file_id,filename)


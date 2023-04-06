#!/usr/bin/python3

import os
import json
import time
import shutil
import argparse
import subprocess
from pyDataverse.api import NativeApi, DataAccessApi, SearchApi
from pyDataverse.models import Dataverse, Dataset
#from var_dump import var_dump

argparser = argparse.ArgumentParser(description ='Mass upload files to existing dataset', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', help='dataset pid to upload to')
argparser.add_argument('-u', '--dataverseBaseUrl', dest ='baseUrl', help='dataverse base URL to upload to')
argparser.add_argument('-k', '--apiKey', dest ='apiKey', help='dataverse API key/token')
argparser.add_argument("infile", nargs='+', help='the name of the file(s) to upload')
args = argparser.parse_args()

#var_dump(args)

curlAvailable=subprocess.run(["curl --version"], shell=True, capture_output=True).returncode == 0

def uploadWithCurl(filename,fileMetadata):
	print("Size of %s is too big (%d bytes), uploading with curl."%(filename,filesize))
	response=subprocess.run(
			'curl -H "X-Dataverse-key:%s" -X POST -F "file=@%s" -F "jsonData=%s" "%s/api/datasets/:persistentId/add?persistentId=%s"'%(
				args.apiKey,filename,fileMetadata,args.baseUrl,args.dataset),
			shell=True, capture_output=True)
	if response.returncode != 0:
		print("Error uploading %s"%filename)
		print("  Response message was: '%s'"%response.stdout)
	else:
		print("Successful upload: %s"%filename)

def upload(filename,fileMetadata):
		response=api.upload_datafile(args.dataset, filename, json_str=fileMetadata, is_pid=True)
		if response.status_code!=200:
			print("Error uploading %s"%filename)
			print("  Response message was: '%s'"%response._content)
#			var_dump(response)
		else:
			print("Successful upload: %s"%filename)


api = NativeApi(args.baseUrl,args.apiKey)
for filename in args.infile:
	filesize=os.lstat(filename).st_size
	fileMetadata=json.dumps({"filename": filename, "directoryLabel": os.path.dirname(filename)})
	#print("File size: %d"%filesize)
	if filesize>=2**31:
		if(not curlAvailable):
			print("ERROR: Not uploading %s: size is too big (%d bytes), but curl is unavailable."%(filename,filesize))
			continue
		uploadWithCurl(filename,fileMetadata)
	else:
		upload(filename,fileMetadata)

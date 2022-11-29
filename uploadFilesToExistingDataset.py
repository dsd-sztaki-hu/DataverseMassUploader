#!/usr/bin/python3

import os
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

def isCurlAvailable():
	return subprocess.run(["curl --version"], shell=True, capture_output=True).returncode == 0

api = NativeApi(args.baseUrl,args.apiKey)
for filename in args.infile:
	#print("File size: %d"%os.lstat(filename).st_size)
	filesize=os.lstat(filename).st_size
	if filesize>=2**31:
		if(not isCurlAvailable()):
			print("ERROR: Not uploading %s: size is too big (%d bytes), but curl is unavailable."%(filename,filesize))
			continue
		print("Size of %s is too big (%d bytes), uploading with curl."%(filename,filesize))
		response=subprocess.run('curl -H "X-Dataverse-key:%s" -X POST -F "file=@%s" -F "jsonData={}" "%s/api/datasets/:persistentId/add?persistentId=%s"'%(
				args.apiKey,filename,args.baseUrl,args.dataset), shell=True, capture_output=True)
		if response.returncode != 0:
			print("Error uploading %s"%filename)
			print("  Response message was: '%s'"%response.stdout)
		else:
			print("Successful upload: %s"%filename)
	else:
		response=api.upload_datafile(args.dataset, filename, json_str=None, is_pid=True)
		if response.status_code!=200:
			print("Error uploading %s"%filename)
			print("  Response message was: '%s'"%response._content)
#			var_dump(response)
		else:
			print("Successful upload: %s"%filename)

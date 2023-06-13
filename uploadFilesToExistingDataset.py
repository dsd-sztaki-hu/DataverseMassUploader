#!/usr/bin/python3

import os
import json
import time
import shutil
import argparse
import subprocess
from functools import partial
from pyDataverse.api import NativeApi, DataAccessApi, SearchApi
from pyDataverse.models import Dataverse, Dataset
from var_dump import var_dump

_csv = partial(str.split, sep=',')

argparser = argparse.ArgumentParser(description ='Mass upload files to existing dataset', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', help='dataset pid to upload to')
argparser.add_argument('-u', '--dataverseBaseUrl', dest ='baseUrl', help='dataverse base URL to upload to')
argparser.add_argument('-k', '--apiKey', dest ='apiKey', help='dataverse API key/token')
argparser.add_argument('-v', '--verbose', dest ='verbosity', action='count', help='verbosity level', default=0)
argparser.add_argument('--description', dest ='description', help='file description to set for all files')
argparser.add_argument('--tags', dest ='tags', type=_csv, help='Comma delimited list of file tags (aka categories) to set for all files. Allowed values are usually: Documentation, Data, Code; however, custom tags are usually allowed')
#argparser.add_argument('--tabularTags', dest ='tabularTags', type=_csv, help='Comma delimited list of tabular file tags to set for all files. Allowed values are usually: Geospatial, Time Series, Event, Network, Panel, Genomics, Survey')
argparser.add_argument("infile", nargs='+', help='the name of the file(s) to upload')
args = argparser.parse_args()

#var_dump(args)

curlAvailable=subprocess.run(["curl --version"], shell=True, capture_output=True).returncode == 0
curlUseThreashold=int(os.environ.get('DataverseMassUploaderCurlUseThreshold', 2**25))
api = NativeApi(args.baseUrl,args.apiKey)

def vp(level: int, str1: str, obj=None):
	if args.verbosity >= level:
		print(str1)
		if obj!=None:
			var_dump(obj)

def uploadWithCurl(filename,fileMetadata):
	print("Size of %s is too big (%d bytes), uploading with curl."%(filename,filesize))
	command='curl -f -H "X-Dataverse-key:%s" -X POST -F "file=@%s" -F \'jsonData=%s\' "%s/api/datasets/:persistentId/add?persistentId=%s"'%(
				args.apiKey,filename,fileMetadata,args.baseUrl,args.dataset)
	vp(1,"runnning command:\n"+command)
	response=subprocess.run(command,shell=True, capture_output=True)
	vp(1,"response:",response)
	if response.returncode != 0:
		print("Error uploading %s"%filename)
		print("  Response message was: '%s'"%response.stdout)
	else:
		print("Successful upload: %s"%filename)
		vp(1,"  Response message was: '%s'"%response.stdout)

def upload(filename,fileMetadata):
	response=api.upload_datafile(args.dataset, filename, json_str=fileMetadata, is_pid=True)
	if response.status_code!=200:
		print("Error uploading %s"%filename)
		print("  Response message was: '%s'"%response._content)
		vp(2,"",response)
	else:
		print("Successful upload: %s"%filename)
		vp(1,"  Response message was: '%s'"%response._content)


for filename in args.infile:
	time.sleep(0.1) # there seems to be a bug in dataverse if files are uploaded to the same dataverse too rapidly. A 0.1s delay seems to fix it -- mostly...
	filesize=os.lstat(filename).st_size
	directoryLabel=os.path.dirname(filename)
	fileMetadata={"filename": filename}
	if directoryLabel: fileMetadata["directoryLabel"]=directoryLabel
	if args.description: fileMetadata["description"]=args.description
	if args.tags: fileMetadata["categories"]=args.tags
#	if args.tabularTags: fileMetadata["tabularTags"]=args.tabularTags
	fileMetadata=json.dumps(fileMetadata)
	vp(1,"File size: %d"%filesize)
	if filesize>=curlUseThreashold:
		if(not curlAvailable):
			print("ERROR: Not uploading %s: size is too big (%d bytes), but curl is unavailable."%(filename,filesize))
			continue
		uploadWithCurl(filename,fileMetadata)
	else:
		upload(filename,fileMetadata)

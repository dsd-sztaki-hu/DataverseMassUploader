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

##### ARGUMENT PARSING BEGIN #####

_csv = partial(str.split, sep=',') # partial function needed for parsing csv-typed arguments

argparser = argparse.ArgumentParser(description ='Mass upload files to existing dataset in a Harvard Dataverse.', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', required=True,
                       help='Dataset pid to upload to.')
argparser.add_argument('-u', '--dataverseBaseUrl', dest ='baseUrl', required=True,
                       help='Dataverse base URL to upload to.')
argparser.add_argument('-k', '--apiKey', dest ='apiKey', default=os.environ.get('DataverseApiKey'),
                       help='Dataverse API key/token; you can also specify the DataverseApiKey environment variable instead.')
argparser.add_argument('-v', '--verbose', dest ='verbosity', action='count', default=0,
                       help='Verbosity level.')
argparser.add_argument('--description', dest ='description',
                       help='File description to set for all files.')
argparser.add_argument('--tags', dest ='tags', type=_csv,
                       help='Comma delimited list of file tags (aka categories) to set for all files. Allowed values are usually: Documentation, Data, Code; however, custom tags are usually allowed')
# It seems that tabular tags cannot be currently uploaded through the API. Until this is fixed, I disabled this feature.
#argparser.add_argument('--tabularTags', dest ='tabularTags', type=_csv,
#                       help='Comma delimited list of tabular file tags to set for all files. Allowed values are usually: Geospatial, Time Series, Event, Network, Panel, Genomics, Survey')
argparser.add_argument("infile", nargs='+',
                       help='The name(s) of the file(s) to upload, with path. Relative path is preferable, as path in the command line will be stored in Dataverse as file path.')
args = argparser.parse_args()

##### ARGUMENT PARSING END #####


##### INITIALIZATION BEGIN #####

curlAvailable=subprocess.run(["curl --version"], shell=True, capture_output=True).returncode == 0
curlUseThreashold=int(os.environ.get('DataverseMassUploaderCurlUseThreshold', 2**25))
maximumRetryCount=int(os.environ.get('DataverseMassUploaderMaximumRetryCount', 10))
maximumWaitBetweenRetries=int(os.environ.get('DataverseMassUploaderMaximumWaitBetweenRetries', 60))
uploadedFiles=0
errorFiles=0
totalErrors=0
if not args.apiKey:
	print("ERROR: API key/token must be defined either on the command line or in an environment variable.")
	exit(argparser.print_usage())
api = NativeApi(args.baseUrl,args.apiKey)

##### INITIALIZATION END #####


##### HELPER FUNCTIONS BEGIN #####

def vp(level: int, str1: str, obj=None):
	if args.verbosity >= level:
		print(str1)
		if obj!=None:
			var_dump(obj)

def printProgress():
#	if args.verbosity==0
#	print('.', end = "")
	print("Files uploaded: %d      Files failed to upload: %d       Total errors: %d"%(uploadedFiles,errorFiles,totalErrors), end='\r', flush=True)

def success(filename, response):
	global uploadedFiles
	vp(1,"Successful upload: %s"%filename)
	vp(2,"  Response message was: '%s'"%response)
	uploadedFiles+=1

def error(filename,responseString,response):
	global totalErrors
	print("\nError uploading %s"%filename)
	print("  Response message was: '%s'"%responseString)
	vp(3,"",response)
	totalErrors+=1
	raise RuntimeError()

def uploadWithCurl(filename,fileMetadata):
	vp(1,"Size of %s is too big (%d bytes), uploading with curl."%(filename,filesize))
	command='curl -f -H "X-Dataverse-key:%s" -X POST -F "file=@%s" -F \'jsonData=%s\' "%s/api/datasets/:persistentId/add?persistentId=%s"'%(
				args.apiKey,filename,fileMetadata,args.baseUrl,args.dataset)
	vp(2,"runnning command:\n"+command)
	response=subprocess.run(command,shell=True, capture_output=True)
	vp(2,"response:",response)
	if response.returncode != 0:
		error(filename,response.stdout,response)
	else:
		success(filename, response.stdout)
	printProgress()

def uploadWithPyDataverse(filename,fileMetadata):
	response=api.upload_datafile(args.dataset, filename, json_str=fileMetadata, is_pid=True)
	if response.status_code!=200:
		error(filename,response._content,response)
	else:
		success(filename, response._content)
	printProgress()

def upload(filesize,filename,fileMetadata):
	if filesize>=curlUseThreashold:
		if(not curlAvailable):
			raise NotImplementedError("ERROR: Not uploading %s: size is too big (%d bytes), but curl is unavailable."%(filename,filesize))
		uploadWithCurl(filename,fileMetadata)
	else:
		uploadWithPyDataverse(filename,fileMetadata)

##### HELPER FUNCTIONS END #####


##### MAIN LOOP FOR PROCESSING FILE UPLOADS BEGIN #####

for filename in args.infile:
	if totalErrors > 0: time.sleep(0.1) # there seems to be a bug in dataverse if files are uploaded to the same dataverse too rapidly. A 0.1s delay seems to fix it -- mostly... We will only wait here if there was a previous error.
	filesize=os.lstat(filename).st_size
	directoryLabel=os.path.dirname(filename)
	fileMetadata={"filename": filename}
	if directoryLabel: fileMetadata["directoryLabel"]=directoryLabel
	if args.description: fileMetadata["description"]=args.description
	if args.tags: fileMetadata["categories"]=args.tags
#	if args.tabularTags: fileMetadata["tabularTags"]=args.tabularTags ## disabled until this is fixed in Dataverse
	fileMetadata=json.dumps(fileMetadata)
	vp(1,"File size: %d"%filesize)
	currentUploadErrors=0
	uploadSuccess=False
	while not uploadSuccess:
		try:
			upload(filesize,filename,fileMetadata)
			uploadSuccess=True
		except NotImplementedError as e:
			print(e)
			continue
		except RuntimeError as e:
			currentUploadErrors+=1
			if currentUploadErrors>maximumRetryCount:
				errorFiles+=1
				break
			retryDelay=min(2**(currentUploadErrors-1),maximumWaitBetweenRetries)
			print("Retrying upload of %s after waiting %d seconds."%(filename,retryDelay))
			time.sleep(retryDelay)

##### MAIN LOOP FOR PROCESSING FILE UPLOADS END #####

print() # normal progress indicator needs a newline at the end

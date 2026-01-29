#!/usr/bin/python3

import os
import json
import time
import shutil
import argparse
import subprocess
import re
import requests
from pyDataverse.api import NativeApi, DataAccessApi, SearchApi
from pyDataverse.models import Dataverse, Dataset
from var_dump import var_dump

argparser = argparse.ArgumentParser(description ='Download files from existing dataset', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', required=False,
                       help='dataset pid or private URL or private URL token to download from')
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
#	print("ERROR: API key/token must be defined either on the command line or in an environment variable.")
#	exit(argparser.print_usage())
	api = NativeApi(args.baseUrl)
	data_api = DataAccessApi(args.baseUrl)
else:
	api = NativeApi(args.baseUrl,args.apiKey)
	data_api = DataAccessApi(args.baseUrl)

####### HELPERS #######
def downloadFile(file_id,filename):
	response = data_api.get_datafile(file_id)
	with open(filename, "wb") as f:
		f.write(response.content)

def downloadFileCurl(file_id,filename):
	#print("Size of %s is too big (%d bytes), downloading with curl."%(filename,filesize))
	if args.apiKey:
		api_key_param=f'-H "X-Dataverse-key:{args.apiKey}"'
	else:
		api_key_param=''
	if cookie:
		cookie_param=f'-b "{cookie}"'
	else:
		cookie_param=''
	#print('curl %s %s -o "%s" "%s/api/access/datafile/%s"'%(
	#			api_key_param,cookie_param,filename,args.baseUrl,file_id))
	response=subprocess.run(
			'curl --fail --silent --show-error %s %s -o "%s" "%s/api/access/datafile/%s"'%(
				api_key_param,cookie_param,filename,args.baseUrl,file_id),
			shell=True, capture_output=True)
	if response.returncode != 0:
		print("Error downloading %s"%filename)
		print("  Response message was: '%s'"%(response.stdout+response.stderr))
	else:
		print("Successful download: %s"%filename)
####### END HELPERS #######

# Detecting whether the dataset designation is is a private/preview access token
if re.match(r".*/privateurl.xhtml\?token=",args.dataset):
	token=re.sub(r".*token=","",args.dataset)
elif re.match(r".*/privateUrlDatasetVersion/",args.dataset):
	token=re.sub(r".*/privateUrlDatasetVersion/","",args.dataset)
elif not re.match(r".*:",args.dataset) and re.match(r"[a-z0-9-]{36}$",args.dataset):
	token=args.dataset
else:
	token=None

if token:
	set_cookie_header = requests.get(f"https://repo.researchdata.hu/privateurl.xhtml?token={token}", allow_redirects=False).raw.headers._container["set-cookie"][1]
	cookie=re.sub(r"; .*","",set_cookie_header)
	dataset = api.get_request(f"{args.baseUrl}/api/datasets/privateUrlDatasetVersion/{token}")
	files_list = dataset.json()['data']['files']
else:
	dataset = api.get_dataset(args.dataset)
	files_list = dataset.json()['data']['latestVersion']['files']

for file in files_list:
	filename = file["dataFile"]["filename"]
	file_id = file["dataFile"]["id"]
	file_size = file["dataFile"]["filesize"]
	#var_dump(file)
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
		#print(e)
		pass
	
	if file_size>2**20 or cookie:
		downloadFileCurl(file_id,filename)
	else:
		downloadFile(file_id,filename)

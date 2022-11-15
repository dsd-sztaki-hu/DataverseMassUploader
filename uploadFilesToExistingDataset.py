#!/usr/bin/python3

import time
import shutil
import argparse
from pyDataverse.api import NativeApi, DataAccessApi, SearchApi
from pyDataverse.models import Dataverse, Dataset
#from var_dump import var_dump

argparser = argparse.ArgumentParser(description ='Mass upload files to existing dataset', argument_default=[])
argparser.add_argument('-d', '--dataset', dest ='dataset', help='dataset pid to upload to')
argparser.add_argument('-u', '--dataverseBaseUrl', dest ='baseUrl', help='dataverse base URL to upload to')
argparser.add_argument('-k', '--apiKey', dest ='apiKey', help='dataverse API key')
argparser.add_argument("infile", nargs='+', help='the name of the file(s) to upload')
args = argparser.parse_args()

#var_dump(args)

api = NativeApi(args.baseUrl,args.apiKey)
for filename in args.infile:
	response=api.upload_datafile(args.dataset, filename, json_str=None, is_pid=True)
	if response.status_code!=200:
		print("Error uploading %s"%filename)
		print("  Response message was: '%s'"%response._content)
#		var_dump(response)
	else:
		print("Successful upload: %s"%filename)

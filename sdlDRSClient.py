import json
import requests
import os

from DRSClient import DRSClient

class sdlDRSClient(DRSClient):

	def __init__(self, ngc_file):
		self.api_url_base = 'https://locate.ncbi.nlm.nih.gov/sdl/2/'
		self.headers = {'Content-Type': 'application/json'}
		self.ngc_file_path = os.path.expanduser(ngc_file)

	def sdl_locality(self, accession, fileType=None):

	#    api_url = '{0}locality?acc={1}&filetype={2}'.format(self.api_url_base, accession, fileType)
		api_url = '{0}locality?acc={1}'.format(self.api_url_base, accession)
		if fileType:
			api_url += '&filetype=' + fileType
		#print (api_url)   
		response = requests.get(api_url, headers=self.headers)

		if response.status_code == 200:
			return json.loads(response.content.decode('utf-8'))
		else:
			return None
		
	def sdl_retrieve(self, accession, location, fileType=None):
	
		jwt_req_headers = {'Metadata-Flavor': 'Google'} 
		jwt_req_url ='http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://www.ncbi.nlm.nih.gov&amp;format=full'
		jwt_response = requests.post(jwt_req_url, headers=jwt_req_headers)
		jwt = jwt_response.text
		print('--- jwt token response ---')
		print(jwt)
		print('--------------------------')
	
	#    locationType = 'gcp_jwt'
	#    api_url = '{0}retrieve?acc={1}&location={2}&filetype={3}'.format(self.api_url_base, accession, location, fileType)
		location = jwt
		#api_url = '{0}retrieve?acc={1}&location={2}'.format(self.api_url_base, accession, location)
		api_url = '{0}retrieve?acc={1}&location-type=gcp_jwt&location={2}'.format(self.api_url_base, accession, jwt)
		print('url for retrieve: {}'.format(api_url))
		files = {'ngc': open(self.ngc_file_path, 'rb')}
		response = requests.post(api_url, files=files)
		if response.status_code == 200:
			return json.loads(response.content.decode('utf-8'))
		else:
			return None
			
    # Get info about a DrsObject
    # See https://ga4gh.github.io/data-repository-service-schemas/preview/develop/docs/#_getobject
	def getObject(self, object_id):		
		p = object_id.split('.')
		accession = p[0]
		fileext = p[-1]
		locality_info = self.sdl_locality(accession,fileext)
		#print(json.dumps(locality_info, indent=2))

		sdlresp = locality_info[0]
		#print (sdlresp['accession'])
		fileList = sdlresp['files']
		for file in fileList:
	#		if file['name'].endswith(fileext):
			if file['type'] == fileext:
				#print(file['name'])
				access_methods = []
				for loc in file['locality']:
					if not loc["service"].endswith("ncbi"):
						am = {"type":loc["service"],"region":loc["region"],"access_id":loc["service"]+"."+loc["region"]}
						access_methods.append(am)
			
				drsdict = {"id": file['object'],"name": file['name'],"size": file['size'],"access_methods":access_methods}	
				return (drsdict)

    # Get a URL for fetching bytes. 
    # See https://ga4gh.github.io/data-repository-service-schemas/preview/develop/docs/#_getaccessurl
	def getAccessURL(self, object_id, access_id):
		p = object_id.split('.')
		accession = p[0]
		fileext = p[-1]
		retrieve_info = self.sdl_retrieve(accession, access_id, fileext)
		print(json.dumps(retrieve_info, indent=2))
	
		am_parts = access_id.split('.')
		service = am_parts[0]
		region = am_parts[1]

		sdlresp = retrieve_info['result'][0]
		fileList = sdlresp['files']
		for file in fileList:
			if file['type'] == fileext:
				for loc in file['locations']:
					if loc["region"].endswith(region):
						drsdict = {"url": loc['link']}
						return (drsdict)


if __name__ == "__main__":
# 	client1 = sdlDRSClient('~/.keys/prj_14565.ngc')
# 	res = client1.getObject('SRR1999478.bam')
# 	print('--Get Info--')
# 	print (res)
# 	print('--Get a URL--')
# 	res = client1.getAccessURL('SRR1999478.bam','gs.us')
# 	print (res)
# 	print ('-----------------')
	client2 = sdlDRSClient('~/.keys/prj_11218_D17199.ngc')
# 	res = client2.getObject('SRR1999478.bam')
# 	print('--Get Info--')
# 	print (res)
# 	print('--Get a URL--')
# 	res = client2.getAccessURL('SRR1999478.bam','gs.us')
# 	print (res)
	res = client2.getObject('SRR5368359.bam')
	print('--Get Info--')
	print (res)
	print('--Get a URL--')
	res = client2.getAccessURL('SRR5368359.bam','gs.us')
	print (res)




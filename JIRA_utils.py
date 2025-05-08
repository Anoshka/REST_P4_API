import requests
from requests.auth import HTTPBasicAuth as http_auth
import json

class Jira:
	def __init__(self, email, project="SSC", api_key="t02sR2UCyz1g4TcXREf69135", link=""):
		"""
		initializes Jira object, sets up vars for auth 

		params:
			email (str): users email address
			project (str): 
			api_key (str): Jira API key, set in web app
   			link (str): atlassian link, such as https://www.companyname.atlassian.net 
		returns:
			None
		"""

		email = email
		api_key = api_key

		self.project = project
		self.auth = http_auth(email, api_key)


		return


	def query_call(self, url_ext, query=None):
		"""
		Makes REST query call to JIRA

		params:
			url_ext (str): the URL extension for desired webhook
			query (dict): the query information for call, not all functions require, None by default
		returns:
			results from REST call

		"""

		url = "{}/rest/api/{}".format(link, url_ext)

		headers = {
			"Accept":"application/json" 
		}

		if query:
			#makes REST request if valid query submitted in args
			query_data = query

			response = requests.request(
				"GET",
				url,
				headers=headers,
				params=query,
				auth=self.auth
				)
		else:
			#makes REST request w/o query
			response = requests.request(
				"GET",
				url,
				headers=headers,
				auth=self.auth
				)


		result = json.dumps(
							json.loads(response.text), 
							sort_keys=True, 
							indent=4, 
							separators=(",", ": "))
		return result


	def get_users(self):
		"""
		Gets user data from Jira
		"""

		url_ext = "2/users/search"

		user_data = self.query_call(url_ext)

		return user_data


	def get_issues(self):
		"""
		Gets ALL active issues for Jira 
		"""

		url_ext = "3/search"

		query_info = {
				"jql":"project = {}".format(self.project)
			}

		str_data = self.query_call(url_ext, query_info)
		#loads JSON string into dict and retuns issues
		data = json.loads(str_data)
		issues = data["issues"]

		return issues


	def user_info(self, active = True, account_type = "atlassian"):

		""" parses user data and returns relevant user data for all active users 
		"""
		data = json.loads(self.get_users())



		self.user_data = []
		self.user_name = []
		self.links = []

		for info in data:

			if not info["accountType"] == account_type:
				continue
			if not info["active"] == active:
				continue  
				
			self.new_dict = {"Name" : info["displayName"],
			"accountId": info["accountId"], 
			"link": info["self"],
			"email": info["emailAddress"]
			}

			self.user_data.append(self.new_dict)


		return self.user_data


	def open_issues(self, user_name = None, email = None):
		"""looks at all open issues and returns relevant information
		params:
			user_name(None/str): optional - if given, returns all open issues 
								 specified user. If not, returns all open issues
		returns:
			a list of dictionaries that contain all open issues and thei info
		"""
		#grabs all open issues and data
		all_items = self.get_issues()

		#this list will store the relevant data
		parsed_issues = []

		if email != None:
			if user_name == None:
				user_name = self.get_user_name(email = email)
		
		#looks at each dictionary 
		for item in all_items:
			#gets issue key, e.g. SSC-145 
			issue = item['key']
			#gets all assignee info
			field = item['fields']['assignee']
			#creates link to issue		
			link = "{}/browse/".format(link) + issue
			#gets issue title
			description = item['fields']['summary']
			#gets priority e.g. highest
			priority = item['fields']['priority']['name']
			#gets current progress e.g. Pending Approval
			status = item['fields']['status']['statusCategory']['name']
			#If field not nonetype, gets the asignee name and appends dict
			if field != None:
				name = field['displayName']
				#checks if user_name param exists and gives specified users data
				if user_name == name:				
					new_dict = {"issue": issue,
								"description": description,
								"priority": priority, 
								"status": status,
								"link": link
								}
					parsed_issues.append(new_dict)
				#if user_name not specified, returns all open issues with usernames
				if user_name == None: 
					new_dict = {"name": name,
								"issue": issue,
								"description": description,
								"priority": priority, 
								"status": status,
								"link": link
								}
					parsed_issues.append(new_dict)
				

		return parsed_issues


	def get_user_name(self, email = None):
		"""takes email Id and returns name associated with it
			params:
				email(str): input user email, egs. anoshka@shaperrigs.com
			returns:
				name: egs. Anoshka Jhaveri
		"""
		if email != None:

			url_ext = "3/groupuserpicker?query=\"{}\"".format(email)
			json_user_data = self.query_call(url_ext)
			user_data = json.loads(json_user_data)
			name = user_data['users']['users'][0]['displayName']
					
		return name

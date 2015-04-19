from django.shortcuts import render
from django.http import HttpResponse
from workday.models import Message, User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

import random
import string
import os
import requests
import json

API_KEY = 'AIzaSyCesfY_AqPlNZMqLq18BsQCMM7wZTHmkpo'
GCM_URL = 'https://android.googleapis.com/gcm/send'
# this should be set in STATICFILES_DIRS variable in settings.py
PICTURES_ROOT = '/var/www/workday_pictures'
PICTURES_DOMAIN = 'http://linode.foamsnet.com:8000/static/'

def rand_filename(length = 8, suffix = ''):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    fname = os.path.join(PICTURES_ROOT, ''.join(random.sample(chars, length)) + suffix)
    print fname
    return fname if not os.path.exists(fname) else rand_filename(length)

# Create your views here.
@csrf_exempt
def message(request):
	if request.method == 'GET':
		sender = request.GET.get('sender')
		receiver = request.GET.get('receiver')
		message = request.GET.get('message')
	elif request.method == 'POST':
		data = json.loads(request.body)
		sender = data.get('sender', '')
		receiver = data.get('receiver', '')
		message = data.get('message', '')
	return send_message(sender, receiver, message)

def send_message(sender, receiver, message):
	# store in DB.
	msg = Message(sender=sender, receiver=receiver , msg=message)
	msg.save()

	# get the user
	user = User.objects.get(username = receiver)
	print user
	if user:
		# send to GCM
		headers = {
			"Content-Type" : "application/json",
			"Authorization" : "key=%s" % API_KEY
		}
		data = {
			"registration_ids" : [user.gcmId],
			"data" : {
				"sender" : sender,
				"message" : message
			}
		}
		resp = requests.post(GCM_URL, headers = headers, data = json.dumps(data))
		print resp.text

	# return
	response_data = {}
	response_data["status_message"] = "success"
	response_data["status_code"] = "200"

	response =  HttpResponse(json.dumps(response_data), content_type="application/json")
	return response

def get_message(request):
	receiver = request.GET.get('receiver')
	response = []

	db_response = Message.objects.filter(receiver=receiver)
	for db_msg in db_response:
			response_data = {}
			response_data['sender'] = db_msg.sender
			response_data['receiver'] = db_msg.receiver
			response_data['message'] = db_msg.msg
			response.append(response_data)

	print response
	response =  HttpResponse(json.dumps(response), content_type="application/json")
	return response

@csrf_exempt
def register(request):
	username = request.GET.get('username')
	password = request.GET.get('password')

	# request_body has the profile picture in png format
	profile_picture = rand_filename(length = 10, suffix = '.png')
	f = open(profile_picture, 'wb')
	f.write(request.body)
	f.close()
	print username +" :: " + password + " :: " + profile_picture
	new_user = User(username=username, password=password, picture = os.path.basename(profile_picture))
	new_user.save()

	response_data = {}
	response_data["status_message"] = "success"
	response_data["status_code"] = "200"

	response =  HttpResponse(json.dumps(response_data), content_type="application/json")
	print response
	return response

@csrf_exempt
def login(request):
	username = request.GET.get('username')
	password = request.GET.get('password')
	user = len(User.objects.filter(username = username, password = password))

	response_data = {}
	response_data["status_message"] = "success" if user else "failure"
	response_data["status_code"] = "200" if user else "-1"

	response =  HttpResponse(json.dumps(response_data), content_type="application/json")
	print response
	return response

@csrf_exempt
def gcm(request):
	response_data = {}
	if request.GET.get('action') == "register":
		data = json.loads(request.body)
		username = data.get('username','')
		gcmId = data.get('gcmId','')
		user = User.objects.get(username = username)
		if user:
			user.gcmId = gcmId
			user.save()
			response_data["status_message"] = "success"
			response_data["status_code"] = "200"
		else:
			response_data["status_message"] = "failure"
			response_data["status_code"] = "-1"
	response =  HttpResponse(json.dumps(response_data), content_type="application/json")
	print response
	return response

@csrf_exempt
def contacts(request):
	response_data = {}
	response_data["status_message"] = "success"
	response_data["status_code"] = "200"
	response_data["contacts"] = get_contact_list(request.GET.get('username'))
	response =  HttpResponse(json.dumps(response_data), content_type="application/json")
	print response
	return response

def get_contact_list(username) :
	contacts = []

	for entry in User.objects.filter(~Q(username = username)) :
		contacts.append({'email': entry.username, 'picture': '%s%s' % (PICTURES_DOMAIN, entry.picture)})

	return contacts
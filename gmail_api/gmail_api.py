#!/usr/bin/env python

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
import base64


def get_message_contents(message):

    payload = message['payload']
    headers = payload['headers']

    message_info = {}
    for header in headers:
        parse_header(header, message_info)


    try:
        parts = payload['parts']
        body = parts[0]['body']
        data = parts[0]['data']
        data_utf8 = base64.b64decode(bytes(data), 'UTF-8')
    
        message_info['body'] = data_utf8
    except:
        pass

    message_info['snippet'] = message['snippet']


    return message_info


def parse_header(header, message_info):

    name = header['name']
    value = header['value']

    if name == 'Subject':
        message_info['subject'] = value
    elif name == 'Date':
        message_info['date'] = value
    elif name == 'From':
        message_info['from'] = value
    else:
        pass


def show_message_compact_content(message_info):
    print("Date: {}".format(message_info['date']))
    print("From: {}".format(message_info['from']))
    print("Subject: {}".format(message_info['subject']))
    print("Snippet: {}".format(message_info['snippet']))
    print("")



def show_list_of_messages(messages):

    if messages is None:
        print("No messages.")
        return

    for message in messages:
        show_message_compact_content(message)


##################################################################################################

class gmail_api():

    def __init__(self, credentials_path, user_id='me', oauth2_storagefile='credentials.json'):

        self.credentials_path = credentials_path
        self.user_id = user_id
        self.oauth2_storagefile = oauth2_storagefile

        # Setup the Gmail API
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = file.Storage(self.oauth2_storagefile)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(self.credentials_path, SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()))


    def get_list_of_message_ids(self, label_ids):

        response = self.service.users().messages().list(userId=self.user_id, labelIds=label_ids).execute()

        list_of_message_ids = response.get('messages')
        return list_of_message_ids

    def get_message_by_id(self, message_id):
        message = self.service.users().messages().get(userId=self.user_id, id=message_id).execute()
        return message


    def extract_messages(self, label_ids, nmessages=5):

        list_of_message_ids = self.get_list_of_message_ids(label_ids=label_ids)

        if list_of_message_ids is None:
            return None

        message_dicts_list = []

        for message_id in list_of_message_ids[:nmessages]:
            message = self.get_message_by_id(message_id['id'])
            message_contents = get_message_contents(message)

            message_dicts_list.append(message_contents)

        return message_dicts_list

    def show_unread_inbox_messages(self):

        label_ids = ['INBOX', 'UNREAD']
        messages = self.extract_messages(label_ids)
        show_list_of_messages(messages)


    def show_all_recent_messages(self, nmessages=5):

        messages = self.extract_messages(label_ids=[], nmessages=nmessages)
        show_list_of_messages(messages)


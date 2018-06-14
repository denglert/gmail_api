#!/usr/bin/env python

import gmail_api.gmail_api as gmail_api

credentials_path = './credentials/client_id.json'

gmail = gmail_api.gmail_api(credentials_path)

#gmail.show_unread_inbox_messages()
gmail.show_all_recent_messages()

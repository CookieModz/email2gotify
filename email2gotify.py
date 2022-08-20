#!/usr/bin/env python3
import argparse
import json
import pycurl
import sys
import html2text
import mailparser

sys.stdin.reconfigure(encoding='utf-8')

parser = argparse.ArgumentParser(description='Send Gotify PUSH based on email message')
parser.add_argument('infile', nargs='?', type=argparse.FileType(mode='r', encoding="UTF-8"), default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--key', help='API key for Gotify', required=True)
parser.add_argument('--url', help='The URL of your Gotify instance (e.g. https://gotify.example.com)', required=True)
parser.add_argument('--debug', help='Enable debug mode', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

msg = mailparser.parse_from_file_obj(args.infile)
args.infile.close()

def debug(debug_type, debug_msg):
    print(f"{debug_type} {debug} {msg}")

def htmlListToString(html): 
    str = ""
    for ele in html:
        str += html2text.html2text(ele) + '\n'
    return str

message = ''
name, emailaddr = msg.from_[0]

if len(msg.text_html):
    message = htmlListToString(msg.text_html).rstrip() + '\n\n';
else:
    message = '\n'.join(msg.text_plain) + '\n'

message = message + name + ' <' + emailaddr + '>'

push_headers = {
    "title": msg.subject,
    "message": message,
    "priority": 5,
}

push_json = json.dumps(push_headers)

gotify_endpoint = args.url + '/message?token=' + args.key

c = pycurl.Curl()
c.setopt(c.URL, gotify_endpoint)
c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
c.setopt(c.USERAGENT, 'Email To Gotify Script')

if debug_mode:
    c.setopt(c.DEBUGFUNCTION, debug)
else:
    c.setopt(c.WRITEFUNCTION, lambda x: None)

c.setopt(c.POSTFIELDS, push_json)
response = c.perform_rs()

http_status = c.getinfo(c.HTTP_CODE)
fail_status = [400, 401, 403, 404, 500, 502, 503]

if http_status in fail_status or debug_mode:
  print(response)

c.close()
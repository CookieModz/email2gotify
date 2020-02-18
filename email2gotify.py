import argparse
import base64
import email
import json
import pycurl
import re
import sys
import unicodedata

parser = argparse.ArgumentParser(description='Send Gotify PUSH based on email message')
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--key', help='API key for Gotify', required=True)
parser.add_argument('--url', help='The URL of your Gotify instance (e.g. https://gotify.example.com)', required=True)
parser.add_argument('--debug', help='Enable debug mode', action='store_true')
args = parser.parse_args()
debug_mode = args.debug

msg = email.message_from_file(args.infile)
args.infile.close()

def decode_field(field_raw):
    match = re.match(r'\=\?([^\?]+)\?([BQ])\?([^\?]+)\?\=', field_raw)
    if match:
        charset, encoding, field_coded = match.groups()
        if encoding == 'B':
            field_coded = base64.decodestring(field_coded)
        return field_coded.decode(charset)
    else:
        return field_raw

def debug(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug, msg)

subject_raw = msg.get('Subject', '')
subject = decode_field(subject_raw)

sender = decode_field(msg.get('From', ''))

body_text = ''
for part in msg.walk():
    if part.get_content_type() == 'text/plain':
        body_part = part.get_payload()
        if part.get('Content-Transfer-Encoding') == 'base64':
            body_part = base64.decodestring(body_part)
        part_encoding = part.get_content_charset()
        if part_encoding:
            body_part = body_part.decode(part_encoding)
        else:
            body_part = body_part.decode()

        if body_text:
            body_text = '%s\n%s' % (body_text, body_part)
        else:
            body_text = body_part

body_text = '%s\nFrom: %s' % (body_text, sender)
body_text = unicodedata.normalize('NFKD',body_text).encode('ascii','ignore')

push_headers = {
    "title": subject,
    "message": body_text,
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
  print response

c.close()



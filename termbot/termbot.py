from flask import Flask, request

import subprocess
import requests
import json
import time


# Credentials from facebook app
TOKEN = '' # page token to send msgs
SECRET = '' # fb app secret to authenticate the app
CHATID = '' # chat id TODO: add users
SECURL = ''  # keep this url secret so no one flood your app


def post_facebook_message(fbid, response, pagetoken):
    """Send the response to the user with the given fbid."""
    # Dont crash if response is a bytestring.
    if not isinstance(response, str):
        response = response.decode('utf-8')
    # Prepare message part and send.
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%pagetoken
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":response}})
    seen_action = json.dumps({"recipient":{"id":fbid}, "sender_action":"mark_seen"})
    typing_action = json.dumps({"recipient":{"id":fbid}, "sender_action":"typing_on"})

    # Display 'seen'.
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=seen_action)
    # Display 'typing'.
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=typing_action)
    # Send the message
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)


# WARNING: this function is not safe use it with caution.
# TODO: Use more secure mechanism to handle linux commands.
def answer_command(cmd):
    """Execute the command and return all the output."""
    # get command
    cmd = cmd.split(' ')
    command = cmd[0]
    args = cmd[1:]
    result = []
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        # TODO: except more specific exceptions ?
        return 'command returned non zero exit code'
    for line in process.stdout:
        if line:
            result.append(line.decode('utf-8'))
    # give the process a delay of 5s then kill
    wait_time = 5
    while process.poll() is None and (wait_time > 0):
        time.sleep(0.5)
        wait_time -= 1
    # close the iobuffer andkill process if still alive
    process.stdout.close()
    process.kill()
    return '\n'.join(result)


# Flask routines
app = Flask(__name__)

# authenticate secret GET
# send msg POST
@app.route('/fb/%s' % SECURL, methods=['GET', 'POST'])
def handle_msg():
    """Handle the authentication and the msg notif event."""
    if request.method == 'GET':
        app.logger.debug('[+] Got a challenge %s' % request.args.get('hub.verify_token', ''))
        if request.args.get('hub.verify_token', 'ErrorNoChallengeGiven') == SECRET:
            return request.args.get('hub.challenge')
        return 'Error, invalid token'

    # else it is a post read the message and answer
    # load the body in json
    incoming_message = request.get_json(force=True)
    app.logger.debug('[+] Icoming msg: %s' % incoming_message)
    for entry in incoming_message['entry']:
        if not 'messaging' in entry:
            continue
        for message in entry['messaging']:
            # Check to make sure the received call is a message call
            # This might be delivery, optin, postback for other events 
            if 'message' in message:  
                # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                # are sent as attachments and must be handled accordingly.
                # prepare an answer
                answer = answer_command(message['message']['text']) 
                post_facebook_message(message['sender']['id'], answer, TOKEN)
    return 'Done.'

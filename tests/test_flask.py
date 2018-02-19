import os
import sys
import unittest
import tempfile
import json
import shutil

from unittest import mock

from termbot.termbot import app

# Mock requests.post
def mocked_requests_post(*args, **kwargs):

    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    return MockResponse(200)


# Main test class
class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


    def test_home_page(self):
        res = self.app.get('/')
        assert '404 NOT FOUND' in res.status

    def test_challenge_correct(self):
        secret = ''
        securl = ''
        challenge = '0000'
        url = '/fb/%s?hub.verify_token=%s&hub.challenge=%s' % (securl, secret, challenge)
        res = self.app.get(url)
        assert challenge in res.data.decode('utf-8')

    def test_challenge_invalid(self):
        secret = 'invalidsecret'
        securl = ''
        challenge = '0000'
        url = '/fb/%s?hub.verify_token=%s&hub.challenge=%s' % (securl, secret, challenge)
        res = self.app.get(url)
        assert 'Error, invalid token' in res.data.decode('utf-8')


    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_run_proc(self, mock_post):
        # prepare file
        challenge = 'random0000'
        file_name = 'test.dat'
        file_path = os.path.join(self.test_dir, file_name)
        with open(file_path, 'w') as fd:
            fd.write(challenge)
        # Prepare payload
        payload = {'entry': [
                       {'messaging': [
                             {'message': {'text': 'cat %s' % file_path},
                              'sender': {'id': 12345}}
                        ]}
                  ]}
        securl = ''
        url = '/fb/%s' % securl
        # test cat
        res = self.app.post(url, data=json.dumps(payload))
        # Assert post called 3 times
        self.assertEqual(len(mock_post.call_args_list), 3)

        # Mark chat as seen
        mock_post.assert_any_call('https://graph.facebook.com/v2.6/me/messages?access_token=',
                                     data='{"recipient": {"id": 12345}, "sender_action": "mark_seen"}',
                                     headers={'Content-Type': 'application/json'})

        # Display typing action
        mock_post.assert_any_call('https://graph.facebook.com/v2.6/me/messages?access_token=',
                                     data='{"recipient": {"id": 12345}, "sender_action": "typing_on"}',
                                     headers={'Content-Type': 'application/json'})

        # Send actual response
        mock_post.assert_any_call('https://graph.facebook.com/v2.6/me/messages?access_token=',
                                     data='{"recipient": {"id": 12345}, "message": {"text": "random0000"}}',
                                     headers={'Content-Type': 'application/json'})
        

if __name__ == '__main__':
    unittest.main()

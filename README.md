# Termbot
Use facebook messenger app as a simple on-the-fly terminal for your server

[![Build Status](https://travis-ci.org/piratos/Termbot.svg?branch=master)](https://travis-ci.org/piratos/Termbot)

## Installation


### Environment
Start always by creating a virtual environment
```
virtualenv <folder> -p <python_bin>
pip install -r requirements.txt
```


### Expose a tls connection to your server
In this tutorial we will use the free version of ngrock which is sufficient for the demonstration
If you intend to send a lot of requests to your bot use Lets encrypt+web server to handle incoming requests.

* Download ngrock binary from the [official website](https://ngrok.com/download).
* Expose a http connection with a opened port `./ngrock http <port>`.
* Markdown the url ngrock will generate in the form of `https://XXXXX.ngrock.io`.


### Setup Facebook app and generate token
* Go to [Facebook developers](https://developers.facebook.com) and create a new app.
* Link the app to an existing page or create a new page.
* Generate a new token for your page.
* Open `app.py`
  * Add the `TOKEN` you generated in the previous step.
  * Add a secret string in `SECRET` for your authentication process with Facebook server.
  * `SECURL` is a string that will be added to the callback url keep it secret and Random maybe.

### Run your flask application through
```
export FLASK_APP=termbot.py
flask run --host=0.0.0.0  --port=<port>
```

### Register your app and test
* Go to [Facebook developers](https://developers.facebook.com).
* Choose your application and go to webhooks.
* The callback should be `https://XXXXX.ngrock.io/fb/<SECURL>`.
* Put the `SECRET` in the next field .
* Select the following events: `messages`, `messaging_postbacks`, `messaging_optins`, `message_deliveries`, `message_reads`.
* Subscribe your page to these events.
* You should be ready to send commands through messenger.


## TODO
- [x] Add a working script.
- [x] Add Installation tutorial in readme.
- [ ] Add a test suite and a CI maybe ?.
- [ ] Add messenger buttons feature.
- [ ] Add notification (Celery ?).

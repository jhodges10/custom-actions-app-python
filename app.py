from flask import Flask, jsonify, request
from lib.video_handler import render_and_upload_slate
from multiprocessing import Pool, Process
from pprint import pprint
import json

app = Flask(__name__)

# GET is not used with custom actions, but tools like Glitch or Postman are often set to try a GET request.
# This is provided so you don't receive a 'Can't GET' notification.

@app.route('/', methods=['GET', 'POST'])
def hello_www():
  return "Hello World!"

# Send a POST request to /actions to create a form in the Frame.io web app

@app.route('/new', methods=['POST'])
def callback():
  data = request.json

  if "data" in data.keys():
    if data['data']['type'] == "slate.generate":
      pprint(data)
      # Grab relevant data
      timecode_burnin = data['data']['timecode']
      client = data['data']['client']
      project = data['data']['project']

      # Pass it to the rendering function
      # p = Process(target=render_and_upload_slate, kwargs={"client": client, "project": project, "timecode_burnin": timecode_burnin})
      # p.start()
      # p.join()

      return jsonify({
        'title': 'Submitted for rendering!',
        'description': 'Your slate is being generated and added to your video'
      })
    else:
      return jsonify({
        'title': 'Bad request',
        'description': 'You hit the endpoint with the wrong info'
      })

  return jsonify({
    'title': 'Add a slate!',
    'description': 'Fill out the following to add a slate to your video!',
    'fields': [
      {
        'type': 'text',
        'name': 'client',
        'label': 'Client'
      },
      {
        'type': 'text',
        'name': 'project',
        'label': 'Project'
      },
      {
        'type': 'select',
        'name': 'timecode',
        'label': 'Timecode Burn-in',
        'options': [
          {
            'name': 'Yes',
            'value': 'yes',
          },
          {
            'name': 'No',
            'value': 'no',
          },
        ],
      },
    ]
  })

if __name__ =="__main__":
    app.run(host="0.0.0.0", debug=True,port=80)

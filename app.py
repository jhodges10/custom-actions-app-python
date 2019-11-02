from flask import Flask, jsonify, request
from lib.video_handler import render_and_upload_slate
from multiprocessing import Pool, Process
from pprint import pprint
from redis import Redis, StrictRedis
import os
import json

app = Flask(__name__)
try:
  redis_conn = StrictRedis(host=os.getenv("REDIS_HOSTNAME", default="localhost"), port=6379, charset="utf-8", decode_responses=True)
except:
  redis_conn = StrictRedis(host=os.getenv("REDIS_HOSTNAME", default="redis"), port=6379, charset="utf-8", decode_responses=True)

# GET is not used with custom actions, but tools like Glitch or Postman are often set to try a GET request.
# This is provided so you don't receive a 'Can't GET' notification.

@app.route('/', methods=['GET', 'POST'])
def hello_www():
  return "Hello World!"

# Send a POST request to /actions to create a form in the Frame.io web app

@app.route('/new', methods=['POST'])
def callback():
  data = request.json
  pprint(data)
  interaction_id = data['interaction_id']
  ## WIP load and pass resource ID on to the encoder so that we can download the correct asset and metadata and get to work.

  try:
    resource_id = data['resource']['id']
    if resource_id:
      # Save the resource ID to the redis with the interaction id so we can call it back in a few seconds when the form is submitted
      redis_conn.hset("interaction_ids", interaction_id, resource_id) 
  except KeyError:
    resource_id = redis_conn.hget("interaction_ids", interaction_id)

  if "data" in data.keys():
    if data['type'] == "slate.generate":
      # pprint(data)
      # Grab relevant data
      try:
        timecode_burnin = data['data']['timecode']
      except KeyError:
        timecode_burnin = None
      client = data['data']['client']
      project = data['data']['project']

      # pprint({
      #   "client": client,
      #   "project": project,
      #   "timecode_burnin": timecode_burnin,
      #   "interaction_id": interaction_id,
      #   "resource_id": resource_id
      # })

      # Pass it to the rendering function so that we can return our response saying the job has started
      p = Process(target=render_and_upload_slate, kwargs={"client": client, "project": project, "timecode_burnin": timecode_burnin, "resource_id": resource_id, "interaction_id": interaction_id})
      p.start()
      # p.join()

      return jsonify({
        'title': 'Submitted for rendering!',
        'description': 'Your slate is being generated and added to your video',
        'resource_id': resource_id, # remove this before going live
        'interaction_id': interaction_id # remove this before going live
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

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
  pprint(data)
  interaction_id = data['interaction_id']

  ## WIP load and pass resource ID on to the encoder so that we can download the correct asset and metadata and get to work.

  try:
    resource_id = data['resource']['id']
    r_data = {interaction_id: resource_id}
    with open("json_store.json", "w") as json_store:
      json.dump(r_data, json_store)
    # Save the resource ID to the json store along with the interaction id so we can call it back in a few seconds when the form is submitted
  except KeyError:
    with open("json_store.json", "r") as json_store:
    # Load the resource ID associated with this interaction id    
      interaction_id_data = json.load(json_store)
      pprint(interaction_id_data)
      print(type(interaction_id_data))

  if "data" in data.keys():
    if data['type'] == "slate.generate":
      pprint(data)
      # Grab relevant data
      try:
        timecode_burnin = data['data']['timecode']
      except KeyError:
        timecode_burnin = None
      client = data['data']['client']
      project = data['data']['project']
      resource_id = list(interaction_id_data.keys())[0]

      # Pass it to the rendering function so that we can return our response saying the job has started
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

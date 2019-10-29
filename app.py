from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# GET is not used with custom actions, but tools like Glitch or Postman are often set to try a GET request.
# This is provided so you don't receive a 'Can't GET' notification.

@app.route('/', methods=['GET', 'POST'])
def hello_www():
  return "Hello World!"

# Send a POST request to /actions to create a form in the Frame.io web app

@app.route('/actions', methods=['POST'])
def callback():
  data = json.loads(request.data)

  if "data" in data:
    user_name = data['data']['name']
    user_color = data['data']['color']
    return jsonify({
      'title': 'Success!',
      'description': 'Hi there ' + user_name + '! Your favorite color is ' + user_color
    })

  return jsonify({
    'title': 'Hello World!',
    'description': 'Tell me about yourself!',
    'fields': [
      {
        'type': 'text',
        'name': 'name',
        'label': 'Name'
      },
      {
        'type': 'select',
        'name': 'color',
        'label': 'Favorite Color',
        'options': [
          {
            'name': 'Blue',
            'value': 'blue',
          },
          {
            'name': 'Red',
            'value': 'red',
          },
        ],
      },
    ]
  })

if __name__ =="__main__":
    app.run(debug=True,port=8080)

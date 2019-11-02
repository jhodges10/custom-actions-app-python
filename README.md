# Frame.io Custom Action driven automated slate rendering.

## R&D

### How to render programmatically with After effects
https://www.themarketingtechnologist.co/creating-dynamic-videos-using-javascript-and-after-effects-the-basics/

https://helpx.adobe.com/after-effects/using/automated-rendering-network-rendering.html


## FFMPEG on AWS

In order to use FFMPEG inside of our AWS instance, we have to set it up on Linux. I've created an AMI that can be re-used that will already have everything installed and ready to go.


## Setup

```
$ export FLASK_APP=custom_action
```

## Usage

```
$ flask run
```

By default the application runs on port 5000, however this can be overridden by setting the `PORT` environment variable. You can do that by adding the port you want to the `flask run` command, as shown:

```
$ flask run -h localhost -p 8000
```

## Troubleshooting

If you need help getting ngrok to work, you can check out our [troubleshooting guide for ngrok](https://docs.frame.io/docs/how-to-setup-and-troubleshoot-ngrok-mac).

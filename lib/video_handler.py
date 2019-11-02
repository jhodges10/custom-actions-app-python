import subprocess
import shutil
import os
import urllib
from random import randint
from pprint import pprint
from frameioclient import FrameioClient
from dotenv import load_dotenv
from pathlib import Path  # python3 only

def render_and_upload_slate(**kwargs):
    # print(f"Resource ID: {kwargs['resource_id']}")
    # print(f"Timecode Burnin: {kwargs['timecode_burnin']}")
    # print(f"Project: {kwargs['project']}")
    # print(f"Client: {kwargs['client']}")

    # Create temp directory
    if os.path.isdir(os.path.join(os.path.curdir, "temp")):
        pass
    else:
        os.mkdir("temp")

    # Initialize FIO Class
    try:
        env_path = Path('') / '.env'
        load_dotenv(dotenv_path=env_path, verbose=False)
    except Exception as e:
        print(e)
        print("Failure to load .env file... Trying one directory up.")
        env_path = Path('..') / '.env'
        load_dotenv(dotenv_path=env_path, verbose=False)

    token = os.environ.get("FRAMEIO_TOKEN")
    client = FrameioClient(token)

    asset_info = client.get_asset(kwargs['resource_id'])
    # pprint(asset_info)
    og_asset_url = asset_info['original']

    # Download original frame.io video
    print("Downloading video...")
    dl_path = os.path.join(os.path.curdir, 'temp', asset_info['name'])
    urllib.request.urlretrieve(og_asset_url, dl_path)
    print("Video downloaded. Continuing...")

    slate_path = generate_slate(client=kwargs['client'], fps=asset_info['fps'], duration=asset_info['duration'], project=kwargs['project'])

    # Merge new slate with video
    ul_filepath = merge_slate_with_video(slate_path, dl_path)

    # Upload new video to Frame.io
    final_video_path = ""
    upload_to_frameio(final_video_path)
    
    # Clean-up temp folder
    # shutil.rmtree("temp")

    return True

def generate_slate(**kwargs):
    print("Generating slate...")
    # Crate slate w/ FFMPEG
    movie_path = f"temp/new_slate_{randint(1,100)}.mp4"

    ffmpeg_string = """-i lib/Slate_v01_blank.mp4 -vf \
    'drawtext=fontfile=lib/AvenirNext.ttc: \
    text={}:fontcolor=white:fontsize=62:box=0: \
    x=1118:y=351, \
    drawtext=fontfile=lib/AvenirNext.ttc: \
    text={}:fontcolor=white:fontsize=62:box=0: \
    x=1118: y=551, \
    drawtext=fontfile=lib/AvenirNext.ttc: \
    text={}:fontcolor=white:fontsize=62:box=0: \
    x=1118: y=742'\
    -an {}
    """.format(kwargs['client'].upper(), kwargs['project'].upper(), kwargs['duration'], movie_path)

    # add -an to end of FFMPEG script, before output specified in order to remove audio from slate.

    with open("output.log", "a") as output:
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -stats {}""".format(ffmpeg_string),
            shell=True, stdout=output, stderr=output
        )

    print("Slate generation completed. Continuing...")
    return movie_path

def upload_to_frameio(final_video_path):
    pass

def merge_slate_with_video(slate_path, video_path):
    # Process w/ FFMPEG
    with open("output.log", "a") as output:
        # Generate intermediate transport streams to prevent re-encoding of h.264
        print("Generating intermediate1.ts")
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i '{}' -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate1.ts""".format(slate_path),
            shell=True, stdout=output, stderr=output
        )
        print("Done Generating intermediate1.ts")
        print("Creating intermediate2.ts")
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i '{}' -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate2.ts""".format(video_path),
            shell=True, stdout=output, stderr=output
        )
        print("Done Generating intermediate2.ts")
        print("Beginning merge...")
        # Merge together transport streams
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i 'concat:intermediate2.ts|intermediate2.ts' -c copy -bsf:v slated_output.mp4""",
            shell=True, stdout=output, stderr=output
        )
        print("Merge completed... Ready to upload!")

    return "slated_output.mp4"
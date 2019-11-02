import subprocess
import shutil
import os
import urllib
from pprint import pprint
from frameioclient import FrameioClient
from dotenv import load_dotenv
from pathlib import Path  # python3 only

def render_and_upload_slate(**kwargs):
    print(f"Resource ID: {kwargs['resource_id']}")
    print(f"Timecode Burnin: {kwargs['timecode_burnin']}")
    print(f"Project: {kwargs['project']}")
    print(f"Client: {kwargs['client']}")

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
    urllib.request.urlretrieve(og_asset_url, os.path.join(os.path.curdir, 'temp', asset_info['name']))

    # Upload new video to Frame.io
    final_video_path = ""
    upload_to_frameio(final_video_path)
    
    # Clean-up temp folder
    shutil.rmtree("temp")

    return True

def generate_slate():
    # Crate slate w/ FFMPEG
    movie_name = "slate.mp4"

    """
    ffmpeg -i input.mp4 -vf drawtext="fontfile=/path/to/font.ttf: \
    text='Stack Overflow': fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5: \
    boxborderw=5: x=(w-text_w)/2: y=(h-text_h)/2" -codec:a copy output.mp4
    """

    with open("/tmp/output.log", "a") as output:
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -stats -i temp/img%03d.jpg -c:v libx264 -vf scale=4096:-1 -vf fps=8 -pix_fmt yuv420p temp/{}""".format(movie_name),
            shell=True, stdout=output, stderr=output
        )
    
    return

def upload_to_frameio(final_video_path):
    pass

def merge_slate_with_video(slate_path, video_path):
    # Process w/ FFMPEG
    with open("/tmp/output.log", "a") as output:
        # Generate intermediate transport streams to prevent re-encoding of h.264
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate1.ts""".format(slate_path),
            shell=True, stdout=output, stderr=output
        )
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate2.ts""".format(video_path),
            shell=True, stdout=output, stderr=output
        )

        # Merge together transport streams
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i 'concat:intermediate1.ts|intermediate2.ts' -c copy -bsf:v  -bsf:a aac_adtstoasc slated_output.mp4""",
            shell=True, stdout=output, stderr=output
        )

    return "slated_output.mp4"
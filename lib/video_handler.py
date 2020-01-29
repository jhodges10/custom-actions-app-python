import subprocess
import shutil
import os
import math
import urllib
from random import randint
from pprint import pprint
from timecode import Timecode
from frameioclient import FrameioClient
from dotenv import load_dotenv
from pathlib import Path  # python3 only


def render_and_upload_slate(**kwargs):
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

    # Get asset info
    asset_info = client.get_asset(kwargs['resource_id'])
    # TODO add handling of version stacks here (really just get the asset id of the latest version and replace asset_info with that)
    # pprint(asset_info)
    og_asset_url = asset_info['original']

    # Download original frame.io video
    print("Downloading video...")
    dl_path = os.path.join(os.path.curdir, 'temp', asset_info['name'])
    urllib.request.urlretrieve(og_asset_url, dl_path)
    print("Video downloaded. Continuing...")

    resolution = {
        "width": asset_info['transcodes']['original_width'],
        "height": asset_info['transcodes']['original_height']
    }

    slate_path = generate_slate(client=kwargs['client'], fps=asset_info['fps'],
                                duration=asset_info['duration'], project=kwargs['project'], resolution=resolution)

    # Merge new slate with video
    ul_filepath = merge_slate_with_video(slate_path, dl_path)

    # Upload new video to Frame.io
    upload_to_frameio(ul_filepath, asset_info, client)

    # Clean-up temp folder
    # shutil.rmtree("temp")

    return True


def generate_slate(**kwargs):
    print("Generating slate...")
    # Crate slate w/ FFMPEG
    movie_path = f"temp/new_slate_{randint(1,100)}.mp4"
    tc = Timecode(kwargs['fps'], f"00:00:{kwargs['duration']}")

    slate_string = """-y -i lib/8s_blank_slate.mp4 -vf \
        'drawtext=fontfile=lib/AvenirNext.ttc: \
        text={}: fontcolor=white: fontsize=62: box=0: \
        x=1114:y=351, \
        drawtext=fontfile=lib/AvenirNext.ttc: \
        text={}: fontcolor=white: fontsize=62: box=0: \
        x=1114: y=551, \
        drawtext=fontfile=lib/AvenirNext.ttc: \
        text={}: fontcolor=white: fontsize=62: box=0: \
        x=1114: y=742, scale={}:{}, fps=fps={}' \
        -pix_fmt yuv420p {} \
        """.format(kwargs['client'].upper(), kwargs['project'].upper(), str(tc).replace(":", "\\\\\\\\\\\\:"), kwargs['resolution']['width'], kwargs['resolution']['height'], kwargs['fps'], movie_path)
    # x=1118: y=742' -vf scale={}:{} \ -- backup line in case getting rid of the additional call  for -vf doesn't work
    # add '-an' to end of FFMPEG script, before output specified in order to remove audio from slate.

    black_slate_string = """-y -i lib/2s_black.mp4 -vf 'scale={}:{}, fps=fps={}' -pix_fmt yuv420p temp/temp_black.mp4 \
        """.format(kwargs['resolution']['width'], kwargs['resolution']['height'], kwargs['fps'])

    with open("output.log", "a") as output:
        # Generate actual slate
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -stats {}""".format(
                slate_string),
            shell=True, stdout=output, stderr=output
        )
        # Generate 2s of black
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -stats {}""".format(
                black_slate_string),
            shell=True, stdout=output, stderr=output
        )

    print("Slate generation completed. Continuing...")
    return movie_path


def merge_slate_with_video(slate_path, video_path):
    # Process w/ FFMPEG
    with open("output.log", "a") as output:

        # Generate intermediate transport streams to prevent re-encoding of h.264
        print("Generating intermediate1.ts")
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i '{}' -c copy -bsf:v h264_mp4toannexb -f mpegts ./temp/intermediate1.ts""".format(slate_path),
            shell=True, stdout=output, stderr=output
        )
        print("Done Generating intermediate1.ts")
        print("Creating intermediate2.ts")
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i ./temp/temp_black.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts ./temp/intermediate2.ts""",
            shell=True, stdout=output, stderr=output
        )
        print("Done Generating intermediate2.ts")
        print("Creating intermediate3.ts")
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i '{}' -c copy -bsf:v h264_mp4toannexb -f mpegts ./temp/intermediate3.ts""".format(video_path),
            shell=True, stdout=output, stderr=output
        )
        print("Done Generating intermediate3.ts")
        print("Beginning merge...")

        # Merge together transport streams
        subprocess.call(
            """docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -y -i 'concat:./temp/intermediate1.ts|./temp/intermediate2.ts|./temp/intermediate3.ts'  -c copy -bsf:a aac_adtstoasc ./temp/slated_output.mp4""",
            shell=True, stdout=output, stderr=output
        )
        print("Merge completed... Ready to upload!")

    return "temp/slated_output.mp4"


def upload_to_frameio(final_video_path, asset_info, client):
    # Rename file to original file name
    new_name = asset_info['name'].split(
        '.')[0] + '_s' + '.' + asset_info['name'].split('.')[1]
    ul_path = os.path.join(os.curdir, 'temp', new_name)
    os.rename(os.path.join(os.curdir, final_video_path), ul_path)

    # Get parent asset and project
    parent_id = asset_info['parent_id']
    # project_id = asset_info['project_id']
    filesize = os.path.getsize(ul_path)

    # Upload
    asset = client.create_asset(
        parent_asset_id=parent_id,
        name=new_name,
        type="file",
        filetype="video/quicktime",
        filesize=filesize
    )
    with open(ul_path, "rb") as file:
        print("Starting upload...")
        client.upload(asset, file)

    print("Upload completed!")


if __name__ == "__main__":
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

    asset_info = client.get_asset('a1a27d9b-181a-4005-b176-27d74cef8150')
    pprint(asset_info)

    upload_to_frameio("temp/slated_output.mp4", asset_info, client)

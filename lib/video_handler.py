import subprocess
import shutil
import os
from frameio_handler import FIO

def render_and_upload_slate(**kwargs):
    # Create temp directory
    if os.path.isdir(os.path.join(os.path.curdir, "temp")):
        pass
    else:
        os.mkdir("temp")
    
    # Download original frame.io video



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
            f"""docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i {slate_path} -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate1.ts""",
            shell=True, stdout=output, stderr=output
        )
        subprocess.call(
            f"""docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i {video_path} -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate2.ts""",
            shell=True, stdout=output, stderr=output
        )

        # Merge together transport streams
        subprocess.call(
            f"""docker run -v $(pwd):$(pwd) -w $(pwd) jrottenberg/ffmpeg:3.2-scratch -i 'concat:intermediate1.ts|intermediate2.ts' -c copy -bsf:v  -bsf:a aac_adtstoasc slated_output.mp4""",
            shell=True, stdout=output, stderr=output
        )

    return "slated_output.mp4"
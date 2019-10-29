import os
import mimetypes
import time
import sys
from dotenv import load_dotenv
from pathlib import Path  # python3 only
from frameioclient import FrameioClient
from pprint import pprint
from fuzzywuzzy import process

class FIO:
    def __init__(self, project_name):
        # Setup
        try:
            env_path = Path('') / '.env'
            load_dotenv(dotenv_path=env_path, verbose=False)
        except Exception as e:
            print(e)
            print("Failure to load .env file... Trying one directory up.")
            env_path = Path('..') / '.env'
            load_dotenv(dotenv_path=env_path, verbose=False)
        # Load client
        self.load_client(project_name)
        print("Frame.io Client initialized")

    @classmethod
    def load_client(self, project_name):
        """
        Attributes
        ----------
        project_name : str
            A string representing the name of the Frame.io project you wish to upload your files to.
        """
        client = FrameioClient(os.getenv("FRAMEIO_TOKEN")) # This won't work unless you have a .env file with the correct token.
        me = client.get_me()
        teams = client.get_all_teams(account_id=me['account_id'])
        selected_team_id = teams.results[0]['id']
        projects = client.get_projects(team_id=selected_team_id) # Make sure that you're selecting correct team via the index value [0] or [1]

        # Create a dict of project names and ids
        project_dict = dict()
        project_names_list = list()
        for project in projects.results:
            project_dict[project['name']] = project['id']
            project_names_list.append(project['name'])

        # Extract the matching one
        matching_name = process.extractOne(project_name, project_names_list)[0]

        print(f"Matched to project: {matching_name}")
        project_id = project_dict[matching_name] # Gets relevant value for matched key
        self.project_id = project_id

        print(f"Project ID set to: {self.project_id}")
        self.client = client

    @classmethod
    def uploader(self, parent_asset_id, file_loc):
        """
        Attributes
        ----------
        parent_asset_id : str
            A UUID representing the parent asset ID.
        file_loc : str
            The location of the file you want to upload
        """

        # Create a new asset.
        asset = self.client.create_asset(
            parent_asset_id=parent_asset_id,
            name=os.path.split(file_loc)[1],
            type="file",
            filetype=mimetypes.read_mime_types(file_loc),
            filesize=os.path.getsize(file_loc)
        )

        return self.client.upload(asset, open(file_loc, "rb"))


if __name__ == "__main__":
    # Declare the location of your file that you want to upload
    your_file_to_upload = os.path.abspath("sample_2.mp4")
    # Declare the parent asset id you want to attach this upload to
    parent_asset_id = "PUT_PARENT_ASSET_ID_HERE"

    # Instantiate the Frame.io client and connect it to the right project using fuzzy matching
    frame_io = FIO("Project name")
    
    # Upload file
    frame_io.uploader(parent_asset_id, your_file_to_upload)

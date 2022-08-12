# returns stream info

import os
from urllib import response

from urllib.parse import urlparse, parse_qs

import googleapiclient.discovery

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.environ["api_key"]

youtube = googleapiclient.discovery.build(
	api_service_name, api_version, developerKey = DEVELOPER_KEY)


def get_youtube_stream():
	# i'm lazy so just get the first result in the "streams" playlist
	request = youtube.playlistItems().list(
		part = "snippet",
		maxResults = 1,
		playlistId = "PLAWgoOAOTXvFT_H--Vnu0KrbPEgnpO8QG"
	)
	response = request.execute()

	return {"title": response["items"][0]["snippet"]["title"],
			"url": f"https://www.youtube.com/watch?v={response['items'][0]['snippet']['resourceId']['videoId']}"}

# get title of specified youtube link
def get_youtube_alt_stream(url):
	vid_id = get_video_id(url)
	if vid_id == None:
		return None
	
	request = youtube.videos().list(
		part = "snippet",
		id = vid_id
	)
	response = request.execute()

	return {"title": response["items"][0]["snippet"]["title"],
			"url": f"https://www.youtube.com/watch?v={vid_id}"}

def get_video_id(url):
	# shamelessly stolen from https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
	query = urlparse(url)
	if query.hostname == 'youtu.be':
		return query.path[1:]
	if query.hostname in ('www.youtube.com', 'youtube.com'):
		if query.path == '/watch':
			p = parse_qs(query.query)
			return p['v'][0]
		if query.path[:7] == '/embed/':
			return query.path.split('/')[2]
		if query.path[:3] == '/v/':
			return query.path.split('/')[2]
	return None

# # used as a backup if the youtube link is incorrect/specified manually
# def get_twitch_title(url: str):
# 	# token might expire so wont implement this yet

# print(get_youtube_alt_stream("https://www.youtube.com/watch?v=Ldv4N72NjXM"))
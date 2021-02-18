from flask import Flask, render_template, request, jsonify, send_file, current_app, after_this_request
import urllib.request
from bs4 import BeautifulSoup
from pytube import YouTube
from moviepy.editor import *
import os
import json
import io

app = Flask(__name__)
mp3 = ''
@app.route("/")
def index():
    # Load current count
    return render_template("index.html")

@app.route("/download",methods=['POST'])
def dwnld():
    song_name = request.form.get("songName")
    print(song_name)
    query = urllib.parse.quote(song_name)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    scripts = soup.findAll('script')
    myscript = scripts[32]
    json_object = json.loads('['+myscript.contents[0][20:-1]+']')

    contents = json_object[0]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
    for content in contents:
        if "videoRenderer" in content.keys():
            title = content["videoRenderer"]["title"]["runs"][0]["text"]
            id = content["videoRenderer"]["videoId"]
            if "Lyric" in title or "lyric" in title:
                print(title)
                youtube_link = 'https://www.youtube.com/watch?v='+id
                mp4 = YouTube(youtube_link).streams.first().download()
                mp3 = mp4.split(".mp4",1)[0]+f".mp3"
                video = VideoFileClip(mp4)
                audio_clip = video.audio
                audio_clip.write_audiofile(mp3)
                audio_clip.close()
                video.close()
                os.remove(mp4)
                break
    return_data = io.BytesIO()
    with open(mp3, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(mp3)
    return send_file(return_data, mimetype='audio/mpeg',
                     attachment_filename=song_name+'.mp3',as_attachment=True)
if __name__ == "__main__":
    app.run()
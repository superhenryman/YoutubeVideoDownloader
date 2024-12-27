from flask import Flask, request, render_template, send_file
from io import BytesIO
import os
import yt_dlp as yt
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        todownload = request.form.get("data")
        if todownload:
            try:
                file_stream, title = Download(todownload=todownload)
                return send_file(
                    file_stream,
                    as_attachment=True,
                    download_name=f"{title}.mp4",
                    mimetype="video/mp4"
                )
            except Exception as e:
                return render_template("index.html", error=f"Error: {str(e)}")
    return render_template("index.html", error=None)
def Download(todownload):
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }
    try:
        with yt.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(todownload, download=True)
            title = info.get('title', 'Unknown Title')
            filename = ydl.prepare_filename(info)

            file_stream = BytesIO()
            with open(filename, 'rb') as file:
                file_stream.write(file.read())
            file_stream.seek(0)

            os.remove(filename)

            return file_stream, title
    except Exception as e:
        print(f"Error! Details: {e}")
if __name__ == "__main__":
    app.run(debug=True)
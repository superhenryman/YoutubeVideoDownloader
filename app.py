from flask import Flask, request, render_template, send_file, logging
from io import BytesIO
import os
import yt_dlp as yt
import logging
import psycopg2
import time
import tempfile
app = Flask(__name__)
database_url = os.getenv('DATABASE_URL')
if not database_url:
    app.logger.error("Database URL is not setup properly.")
    raise Exception("Database URL is not setup properly.")
def get_connection():
    retry_count = 5
    for i in range(retry_count):
        try:
            conn = psycopg2.connect(database_url)
            return conn
        except Exception as e:
            print(f"Attempt {i} failed: {e}")
            time.sleep(2 ** i)
    raise Exception("I can't connect :(")
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS links(
        id SERIAL PRIMARY KEY,
        link TEXT NOT NULL
    );""")
    conn.commit()
    cur.close()
    conn.close()
init_db()
if not app.debug:
    logging.basicConfig(level=logging.DEBUG)
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
            return filename, title
            #file_stream = BytesIO()
            #with open(filename, 'rb') as file:
                #file_stream.write(file.read())
            #file_stream.seek(0)

            #os.remove(filename)

            return file_stream, title
    except Exception as e:
        app.logger.error(f"Error! Details: {e}")
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        todownload = request.form.get("data")
        if todownload:
            try:
                if "youtube.com" not in todownload and "youtu.be" not in todownload:
                    raise ValueError("Only Youtube links are allowed!")
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO links (link) VALUES (%s)", (todownload,))
                conn.commit()
                cur.close()
                conn.close()
                filepath, title = Download(todownload=todownload)
                with open(filepath, 'rb') as f:
                    file_stream = BytesIO(f.read())
                return send_file(
                    file_stream,
                    as_attachment=True,
                    download_name=f"{title}.mp4",
                    mimetype="video/mp4"
                )
            except Exception as e:
                return render_template("index.html", error=f"Error: {str(e)}")
            finally:
                  if filepath and os.path.exists(filepath):  # Safely remove the file
                    os.remove(filepath)
    return render_template("index.html", error=None)

if __name__ == "__main__":
    app.run()

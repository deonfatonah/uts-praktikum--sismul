from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import numpy as np
import cv2
from pydub import AudioSegment
import pydub
pydub.AudioSegment.converter = 'C:/Users/ASUS/AppData/Local/ffmpegio/ffmpeg-downloader/ffmpeg/bin/3ffmpeg.exe'
app = Flask(__name__)



def read_image(file):
    img = Image.open(io.BytesIO(file))
    img = img.convert("RGB")
    return np.array(img)


def apply_filter(img, filter_type):
    if filter_type == "grayscale":
        img = np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])
    elif filter_type == "red":
        red_filter = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
        img = np.dot(img, red_filter)
    elif filter_type == "blur":
        img = cv2.GaussianBlur(img, (15, 15), 0)
    elif filter_type == "edge_detection":
        img = cv2.Canny(img, 100, 200)
    return img.astype("uint8")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/filter", methods=["POST"])
def filter():
    file = request.files["image"]
    filter_type = request.form.get("filter")
    img = read_image(file.read())
    filtered_img = apply_filter(img, filter_type)
    pil_img = Image.fromarray(filtered_img)
    img_io = io.BytesIO()
    pil_img.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype="image/jpeg")


@app.route("/cut-audio", methods=["POST"])
def cut_audio():
    start = int(request.form["start"]) * 1000
    end = int(request.form["end"]) * 1000
    file = request.files["file"]
    audio = AudioSegment.from_file(file)
    sliced_audio = audio[start:end]
    sliced_audio.export("output.wav", format="wav")
    return "Audio has been cut"


if __name__ == "__main__":
    app.run(debug=True)

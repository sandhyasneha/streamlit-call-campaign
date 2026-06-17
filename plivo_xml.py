from flask import Flask, request, Response
import html

app = Flask(__name__)

@app.route("/plivo-answer", methods=["GET", "POST"])
def plivo_answer():
    audio_url = request.args.get("audio", "")

    if not audio_url:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Audio file is missing.</Speak>
</Response>"""
    else:
        safe_audio_url = html.escape(audio_url, quote=True)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{safe_audio_url}</Play>
</Response>"""

    return Response(xml, mimetype="application/xml")


@app.route("/", methods=["GET"])
def health():
    return "Plivo XML endpoint is running"
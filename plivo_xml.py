from flask import Flask, request, Response
from xml.sax.saxutils import escape

app = Flask(__name__)


def xml_response(xml: str) -> Response:
    return Response(
        xml,
        status=200,
        content_type="text/xml; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


@app.route("/", methods=["GET"])
def health():
    return "Plivo XML endpoint is running", 200


@app.route("/plivo-test", methods=["GET", "POST"])
def plivo_test():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>TruckTaxOnline Plivo XML test is working.</Speak>
</Response>"""
    return xml_response(xml)


@app.route("/plivo-answer", methods=["GET", "POST"])
def plivo_answer():
    audio_url = request.args.get("audio", "").strip()

    if not audio_url:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Audio file is missing.</Speak>
</Response>"""
        return xml_response(xml)

    safe_audio_url = escape(audio_url)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Please listen to this important TruckTaxOnline message.</Speak>
    <Play>{safe_audio_url}</Play>
</Response>"""
    return xml_response(xml)

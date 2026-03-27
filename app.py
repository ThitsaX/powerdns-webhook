from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PDNS_API_URL = os.environ["PDNS_API_URL"]
PDNS_API_KEY = os.environ["PDNS_API_KEY"]
PDNS_SERVER = os.environ.get("PDNS_SERVER", "localhost")
PDNS_ZONE = os.environ["PDNS_ZONE"]

headers = {
    "X-API-Key": PDNS_API_KEY,
    "Content-Type": "application/json"
}

def update_txt_record(name, value, action):
    url = f"{PDNS_API_URL}/servers/{PDNS_SERVER}/zones/{PDNS_ZONE}"

    if action == "present":
        records = [{
            "content": f"\"{value}\"",
            "disabled": False
        }]
        changetype = "REPLACE"
    else:
        records = []
        changetype = "DELETE"

    payload = {
        "rrsets": [{
            "name": name,
            "type": "TXT",
            "ttl": 60,
            "changetype": changetype,
            "records": records
        }]
    }

    r = requests.patch(url, json=payload, headers=headers, verify=False)
    r.raise_for_status()


@app.route("/present", methods=["POST"])
def present():
    data = request.json
    fqdn = data["fqdn"]
    value = data["value"]

    update_txt_record(fqdn, value, "present")
    return jsonify({"status": "ok"})


@app.route("/cleanup", methods=["POST"])
def cleanup():
    data = request.json
    fqdn = data["fqdn"]

    update_txt_record(fqdn, "", "cleanup")
    return jsonify({"status": "ok"})


@app.route("/healthz")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
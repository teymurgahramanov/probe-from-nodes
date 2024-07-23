from flask import Flask, render_template, request, session, redirect, url_for
from kubernetes import client, config
from os import getenv,urandom
import requests
import concurrent.futures

if getenv('KP_LOCAL_DEBUG') == "1":
    config.load_kube_config()
    current_namespace = "default"
else:
    config.load_incluster_config()
    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
        current_namespace = f.read().strip()

v1 = client.CoreV1Api()
label_selector = getenv('KP_EXPORTER_LABEL_SELECTOR',"app=from-node-exporter")
probe_timeout = int(getenv('KP_PROBE_TIMEOUT','3'))
kp_version = 'v1.0.0'
app = Flask(__name__)
app.secret_key = urandom(24)

@app.route('/')
def index():
    return render_template('index.html', timeout=probe_timeout, version=kp_version)

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        "module": "tcp",
        "address": request.form['address'],
        "timeout": probe_timeout
    }
    exporters = {}
    session['results'] = []
    pods = v1.list_namespaced_pod(namespace=current_namespace, label_selector=label_selector)
    
    if not pods.items:
        session['results'].append({
            "host": 0,
            "result": f"Can't find from-node-exporter pods with label selector {label_selector}"
        })
    else:
        for pod in pods.items:
            exporters[pod.metadata.name] = {
                "host": pod.status.host_ip,
                "api_url": f"http://{pod.status.pod_ip}:8080/probe"
            }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(probe, exporter, data) for exporter in exporters.values()]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    session['results'].append(result)

    return render_template('index.html', timeout=probe_timeout, version=kp_version, results=session['results'])

def probe(exporter, data):
    try:
        response = requests.post(exporter["api_url"], json=data, timeout=data['timeout']*2)
        response_data = response.json()
        result = response_data.get("error", response_data.get("result"))
    except Exception as e:
        result = str(e)

    return {
        "host": exporter["host"],
        "result": result
    }

if __name__ == '__main__':
    app.run()
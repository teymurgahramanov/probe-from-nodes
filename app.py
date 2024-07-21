from flask import Flask, render_template, request, session
from kubernetes import client, config
from os import environ
import requests
import concurrent.futures

if environ.get('KP_LOCAL_DEBUG') == "1":
    config.load_kube_config()
    current_namespace = "default"
else:
    config.load_incluster_config()
    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
        current_namespace = f.read().strip()

v1 = client.CoreV1Api()
label_selector = environ.get('KP_EXPORTER_LABEL_SELECTOR') or "app=from-node-exporter"
app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        "module": "tcp",
        "address": request.form['address'],
        "timeout": 5
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

    return render_template('index.html', results=session['results'])

def probe(exporter, data):
    try:
        response = requests.post(exporter["api_url"], json=data, timeout=10)
        response_data = response.json()
        result = response_data.get("result", response_data.get("error", "Unknown error"))
    except requests.exceptions.RequestException as e:
        result = str(e)
    except ValueError:
        result = "Invalid response from server"

    return {
        "host": exporter["host"],
        "result": result
    }

if __name__ == '__main__':
    app.run()
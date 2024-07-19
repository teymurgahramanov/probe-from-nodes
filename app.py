from flask import Flask, render_template, request
from kubernetes import client, config
from os import environ
import requests

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    module = "tcp"
    address = request.form['address']
    timeout = 5

    exporters = {}
    results = []
    pods = v1.list_namespaced_pod(namespace=current_namespace, label_selector=label_selector)
    if not pods.items:
        results.append({
            "host": 0,
            "result": f"Can't find from-node-exporter pods with label selector {label_selector}"
        })
    else:
        for pod in pods.items:
            exporters[pod.metadata.name] = {"host":f"{pod.status.host_ip}", "api_url": f"http://{pod.status.pod_ip}:8080/probe"}

        for exporter in exporters.values():
            data = {
                "module": module,
                "address": address,
                "timeout": timeout
            }
            try:
                response = requests.post(exporter["api_url"], json=data, timeout=10)
                print(response)
                response_data = response.json()
                if "error" in response_data:
                    result = response_data["error"]
                else:
                    result = response_data.get("result", False)
            except requests.exceptions.RequestException as e:
                result = str(e)

            results.append({
                "host": exporter["host"],
                "result": result
            })

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run()
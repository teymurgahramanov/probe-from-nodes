from flask import Flask, render_template, request
from kubernetes import client, config
import requests

exporters = {}
config.load_kube_config()
#config.load_incluster_config()
v1 = client.CoreV1Api()
#with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
#    current_namespace = f.read().strip()
label_selector = "app=from-node-exporter"
pods = v1.list_namespaced_pod(namespace="default", label_selector=label_selector)
for pod in pods.items:
    exporters[pod.metadata.name] = {"host":f"{pod.status.host_ip}", "api_url": f"http://{pod.metadata.name}:8080/probe"}
print(exporters)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    dropdown_value = request.form['dropdown']
    text_input = request.form['text_input']
    timeout = int(request.form.get('timeout', 15))
    results = []

    for exporter in exporters.values():
        data = {
            "dropdown_value": dropdown_value,
            "text_input": text_input,
            "timeout": timeout
        }
        try:
            response = requests.post(exporter["api_url"], json=data, timeout=10)
            response_data = response.json()
            result = response_data.get("result", False)
            if "error" in response_data:
                result = response_data["error"]
        except requests.exceptions.RequestException as e:
            result = str(e)

        results.append({
            "host": exporter["host"],
            "result": result
        })

    return render_template('result.html', results=results)

if __name__ == '__main__':
    app.run(debug=False)

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    api_urls = [
        "http://localhost:8080/probe"
        # Add more URLs as needed
    ]

    dropdown_value = request.form['dropdown']
    text_input = request.form['text_input']
    results = []

    for url in api_urls:
        data = {
            "module": dropdown_value,
            "address": text_input
        }
        response = requests.post(url, json=data)
        response_data = response.json()
        results.append({
            "api_url": url,
            "result": response_data.get("result", False)
        })

    return render_template('result.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)

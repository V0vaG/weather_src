# sudo docker-compose up -d --build --scale app=3
from flask import Flask, request, render_template, redirect, send_from_directory
import os
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest
import weather_utils
import socket
import boto3
from datetime import datetime
import json
import logging

to_no_sql = None

key_id = os.getenv('key_id')
secret_id = os.getenv('secret_id')
table_name = os.getenv('table_name')
region = os.getenv('region')
color = os.getenv('BG_COLOR')
build_num = os.getenv('B_NUM')

def to_nosql(data):
    try:
        dynamodb = boto3.resource("dynamodb",
                                  aws_access_key_id=key_id,
                                  aws_secret_access_key=secret_id,
                                  region_name=region)
        table = dynamodb.Table(table_name)
        table.put_item(Item={table_name: str(data)})
        print("Item successfully added to DynamoDB table.")

    except Exception as e:
        print("Error:", e)
    return redirect('/')


app = Flask(__name__)  # initialize flask app
metrics = PrometheusMetrics(app)

# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('./logs/app.log')  # Log to a file
app.logger.addHandler(handler)


# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')
cities_metric = Counter('cities', 'Cities view', ['city_name'])

dt = datetime.now()


def make_json(city):
    os.system("sh json_fix.sh")
    dict1 = {"city": city, "data_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "host_name": socket.gethostname()}
    out_file = open("json/myfile.json", "a")
    json.dump(dict1, out_file, indent=4)
    out_file.close()
    os.system("sh json_fix2.sh")


@app.route("/json")
def download_json():
    return send_from_directory('./json/', 'myfile.json', as_attachment=True)
    
@app.route("/logs")
def download_logs():
    return send_from_directory('./logs/', 'app.log', as_attachment=True)

@app.route("/metrics")
def metrics():
    return generate_latest()


@app.route("/", methods=['POST', 'GET'])
def home():
    """
    The function render the home page, get user input and render again
    """

    if request.method == 'POST':  # When the user Click on search button he doses a POST request
        city_input = request.form['user_input']  # The function put the user input in the variable "city_input"

        make_json(city_input)
        app.logger.info(f'TIME: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}, Host: {socket.gethostname()}, Searched: {city_input}')
        # after city call
        cities_metric.labels(city_name=city_input).inc()
        weather_data = weather_utils.get_data(city_input)
        # The program go the function "get_data" with the user input as argument
        global to_no_sql
        to_no_sql = weather_data
        if weather_data == 404 or weather_data == "API Error":
            app.logger.error('Search Error!!!!!')
            err_dict = {
                "code_name": weather_data,
                "host_name": socket.gethostname()
            }
            return render_template('weather.html', error_data=err_dict, env_build_num=build_num, env_color=color)
        return render_template('weather.html', weather_data=weather_data, env_build_num=build_num, env_color=color)
    return render_template('weather.html', env_color=color, env_build_num=build_num)


@app.route('/dynamodb', methods=["POST"])
def dynamodb():
    print(to_no_sql)
    to_nosql(to_no_sql)
    return redirect('/')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

from flask import Flask , jsonify

app = Flask(__name__)

# from flask_accept import accept
from waitress import serve

# General
# Function to timestamp API call in UTC
from flask_backend.general.time_stamp_api_call import utc_timestamp_data_api_call

# Function that returns Campus Power Composition
from flask_backend.general.percent_campus_power import get_campus_power_composition

# Function that returns 24hr Campus Energy Intensity
from flask_backend.general.energy_intensity_24hr_data import query_influxdb_campus_energy_emission_intensity

# Function to get Energy Report Timeframe dates
from flask_backend.general.energy_report_timeframe import get_er_timeframe_dict

# User Specific u_kr
# Function to get sum of Dorm Room CO2 from InfluxDB
from flask_backend.user_specific.u_kr.dorm_room_co2_u_kr import query_influxdb_dorm_co2_data_u_kr
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_kr.dorm_room_energy_u_kr import query_influxdb_dorm_energy_data_u_kr
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_kr.dorm_energy_data_24hr_graph_u_kr import dorm_daily_data_combination_u_kr
# Function to get Room Environment Data from Sensors
from flask_backend.user_specific.u_kr.room_sensor_data_u_kr import get_sensor_data_u_kr

# User Specific u_a1
# Function to get sum of Dorm Room CO2 from InfluxDB
from flask_backend.user_specific.u_a1.dorm_room_co2_u_a1 import query_influxdb_dorm_co2_data_u_a1
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a1.dorm_room_energy_u_a1 import query_influxdb_dorm_energy_data_u_a1
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a1.dorm_energy_data_24hr_graph_u_a1 import dorm_daily_data_combination_u_a1
# Function to get Room Environment Data from Sensors
from flask_backend.user_specific.u_a1.room_sensor_data_u_a1 import get_sensor_data_u_a1

# User Specific u_a2
# Function to get sum of Dorm Room CO2 from InfluxDB
from flask_backend.user_specific.u_a2.dorm_room_co2_u_a2 import query_influxdb_dorm_co2_data_u_a2
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a2.dorm_room_energy_u_a2 import query_influxdb_dorm_energy_data_u_a2
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a2.dorm_energy_data_24hr_graph_u_a2 import dorm_daily_data_combination_u_a2
# Function to get Room Environment Data from Sensors
from flask_backend.user_specific.u_a2.room_sensor_data_u_a2 import get_sensor_data_u_a2

# User Specific u_a3
# Function to get sum of Dorm Room CO2 from InfluxDB
from flask_backend.user_specific.u_a3.dorm_room_co2_u_a3 import query_influxdb_dorm_co2_data_u_a3
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a3.dorm_room_energy_u_a3 import query_influxdb_dorm_energy_data_u_a3
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a3.dorm_energy_data_24hr_graph_u_a3 import dorm_daily_data_combination_u_a3
# Function to get Room Environment Data from Sensors
from flask_backend.user_specific.u_a3.room_sensor_data_u_a3 import get_sensor_data_u_a3

# User Specific u_a4
# Function to get sum of Dorm Room CO2 from InfluxDB
from flask_backend.user_specific.u_a4.dorm_room_co2_u_a4 import query_influxdb_dorm_co2_data_u_a4
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a4.dorm_room_energy_u_a4 import query_influxdb_dorm_energy_data_u_a4
# Function to get sum of Dorm Room Energy from InfluxDB
from flask_backend.user_specific.u_a4.dorm_energy_data_24hr_graph_u_a4 import dorm_daily_data_combination_u_a4
# Function to get Room Environment Data from Sensors
from flask_backend.user_specific.u_a4.room_sensor_data_u_a4 import get_sensor_data_u_a4


# General
# Campus Power Composition
@app.route('/api/v1/resources/campus_power/current' , methods=['GET'])
def flask_campus_power_composition_general() :
    # Get Campus Power Composition
    campus_power_comp_dict = get_campus_power_composition()
    json_data = jsonify(campus_power_comp_dict)

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **campus_power_comp_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# General
# Campus Energy Intensity
@app.route('/api/v1/resources/campus_energy_intensity/24hr' , methods=['GET'])
def flask_campus_energy_intensity_general() :
    # Get 24hr Campus Energy Intensity
    campus_energy_intensity_dict = query_influxdb_campus_energy_emission_intensity()
    json_data = jsonify(campus_energy_intensity_dict)

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **campus_energy_intensity_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# General
# Energy Report Timeframe date labels
@app.route('/api/v1/resources/dormroom_er_tf/current' , methods=['GET'])
def flask_er_timeframe_labels() :
    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User Specific U_kr
# Room Environment Data u_kr
@app.route('/api/v1/resources/u/kr/dormroom_enviro/current' , methods=['GET'])
def flask_dorm_environment_sensing_kr() :
    # Get Dorm Room Air Sensor Data
    dorm_environment_sensing_data_dict = get_sensor_data_u_kr()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_environment_sensing_data_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# Room Power and CO2 Footprint Data
@app.route('/api/v1/resources/u/kr/dorm_power_co2/current' , methods=['GET'])
def flask_dorm_power_co2_sensing_u_kr() :
    # Dorm Room CO2
    dorm_co2_data_dict = query_influxdb_dorm_co2_data_u_kr()

    # Dorm Room Energy
    dorm_energy_data_dict = query_influxdb_dorm_energy_data_u_kr()

    # 24 hour Energy Graph Data
    dorm_24hr_energy_data_dict = dorm_daily_data_combination_u_kr()

    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_co2_data_dict ,
        **dorm_energy_data_dict ,
        **dorm_24hr_energy_data_dict ,
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User Specific U_a1
# Room Environment Data u_a1
@app.route('/api/v1/resources/u/a1/dormroom_enviro/current' , methods=['GET'])
def flask_dorm_environment_sensing_u_a1() :
    # Get Dorm Room Air Sensor Data
    dorm_environment_sensing_data_dict = get_sensor_data_u_a1()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_environment_sensing_data_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User A1
# Room Power and CO2 Footprint Data
@app.route('/api/v1/resources/u/a1/dorm_power_co2/current' , methods=['GET'])
def flask_dorm_power_co2_sensing_u_a1() :
    # Dorm Room CO2
    dorm_co2_data_dict = query_influxdb_dorm_co2_data_u_a1()

    # Dorm Room Energy
    dorm_energy_data_dict = query_influxdb_dorm_energy_data_u_a1()

    # 24 hour Energy Graph Data
    dorm_24hr_energy_data_dict = dorm_daily_data_combination_u_a1()

    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_co2_data_dict ,
        **dorm_energy_data_dict ,
        **dorm_24hr_energy_data_dict ,
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User Specific U_a2
# Room Environment Data u_a2
@app.route('/api/v1/resources/u/a2/dormroom_enviro/current' , methods=['GET'])
def flask_dorm_environment_sensing_u_a2() :
    # Get Dorm Room Air Sensor Data
    dorm_environment_sensing_data_dict = get_sensor_data_u_a2()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_environment_sensing_data_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User A2
# Room Power and CO2 Footprint Data
@app.route('/api/v1/resources/u/a2/dorm_power_co2/current' , methods=['GET'])
def flask_dorm_power_co2_sensing_u_a2() :
    # Dorm Room CO2
    dorm_co2_data_dict = query_influxdb_dorm_co2_data_u_a2()

    # Dorm Room Energy
    dorm_energy_data_dict = query_influxdb_dorm_energy_data_u_a2()

    # 24 hour Energy Graph Data
    dorm_24hr_energy_data_dict = dorm_daily_data_combination_u_a2()

    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_co2_data_dict ,
        **dorm_energy_data_dict ,
        **dorm_24hr_energy_data_dict ,
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User Specific U_a3
# Room Environment Data u_a3
@app.route('/api/v1/resources/u/a3/dormroom_enviro/current' , methods=['GET'])
def flask_dorm_environment_sensing_u_a3() :
    # Get Dorm Room Air Sensor Data
    dorm_environment_sensing_data_dict = get_sensor_data_u_a3()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_environment_sensing_data_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User A3
# Room Power and CO2 Footprint Data
@app.route('/api/v1/resources/u/a3/dorm_power_co2/current' , methods=['GET'])
def flask_dorm_power_co2_sensing_u_a3() :
    # Dorm Room CO2
    dorm_co2_data_dict = query_influxdb_dorm_co2_data_u_a3()

    # Dorm Room Energy
    dorm_energy_data_dict = query_influxdb_dorm_energy_data_u_a3()

    # 24 hour Energy Graph Data
    dorm_24hr_energy_data_dict = dorm_daily_data_combination_u_a3()

    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_co2_data_dict ,
        **dorm_energy_data_dict ,
        **dorm_24hr_energy_data_dict ,
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User Specific U_a4
# Room Environment Data u_a4
@app.route('/api/v1/resources/u/a4/dormroom_enviro/current' , methods=['GET'])
def flask_dorm_environment_sensing_u_a4() :
    # Get Dorm Room Air Sensor Data
    dorm_environment_sensing_data_dict = get_sensor_data_u_a4()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_environment_sensing_data_dict ,
        **timestamp_utc_data_dict
    }

    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


# User A4
# Room Power and CO2 Footprint Data
@app.route('/api/v1/resources/u/a4/dorm_power_co2/current' , methods=['GET'])
def flask_dorm_power_co2_sensing_u_a4() :
    # Dorm Room CO2
    dorm_co2_data_dict = query_influxdb_dorm_co2_data_u_a4()

    # Dorm Room Energy
    dorm_energy_data_dict = query_influxdb_dorm_energy_data_u_a4()

    # 24 hour Energy Graph Data
    dorm_24hr_energy_data_dict = dorm_daily_data_combination_u_a4()

    # Energy Report Timeframe date labels
    er_timeframe_labels_data_dict = get_er_timeframe_dict()

    # Timestamp API call
    timestamp_utc_data_dict = utc_timestamp_data_api_call()

    # Combines data from all functions
    total_data_dict = {
        **dorm_co2_data_dict ,
        **dorm_energy_data_dict ,
        **dorm_24hr_energy_data_dict ,
        **er_timeframe_labels_data_dict ,
        **timestamp_utc_data_dict
    }
    json_data = jsonify(total_data_dict)

    # Enables CORS in Flask servers
    # Source: https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
    # Enable Access-Control-Allow-Origin
    json_data.headers.add("Access-Control-Allow-Origin" , "*")

    return json_data


if __name__ == '__main__' :
    # Serve with waitress; Increase number of threads
    serve(app , host='0.0.0.0' , port=4545 , threads=10)
    # app.run(port=4545 , host='0.0.0.0')

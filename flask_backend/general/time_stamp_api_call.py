import pendulum

def utc_timestamp_data_api_call():
    time_now_pendulum = pendulum.now('UTC')
    time_now_pendulum_string = time_now_pendulum.strftime('%Y-%m-%dT%H:%M:%S%z')

    # Add a colon to timezone offset when using datetime.strftime
    # Source: https://gist.github.com/mattstibbs/a283f55a124d2de1b1d732daaac1f7f8
    # Add a colon separator to the offset segment
    sensor_timestamp_utc = "{0}:{1}".format(
        time_now_pendulum_string[:-2] ,
        time_now_pendulum_string[-2 :]
    )
    # Make dictionary with timestamp data
    data_dict = {
        'timestamp_utc': sensor_timestamp_utc
    }

    return data_dict
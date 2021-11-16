from datetime import datetime
import datetime as dt


# Function to generate 'date_time_begin_strftime' for PJM API Url call
def date_time_begin_fn() :
    time_now = datetime.now()
    prev_hours = -2  # Originally set to 2; now changed to 1 for mqtt run to only give recent data
    prev_hours_added = dt.timedelta(hours=prev_hours)
    date_time_begin = time_now + prev_hours_added
    date_time_begin_strftime = date_time_begin.strftime("%m-%d-%Y %H:00")
    return date_time_begin_strftime


# Function to generate 'date_time_end_strftime' for PJM API Url call
def date_time_end_fn() :
    time_now = datetime.now()
    fut_hours = 0
    fut_hours_added = dt.timedelta(hours=fut_hours)
    date_time_end = time_now + fut_hours_added
    date_time_end_strftime = date_time_end.strftime("%m-%d-%Y %H:00")
    return date_time_end_strftime


# Function to generate URL for PJM API Call
def pjm_api_call() :
    # Keep URL below for returning to and for template
    URL_start = 'https://pjm_api_url_here'

    # date_time_begin = '6-14-2020 22:00'  # Sample of what 'date_time_begin_strftime' should look like
    date_time_begin_strftime = date_time_begin_fn()
    date_time_to = ' to '

    # date_time_end = '6-15-2020 04:00' # Sample of what 'date_time_end_strftime' should look like
    date_time_end_strftime = date_time_end_fn()
    response_format = '&format=json'  # JSON
    api_key = '&subscription-key=$private_key_here'
    Tot_url = URL_start + date_time_begin_strftime + date_time_to + date_time_end_strftime + response_format + api_key  # Complete API URL call
    return Tot_url

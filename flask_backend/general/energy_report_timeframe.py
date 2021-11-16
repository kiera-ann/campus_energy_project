''' Module to return Energy Report Timeframe dates.'''
# Pendulum Module
import pendulum


# Function to return Energy Report Timeframe dates
def get_er_timeframe_dict() :
    data_dict = { }  # Initialize dictionary

    # Gets time now in timezone 'US/Eastern' using pendulum module
    today = pendulum.now('US/Eastern')

    # To Modify start and end of week
    # Soure: https://stackoverflow.com/questions/19216334/python-give-start-and-end-of-week-data-from-a-given-date
    # pendulum.week_starts_at(pendulum.SUNDAY)
    # pendulum.week_ends_at(pendulum.SATURDAY)

    # Gets date/time information for previous day
    yesterday_full = pendulum.yesterday('US/Eastern')

    # Gets date/time information for week
    start = today.start_of('week')
    end = today.end_of('week')

    # Note to remove leading 0 values, use '-' like %-d
    # Source: https://stackoverflow.com/questions/904928/python-strftime-date-without-leading-0
    new_today = today.strftime('%-m.%-d')
    yesterday_date = yesterday_full.strftime('%-m.%-d')
    new_start = start.strftime('%-m.%-d')
    new_end = end.strftime('%-m.%-d')
    this_week = new_start + "-" + new_end
    this_month = today.strftime('%-m.%Y')

    data_dict = {
        'energy_report_timeframe' :
            {
                'today' : new_today ,
                'today_fmt' : "MM.DD" ,
                'yesterday' : yesterday_date ,
                'yesterday_fmt' : "MM.DD" ,
                'this_week' : this_week ,
                'this_week_fmt' : "MM.DD-MM.DD" ,
                'this_month' : this_month ,
                'this_month_fmt' : "MM.YYYY"
            }
    }
    return (data_dict)

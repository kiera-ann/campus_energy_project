import PropTypes from 'prop-types'
import { Component } from 'react'

class WeatherInfo extends Component {
    constructor(props) {
        super(props);

        if ('geolocation' in navigator) {
            console.log('geo available');
        } else {
            console.log('geo unavailable');
        }

        this.state = {
            color: '#42B0ED',
            w: 260,
            h: 140,
            clouds: 1,
            humidity: 30,
            wind: 10,
            weather: 'clear',
            temp: 40,
            long: -76.65,
            lat: 40.3,
            locationRetrived: false,
        }
    }

    componentDidMount() {
        if(!this.state.locationRetrived) { 
            this.getPosition()
        }
        this.updateWeather();
        this.timer = setInterval(() => this.updateWeather(), 30000);
    }

    getPosition() {
        const success = position => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            this.setState({
                long: longitude,
                lat: latitude,
            });
        }
        
        const error = () => {
            console.log('unable to retrieve location')
        }

        navigator.geolocation.getCurrentPosition(success, error);

        this.setState({ locationRetrived: true, })
    }

    updateWeather() {
        fetch('http://api.openweathermap.org/data/2.5/weather?lat=' + this.state.lat + 
        '&lon=' + this.state.long + '&appid=2fccc20373f66c6474568d4ef2852b4f')
            .then(response => response.json())
            .then(result => {
                this.setState({
                    clouds: result.clouds.all,
                    humidity: result.main.humidity,
                    wind: Math.round(result.wind.speed * 2.23),
                    weather: result.weather[0].main,
                    temp: Math.round((result.main.temp-273.15)*1.8+32),
                });
            })
    }

    render() {
        return (
            <div class='colorBox' style={{ backgroundColor: this.state.color, width: this.state.w, 
                                        height: this.state.h, marginLeft: 0, borderTopLeftRadius: 0, 
                                        borderBottomLeftRadius: 0, marginBottom: 5}}>
                <h1 style={{ marginBottom: 0 }}>weather</h1>
                    <div style={{ height: 100, alignContent: 'stretch' }}>
                        <div style={{ display: 'inline-block', marginRight: 17 }}>
                        <p class='bottomText'>clouds: {this.state.clouds}%
                        <br />humidity: {this.state.humidity}%
                        <br />wind: {this.state.wind} mph
                        </p>
                    </div>
                    <div style={{ display: 'inline-block' }}>
                        <p style={{ fontSize: 70, marginTop: -17 }}> {this.state.temp}{'\u00b0'}</p>
                        Princeton, NJ
                        <br /> {this.state.weather}
                    </div>
                </div>
            </div>
        )
    }
}

export default WeatherInfo

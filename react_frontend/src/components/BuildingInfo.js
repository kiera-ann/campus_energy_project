import PropTypes from 'prop-types'
import { Component } from 'react'

class BuildingInfo extends Component {
    constructor(props) {
        super(props);

        this.state = {
            color: '#42B0ED',
            w: 243,
            h: 140,
            buildingName: '',
            humidity: 0,
            temp: 0,
        }
    }

    componentDidMount() {
        this.fetchBuilding();
        this.timer = setInterval(() => this.fetchBuilding, 30000)
    }

    fetchBuilding() {
        fetch('http://140.180.133.113:4545/api/v1/resources/u/kr/dormroom_enviro/current')
            .then(response => response.json())
            .then(results => {
                this.setState({
                    buildingName: results.room_building_info.full_room_location,
                    humidity: results.room_building_info.humidity_value,
                    temp: results.room_building_info.temperature_value,
                });
            })

    }

    render() {
        return(
            <div class='colorBox' style={{ backgroundColor: this.state.color, width: this.state.w, 
                height: this.state.h, marginBottom: 5  }}>
                <h1 style={{ marginBottom: 55 }}>room|building info</h1>
                <p class='bottomText'> { this.state.buildingName }
                <br />temperature { this.state.temp }{'\u00b0'}F
                <br />humidity { this.state.humidity }%
                </p>
            </div> 
        )
    }
}

export default BuildingInfo

import React, { Component } from 'react'
import PropTypes from 'prop-types'

class EnergyDistribution extends Component {
    constructor(props) {
        super(props);

        this.state = {
            w: 243,
            h: 140,
            color: '#42B0ED',
            solarComp: 0,
            powerComp: 0,
            gridComp: 0,
        }
    }

    componentDidMount() {
        this.fetchData();
        this.timer = setInterval(() => this.fetchData(), 30000);
    }

    fetchData() {
        fetch('http://140.180.133.113:4545/api/v1/resources/campus_power/current')
            .then(response => response.json())
            .then(result => {
                this.setState({
                    solarComp: result.campus_power_composition.solar,
                    powerComp: result.campus_power_composition.campus_power_plant,
                    gridComp: result.campus_power_composition.grid,
                })
            })
            .catch(e => {
                this.setState({ errorMessage: e.toString() });
                console.error('There was an error!', e);
            });
    }

    render() {
        return (
            <div class='colorBox' style={{ backgroundColor: this.state.color, width: this.state.w, 
                                        height: this.state.h, verticalAlign: 'top', margin: 0 }}>
                <h1 style={{ marginBottom: 50 }}>energy composition</h1>
                <div style={{ alignContent: 'bottom', display: 'block'}}>
                    <div style={{ display: 'inline-block', textAlign: 'left', width: 69 }}>
                        <h6>{this.state.solarComp}%</h6>
                        Solar
                    </div>
                    <div style={{ display: 'inline-block', textAlign: 'center', width: 69 }}>
                        <h6>{this.state.powerComp}%</h6>
                        CoGen Plant
                    </div>
                    <div style={{ display: 'inline-block', textAlign: 'right', width: 69 }}>
                        <h6>{this.state.gridComp}%</h6>
                        Grid 
                    </div>
                </div>
            </div>
        );

    }
}

export default EnergyDistribution
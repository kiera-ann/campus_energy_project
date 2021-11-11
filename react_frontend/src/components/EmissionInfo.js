import { Component } from 'react'

class EmissionInfo extends Component {
    constructor(props) {
        super(props);

        this.state = {
            color: '#0D6CA1',
            w: 243,
            h: 293,
            dayEnergy: 0,
            dayCarbon: 0,
            day: '',
            weekEnergy: 0,
            weekCarbon: 0,
            week: '',
            monthEnergy: 0,
            monthCarbon: 0,
            month: '',
        }
    }

    componentDidMount() {
        this.fetchEmissions();
        this.timer = setInterval(() => this.fetchEmissions(), 30000)
    }
    
    fetchEmissions() {
        fetch('http://140.180.133.113:4545/api/v1/resources/u/kr/dorm_power_co2/current')
            .then(response => response.json())
            .then(results => {
                this.setState({
                    dayEnergy: results.energy_report_dorm_power.total_KWH_today,
                    weekEnergy: results.energy_report_dorm_power.total_KWH_week,
                    yestEnergy: results.energy_report_dorm_power.total_KWH_yesterday,
                    dayCarbon: results.energy_report_co2.total_co2_today,
                    weekCarbon: results.energy_report_co2.total_co2_week,
                    yestCarbon: results.energy_report_co2.total_co2_yesterday,
                    day: results.energy_report_timeframe.today,
                    week: results.energy_report_timeframe.this_week,
                    yest: results.energy_report_timeframe.yesterday,
                });
            })
    }

    render() {
        return (
            <div class='colorBox' style={{ backgroundColor: this.state.color, width: this.state.w, 
                                        height: this.state.h, marginTop: 5 }}>
            <h1 style={{ marginBottom: 33 }}>energy report</h1>
                <div style={{ display: 'inline-flex', width: 209, justifyContent: 'space-between',
                            opacity: 35, marginBottom: 25 }}>
                    <p>timeframe <br />reported</p>
                    <p>energy <br /> kwatt hour</p>
                    <p>carbon <br /> lbs</p>
                </div>

                <div style={{ display: 'inline-flex', width: 209, justifyContent: 'space-between',
                            marginBottom: 13 }}>
                    <p>today <br />{ this.state.day }</p>
                    <p style={{ fontSize: 40, marginTop: -10, textTransform: 'none'}}> 
                    { this.state.dayEnergy } kWh <br /> { this.state.dayCarbon } Lbs
                    </p>
                </div>

                <div style={{ display: 'inline-flex', width: 209, justifyContent: 'space-between',
                            marginBottom: 12 }}>
                    <p style={{width: 55}}>yesterday<br /> { this.state.yest } </p>
                    <p style={{width: 45}}>{ this.state.yestEnergy }</p>
                    <p style={{width: 35}}>{ this.state.yestCarbon }</p>
                </div>

                <div style={{ display: 'inline-flex', width: 209, justifyContent: 'space-between' }}>
                    <p style={{width: 55}}>this week<br />{ this.state.week }</p>
                    <p style={{width: 45}}>{ this.state.weekEnergy }</p>
                    <p style={{width: 35}}>{ this.state.weekCarbon }</p>
                </div>
            </div>
        )
    }
}

export default EmissionInfo

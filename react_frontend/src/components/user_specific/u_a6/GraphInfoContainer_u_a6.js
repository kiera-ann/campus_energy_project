import React from 'react'
import { Bar } from 'react-chartjs-2';
import 'chart.js'
import EnergyDistribution from './EnergyDistribution'

const days = ['Hourly energy use (Wh)', 'Hourly energy intensity (lbs CO2/kWh)']
const dataUnits = ['watt-hours', 'lbs CO2/kWh']
const dataLabel = ['energy', 'intensity']

class GraphInfoContainer_u_a1 extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            graphH: 140,
            graphW: 503,
            graphColor: '#0D6CA1',
            clabels: [],
            cvalues: [],
            ilabels: [],
            ivalues: [],
            toggle: 0,
        }
    }
    
    componentDidMount() {
        this.fetchGraphInfo();
        this.timer = setInterval(() => this.toggleDayWeek(), 60000);
        this.timer2 = setInterval(() => this.fetchGraphInfo(), 120000);
    }

    componentWillUnmount () {
        this.timer && clearInterval(this.timer);
        this.timer = false;
        this.timer2 && clearInterval(this.timer2);
        this.timer2 = false;
    }

    fetchGraphInfo() {
        this.fetchIntensity();
        this.fetchConsumption();
    }

    fetchIntensity() {
        let mounted = true;
        fetch('http://140.180.133.113:4545/api/v1/resources/campus_energy_intensity/24hr')
            .then(response => response.json())
            .then(results => {
                if(mounted) {
                    if (results.campus_energy_intensity && Object.keys(results.campus_energy_intensity)) {
                        this.setState({
                            ilabels: Object.keys(results.campus_energy_intensity),
                            ivalues: Object.values(results.campus_energy_intensity),
                        });
                    }
                }
            })
        return () => mounted = false;
    }

    fetchConsumption() {
        let mounted = true;
        fetch('http://140.180.133.113:4545/api/v1/resources/u/a6/dorm_power_co2/current')
            .then(response => response.json())
            .then(results => {
                if(mounted) {
                    if (results.daily_graph_energy_wh_data && Object.keys(results.daily_graph_energy_wh_data)) {
                        this.setState({
                            clabels: Object.keys(results.daily_graph_energy_wh_data),
                            cvalues: Object.values(results.daily_graph_energy_wh_data),
                        });
                    }
                }
            })
        return () => mounted = false;
    }

    toggleDayWeek = () => {
        this.setState({ toggle: (this.state.toggle+1)%2 });
    }

    setConsumptionGraph = () => {
        this.setState({ toggle: 0 })
    }

    setIntensityGraph = () => {
        this.setState({ toggle: 1 })
    }

    getCorrectLabels = () => {
        if(this.state.toggle) return this.state.ilabels;
        else return this.state.clabels;
    }

    getCorrectValues = () => {
        if(this.state.toggle) return this.state.ivalues;
        else return this.state.cvalues;
    }

    render() {
        return (
            <div class='graphContainer'>
                <div class='colorBox' style={{ backgroundColor: this.state.graphColor, width: this.state.graphW, 
                                        height: this.state.graphH, margin: 0}}>
                <h1>energy tracker|currently displaying: <b>{days[this.state.toggle]}</b></h1>
                <Bar ref={this.chartReference}
                data={{
                    labels: this.getCorrectLabels(),
                    datasets:[{
                        label: dataLabel[this.state.toggle],
                        data: this.getCorrectValues(),
                        backgroundColor: '#fff',
                    }]

                }} 
                width={460} height={100}
                options={{
                    maintainAspectRatio: false,
                    legend: { display: false },
                    scales: {
                        yAxes: [{ 
                            position: 'right',
                            gridLines: [{ display: false }],
                            ticks: { 
                                fontColor: '#fff',
                                fontSize: 8,
                                maxTicksLimit: 5,
                                padding: 10,
                                min: this.state.toggle ? Math.round((Math.min(...this.state.ivalues)-.1)/.1)*.1 : 
                                                         Math.round(Math.max(Math.min(...this.state.cvalues)-100, 0)/100)*100,
                            },
                            scaleLabel: {
                                display: true,
                                labelString: dataUnits[this.state.toggle],
                                fontColor: '#fff',
                                fontSize: 8,
                            },
                        }],
                        xAxes: [{ 
                            // display: true, // change this to false to remove x-axis labels
                            display: false, // change this to false to remove x-axis labels
                            ticks: {
                                maxTicksLimit: 4,
                                fontColor: '#fff',
                                fontSize: 8,
                                align: 'center',
                            }
                        }],
                    },
                    dataset: { barPercentage: .95, },
                    layout: {
                        padding: {
                            left: 0,
                            right: -4,
                            top: 10,
                            bottom: 12,
                        }
                    }
                }}
                />
            </div>
            
                <div class='lowerContainer' style={{ marginTop: 10 }}>
                    <div class='buttonContainer'>
                        <button class="defaultButton" onClick={this.setConsumptionGraph}>display personal energy use</button>
                        <button class="defaultButton" onClick={this.setIntensityGraph}>display campus energy intensity</button>
                    </div>
                    <EnergyDistribution />
                </div>
            </div>
        )
    }  
}

export default GraphInfoContainer_u_a1

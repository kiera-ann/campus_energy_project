import PropTypes from 'prop-types'
import { Component } from 'react'

class DateTime extends Component {
    constructor(props) {
        super(props);

        this.state = {
            w: 243,
            h: 140,
            color: '#42B0ED',
            dayString: 'Friday',
            dateString: '00/00/0000',
            timeString: '00:00 AM',
            days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        }
    }

    componentDidMount() {
        this.updateDate();
        this.timer = setInterval(() => this.updateDate(), 30000);
    }

    updateDate() {      
        this.setState({
            dayString: this.state.days[new Date().getDay()],
            dateString: new Date().toLocaleDateString(),
            timeString: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric' }),
        })          
    }

    render() {
        return (
            <div class='colorBox' style={{ backgroundColor: this.state.color, width: this.state.w, 
                                        height: this.state.h, marginRight: 0, borderTopRightRadius: 0, 
                                        borderBottomRightRadius: 0, marginBottom: 5 }}>
                <h1 style={{ marginBottom: 55 }}>date|time</h1>
                <p class='bottomText'> {this.state.dayString}
                <br />{this.state.dateString}
                <br />{this.state.timeString}
                </p>
            </div>
        );
    }
}

export default DateTime

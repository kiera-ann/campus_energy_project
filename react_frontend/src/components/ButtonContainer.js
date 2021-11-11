import React from 'react'

class ButtonContainer extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        return (
            <div class='buttonContainer'>
                <button class="defaultButton" onClick={(c) => this.props.upDW(c, 0)}>display personal energy use</button>
                <button class="defaultButton" onClick={(c) => this.props.upDW(c, 1)}>display campus energy intensity</button>
            </div>
        )
    } 
}

export default ButtonContainer

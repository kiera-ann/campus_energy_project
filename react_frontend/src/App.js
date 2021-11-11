import {BrowserRouter, Route, Switch} from 'react-router-dom';

// General Containers
import DateTime from './components/DateTime'
import WeatherInfo from './components/WeatherInfo'

// User Specific Containers

// User kr
import BuildingInfo_u_kr from './components/user_specific/u_kr/BuildingInfo_u_kr'
import EmissionInfo_u_kr from './components/user_specific/u_kr/EmissionInfo_u_kr'
import GraphInfoContainer_u_kr from './components/user_specific/u_kr/GraphInfoContainer_u_kr'

// User A1
import BuildingInfo_u_a1 from './components/user_specific/u_a1/BuildingInfo_u_a1'
import EmissionInfo_u_a1 from './components/user_specific/u_a1/EmissionInfo_u_a1'
import GraphInfoContainer_u_a1 from './components/user_specific/u_a1/GraphInfoContainer_u_a1'

// User A2
import BuildingInfo_u_a2 from './components/user_specific/u_a2/BuildingInfo_u_a2'
import EmissionInfo_u_a2 from './components/user_specific/u_a2/EmissionInfo_u_a2'
import GraphInfoContainer_u_a2 from './components/user_specific/u_a2/GraphInfoContainer_u_a2'

// User A3
import BuildingInfo_u_a3 from './components/user_specific/u_a3/BuildingInfo_u_a3'
import EmissionInfo_u_a3 from './components/user_specific/u_a3/EmissionInfo_u_a3'
import GraphInfoContainer_u_a3 from './components/user_specific/u_a3/GraphInfoContainer_u_a3'

// User A4
import BuildingInfo_u_a4 from './components/user_specific/u_a4/BuildingInfo_u_a4'
import EmissionInfo_u_a4 from './components/user_specific/u_a4/EmissionInfo_u_a4'
import GraphInfoContainer_u_a4 from './components/user_specific/u_a4/GraphInfoContainer_u_a4'

// User A5
import BuildingInfo_u_a5 from './components/user_specific/u_a5/BuildingInfo_u_a5'
import EmissionInfo_u_a5 from './components/user_specific/u_a5/EmissionInfo_u_a5'
import GraphInfoContainer_u_a5 from './components/user_specific/u_a5/GraphInfoContainer_u_a5'

// User A6
import BuildingInfo_u_a6 from './components/user_specific/u_a6/BuildingInfo_u_a6'
import EmissionInfo_u_a6 from './components/user_specific/u_a6/EmissionInfo_u_a6'
import GraphInfoContainer_u_a6 from './components/user_specific/u_a6/GraphInfoContainer_u_a6'

//Old general code
// import BuildingInfo_u_a2 from './components/BuildingInfo_u_a2'
// import EmissionInfo_u_a1 from './components/EmissionInfo_u_a1'
// import GraphInfoContainer_u_a1 from './components/GraphInfoContainer_u_a1'


function App() {
    return (
        <div className="container">
            <div>
                <BrowserRouter>
                    <Switch>
                        <Route path="/kr">
                            <BuildingInfo_u_kr/>
                        </Route>
                        <Route path="/a1">
                            <BuildingInfo_u_a1/>
                        </Route>
                        <Route path="/a2">
                            <BuildingInfo_u_a2/>
                        </Route>
                        <Route path="/a3">
                            <BuildingInfo_u_a3/>
                        </Route>
                        <Route path="/a4">
                            <BuildingInfo_u_a4/>
                        </Route>
                        <Route path="/a5">
                            <BuildingInfo_u_a5/>
                        </Route>
                        <Route path="/a6">
                            <BuildingInfo_u_a6/>
                        </Route>
                    </Switch>
                </BrowserRouter>
                <DateTime/>
                <WeatherInfo/>
            </div>
            <div style={{height: 293}}>
                <BrowserRouter>
                    <Switch>
                        <Route path="/kr">
                            <EmissionInfo_u_kr/>
                            <GraphInfoContainer_u_kr/>
                        </Route>
                        <Route path="/a1">
                            <EmissionInfo_u_a1/>
                            <GraphInfoContainer_u_a1/>
                        </Route>
                        <Route path="/a2">
                            <EmissionInfo_u_a2/>
                            <GraphInfoContainer_u_a2/>
                        </Route>
                        <Route path="/a3">
                            <EmissionInfo_u_a3/>
                            <GraphInfoContainer_u_a3/>
                        </Route>
                        <Route path="/a4">
                            <EmissionInfo_u_a4/>
                            <GraphInfoContainer_u_a4/>
                        </Route>
                        <Route path="/a5">
                            <EmissionInfo_u_a5/>
                            <GraphInfoContainer_u_a5/>
                        </Route>
                        <Route path="/a6">
                            <EmissionInfo_u_a6/>
                            <GraphInfoContainer_u_a6/>
                        </Route>
                    </Switch>
                </BrowserRouter>

            </div>
        </div>
    );
}

export default App;

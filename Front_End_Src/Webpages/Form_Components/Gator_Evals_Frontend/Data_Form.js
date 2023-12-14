import { Component, useCallback, useEffect, useMemo, useState, componentDidMount} from 'react'
import axios from 'axios'

export default class Form extends Component{
    constructor(props){
        super(props)
        this.state = {
            totalSum : 1,  
            scaledVector : [].concat(Array(this.props.Questions.length).fill(1/this.props.Questions.length)), 
            showOverfillWarning : "None",
            SelDept : "Mathematics", 

            // STORE VECTOR CALCULATION RESULT IN HERE:
            NameList : [] 
        }; 
    }

    async Get_Nearest_GE_Call(e){
        const data_to_send = {
            Scaled_Vect : this.state.scaledVector, 
            Selected_Department: this.state.SelDept
        }

        await axios.post("http://127.0.0.1:5000/api/Get_Nearest_GE", data_to_send, {

        })
        .then(response =>{
            this.setState({NameList : response.data}, ()=>
            console.log(this.state.NameList))
        
        }).catch(error => {
            console.log(error)
        })


    }

    SumList(list){
        let r_sum = 0; 
        for(let i = 0 ; i < list.length; i++){
            r_sum += list[i]; 
        }
        return r_sum; 
    }

    /*
        Handles the changes of in the Question department and 

    */

    HandleRateChange(e){
        // receive the q_id and q_value
        let q_id = e.target.id; 
        let q_value = parseInt(e.target.value)/100; 

        // reset the scaledVector
        let scVecCopy = [...this.state.scaledVector]; 
        scVecCopy[q_id] = q_value; 

        // Determine whether to show the value
       let diff_list = this.SumList(scVecCopy); 
       this.setState({totalSum : diff_list}); 

       let EstScore = (Math.round((diff_list - 1)*100))/100; 

        if(EstScore < 0){
            this.setState({showOverfillWarning : "Underfill"})
            
        }
        else if(EstScore > 0){
            this.setState({showOverfillWarning : "Overfill"})
        }
        else{
            this.setState({showOverfillWarning : "None"})
        }

        this.setState({scaledVector : scVecCopy})


        
    }


    /*
     OnClick() event that corresponds to dividing each value of the scaled vector
     but the sum of the scaled vector to turn it back into a probability vector
     */ 

    RescaleValues(e){
        let scaled_vector_copy = [...this.state.scaledVector]
        let scaled_sum = this.SumList(scaled_vector_copy)
        for(let i = 0; i < scaled_vector_copy.length; i++){
            scaled_vector_copy[i] = scaled_vector_copy[i]/scaled_sum
        }

        this.setState({scaledVector : scaled_vector_copy})
        this.setState({showOverfillWarning : "None"})
    }



    render(){
        return(
            <div>
                



                <h3 style={{textAlign : 'center'}}>Please Fill out the questions below (using 100% as a scale)</h3>

                <select onChange = {(e) => this.setState({SelDept : e.target.value}, ()=>console.log(this.state.SelDept))}>
                    <option>Mathematics</option>
                    <option>Computer Science</option>
                </select>
                
                {this.props.Questions.map((value, index) => 
                <div key = {index}>
                    <p>{value}</p>
                    <input type = "range" min = "0" max = "100"  id={index}
                    value = {this.state.scaledVector[index] * 100} onChange = {(e) => {this.HandleRateChange(e)}}
                    style = {{width : '200px'}}/>
                    <label style={{paddingLeft : '20px'}}>{Math.round(this.state.scaledVector[index] * 100)}%</label>
                </div>)}



                {this.state.showOverfillWarning == "Overfill" ? 
                <div>
                    <p style={{color : 'red'}}>Overfill</p>
                    <p style={{color : 'red'}}> Excess : {Math.round((this.state.totalSum - 1) * 100)}%</p>
                </div> 
                : null}

                {this.state.showOverfillWarning == "Underfill" ? 
                <div>
                    <p style={{color : 'red'}}>Underfill</p>
                    <p style={{color : 'red'}}> Remaining : {Math.round((1 - this.state.totalSum) * 100)}%</p>
                </div> 
                : null} 

                {this.state.showOverfillWarning == "None" ? 
                <div>
                    <p style={{color : 'green'}}>Perfect!</p>
                </div> 
                : null} 

                <button onClick={(e)=>this.RescaleValues(e)}>Rescale Values</button>

                {this.state.showOverfillWarning == "None" ? <button onClick = {(e) => this.Get_Nearest_GE_Call(e)}>Submit</button> : 
                <button disabled>Submit</button> }

                <ol>
                {this.state.NameList.map((value, index) => 
                
                    <li key = {index}>{value}</li>
                )}
                </ol> 

            </div>
            )
        }
}
import { Component, useCallback, useEffect, useMemo, useState, componentDidMount} from 'react'
import Plot from 'react-plotly.js';
import axios from 'axios'


const ScatterPlot = (props) => {
    const data = [
      {
        x: props.x_data,
        y: props.y_data,
        mode: 'markers',
        type: 'scatter',
        marker: { size: 12,
        color : props.color_data
    },
      },
    ];
  
    const layout = {
      title: 'tSNE Plot',
      xaxis: { title: 'X Axis' },
      yaxis: { title: 'Y Axis' },
      showlegend: true, // Hide legend for this example
    };
  
    return (
      <div>
        <Plot data={data} layout={layout} />
      </div>
    );
  };
  


export default class RMP_Expressor extends Component{
    constructor(props){
        super(props)
        this.state = {
            SelDept : "Mathematics", 
            Prof_Name : "", 
            TSNE_Perp_Slider : 5,
            K_Means_K_Count : 3, 
            X_Tsne_Plots : [10, 15, 25],
            Y_Tsne_Plots : [20, 10, 12], 
            TSNE_Clustering_Labels : [],
            max_tsne : 25,

            attribute_vectors : [], 
            colorlist : ["red", "blue", "green", "pink", "purple", "orange", "brown",
            "black", "yellow", "cyan"], 
            chosen_cluster : 0, 
        }
    }

    SetName(new_name){
      this.setState({Prof_Name : new_name}, ()=>
      this.Get_MAX_tsne_Perp())
    }

    async Get_CLUSTER_data(e){
      const data_to_send = {
        Cluster_Num : this.state.K_Means_K_Count, 
        dept_name : this.state.SelDept, 
        prof_name : this.state.Prof_Name, 
      }

      await axios.post("http://127.0.0.1:5000/api/ClusterEmbeddings", data_to_send, {

      })
      .then(response =>{
        console.log(response.data)
        this.setState({TSNE_Clustering_Labels : response.data["Point_Color_Codes"], 
        attribute_vectors : response.data["Resultant Classifcation Vectors"]},
        console.log("Look ", this.state.attribute_vectors))
        
      }).catch(error => {
          console.log(error)
      })
    }


    async Get_MAX_tsne_Perp(){
      const data_to_send = {
        dept_name : this.state.SelDept, 
        prof_name : this.state.Prof_Name
      }

      console.log(data_to_send)

      await axios.post("http://127.0.0.1:5000/api/GetDataLength", data_to_send, {

      })
      .then(response =>{
        console.log(response)
        this.setState({max_tsne : response.data["max"]}) 
      
      }).catch(error => {
          console.log(error)
      })

    }


    async Get_TSNE_data(e){
      const data_to_send = {
          dept_name : this.state.SelDept,
          tsne_perplexity : this.state.TSNE_Perp_Slider , 
          prof_name : this.state.Prof_Name, 
      }

      await axios.post("http://127.0.0.1:5000/api/TSNE_Visualization", data_to_send, {

      })
      .then(response =>{
        console.log(response.data)
        this.setState({X_Tsne_Plots : response.data['x_data'], Y_Tsne_Plots : response.data['y_data']})
      
      }).catch(error => {
          console.log(error)
      })
    }





    render(){
        return(
            <div>
                <h3 style={{textAlign:'center'}}>Text Classification using SVD</h3>
                <br></br>
                <br></br>

                <select onChange = {(e) => this.setState({SelDept : e.target.value}, ()=>console.log(this.state.SelDept))}>
                    <option>Mathematics</option>
                    <option>Computer Science</option>
                </select>

                <br></br>
                <br></br>

                <p for="name" >Please enter the professor name Here:</p>
                <input id = "name" type="text" onChange = {(e)=>this.setState({Prof_Name : e.target.value})} 
                value = {this.state.Prof_Name} placeholder = "Professor Name"/>

                <Name_List dept={this.state.SelDept} trial_name={this.state.Prof_Name} 
                PassTo = {(e) => this.SetName(e)}/>

                <br></br>
                <br></br>
                <br></br>

                <span style={{display:'flex'}}>
                <div>
                <label for="tsne_label">Tsne Perplexity</label>
                <span style={{display : 'flex'}}>
                <input type='range' for = "tsne_label" min = {2} max = {this.state.max_tsne} onChange = {(e) => this.setState({TSNE_Perp_Slider : e.target.value})}/>
                <p>{this.state.TSNE_Perp_Slider}</p>
                </span>
                <button onClick = {(e) => this.Get_TSNE_data(e)}>Recalculate TSNE</button>

                <br></br>
                <br></br>

                <label for="K_Means_Label">K Means Cluster</label>
                <span style={{display : 'flex'}}>
                <input type='range' for="K_Means_Label" min = {2} max = {10} onChange = {(e) => this.setState({K_Means_K_Count: e.target.value})}/>
                 <p>{this.state.K_Means_K_Count}</p>
                 </span>
                 <button onClick = {(e) => this.Get_CLUSTER_data(e)}>Recalculate KMeans</button>
                </div>

                
                 

                <div style = {{display : 'flex'}}>

                

                
                
                 <ScatterPlot x_data = {this.state.X_Tsne_Plots} y_data = {this.state.Y_Tsne_Plots} color_data = {this.state.TSNE_Clustering_Labels}/>
                <div style={{display : 'flex'}}>
                 <div>
                 <table>
                 {this.state.attribute_vectors.map((values, index) => 
                  <tr> <button style = {{color : this.state.colorlist[index]}} key = {index} id = {index}
                  onClick = {(e) => this.setState({chosen_cluster : e.target.id})}>Cluster {index}</button>
                  </tr>
                )}
                </table>
                </div> 

                <div>
                { this.state.attribute_vectors.length > 0 ? 
                
          
                
                <table>
                  <th>Category</th>
                  <th>Score</th>
                  {this.state.attribute_vectors[this.state.chosen_cluster][1].map((values, index) => 
                      
                      
                      <tr index={index}>
                        <td>{values[0]}</td>
                        <td>{Math.round(values[1] * 100) / 100}</td>
                      </tr>
                  )}

                </table>
                : 
                null

                }
                </div>




                </div>
                </div>
                 </span>
            </div>
            
        )
    }

}

class Name_List extends Component{
  constructor(props){
    super(props)
    this.state = {
      cs_names : ['Lisa Anthony', 'Arunava Banerjee', 'Vincent Bindschaedler', 'Christina Boucher', 'Shigang Chen', 'Sharon Lynn Chu', 'Laura Melissa Cruz Castro', 'Alin Dobra', 'Alireza Entezari', 'Joshua Fox', 'Kiley Graim', 'Christan Grant', 'Ahmed Helmy', 'Kejun Huang', 'Eakta Jain', 'Tamer Kahveci', 'Jonathan Kavalan', 'Kyla McMullen', 'Prabhat Mishra', 'Jorg Peters', 'Eric Ragan', 'Anand Rangarajan', 'Sanjay Ranka', 'Cheryl Resch', 'Jaime Ruiz', 'Markus Schneider', 'Alexandre Gomes de Siqueira', 'Meera Sitharam', 'Patrick Traynor', 'Daisy Zhe Wang', 'Joseph N. Wilson', 'Rong Zhang', 'Lisha Zhou'],
      math_names : [' Henry Adams', ' Stephen Adams', ' Krishnaswami Alladi', ' Dana Bartosova', ' Alexander Berkovich', ' Philip Boyland', ' Patrick Carmichael', ' Kwai-Lee Chui', ' Richard Crew', ' Carol Demas', ' Luca Fabrizio Di Cerbo', ' Alex Dranishnikov', ' David Groisser', ' Zachary Hamaker', ' Jason Harrington', ' Shu-Jen Huang', ' Nan Jiang', ' Michael Jury', ' Kevin Keating', ' Willard Scott Keeran', ' Jonathan King', ' Kevin Knudson', ' Arnaud Marsiglietti', ' Maia Martcheva', ' Scott McCullough', ' Calistus Ngonghala', ' Jason Nowell', ' Youngmin Park', ' Sergei Pilyugin', ' Sara Pollock', ' Ross Ptacek', ' Paul Robinson', ' Libin Rong', ' Yuli Rudyak', ' Sergei Shabanov', ' Peter Sin', ' Tracy Stepien', ' John Streese', ' Vincent Vatter', ' Andrew Vince', ' Hubert Wagner', ' Chunmei Wang', ' Larissa Williamson', ' Alex York', ' Cheng Yu', ' Jindrich Zapletal', ' Lei Zhang']
    }
  }

  getClosest(trial){
    let name_list = []
    let in_list = []
    if (this.props.dept == "Computer Science"){
      name_list = this.state.cs_names
    }
    else{
      name_list = this.state.math_names
    }

    for(let i =  0 ; i < name_list.length; i++){
      if(name_list[i].includes(trial)){
        in_list.push(name_list[i])
      }
    }

    return in_list
  }

  PassOutput(e){
    this.props.PassTo(e.target.id)
  }

  

  render(){
    return(
      <div style={{overflow:"auto", height: "200px"}}>; 
        <table>
          {this.getClosest(this.props.trial_name).map((value, index) => 
          <tr key = {index}>
            <td>{value}</td>
            <td><input value = "Choose" type="Button" id={value} onClick = {(e) => this.PassOutput(e)}/></td>
          </tr>)}

        </table>



      </div>
    )
  }


}



import logo from './logo.svg';
import './App.css';
import Form from './Webpages/Form_Components/Gator_Evals_Frontend/Data_Form.js'
import RMP_Expressor from './Webpages/RMP_Components/RMP_Expressor.js'

function App() {
  return (
    
    <div>
    <h1 style = {{textAlign : 'center'}}>EigenReview</h1>

    <Form Questions = {["I appreciate when the instructor is enthusiastic about the course. [False -> True]", 
    "When instructors give a lecture, it is important [For me to attend lecture for attendance purposes, but I learn everything on my own anyways -> For the instructor to explain material clearly and in a way that enhances my understanding]", 
    "I value when instructors have clear standards for responses and availability [False->True]", 
    "My ideal learning environment looks like: [Attending lectures but just there to listen and leave->Engaging with the instructor during lectures, office hours, etc.]", 
    "I value the prompt feedback that instructors give on my work and performance in the course [False->True]", 
    "I prefer to learn by [Myself->The instructor]", 
    "I find it most important for course content to be [Easy assignments and readings for an easy A->Relevant and useful for my major and intended career path]",
  "I prefer to have [Minimal interaction with the instructor->Regular interaction with the instructor]", 
  "During the course, I want assignments and activities that [Are easy and quick to complete  -> May be on the harder side, but improve my ability to analyze, solve problems, and think critically]", 
  "It is important for me for courses to be  [Something to get done because its required -> A valuable educational experience]"]}/>
    <RMP_Expressor/>
    </div>

  )
}

export default App;

# import autogen

# # Define event parameters
# event_type = 'farewell'
# number_of_people = 50
# budget_max = 20000
# working_team_size = 5

# # Configure the LLM
# llm_config = {
#     "model": "phi3",
#     "api_key": "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",
#     "base_url": "http://localhost:1234/v1",
#     "max_tokens": 1000,
#     "timeout": 300,
#     "cache_seed": 42
# }

# def plan_event(event_type, number_of_people, budget_max, working_team_size):

#     Message_prompt = {
#     "role": "system",
#     "content": f"""
#     Please note that all costs are in Indian Rupees.
    
#     We are organizing a single-day event, specifically a {event_type}. The key details are as follows:
#     - Expected number of attendees: {number_of_people}
#     - Maximum budget: {budget_max} INR
#     - Number of team members involved in organizing: {working_team_size}
    
#     Please create a comprehensive plan for the event that includes:
#     - A detailed list of all tasks and responsibilities required for the event.
#     - Time and cost estimates for each task, along with prioritization of tasks.
#     - Clear work distribution among the team members, assigning specific tasks to each member.
    
#     The output should be structured in the following format:
    
#     EVENT PLAN FOR: {event_type}
    
#     TASK LIST:
#     1. Task 1: Detailed task description - Estimated Cost: Rs X
#     2. Task 2: Detailed task description - Estimated Cost: Rs Y
#     ...
    
#     TEAM ASSIGNMENTS:
#     PERSON 1: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
#     PERSON 2: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
#     ...
#     PERSON N: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
    
#     Please ensure that the plan is realistic, practical, and takes into account potential challenges. The plan should also include any recommendations for optimizing the budget and resources.
    
#     END OF MESSAGE
#     """
#     }



#     # Message_prompt = {
#     #     "role": "system",
#     #     "content": f"""
#     #     Note that all the payments are in Indian Rupee 
#     #     We are planning a single-day event, specifically a {event_type}. Here are the details:
#     #     - Number of people attending: {number_of_people}
#     #     - Budget maximum: {budget_max}
#     #     - Number of working team members: {working_team_size}
        
#     #     Create a detailed plan for the event including:
#     #     - A list of tasks and assignments for the working team members
#     #     - Time and cost estimates for each task
#     #     - Work distribution among team members
        
#     #     The output should be in the following format:
#     #     EVENT: {event_type}
#     #     THINGS NEEDED TO DO(LIST):

#     #     WORK DISTRIBUTION:
#     #     PERSON 1: Task description - Cost Rs
#     #     PERSON 2: Task description - Cost Rs, Time duration
#     #     PERSON 3: Task description - Cost Rs
#     #     ...
#     #     ...
#     #     PERSON N: Task description - Cost Rs
        
#     #     TERMINATE
#     #     """
#     # }

#     # Define the agents
#     user_proxy = autogen.UserProxyAgent(
#         name="Admin",
#         system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
#         code_execution_config={
#             "work_dir": "code",
#             "use_docker": False
#         },
#         human_input_mode="TERMINATE",
#     )

#     budget_manager = autogen.AssistantAgent(
#         name="Budget Manager",
#         llm_config=llm_config,
#         system_message="Budget Manager. Focus on minimizing the budget while ensuring all tasks are covered.",
#     )

#     event_coordinator = autogen.AssistantAgent(
#         name="Event Coordinator",
#         llm_config=llm_config,
#         system_message="Event Coordinator. Plan and schedule all activities and ensure smooth execution.",
#     )

#     logistics_manager = autogen.AssistantAgent(
#         name="Logistics Manager",
#         llm_config=llm_config,
#         system_message="Logistics Manager. Handle all logistics including setup, decorations, and other requirements.",
#     )

#     planner = autogen.AssistantAgent(
#         name="Planner",
#         llm_config=llm_config,
#         system_message="Planner. Suggest an event plan. Revise the plan based on feedback from admin and critic, until admin approval.",
#     )

#     critic = autogen.AssistantAgent(
#         name="Critic",
#         llm_config=llm_config,
#         system_message="Critic. Double check the plan, claims, code from other agents and provide feedback.",
#     )

#     retrieval_agent = autogen.AssistantAgent(
#         name="Retrieval Agent",
#         llm_config=llm_config,
#         system_message="Retrieve relevant information about vendors, decorations, and other resources needed for the event.",
#     )

#     # Initialize the group chat
#     group_chat = autogen.GroupChat(
#         agents=[user_proxy, budget_manager, event_coordinator, logistics_manager, planner, critic, retrieval_agent], 
#         messages=[Message_prompt], 
#         max_round=6
#     )

#     # Manage the group chat
#     manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

#     try:
#     # Start the conversation
#         user_proxy.initiate_chat(manager, message=Message_prompt)
#     except:
#         pass

    
#     q = group_chat.messages[1]['content']
    
#     lines = q.split('\n')
#     ans = ""
#     for line in lines:
#         ans += line + '\n'
    
#     with open('output.txt', 'w') as file:
#         file.write(ans)
    
#     return
#     # Check the messages after initiating the chat
#     # for msg in group_chat.messages:
#     #     print(msg.get('content', 'No content available'))


# plan_event(event_type, number_of_people, budget_max, working_team_size)




import autogen
import streamlit as st
import re


st.header('AI POWERED Event Manager 🎉')
st.subheader('Get a plan for your event in your way!!!')

#st.image("sunrise.jpg", caption="Sunrise by the mountains")
import streamlit as st
import streamlit.components.v1 as components

# Create a directory named 'static' in your project folder and place your images there

components.html(
    """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {box-sizing: border-box;}
body {font-family: Verdana, sans-serif;}
.mySlides {display: none;}
img {vertical-align: middle;}

/* Slideshow container */
.slideshow-container {
  max-width: 1000px;
  position: relative;
  margin: auto;
}

/* Caption text */
.text {
  color: #f2f2f2;
  font-size: 15px;
  padding: 8px 12px;
  position: absolute;
  bottom: 8px;
  width: 100%;
  text-align: center;
}

/* Number text (1/3 etc) */
.numbertext {
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
}

/* The dots/bullets/indicators */
.dot {
  height: 15px;
  width: 15px;
  margin: 0 2px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease;
}

.active {
  background-color: #717171;
}

/* Fading animation */
.fade {
  animation-name: fade;
  animation-duration: 1.5s;
}

@keyframes fade {
  from {opacity: .4} 
  to {opacity: 1}
}

/* On smaller screens, decrease text size */
@media only screen and (max-width: 300px) {
  .text {font-size: 11px}
}
</style>
</head>
<body>

<p style='color:white';>Some of the places to choose from!</p>

<div class="slideshow-container">

<div class="mySlides fade">
  <div class="numbertext">1 / 2</div>
  <img src="https://img.freepik.com/premium-photo/happy-birthday-card-with-colorful-flags-confetti-white-background_962620-1469.jpg?uid=R160477416&ga=GA1.1.1563751239.1719004029&semt=ais_hybrid" style="width:100%">
  <div class="text">Birthday</div>
</div>

<div class="mySlides fade">
  <div class="numbertext">2 / 2</div>
  <img src="https://img.freepik.com/free-photo/group-people-cheering-arms-raised-joy-generated-by-ai_188544-39282.jpg?uid=R160477416&ga=GA1.1.1563751239.1719004029&semt=ais_hybrid" style="width:100%">
  <div class="text">farewell</div>
</div>

</div>
<br>

<div style="text-align:center">
  <span class="dot"></span> 
  <span class="dot"></span> 
</div>

<script>
let slideIndex = 0;
showSlides();

function showSlides() {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}    
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
  setTimeout(showSlides, 2000); // Change image every 2 seconds
}
</script>

</body>
</html>
    """,
    height=600,
)



event_type = 'farewell'
number_of_people = 50
budget_max = 20000
working_team_size = 5

# Configure the LLM
llm_config = {
    # zephyr-7B-beta-GGUF
    "model": "TheBloke/zephyr-7B-beta-GGUF",
    "api_key": "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",
    "base_url": "http://localhost:1234/v1",
    "max_tokens": 1000,
    "timeout": 300,
    "cache_seed": 43
}

def plan_event(event_type, number_of_people, budget_max, working_team_size,additional_context):

    Message_prompt = {
    "role": "system",
    "content": f"""
    Please note that all costs are in Indian Rupees.
    
    We are organizing a single-day event, specifically a {event_type}. The key details are as follows:
    - Expected number of attendees: {number_of_people}
    - Maximum budget: {budget_max} INR
    - Number of team members involved in organizing: {working_team_size}
    -Additional instryuctions : {additional_context}
    Please create a comprehensive plan for the event that includes:
    - A detailed list of all tasks and responsibilities required for the event.
    - Time and cost estimates for each task, along with prioritization of tasks.
    - Clear work distribution among the team members, assigning specific tasks to each member.
    
    The output should be structured in the following format:
    
    EVENT PLAN FOR: {event_type}
    
    TASK LIST:
    1. Task 1: Detailed task description - Estimated Cost: Rs X
    2. Task 2: Detailed task description - Estimated Cost: Rs Y
    ...
    
    TEAM ASSIGNMENTS:
    PERSON 1: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
    PERSON 2: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
    ...
    PERSON N: Assigned Task(s) - Estimated Cost: Rs Z - Estimated Time: T hours
    
    Please ensure that the plan is realistic, practical, and takes into account potential challenges. The plan should also include any recommendations for optimizing the budget and resources.
    OTHER RECOMMENDATIONS FOR OPTIMIZING BUDGET AND RESOURCES
    END OF MESSAGE
    """
    }

    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
        code_execution_config={
            "work_dir": "code",
            "use_docker": False
        },
        human_input_mode="TERMINATE",
    )

    budget_manager = autogen.AssistantAgent(
        name="Budget Manager",
        llm_config=llm_config,
        system_message="Budget Manager. Focus on minimizing the budget while ensuring all tasks are covered.",
    )

    event_coordinator = autogen.AssistantAgent(
        name="Event Coordinator",
        llm_config=llm_config,
        system_message="Event Coordinator. Plan and schedule all activities and ensure smooth execution.",
    )

    logistics_manager = autogen.AssistantAgent(
        name="Logistics Manager",
        llm_config=llm_config,
        system_message="Logistics Manager. Handle all logistics including setup, decorations, and other requirements.",
    )

    planner = autogen.AssistantAgent(
        name="Planner",
        llm_config=llm_config,
        system_message="Planner. Suggest an event plan. Revise the plan based on feedback from admin and critic, until admin approval.",
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        llm_config=llm_config,
        system_message="Critic. Double check the plan, claims, code from other agents and provide feedback.",
    )

    retrieval_agent = autogen.AssistantAgent(
        name="Retrieval Agent",
        llm_config=llm_config,
        system_message="Retrieve relevant information about vendors, decorations, and other resources needed for the event.",
    )

    # Initialize the group chat
    group_chat = autogen.GroupChat(
        agents=[user_proxy, budget_manager, event_coordinator, logistics_manager, planner, critic, retrieval_agent], 
        messages=[Message_prompt], 
        max_round=6
    )

    # Manage the group chat
    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    try:
    # Start the conversation
        user_proxy.initiate_chat(manager, message=Message_prompt)
    except:
        pass

    
    q = group_chat.messages[1]['content']
    
    lines = q.split('\n')
    ans = ""
    for line in lines:
        ans += line + '\n'

    
    with open('output.txt', 'w') as file:
        file.write(ans)
    st.write(ans)
    # task_pattern = r"(\d+\.\s.+?\s-\sEstimated\sCost:\sRs\s\d+\s-\sEstimated\sTime:\s.+?\nTasks\sand\sresponsibilities:.+?)(?=\n\d+\.|\Z)"
    # team_pattern = r"(PERSON\s\d+\s\(.*?\):\s.+?)(?=\nPERSON\s\d+|\Z)"

    # tasks = re.findall(task_pattern, ans, re.DOTALL)
    # team_assignments = re.findall(team_pattern, ans, re.DOTALL)
    # print(tasks,team_assignments)
    # st.subheader("Task")
    # for task in tasks:
    #     st.text(task.strip())

    # st.subheader("Team Assignments")

    # for assignment in team_assignments:
    #     st.text(assignment.strip())
    return ans
  


  

st.markdown("# :calendar: Event Planner")
event_type = st.text_input(":tada: Event Type", "farewell")
number_of_people = st.number_input(":busts_in_silhouette: Number of People Attending", min_value=1, value=50)
budget_max = st.number_input(":moneybag: Maximum Budget (INR)", min_value=0, value=20000)
working_team_size = st.number_input(":handshake: Working Team Size", min_value=1, value=5)
additional_context = st.text_input("📝 Additinal Information")

if st.button(":rocket: Submit"):
    plan_event(event_type, number_of_people, budget_max, working_team_size,additional_context)
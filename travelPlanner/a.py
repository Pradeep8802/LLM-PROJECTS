import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import streamlit as st
import pandas as pd


# GENERATE DATA FOR RAG
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Travel Itinerary & Budget", page_icon="🌍", layout="wide")
def fetch_content(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except requests.RequestException:
        return ""

def func(location_name):
    search_url = f"https://www.google.com/search?q={requests.utils.quote(location_name)}"
    
    r = requests.get(search_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    ans = soup.get_text(separator='\n', strip=True)

    all_links = soup.find_all('a', href=True)
    count = 0

    for link in all_links:
        href = link.attrs['href']
        if href.startswith('/url?q='):
            # Extract actual URL by stripping the prefix and additional parameters
            actual_url = href[7:].split('&')[0]
            ans += fetch_content(actual_url)
            count += 1
            if count >= 5:  # Stop after fetching content from 5 links
                break
    
    return ans


def write_output(ans):

    # Extract days and events using regular expressions
    days_events = re.findall(r"(Day \d+ \(.*?\))(.*?)(?=Day \d+ \(|$)", ans, re.DOTALL)
    budget_breakdown = re.search(r"Total Budget Breakdown:(.*)", ans, re.DOTALL).group(1).strip()

    # Streamlit setup

    st.title("Travel Itinerary & Budget Breakdown")

    # Display the itinerary
    for day, events in days_events:
        st.subheader(day)
        events = re.sub(r'\d+\.\s*', '- ', events).strip()  # Convert numbered items to bullet points
        st.markdown(events)

    # Display the budget breakdown
    st.subheader("Budget Breakdown")
    st.markdown(budget_breakdown)

    # Add a cool footer
    st.markdown("""
        <style>
        footer {
            visibility: hidden;
        }
        </style>
        <footer>
        <p style='text-align: center;'>🧳 Safe Travels and Enjoy Your Trip! 🚀</p>
        </footer>
        """, unsafe_allow_html=True)



def f(no_of_people ,start_location ,end_location, location,start_date,end_date,context):

    # LLM CONFIGURATION
    llm_config = {
        "model": "TheBloke/zephyr-7B-beta-GGUF",
        "api_key": "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",
        "base_url": "http://localhost:1234/v1",
        "max_tokens": 1000,
        "timeout": 300,
        "cache_seed": 42
    }

    # storing 
    from chromadb.utils import embedding_functions

    huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key="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",
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # location='Delhi'
    # location='tourist places '+location
    ans=func(location)
    with open(f"travel/{location}_data.txt", 'w', encoding='utf-8') as f:
        f.write(ans)

    f.close()

    user_proxy = RetrieveUserProxyAgent(
        name="Admin",
        system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved "
                    "by this admin.",
        code_execution_config={
            # "work_dir": "travel",
            "use_docker": False
        },
        retrieve_config={
            "task": "qa",
            "docs_path": f"travel/{location}_data.txt",
            "embedding_function": huggingface_ef,

        },
        human_input_mode="TERMINATE",
    )

    budget_manager = autogen.AssistantAgent(
        name="Budget Manager",
        llm_config=llm_config,
        system_message="""Budget Manager. Focus on minimizing the budget without sacrificing comfort.""",
    )

    transport_manager = autogen.AssistantAgent(
        name="Transport Manager",
        llm_config=llm_config,
        system_message="""Transport Manager. Decide the mode of transport (bus, cab, auto) based on budget and comfort for the given number of people.""",
    )

    hotel_manager = autogen.AssistantAgent(
        name="Hotel Manager",
        llm_config=llm_config,
        system_message="""Hotel Manager. Book hotels and ensure comfortable accommodations.""",
    )

    travel_manager = autogen.AssistantAgent(
        name="Travel Manager",
        llm_config=llm_config,
        system_message="""Travel Manager. Plan the itinerary to cover the most places comfortably within the given time frame.""",
    )
    planner = autogen.AssistantAgent(
        name="Planner",
        system_message="""Planner. Suggest a travel plan. Revise the plan based on feedback from admin and critic, until admin approval.
    The plan may involve a budget manager, transport manager, hotel manager, and travel manager.
    Explain the plan first. Be clear which step is performed by each manager.""",
        llm_config=llm_config,
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        system_message="Critic. Double check the plan, claims, code from other agents and provide feedback. Ensure the plan includes verifiable info such as source URL.",
        llm_config=llm_config,
    )
    huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key="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",
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    retrieval_agent = autogen.AssistantAgent(
        name="Retrieval Agent",
        llm_config=llm_config,
        system_message=f"Retrieve relevant information about transportation, hotels, and places to visit in {location}.",
    
    )

    group_chat = autogen.GroupChat(
        agents=[user_proxy, budget_manager, transport_manager, hotel_manager, travel_manager, planner, critic, retrieval_agent], 
        messages=[], 
        max_round=12
    )

    # 'Try to cover more places, have a comfort, trip avoid public transport when every possible at a budget close to 50,000 INR, also on end date, reach 2 hours before to Hyd Airport'
        

    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)
    # Message_prompt=f"""
    #     NOT A PYTHON CODE, give me text as below for my prompt
    #     MAKE SURE EACH PROMPT GENERATES LESS THAN 500 TOKENS FOR EACH DAY, IF NEEDED , COMPROMISE THE ENGLISH GRAMMER WORDS AND WRITE ONLY THE MAIN STUFF
    #     Assume user has choosen following values, then sample output is as follows:
    #     - Number of people: {no_of_people}
    #     - Start location: {start_location}
    #     - End location: {end_location}
    #     - Location: {location}
    #     - Start date: {start_date}
    #     - End date: {end_date}
    #     - Start time: {start_time}
    #     - End time: {end_date}
    #     - Context: {context}

    #     Create a travel plan considering all the details and roles. The final output should include:
    #     - Daily itinerary with transport and hotel bookings
    #     - Total budget breakdown
    #     Below is just the expected format of output, assume user asked for hyderabad with starting daya time at 9am, for 5 days and reach airport 2 hrs before 21:00, 
    #     Day 1 (Start date)
    #     i. Reached hyderabad at 9am
    #     ii. Book a cab to the hotel named ..... fair = 200Rs
    #     iii. Then go to the ... in a cab, fair = 500Rs
    #     ...
    #     ...
    #     ...
    #     Day 5 (end date)
    #     i. ..
    #     ii. ..
    #     ..
    #     ..
    #     .. Vacate the room
    #     .. Start to the airport around .... book cab, cab fair = 600Rs
    #     ... Reached the airport 2 hours before 21:00 IST
        
    #     At the end, provide the total budget as the sum of each manager's cost, e.g., 5000Rs (travel) + 4000Rs (hotel).... = 15000Rs
    #     TERMINATE
    #     """
    
    Message_prompt = f"""
NOT A PYTHON CODE, give me text as below for my prompt.
MAKE SURE EACH PROMPT GENERATES LESS THAN 500 TOKENS FOR EACH DAY. IF NEEDED, COMPROMISE ON ENGLISH GRAMMAR AND FOCUS ONLY ON MAIN POINTS.
Assume user has provided the following values:
- Number of people: {no_of_people}
- Start location: {start_location}
- End location: {end_location}
- Location: {location}
- Start date: {start_date}
- End date: {end_date}
- Start time: {start_time}
- End time: {end_time}
- Context: {context}

Create a travel plan specific to {location}, considering all the details and roles. The final output should include:
- Daily itinerary with transport and hotel bookings
- Total budget breakdown

Below is the expected format of the output, assuming the user selected {location} with a start time at {start_time}, for {end_date - start_date} days and reaching the airport 2 hours before {end_time} on the final day:

Day 1 ({start_date})
i. Reached {location} at {start_time}
ii. Book a cab to the hotel named XYZ Hotel - Fare: 200Rs
iii. Visit place1 in a cab - Fare: 500Rs
...
...

Day {end_date - start_date} ({end_date})
i. Breakfast at the hotel - No cost
ii. Check out from XYZ Hotel
iii. Book a cab to {end_location} Airport, leaving around .... - Fare: 600Rs
iv. Reach airport 2 hours before departure

At the end, provide the total budget as the sum of each manager's cost, e.g., 5000Rs (travel) + 4000Rs (hotel) + ... = 15000Rs

TERMINATE
"""

    try:
        user_proxy.initiate_chat(
            manager,
            message=Message_prompt
        )
    except:
        pass

    q = group_chat.messages[1]['content']
    lines = q.split('\n')
    ans = ""

    for line in lines:
        ans += line + '\n'
    # st.write(ans)
    # print(ans)
    # with open('output_final.txt', 'w') as file:
    #     file.write(ans)
    # file.close()


    # try:
    #         # Start the conversation
    #         user_proxy.initiate_chat(
    #             manager,
    #             message=Message_prompt
    #         )
    # except:
    #         pass
    # q=group_chat.messages[1]['content']
    st.markdown("""---""")
    st.write('Travel Plan')
    st.markdown("""---""")
    # lines=q.split('\n')
    # ans=""
    # for line in lines:
    #     ans+=line+'\n'
    return ans

st.header('AI POWERED TRAVEL PLANNER🌍✈️')
st.subheader('Make your travel plan now!!!')
st.subheader("Start Your Adventure 🚀")
st.text("")
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
  <div class="numbertext">1 / 3</div>
  <img src="https://img.freepik.com/free-photo/aerial-view-beautiful-sky-road-top-mountains-with-green-jungle-nan-province-thailand_335224-1063.jpg?w=900&t=st=1723358727~exp=1723359327~hmac=0db90966c1b98ff450e5b1285f5f4aa046a1aac8d124a02cb1022f0bba8b70c7" style="width:100%">
  <div class="text">ooty</div>
</div>

<div class="mySlides fade">
  <div class="numbertext">2 / 3</div>
  <img src="https://img.freepik.com/free-photo/high-angle-shot-wooden-house-surrounded-by-forested-mountain-covered-snow-winter_181624-10162.jpg?size=626&ext=jpg&ga=GA1.1.1563751239.1719004029&semt=ais_hybrid" style="width:100%">
  <div class="text">manali</div>
</div>

<div class="mySlides fade">
  <div class="numbertext">3 / 3</div>
  <img src="https://img.freepik.com/free-photo/swimming-pool_74190-2104.jpg?ga=GA1.1.1563751239.1719004029&semt=ais_hybrid" style="width:100%">
  <div class="text">goa</div>
</div>

</div>
<br>

<div style="text-align:center">
  <span class="dot"></span> 
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


st.write('Fill your data below, and get the plan!!!')

no_of_people = st.number_input(label='Number of People',value=4, min_value=1, step=1, max_value=10)

start_location = st.text_input(label='Start Location', value='RGIA AIRPORT')
end_location = st.text_input(label='End Location', value='RGIA AIRPORT')
location = st.text_input(label='Location', value='Hyderabad')

start_date = st.date_input(label='Start Date', value=pd.to_datetime('2024-06-21'))
end_date = st.date_input(label='End Date', value=pd.to_datetime('2024-06-23'))

start_time = st.time_input(label='Start Time', value=pd.to_datetime('09:00').time())
end_time = st.time_input(label='End Time', value=pd.to_datetime('17:00').time())

context = st.text_area(label='Context', value='Try to cover more places, have a comfort, trip avoid public transport when every possible at a budget close to 50,000 INR, also on end date, reach 2 hours before to Hyd Airport')

if st.button('Curate my travel vibes!!!'):
    ans = f(no_of_people, start_location, end_location, location, start_date, end_date, context)
    st.write(ans)
    st.markdown("### 🚗 Happy Journey!")
    # write_output(ans)
    
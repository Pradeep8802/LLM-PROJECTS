import streamlit as st
import pandas as pd
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from streamlit_option_menu import option_menu

from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer

import requests
import urllib.parse
import os 
import random

import json
from chromadb.utils import embedding_functions
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key="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",
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
import autogen


import os
import requests
# put your hugging face api key here
HUGGINGFACE_KEY=""
# omdb api keys here
api_key=""

def scrape_info(name, folder_path):

    url = f"https://example.com/search?query={name}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return
    html_content = response.text
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, 'a.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"Complete page saved to {file_path}")


def makedata(curr_data,movie_name):
    random_int = random.randint(1000, 9999) 
    folder_name = f"{random_int}_curr_data"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, "a.txt")
    
    curr_data=json.dumps(curr_data)
    with open(file_path, "w") as file:
        file.write(curr_data)
    scrape_info(movie_name, folder_name)
    return folder_name

def RAG(folder_name,movie_name):
    os.environ['HUGGINGFACEHUB_API_TOKEN'] = HUGGINGFACE_KEY
    
    llm_config = {
        "model": "TheBloke/zephyr-7B-beta-GGUF",
        "api_key": HUGGINGFACE_KEY,
        "base_url": "http://localhost:1234/v1",
        "max_tokens": 1000,
        "timeout": 300,
        "cache_seed": 42
    }
    user_proxy = RetrieveUserProxyAgent(
        name="Admin",
        system_message="A human admin. Interact with the movie lover and data to understand. Don't ask human to end conversation, just end when right.",
        code_execution_config={"use_docker": False},
        retrieve_config={
            "task": "qa",
            "docs_path": folder_name,
            "embedding_function": huggingface_ef,
        },
        human_input_mode="TERMINATE",
    )

    movie_lover = autogen.AssistantAgent(
        name="Movie Lover",
        llm_config=llm_config,
        system_message="""Movie Lover. With given information of the movie, and with your knowledge, try your best to create curiosity in the user.""",
    )

    prevent_spoiler = autogen.AssistantAgent(
        name="",
        llm_config=llm_config,
        system_message="""Prevent the agent providing spoiler to the movie. Your role is to scrutinize the review for potential spoilers. Ensure the story and review only include non-spoiler content, and politely rephrase or remove any content that could ruin key plot points for someone who hasn't seen the movie.""",
    )

    group_chat = autogen.GroupChat(
        agents=[user_proxy, movie_lover, prevent_spoiler],
        messages=[],
        max_round=4,
    )

    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    Message_prompt = f"""
        NOT A PYTHON CODE, provide text for the following prompt.
        Given the movie {movie_name},
        I need a clear and engaging movie review format that includes:
        1. **General Overview:** Start with a brief, common summary of the movie to set the stage.
        2. **Movie Story:** Provide a concise description of the movie's plot, highlighting key elements.
        3. **Key Points:** End with a few intriguing points or aspects of the movie to spark curiosity.

        The data needed to create this review is already provided using RAG (retrieval-augmented generation).
        Fit the final response in less than 800 words, dont give too much description. 
        When the task is completed, end the conversation with TERMINATE.
        TERMINATE
    """

    try:
        user_proxy.initiate_chat(manager, message=Message_prompt)
    except Exception as e:
        print(f"Error: {e}")
    q = group_chat.messages[1]['content']
    lines = q.split('\n')
    ans = ""

    for line in lines:
        ans += line + '\n'
    st.write(ans)


def fetch_movie_details(movie_name, api_key):
    # url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
    import re
    movie_name = re.sub(r'\s*\(\d{4}\)', '', movie_name)
    movie_name = urllib.parse.quote(movie_name)

    url=f'https://www.omdbapi.com/?t={movie_name}&apikey={api_key}'
    response = requests.get(url)
    ans= response.json()
    return ans


def getLLM(movie_name):
    if movie_name:
        print(movie_name)
        movie_data = fetch_movie_details(movie_name, api_key)
        if movie_data['Response'] == 'True':
            st.title(f"{movie_data['Title']} ({movie_data['Year']})")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie_data['Poster'], use_column_width=True)
            with col2:
                st.markdown(f"**🎬 Rating:** {movie_data['Rated']}")
                st.markdown(f"**📅 Released:** {movie_data['Released']}")
                st.markdown(f"**⏳ Runtime:** {movie_data['Runtime']}")
                st.markdown(f"**🎥 Genre:** {movie_data['Genre']}")
                st.markdown(f"**🎬 Director:** {movie_data['Director']}")
                st.markdown(f"**✍️ Writer:** {movie_data['Writer']}")
                st.markdown(f"**🎭 Actors:** {movie_data['Actors']}")
                st.markdown(f"**📝 Plot:** {movie_data['Plot']}")
                st.markdown(f"**🌐 Language:** {movie_data['Language']}")
                st.markdown(f"**🌍 Country:** {movie_data['Country']}")
                st.markdown(f"**🏆 Awards:** {movie_data['Awards']}")
                
                st.subheader("Ratings")
                for rating in movie_data['Ratings']:
                    st.markdown(f"- **{rating['Source']}:** {rating['Value']}")
                st.markdown(f"**🎯 Metascore:** {movie_data['Metascore']}")
                st.markdown(f"**⭐ IMDb Rating:** {movie_data['imdbRating']}")
                st.markdown(f"**🗳️ IMDb Votes:** {movie_data['imdbVotes']}")
                st.markdown(f"**💰 Box Office:** {movie_data['BoxOffice']}")
                st.markdown(f"**🏢 Production:** {movie_data['Production']}")
                st.markdown(f"**🔗 Website:** {movie_data['Website']}")
            RAG(makedata(movie_data,movie_name),movie_name)
        else:
            st.write("We couldn't perform further analysis as we didn't find that movie in our database. Please check the name.")        
    else:
        st.write("Please enter a movie name.")


st.header('Movie Recommender 🎬!!!')
st.subheader('Your Movie Suggester')
@st.cache_data
def load_movie_titles(file_path):
    movie = pd.read_csv(file_path)
    return movie['title'].tolist()

file_path = "moviedata/movies.csv"
movies = load_movie_titles(file_path)

@st.cache_data
def recommender1():
    df  = pd.read_csv("moviedata/movies.csv")
    # df.head()
    df =  df.drop_duplicates()
    def processGenre(s):
        genres = s.split('|')
        ans=''
        for genre in genres:
            ans=ans+' '+genre
        return ans

    for index,row in df.iterrows():
        df.loc[index,'genres']=processGenre(row['genres'])

    tf_rep=TfidfVectorizer(stop_words = "english")
    tf_idf = tf_rep.fit_transform(df["genres"])
    cosine_similarity = linear_kernel(tf_idf,tf_idf)
    return df,cosine_similarity

rec1_df,cos_sim=recommender1()

def content_recommendation(movie_name, df, cosine_similarity, count=5):
    row = df[df['title'] == movie_name].index[0]
    similarity = []
    for index in df.index:
        similarity.append(cosine_similarity[row, index])
    
    similarity_scores = list(enumerate(similarity))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in similarity_scores[1:count+1]]
    return df['title'].iloc[movie_indices].tolist()

def filter_movies(query):
    return [movie for movie in movies if query.lower() in movie.lower()]

# take inputs
user_input = st.text_input("Movie Name", placeholder='Enter movie name here')
filtered_movies = filter_movies(user_input) if user_input else []
selected_movie = None
if filtered_movies:
    selected_movie = option_menu(
        "Filtered Movies",
        filtered_movies,
        default_index=0,
        menu_icon="cast",
        key="movie_select"
    )
    st.write("Movie selected:", selected_movie)
else:
    st.write("No movies found. Please check your input.")

count = st.number_input("Number of Results", min_value=1, max_value=20, step=1,value=5,key='number_of_obs')
st.markdown("<hr>", unsafe_allow_html=True)
get_results = st.button("Get Your Movies", key='submit')

if get_results:
    if selected_movie is None or count is None:
        st.warning("Please select a movie and specify the number of results.")
    else:

        st.write(f"Selected movie: {selected_movie}")
        st.write(f"Number of results: {count}")
        
        movies_list=content_recommendation(selected_movie, rec1_df,cos_sim, count)
        for movie_recommended in movies_list:
            st.write(movie_recommended)

        st.markdown("<hr>", unsafe_allow_html=True)
        getLLM(selected_movie)
        st.markdown("<hr>", unsafe_allow_html=True)


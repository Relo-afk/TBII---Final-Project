import streamlit as st
import pandas as pd
from registration_page import registration_page
from helpers import connect_to_collection
import time
from hugchat.login import Login
from hugchat import hugchat

# Set page configuration
st.set_page_config(page_title="tbi_botanagochi", page_icon="🌱")

# Adding an audioplayer for users to listen while playing the game or visiting the app
# Information taken from: https://www.w3schools.com/html/html5_audio.asp
st.markdown(
    """
    <audio controls autoplay loop style="width: 100%;">
        <source src="https://d1o44v9snwqbit.cloudfront.net/musicfox_demo_MF-790.mp3" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """,
    unsafe_allow_html=True,
)

# Initialize session state variables to store data or progress to ensure smooth page navigation and user experience
if "page" not in st.session_state:
    st.session_state.page = "login"
if "credentials_check" not in st.session_state:
    st.session_state.credentials_check = False
if "plant" not in st.session_state:
    st.session_state.plant = None
if "soil_selection" not in st.session_state:
    st.session_state.soil_selection = None
if "sunlight_selection" not in st.session_state:
    st.session_state.sunlight_selection = None
if "watering_selection" not in st.session_state:
    st.session_state.watering_selection = None
if "error_origin" not in st.session_state:
    st.session_state.error_origin = "home"
if "plant1" not in st.session_state:
    st.session_state.plant1 = None
if "plant2" not in st.session_state:
    st.session_state.plant2 = None

# Using CSS to style all Streamlit buttons according to the plant theme
# This information was taken from https://www.restack.io/docs/streamlit-knowledge-streamlit-button-color-guide

# Using !important to make sure streamlit do not override the style
# This information was taken from https://www.w3schools.com/css/css_important.asp#:~:text=What%20is%20!important%3F,specific%20property%20on%20that%20element!
button_style = """
<style>
div.stButton > button {
  background-color: #2b7735 !important;
  color: white !important;
  padding: 12px 20px !important;
  font-size: 16px !important;
  border-radius: 25px !important;
  border: none !important;
  cursor: pointer !important;
}

/* Hover effect for depth */
div.stButton > button:hover {
  background-color: #45a049 !important;
}
</style>
"""
st.markdown(button_style, unsafe_allow_html=True)
# /*......*/ is a way to use comments while using CSS that I learned while searching online

# Creating the function to navigate between pages
def navigate_to(page, origin=None):
    st.session_state.page = page
    if origin:
        st.session_state.error_origin = origin
    st.rerun() #to elimilate the issue with clicking the button twice to proceed. Information taken from https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun

# Login Page - the code was taken from the in-class practices and adjusted according to the app
def login_page():
    st.image("images/loginpage_banner.gif")
    # Adding markdown to customize the color and size of some of the texts
    st.markdown(
        '<p style="font-size: 20px; color:green">Hello! Please enter your login info.<br>'
        'If this is your first time, click Register.</p>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        user_name = st.text_input("Username", placeholder="Enter your username").strip().lower()
        password = st.text_input("Password", placeholder="Enter your password", type="password").strip()
        login_button = st.form_submit_button("Login")
        register_button = st.form_submit_button("Register")

    if login_button:
        collection = connect_to_collection('streamlit_registration_data', 'userinfo')
        user_data = pd.DataFrame(list(collection.find({}, {"user_name": 1, "password": 1, "plant1": 1, "plant2": 1})))
        user_names = user_data["user_name"].tolist() if not user_data.empty else []

        if user_name in user_names:
            registered_password = user_data.loc[user_data["user_name"] == user_name, "password"].values[0]
            # To be able to fetch plant names and store them in session state so that we can display the names in game
            if password == registered_password:
                st.session_state.plant1 = user_data.loc[user_data["user_name"] == user_name, "plant1"].values[0]
                st.session_state.plant2 = user_data.loc[user_data["user_name"] == user_name, "plant2"].values[0]
                st.session_state.credentials_check = True
                navigate_to("home")
            else:
                st.error("Incorrect username/password.")
        else:
            st.error("User not found. Please register.")

    if register_button:
        navigate_to("register")

# Registration Page - the code was taken from the in-class practices and adjusted according to the app
def register_page():
    registration_page()
    if st.button("Back to Login"):
        navigate_to("login")

# Home Page
def home():
    st.image("images/loginpage_banner.gif")
    st.markdown(
        "<h1 style='text-align: center; color: #2b7735;'>How would you like to proceed with your virtual world? 🌱</h1>",
        unsafe_allow_html=True
    )

    # Creating 2 columns for better visual layout
    col1, col2 = st.columns(2)

    # Left Column: Start Game and Plant Chores Checklist
    with col1:
        st.image("images/game_start.gif", use_container_width=True)
        if st.button("Start the game"):
            navigate_to('game_start_page')

        st.image("images/checklist.gif", use_container_width=True)
        if st.button("Plant Chores Checklist"):
            navigate_to('plant_chores_checklist')
    # Right Column: AI Chatbot to identify plants and Plant Trading Community
    with col2:
        st.image("images/ai.gif", use_container_width=True)
        if st.button("AI Chatbot: Identify Your Plant"):
            navigate_to('ai_chatbot')

        st.image("images/plant_community.gif", use_container_width=True)
        if st.button("Plant Trading Community"):
            navigate_to('plant_trade_community')

# AI Chatbot Page - the code for hugging face was taken from in-class activities and adjusted
def ai_chatbot_page():
    st.image("images/ai_banner.png")
    st.markdown("""
        Rooty is an intelligent chatbot designed to help you identify plants based on their features. 
        Please answer the following questions to help Rooty provide the best possible identification. 🌱
        """)

    @st.cache_resource
    def connect_to_hugging_face():
        hf_email = st.secrets['email']
        hf_pass = st.secrets['hf_password']

        sign = Login(hf_email, hf_pass)
        cookies = sign.login()

        return cookies

    def generate_response(prompt):
        cookies = connect_to_hugging_face()
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

        # Enhancing the initial prompt for better plant identification
        enhanced_prompt = (
                "You are a plant expert chatbot. Your task is to help users identify plants based on their features. "
                "Always use plant-related emojis (🌱, 🌿, 🌳, 🌺, etc.) in your responses but do not overuse emojis! "
                "The user's input is: " + prompt
        )
        # Getting the response from the chatbot
        response = chatbot.chat(enhanced_prompt)

        # Ensure emojis are included (fallback if the chatbot doesn't add them)
        # This information was taken from ChatGPT as at first the response did not include emojis.
        if "🌱" not in response and "🌿" not in response and "🌳" not in response:
            response += " 🌱"  # Add a default plant emoji

        return response

    # Step 1: Asking for leaf shape
    leaf_shape = st.selectbox(
        "What is the shape of the leaves?",
        options=["Oval", "Heart-shaped", "Needle-like", "Lobed", "Other"]
    )

    # Step 2: Ask for leaf color
    leaf_color = st.selectbox(
        "What is the color of the leaves? 🌱 ",
        options=["Green", "Red", "Yellow", "Variegated", "Other"]
    )

    # Step 3: Ask for leaf size
    plant_size = st.selectbox(
        "What is the size of the leaves of the plant?",
        options=["Small", "Medium", "Large"]
    )

    # Step 4: Ask for flower details
    has_flowers = st.radio(
        "Does the plant have flowers?",
        options=["Yes", "No", "Seasonally"]
    )
    if has_flowers == "Yes":
        flower_color = st.selectbox(
            "What is the color of the flowers?",
            options=["White", "Yellow", "Red", "Pink", "Purple", "Other"]
        )
        flower_shape = st.selectbox(
            "What is the shape of the flowers?",
            options=["Star-shaped", "Bell-shaped", "Tubular", "Other"]
        )
    else:
        flower_color = None
        flower_shape = None

    # Asking additional questions on the flowers depending on user input
    additional_details = st.text_area(
        "Provide any additional details about the plant (e.g., texture, fruits, location):"
    )
    # Button to generate response when the user clicks
    if st.button("Identify Plant"):
        # Construct the prompt based on user inputs
        prompt = (

            f"Identify a plant with the following features: "
            f"Leaf shape: {leaf_shape}, "
            f"Leaf color: {leaf_color}, "
            f"Plant size: {plant_size}, "
            f"Has flowers: {has_flowers}"
        )
        if has_flowers == "Yes":
            prompt += f", Flower color: {flower_color}, Flower shape: {flower_shape}"
        if additional_details:
            prompt += f", Additional details: {additional_details}"

        with st.spinner("Finding the plant..."):
            try:
                response = generate_response(prompt)
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    # I had the idea to filter and structure the input for better identification with selections.
    # I started the process but got help from DeepSeek to further connect the prompt, selection and response generating.

    # Button to go back to home page
    if st.button("Back to Home"):
        navigate_to('home')

# Plant Community Page displaying a QR code to a Telegram group
def plant_trade_community():
    # Using markdown and CSS to change the color of the titles.
    # Information taken from https://discuss.streamlit.io/t/change-font-size-and-font-color/12377/3
    st.markdown(
        "<h1 style='color: #2b7735;'>Would you like to join our plant trading and sharing Telegram Community? 🌟</h1>",
        unsafe_allow_html=True
    )
    st.subheader("You can join our Plant Trading and Sharing Telegram Community. This is a space where plant lovers from Hamburg, Lüneburg, and surrounding cities can exchange, trade, and share plants, cuttings, and care tips.")
    st.write("Whether you're looking for a rare species, want to share your extra cuttings, or simply connect with other plant enthusiasts, this is the place for you! 🌿")

    # Adding 3 columns to center the QR code and the back button for visual aesthetics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("images/arrow_right.png", use_container_width=True)

    with col2:
        st.image("images/qr_code.png", use_container_width=True)

        if st.button("Back to Home"):
            navigate_to('home')

    with col3:
        st.image("images/arrow_left.png", use_container_width=True)

# Plant Chores Checklist Page where the user is given a To-Do list to check if they need in real life
def plant_chores_checklist():
    st.image("images/plant_chores_banner.png")
    st.markdown(
        "<h1 style='color: #2b7735;'>Plant Care Checklist</h1>",
        unsafe_allow_html=True
    )
    # Dictionary to track checkbox states
    chores = {
        "Daily Chores": ["Check for pests and diseases"],
        "Weekly/Biweekly Chores": ["Water plants", "Dust leaves to remove dirt", "Rotate plants for even growth"],
        "Monthly Chores": ["Fertilize plants (every two months)", "Prune dead or yellowing leaves"],
        "Yearly Chores": ["Repot plants if they outgrow their pots", "Deep clean pots and trays"]
    }
    # Creating checkboxes
    # Information taken from https://docs.streamlit.io/develop/api-reference/widgets/st.checkbox
    for category, tasks in chores.items():
        st.markdown(f"### {category}")
        for task in tasks:
            # Key parameter ensures each task gets its own checkbox
            # Information taken from https://docs.streamlit.io/develop/concepts/architecture/widget-behavior
            st.checkbox(task, key=task)


    if st.button("Back to Home"):
        navigate_to('home')

# Game Pages
# Game starting page where you can choose one of the two plants given to grow
def game_start_page():
    st.image("images/cover_page.gif")
    if st.button("Start the Game"):
        navigate_to('plant_selection')

# Plant selection page to ask user which plant they want to grow
def plant_selection():
    st.markdown(
        f"<h1 style='color: #2b7735;'> Choose Your Plant </h1>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        st.image("images/spiderplant.png", use_container_width=True)
        if st.button(f"Choose {st.session_state.plant1} (Your Spider Plant)"):
            st.session_state.plant = 'Spider Plant'
            navigate_to('soil_selection')
    with col2:
        st.image("images/succulent.png", use_container_width=True)
        if st.button(f"Choose {st.session_state.plant2} (Your succulent)"):
            st.session_state.plant = 'Succulent'
            navigate_to('soil_selection')

#Soil selection page where depending on the session_state.plan the user is taken to next page when they give the respective correct answer
#setting origin= for the user to continue from the same page and not from the start when they make a mistake.
# This logic applies to all game pages.
def soil_selection():
    plant_name = st.session_state.plant1 if st.session_state.plant == 'Spider Plant' else st.session_state.plant2
    st.markdown(
        f"<h1 style='color: #2b7735;'>Select Soil for {plant_name}</h1>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/well_draining_soil.png", use_container_width=True)
        if st.button("Well draining soil"):
            navigate_to('placement') if st.session_state.plant == 'Spider Plant' else navigate_to('error', origin='soil_selection')
    with col2:
        st.image("images/cactus_mix.png", use_container_width=True)
        if st.button("Cactus mix"):
            navigate_to('placement') if st.session_state.plant == 'Succulent' else navigate_to('error', origin='soil_selection')
    with col3:
        st.image("images/poor_draining_soil.png", use_container_width=True)
        if st.button("Poor draining soil"):
            navigate_to('error', origin='soil_selection')

# Placement page where the user select the correct sun placement for each plant.
def placement():
    plant_name = st.session_state.plant1 if st.session_state.plant == 'Spider Plant' else st.session_state.plant2
    st.markdown(
        f"<h1 style='color: #2b7735;'>Placement for {plant_name}</h1>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/direct_sunlight.png", use_container_width=True)
        if st.button("Direct sunlight"):
            navigate_to('error', origin='placement')
    with col2:
        st.image("images/indirect_sunlight.png", use_container_width=True)
        if st.button("Indirect sunlight"):
            navigate_to('congratulations_one')
    with col3:
        st.image("images/shade.png", use_container_width=True)
        if st.button("Shade"):
            navigate_to('error', origin='placement')

# The first congratulations page to level up the user
def congratulations_one():
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations! 🌱</h1>",
        unsafe_allow_html=True
    )
    st.image("images/congratulation_one.png")
    if st.button("Proceed to Watering"):
        navigate_to('watering')

#Watering page where the user picks how often they should water the respective plant
def watering():
    plant_name = st.session_state.plant1 if st.session_state.plant == 'Spider Plant' else st.session_state.plant2
    st.markdown(
        f"<h1 style='color: #2b7735;'>Watering for {plant_name}</h1>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/water_once_every_two_weeks.gif", use_container_width=True)
        if st.button("Water once every 2 weeks"):
            navigate_to('congratulations_two') if st.session_state.plant == 'Succulent' else navigate_to('error', origin='watering')
    with col2:
        st.image("images/water_once_a_week.gif", use_container_width=True)
        if st.button("Water once a week"):
            navigate_to('congratulations_two') if st.session_state.plant == 'Spider Plant' else navigate_to('error', origin='watering')
    with col3:
        st.image("images/water_every_three_days.gif", use_container_width=True)
        if st.button("Water every 3 days"):
            navigate_to('error', origin='watering')

# The Second congratulations page to level up the user
def congratulations_two():
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations!🎉</h1>",
        unsafe_allow_html=True
    )
    st.image("images/congratulation_two.png")
    if st.button("Take the Final Challenge"):
        if st.session_state.plant == 'Spider Plant':
            navigate_to('spider_plant_challenge')
        elif st.session_state.plant == 'Succulent':
            navigate_to('succulent_challenge')

#The last step before the user grows an adult plant. There are two different challanges for two different plants.
def spider_plant_challenge():
    st.markdown(
        f"<h1 style='color: #2b7735;'>{st.session_state.plant1} Challenge: Yellowing Leaves</h1>",
        unsafe_allow_html=True
    )
    st.write(f"Your {st.session_state.plant1} has yellow leaves. What could be the problem?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/overwatering.gif", use_container_width=True)
        if st.button("Overwatering"):
            navigate_to('congratulation_final_spider_plant')
    with col2:
        st.image("images/too_much_sunlight.gif", use_container_width=True)
        if st.button("Too much sunlight"):
            navigate_to('error', origin='spider_plant_challenge')
    with col3:
        st.image("images/pest_infestation.gif", use_container_width=True)
        if st.button("Pest infestation"):
            navigate_to('error', origin='spider_plant_challenge')

def succulent_challenge():
    st.markdown(
        f"<h1 style='color: #2b7735;'>{st.session_state.plant1} Challenge: Leggy Growth</h1>",
        unsafe_allow_html=True
    )
    st.write(f"Your {st.session_state.plant2} is growing tall and spindly (leggy). What is the cause of this?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/too_much_sunlight_succulent.gif", use_container_width=True)
        if st.button("Too much sunlight"):
            navigate_to('error', origin='succulent_challenge')
    with col2:
        st.image("images/too_little_sunlight.gif", use_container_width=True)
        if st.button("Too little sunlight"):
            navigate_to('congratulation_final_succulent')
    with col3:
        st.image("images/overwatering_succulent.gif", use_container_width=True)
        if st.button("Overwatering"):
            navigate_to('error', origin='succulent_challenge')

# The third congratulations page to level up the user. There are different displays for different plants
def congratulation_final_spider_plant():
    st.balloons()
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations!🌟</h1>",
        unsafe_allow_html=True
    )
    st.write(f"You've mastered the care of your {st.session_state.plant1}!")
    st.image("images/final_spider_plant.gif")
    if st.button("Claim Your Reward"):
        navigate_to('reward_spider_plant')

def congratulation_final_succulent():
    st.balloons()
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations!🌟</h1>",
        unsafe_allow_html=True
    )
    st.write(f"You've mastered the care of your {st.session_state.plant2}!")
    st.image("images/final_succulent.gif")
    if st.button("Claim Your Reward"):
        navigate_to('reward_succulent')

# Reward Page for Spider Plant - A care video
def reward_page_spider_plant():
    st.balloons()
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations!🌟</h1>",
        unsafe_allow_html=True
    )
    st.write(f"You've successfully completed the Final Spiderplant Challenge! Enjoy a litte care video as a reward! ⬇️ ")
    # Show spinner while "loading" the reward
    with st.spinner("Waiting for your reward to load..."):
        time.sleep(2.5)

    file_path = "https://www.youtube.com/watch?v=D1AvsRCyo9Y"
    st.video(file_path, muted=True, autoplay=True, start_time=2)

    if st.button("Go to Home"):
        navigate_to('home')

# Reward Page for Spider Plant - A care video
def reward_page_succulent():
    st.balloons()
    st.markdown(
        f"<h1 style='color: #2b7735;'>Congratulations!🌟</h1>",
        unsafe_allow_html=True
    )
    st.write(f"You've successfully completed the final Succulent Challenge! Enjoy a litte care video as a reward! ⬇️")

    with st.spinner("Waiting for your reward to load..."):
        time.sleep(2.5)

    file_path = "https://www.youtube.com/watch?v=6jpc9LN_Gkk"
    st.video(file_path, muted=True, autoplay=True, start_time=2)

    if st.button("Go to Home"):
        navigate_to('home')

#Error page where the user is taken when they make a mistake. The origion comes in handy in this page!
def error_page():
    st.image("images/error_page.png")
    if st.button("Go Back"):
        navigate_to(st.session_state.error_origin)

# Page Rendering Logic - where we make sure that the correct page is displaye based on the current state of st.session_state.xxx.
#I asked ChatGPT to help me out with the logic.
if st.session_state.page == "login" and not st.session_state.credentials_check:
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.credentials_check:
    if st.session_state.page == "home":
        home()
    elif st.session_state.page == "game_start_page":
        game_start_page()
    elif st.session_state.page == "plant_selection":
        plant_selection()
    elif st.session_state.page == "soil_selection":
        soil_selection()
    elif st.session_state.page == "placement":
        placement()
    elif st.session_state.page == "congratulations_one":
        congratulations_one()
    elif st.session_state.page == "watering":
        watering()
    elif st.session_state.page == "congratulations_two":
        congratulations_two()
    elif st.session_state.page == "spider_plant_challenge":
        spider_plant_challenge()
    elif st.session_state.page == "succulent_challenge":
        succulent_challenge()
    elif st.session_state.page == "congratulation_final_spider_plant":
        congratulation_final_spider_plant()
    elif st.session_state.page == "congratulation_final_succulent":
        congratulation_final_succulent()
    elif st.session_state.page == "reward_spider_plant":
        reward_page_spider_plant()
    elif st.session_state.page == "reward_succulent":
        reward_page_succulent()
    elif st.session_state.page == "plant_trade_community":
        plant_trade_community()
    elif st.session_state.page == "plant_chores_checklist":
        plant_chores_checklist()
    elif st.session_state.page == "ai_chatbot":
        ai_chatbot_page()
    elif st.session_state.page == "error":
        error_page()

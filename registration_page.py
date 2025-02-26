import streamlit as st
import datetime
import pandas as pd
from helpers import connect_to_collection

def registration_page():
    placeholder = st.empty()
    with placeholder.form("Register to your plant care app: tbi_botanagochi"):
        st.image("images/registrationpage_banner.png")
        st.subheader("🌱 REGISTER NEW USER🌱")
        username = st.text_input("User Name*")
        password = st.text_input("Password*", type="password")
        repeat_password = st.text_input("Repeat Password*", type="password")
        name = st.text_input("Enter Name")
        plant1 = st.text_input("Enter Your Spider Plant's Name")
        plant2 = st.text_input("Enter Your Succulent's Name")
        submit_button = st.form_submit_button("Register")

    if submit_button:
        # define the database
        db_name = 'streamlit_registration_data'
        # define the collection
        collection_name = 'userinfo'
        collection = connect_to_collection(db_name, collection_name)

        # write some dummy data to the collection so it does not error
        dummy_data = {"user_name": "test"}
        collection.insert_one(dummy_data)

        # read the data from the collection and identify user names
        user_data = pd.DataFrame(list(collection.find()))
        usernames = list(user_data.user_name)

        if len(username) < 1:
            st.error("ENTER USERNAME", icon="⚠️")
        elif len(password) < 1:
            st.error("ENTER PASSWORD", icon="⚠️")
        elif len(name) < 1:
            st.error("ENTER NAME", icon="⚠️")
        elif len(plant1) < 1:
            st.error("ENTER YOUR SPIDER PLANT'S NAME", icon="⚠️")
        elif len(plant2) < 1:
            st.error("ENTER YOUR SUCCULENT'S NAME", icon="⚠️")
        elif password != repeat_password:
            st.warning("PASSWORDS DONT MATCH", icon="⚠️")
        elif username in usernames:
            st.warning("USERNAME ALREADY EXISTS", icon="🔥")
        else:
            # creating a document with the data we want to write to this collection
            document = {"user_name": username,
                        "password": password,
                        "name": name,
                        "plant1": plant1,
                        "plant2": plant2,
                        "created_at": datetime.datetime.now()}

            # write this document to the collection
            collection.insert_one(document)

            # clear everything and set credential check flag to True
            placeholder.empty()

            st.title(f"Welcome New User")
            st.subheader(f"Please refresh the page or click the button to login to the virtual world of tbi_botanagochi!🌱")
            st.image("images/loginpage_banner.gif")
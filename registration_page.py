import streamlit as st
import datetime
import pandas as pd
from helpers import connect_to_collection


def registration_page():
    placeholder = st.empty()
    with placeholder.form("Register to your plant care app: tbi_botanagochi"):
        st.image("images/registrationpage_banner.png")
        st.subheader("🌱 REGISTER NEW USER🌱")

        # I put the fields with .strip() and .lower() to make sure data when a user is making a username with capital letters, the data is taken without an issue.
        username = st.text_input("User Name* (min. 4 characters)").strip().lower()
        password = st.text_input("Password* (min. 5 characters)", type="password").strip()
        repeat_password = st.text_input("Repeat Password*", type="password").strip()
        email = st.text_input("Enter Your Email*").strip().lower()
        plant1 = st.text_input("Enter Your Spider Plant's Name*").strip()
        plant2 = st.text_input("Enter Your Succulent's Name*").strip()

        submit_button = st.form_submit_button("Register")

    if submit_button:

        # Define the database and collection
        db_name = 'streamlit_registration_data'
        collection_name = 'userinfo'
        collection = connect_to_collection(db_name, collection_name)

        # Read the data from the collection and identify existing usernames
        user_data = pd.DataFrame(list(collection.find({}, {"user_name": 1})))
        #The purpoe of the {"user_name":1] query is to only check the username. This makes the process faster as it does not check other inputs and saves time.
        usernames = user_data["user_name"].tolist() if not user_data.empty else []

        # Validating the inputs
        if not username:
            st.error("Username is required.", icon="⚠️")
        elif len(username) < 4:
            st.error("Username must be at least 4 characters long.", icon="⚠️")
        elif not password:
            st.error("Password is required.", icon="⚠️")
        elif len(password) < 5:
            st.error("Password must be at least 5 characters long.", icon="⚠️")
        elif not email:
            st.error("Email is required.", icon="⚠️")
        elif "@" not in email or "." not in email:
            st.error("Please enter a valid email address.", icon="⚠️")
        elif not plant1:
            st.error("Please enter your Spider Plant's name.", icon="⚠️")
        elif not plant2:
            st.error("Please enter your Succulent's name.", icon="⚠️")
        elif password != repeat_password:
            st.warning("Passwords do not match.", icon="⚠️")
        elif username in usernames:
            st.warning("Username already exists. Please choose a different username.", icon="🔥")
        else:
            # Create a document with the data to write to the collection
            document = {
                "user_name": username,
                "password": password,
                "email": email,
                "plant1": plant1,
                "plant2": plant2,
                "created_at": datetime.datetime.now()
            }

            # Writing this document to the collection
            collection.insert_one(document)

            # Clearing the form and displaying the success message
            placeholder.empty()
            st.title(f"Welcome, {username}!")
            st.subheader("🎉 Registration successful! 🎉")
            st.subheader(
                "Please refresh the page or click the button to log in to the virtual world of tbi_botanagochi! 🌱")
            st.image("images/loginpage_banner.gif")
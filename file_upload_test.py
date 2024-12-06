# Test for file upload

import streamlit as st

with st.form("user_inputs"):
    #file upload
    uploaded_files = st.file_uploader("Upload your PDF file here", type = ['pdf'], accept_multiple_files = False)

    #Create button
    submit = st.form_submit_button("Generate Quiz")

    if submit:

        if uploaded_files is not None:
            # for uploaded_file in uploaded_files:
            uploaded_file = uploaded_files
            file_details = {
                'FileName' : uploaded_file.name,
                'FileType' : uploaded_file.type
            }

            with open(file_details['FileName'], "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Saved File")

import streamlit as st
import openai
import os

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title("Orthodontic Treatment Planner")

# Create input fields
age = st.number_input("Age", min_value=0, max_value=120, step=1)
gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
main_concern = st.text_input("Main Concern")
bite_type = st.selectbox("Bite Type", ["", "Normal", "Overbite", "Underbite", "Crossbite", "Open bite"])
crowding = st.selectbox("Crowding", ["", "None", "Mild", "Moderate", "Severe"])
treatment_history = st.text_area("Treatment History")

if st.button("Get Treatment Plan"):
    if not all([age, gender, main_concern, bite_type, crowding]):
        st.error("Please fill in all required fields.")
    else:
        # Prepare the prompt for OpenAI API
        prompt = f"""
        Patient Information:
        - Age: {age}
        - Gender: {gender}
        - Main Concern: {main_concern}
        - Bite Type: {bite_type}
        - Crowding: {crowding}
        - Treatment History: {treatment_history}

        Based on the above information, provide a suggested orthodontic treatment plan.
        Include recommendations for appliances, estimated treatment duration, and any additional considerations.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced orthodontist providing treatment plans."},
                    {"role": "user", "content": prompt}
                ]
            )
            treatment_plan = response.choices[0].message.content
            st.subheader("Treatment Plan")
            st.write(treatment_plan)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add a note about the app's purpose
st.markdown("""
    ---
    **Note**: This app uses AI to generate treatment plan suggestions based on input data. 
    It should be used as a tool to assist professional judgment, not as a replacement for expert medical advice.
    """)
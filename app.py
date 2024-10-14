import streamlit as st
import openai
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Check if required libraries are installed
try:
    import openai
    import pandas
    import plotly
except ImportError as e:
    st.error(f"Required library not installed: {e.name}. Please install it using: pip install {e.name}")
    st.stop()

# Set up OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API key to proceed.")
        st.stop()

openai.api_key = api_key

# Initialize session state
if 'patients' not in st.session_state:
    st.session_state.patients = {}

# Main app layout
st.title("Advanced Orthodontic Treatment Planner")

# Sidebar for patient selection/creation
st.sidebar.header("Patient Management")
patient_action = st.sidebar.radio("Choose an action:", ["Create New Patient", "Select Existing Patient"])

if patient_action == "Create New Patient":
    new_patient_name = st.sidebar.text_input("Enter new patient name")
    if st.sidebar.button("Create Patient"):
        if new_patient_name and new_patient_name not in st.session_state.patients:
            st.session_state.patients[new_patient_name] = {
                "info": {},
                "treatment_history": []
            }
            st.success(f"Patient {new_patient_name} created successfully!")
        elif new_patient_name in st.session_state.patients:
            st.sidebar.error("Patient already exists!")
        else:
            st.sidebar.error("Please enter a valid patient name.")

patient_name = st.sidebar.selectbox("Select Patient", list(st.session_state.patients.keys()))

if patient_name:
    st.header(f"Patient: {patient_name}")
    patient = st.session_state.patients[patient_name]

    # Patient Information Form
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient['info']['age'] = st.number_input("Age", min_value=0, max_value=120, step=1, value=patient['info'].get('age', 0))
        patient['info']['gender'] = st.selectbox("Gender", ["", "Male", "Female", "Other"], index=["", "Male", "Female", "Other"].index(patient['info'].get('gender', "")))
        patient['info']['main_concern'] = st.text_input("Main Concern", value=patient['info'].get('main_concern', ""))
    with col2:
        patient['info']['bite_type'] = st.selectbox("Bite Type", ["", "Normal", "Overbite", "Underbite", "Crossbite", "Open bite"], index=["", "Normal", "Overbite", "Underbite", "Crossbite", "Open bite"].index(patient['info'].get('bite_type', "")))
        patient['info']['crowding'] = st.selectbox("Crowding", ["", "None", "Mild", "Moderate", "Severe"], index=["", "None", "Mild", "Moderate", "Severe"].index(patient['info'].get('crowding', "")))
        patient['info']['treatment_history'] = st.text_area("Treatment History", value=patient['info'].get('treatment_history', ""))

    # Generate Treatment Plan
    if st.button("Generate Treatment Plan"):
        if not all([patient['info'].get(field) for field in ['age', 'gender', 'main_concern', 'bite_type', 'crowding']]):
            st.error("Please fill in all required fields.")
        else:
            prompt = f"""
            Patient Information:
            - Age: {patient['info']['age']}
            - Gender: {patient['info']['gender']}
            - Main Concern: {patient['info']['main_concern']}
            - Bite Type: {patient['info']['bite_type']}
            - Crowding: {patient['info']['crowding']}
            - Treatment History: {patient['info']['treatment_history']}

            Based on the above information, provide a detailed orthodontic treatment plan.
            Include the following:
            1. Specific recommendations for appliances
            2. Estimated treatment duration
            3. Phases of treatment (if applicable)
            4. Potential challenges and how to address them
            5. Post-treatment retention strategy
            6. Estimated cost range for the treatment (in USD)
            7. Any lifestyle or dietary recommendations during treatment

            Format the response in markdown for better readability.
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an experienced orthodontist providing detailed treatment plans."},
                        {"role": "user", "content": prompt}
                    ]
                )
                treatment_plan = response.choices[0].message.content
                st.subheader("Generated Treatment Plan")
                st.markdown(treatment_plan)

                # Add to treatment history
                patient['treatment_history'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plan": treatment_plan
                })
                st.success("Treatment plan added to patient history.")
            except Exception as e:
                st.error(f"An error occurred while generating the treatment plan: {str(e)}")
                st.info("Please check your OpenAI API key and internet connection.")

    # Display Treatment History
    if patient['treatment_history']:
        st.subheader("Treatment History")
        for i, entry in enumerate(patient['treatment_history']):
            with st.expander(f"Treatment Plan {i+1} - {entry['date']}"):
                st.markdown(entry['plan'])

    # Visual Treatment Timeline
    if patient['treatment_history']:
        st.subheader("Treatment Timeline")
        df = pd.DataFrame(patient['treatment_history'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        fig = go.Figure(data=[go.Scatter(x=df['date'], y=[1]*len(df), mode='markers+text', 
                                         text=[f"Plan {i+1}" for i in range(len(df))], 
                                         textposition="top center")])
        fig.update_layout(title="Treatment Plan Timeline", xaxis_title="Date", yaxis_title="",
                          yaxis=dict(tickmode='array', tickvals=[1], ticktext=[''], showticklabels=False))
        st.plotly_chart(fig)

# Add a note about the app's purpose
st.markdown("""
    ---
    **Note**: This app uses AI to generate treatment plan suggestions based on input data. 
    It should be used as a tool to assist professional judgment, not as a replacement for expert medical advice.
    """)
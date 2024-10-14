import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from openai import OpenAI

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

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Initialize session state
if 'patients' not in st.session_state:
    st.session_state.patients = {}

# Main app layout
st.title("Professional Orthodontic Treatment Planner")

# Sidebar for patient selection/creation
st.sidebar.header("Patient Management")
patient_action = st.sidebar.radio("Choose an action:", ["Create New Patient", "Select Existing Patient"])

if patient_action == "Create New Patient":
    new_patient_name = st.sidebar.text_input("Enter new patient name")
    if st.sidebar.button("Create Patient"):
        if new_patient_name and new_patient_name not in st.session_state.patients:
            st.session_state.patients[new_patient_name] = {
                "info": {},
                "treatment_plans": []
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
        patient['info']['name'] = st.text_input("Patient Name", value=patient['info'].get('name', patient_name))
        patient['info']['dob'] = st.date_input("Date of Birth", value=patient['info'].get('dob'))
        patient['info']['consultation_date'] = st.date_input("Date of Consultation", value=datetime.now())
        patient['info']['orthodontist'] = st.text_input("Orthodontist", value=patient['info'].get('orthodontist', "Dr. "))
    with col2:
        patient['info']['patient_id'] = st.text_input("Patient ID", value=patient['info'].get('patient_id', ""))
        patient['info']['chief_complaint'] = st.text_area("Chief Complaint", value=patient['info'].get('chief_complaint', ""))

    # Clinical Examination
    st.subheader("Clinical Examination")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Extraoral Examination")
        patient['info']['facial_symmetry'] = st.selectbox("Facial symmetry", ["Symmetric", "Asymmetric"], index=["Symmetric", "Asymmetric"].index(patient['info'].get('facial_symmetry', "Symmetric")))
        patient['info']['lip_competency'] = st.selectbox("Lip competency", ["Competent", "Incompetent"], index=["Competent", "Incompetent"].index(patient['info'].get('lip_competency', "Competent")))
        patient['info']['smile_line'] = st.selectbox("Smile line", ["High", "Low", "Normal"], index=["High", "Low", "Normal"].index(patient['info'].get('smile_line', "Normal")))
        patient['info']['chin_position'] = st.selectbox("Chin position", ["Protrusive", "Retrusive", "Normal"], index=["Protrusive", "Retrusive", "Normal"].index(patient['info'].get('chin_position', "Normal")))
    with col2:
        st.write("Intraoral Examination")
        patient['info']['arch_form'] = st.selectbox("Arch form", ["U-shaped", "V-shaped"], index=["U-shaped", "V-shaped"].index(patient['info'].get('arch_form', "U-shaped")))
        patient['info']['crowding'] = st.selectbox("Crowding", ["Mild", "Moderate", "Severe"], index=["Mild", "Moderate", "Severe"].index(patient['info'].get('crowding', "Mild")))
        patient['info']['spacing'] = st.selectbox("Spacing", ["Present", "Absent"], index=["Present", "Absent"].index(patient['info'].get('spacing', "Absent")))
        patient['info']['crossbite'] = st.selectbox("Crossbite", ["Present", "Absent"], index=["Present", "Absent"].index(patient['info'].get('crossbite', "Absent")))
        patient['info']['overbite'] = st.selectbox("Overbite", ["Normal", "Deep", "Open"], index=["Normal", "Deep", "Open"].index(patient['info'].get('overbite', "Normal")))
        patient['info']['overjet'] = st.selectbox("Overjet", ["Increased", "Decreased", "Normal"], index=["Increased", "Decreased", "Normal"].index(patient['info'].get('overjet', "Normal")))
        patient['info']['occlusion_class'] = st.selectbox("Occlusion Class", ["Class I", "Class II", "Class III"], index=["Class I", "Class II", "Class III"].index(patient['info'].get('occlusion_class', "Class I")))

    # Radiographic Analysis
    st.subheader("Radiographic Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Cephalometric Analysis")
        patient['info']['sna'] = st.number_input("SNA (degrees)", value=patient['info'].get('sna', 82.0), format="%.1f")
        patient['info']['snb'] = st.number_input("SNB (degrees)", value=patient['info'].get('snb', 80.0), format="%.1f")
        patient['info']['anb'] = st.number_input("ANB (degrees)", value=patient['info'].get('anb', 2.0), format="%.1f")
        patient['info']['fma'] = st.number_input("FMA (degrees)", value=patient['info'].get('fma', 25.0), format="%.1f")
    with col2:
        st.write("Panoramic X-ray")
        patient['info']['impacted_teeth'] = st.selectbox("Impacted teeth", ["Present", "Absent"], index=["Present", "Absent"].index(patient['info'].get('impacted_teeth', "Absent")))
        patient['info']['root_resorption'] = st.selectbox("Root resorption", ["Present", "Absent"], index=["Present", "Absent"].index(patient['info'].get('root_resorption', "Absent")))
        patient['info']['eruption_pattern'] = st.selectbox("Eruption pattern", ["Normal", "Delayed"], index=["Normal", "Delayed"].index(patient['info'].get('eruption_pattern', "Normal")))

    # Generate Treatment Plan
    if st.button("Generate Treatment Plan"):
        prompt = f"""
        Based on the following patient information, generate a detailed orthodontic treatment plan:

        Patient Name: {patient['info']['name']}
        Date of Birth: {patient['info']['dob']}
        Date of Consultation: {patient['info']['consultation_date']}
        Orthodontist: {patient['info']['orthodontist']}
        Patient ID: {patient['info']['patient_id']}

        Chief Complaint: {patient['info']['chief_complaint']}

        Clinical Examination:
        - Facial symmetry: {patient['info']['facial_symmetry']}
        - Lip competency: {patient['info']['lip_competency']}
        - Smile line: {patient['info']['smile_line']}
        - Chin position: {patient['info']['chin_position']}
        - Arch form: {patient['info']['arch_form']}
        - Crowding: {patient['info']['crowding']}
        - Spacing: {patient['info']['spacing']}
        - Crossbite: {patient['info']['crossbite']}
        - Overbite: {patient['info']['overbite']}
        - Overjet: {patient['info']['overjet']}
        - Occlusion Class: {patient['info']['occlusion_class']}

        Radiographic Analysis:
        - SNA: {patient['info']['sna']}
        - SNB: {patient['info']['snb']}
        - ANB: {patient['info']['anb']}
        - FMA: {patient['info']['fma']}
        - Impacted teeth: {patient['info']['impacted_teeth']}
        - Root resorption: {patient['info']['root_resorption']}
        - Eruption pattern: {patient['info']['eruption_pattern']}

        Please provide a comprehensive treatment plan including:
        1. Diagnosis
        2. Treatment Objectives
        3. Detailed Treatment Plan (including appliance therapy, archwire sequence, and any adjunctive therapies)
        4. Retention Phase
        5. Estimated Treatment Duration
        6. Potential Risks and Complications

        Format the response in markdown for better readability.
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )
            treatment_plan = chat_completion['choices'][0]['message']['content']
            st.subheader("Generated Treatment Plan")
            st.markdown(treatment_plan)

            # Add to treatment plans
            patient['treatment_plans'].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plan": treatment_plan
            })
            st.success("Treatment plan added to patient history.")
        except Exception as e:
            st.error(f"An error occurred while generating the treatment plan: {str(e)}")
            st.info("Please check your OpenAI API key and internet connection.")

    # Display Treatment History
    if patient['treatment_plans']:
        st.subheader("Treatment History")
        for i, entry in enumerate(patient['treatment_plans']):
            with st.expander(f"Treatment Plan {i+1} - {entry['date']}"):
                st.markdown(entry['plan'])

    # Visual Treatment Timeline
    if patient['treatment_plans']:
        st.subheader("Treatment Timeline")
        df = pd.DataFrame(patient['treatment_plans'])
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
    **Note**: This app uses AI to generate orthodontic treatment plan suggestions based on input data. 
    It should be used as a tool to assist professional judgment, not as a replacement for expert medical advice.
    Always consult with a qualified orthodontist for actual patient care.
    """)

import os
from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_treatment_plan", methods=["POST"])
def get_treatment_plan():
    patient_data = request.json

    # Prepare the prompt for OpenAI API
    prompt = f"""
    Patient Information:
    - Age: {patient_data['age']}
    - Gender: {patient_data['gender']}
    - Main Concern: {patient_data['mainConcern']}
    - Bite Type: {patient_data['biteType']}
    - Crowding: {patient_data['crowding']}
    - Treatment History: {patient_data['treatmentHistory']}

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
        return jsonify({"treatment_plan": treatment_plan})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
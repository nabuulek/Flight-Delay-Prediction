import streamlit as st
import joblib
import pandas as pd

# Load the trained model
model_path = 'flight_delay_model.pkl'  # Update with your actual path
model = joblib.load(model_path)

# App Title
st.title('Flight Delay Prediction')

# Explanation of input fields
st.markdown("""
- **STATUS**: Flight status.
    - **ATA**: Actual Time of Arrival
    - **DEL**: Delayed
    - **DEP**: Departed
    - **RTR**: Returned
    - **SCH**: Scheduled
""")

# Input Fields
with st.form("flight_info"):
    st.header("Flight Information")

    status_options = ['ATA', 'DEL', 'DEP', 'RTR', 'SCH']  # Assuming these are valid STATUS values
    selected_status = st.selectbox('Flight Status', status_options)
    status_cols = [f'STATUS_{status}' for status in status_options]

    # Create input fields for selected status columns
    status_values = {col: 0 for col in status_cols}
    status_values[f'STATUS_{selected_status}'] = 1

    year = st.number_input('Year', min_value=2000, max_value=2099, value=2024)
    month = st.number_input('Month', min_value=1, max_value=12, value=6)
    day = st.number_input('Day', min_value=1, max_value=31, value=15)

    std_hour = st.number_input('Scheduled Departure Hour (24-hour format)', min_value=0, max_value=23, value=12)
    sta_hour = st.number_input('Scheduled Arrival Hour (24-hour format)', min_value=0, max_value=23, value=14)

    # Calculate Flight Hours (optional, can be removed if not used by the model)
    flight_hours = sta_hour - std_hour if sta_hour >= std_hour else 24 + sta_hour - std_hour

    # Submit Button
    submit_button = st.form_submit_button(label='Predict Delay')

# Make predictions upon form submission
if submit_button:
    # Create input data as a DataFrame
    input_data = pd.DataFrame({
        **status_values, 
        'Year': [year], 'Month': [month], 'Day': [day], 
        'Hour_STD': [std_hour], 'Hour_STA': [sta_hour], 
        'Flight_Hours': [flight_hours]
    })

    # Ensure input data matches the expected columns (reorder if needed)
    try:
        if hasattr(model, 'feature_name_'):
            expected_features = model.feature_name_
        else:
            expected_features = model.booster_.feature_name()

        # Align input data to the model's expected features
        input_data = input_data.reindex(columns=expected_features).fillna(0)

        # Predict
        prediction = model.predict(input_data)

        # Display results
        delay_duration = prediction[0]
        if delay_duration == 0:
            st.success('The flight is predicted to be on time.')
        else:
            st.warning(f'The flight is predicted to be delayed by {delay_duration:.2f} minutes.')
    except AttributeError as ae:
        st.error(f"Attribute error: {str(ae)}")
    except Exception as e:
        st.error(f"Error in prediction: {str(e)}")

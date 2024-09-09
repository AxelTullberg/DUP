# Step 3: 1RM input for selected exercises
st.write("**Step 3: Enter Your Max Lifts (1RM) for Selected Exercises (kg)**")

# Ensure the key is unique and handle empty exercise list
if selected_exercises:
    max_lifts = {
        exercise: st.number_input(f"Max {exercise.capitalize()} (kg)", value=100, key=f"max_lifts_{exercise}")
        for exercise in selected_exercises
    }
else:
    max_lifts = {}

# Input for fatigue level
fatigue = st.slider("Fatigue level (1-10)", 1, 10, 5)

# Input for max reps for bodyweight exercises
max_reps_bodyweight = st.number_input("Max reps for bodyweight exercises (e.g., pull ups)", value=10)

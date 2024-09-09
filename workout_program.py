import streamlit as st
import random

# List of available exercises with their substitutions
exercise_options = {
    "legs": {
        "primary": ["back squat", "front squat", "leg press", "Bulgarian squats"],
        "alternatives": ["squats", "front squat", "Bulgarian squats", "leg press", "hack squat"]
    },
    "chest": {
        "primary": ["bench press", "dumbbell press"],
        "alternatives": ["bench press", "dumbbell press", "smith machine bench press"]
    },
    "upper_back": {
        "primary": ["pull ups", "barbell rows", "dumbbell rows"],
        "alternatives": ["barbell row", "dumbbell row", "pull ups"]
    },
    "lower_back": {
        "primary": ["deadlift", "stiff leg deadlift", "trap bar deadlift"],
        "alternatives": ["deadlift", "trap bar deadlift", "stiff leg deadlift"]
    },
    "shoulders": {
        "primary": ["shoulder press", "dumbbell shoulder press"],
        "alternatives": ["dumbbell shoulder press", "behind the neck press", "barbell shoulder press"]
    },
    "abs": {
        "primary": ["leg raises", "ab roller"],
        "alternatives": ["ab roller"]
    }
}

class ExerciseProgram:
    def __init__(self, max_lifts, sets_per_week, fatigue, fitness, max_reps_bodyweight):
        self.max_lifts = max_lifts
        self.sets_per_week = sets_per_week
        self.program = []
        self.current_day = 1
        self.current_week = 1
        self.fatigue = fatigue
        self.fitness = fitness
        self.form = fatigue - fitness  # Calculate Form (Fatigue - Fitness)
        self.max_reps_bodyweight = max_reps_bodyweight

    def calculate_weight(self, max_weight, intensity):
        """ Calculate the working weight based on a percentage of the max lift. """
        return round(max_weight * intensity, 1)

    def adjust_volume(self):
        """ Adjust the total volume (sets) based on the difference between Fatigue and Fitness (Form). """
        if self.form > 0:
            total_adjustment = int(self.form)  # Reduce sets by the number of positive form points
            exercises = ["back squat", "deadlift", "front squat", "bench press", "shoulder press", "pull ups"]  # Prioritize compound exercises
            
            for exercise in exercises:
                if total_adjustment <= 0:
                    break
                sets_to_reduce = min(total_adjustment, self.sets_per_week[exercise])
                self.sets_per_week[exercise] = max(0, self.sets_per_week[exercise] - sets_to_reduce)
                total_adjustment -= sets_to_reduce

    def split_sets(self, total_sets):
        """ Split the total sets evenly across 3 days. """
        base_sets = total_sets // 3
        remainder = total_sets % 3
        day_sets = [base_sets] * 3
        for i in range(remainder):
            day_sets[i] += 1
        return day_sets

    def generate_day(self, selected_exercises, intensities, reps, sets_distribution, day, max_lifts):
        """ Generate a workout day with weight, reps, and sets for each exercise, recalculating for alternatives. """
        day_program = {}
        for exercise, intensity, rep_range, sets in zip(selected_exercises, intensities, reps, sets_distribution):
            weight = self.calculate_weight(max_lifts.get(exercise, 0), intensity)
            day_program[exercise] = {
                "weight (kg)": weight if weight > 0 else "Bodyweight",
                "reps": rep_range,
                "sets": sets[day - 1]  # Get sets for the current day
            }
        self.program.append({f"Day {day}": day_program})

    def generate_program(self, selected_exercises, week, max_lifts):
        """ Generate the full weekly DUP program with weekly undulation. """
        # Weekly undulation: intensity changes over different weeks
        base_intensities = [[0.75, 0.85, 0.65] for _ in selected_exercises]

        # Reps will vary over the week
        reps = [[5, 3, 8] for _ in selected_exercises]

        # Distribute sets per week across 3 days
        sets_distribution = {exercise: self.split_sets(self.sets_per_week[exercise]) for exercise in selected_exercises}

        # Generate program for 3 days in a week
        for day in range(1, 4):
            day_intensities = [intensity[day - 1] for intensity in base_intensities]
            day_reps = [rep[day - 1] for rep in reps]
            day_sets = [sets_distribution[exercise] for exercise in selected_exercises]
            self.generate_day(selected_exercises, day_intensities, day_reps, day_sets, day, max_lifts)

    def get_upcoming_workout(self, selected_exercises, alternative_exercises, max_lifts):
        """ Display the upcoming workout based on the current day and week, updating based on alternatives selected and recalculating weight using new 1RM. """
        if self.current_day > 3:
            self.current_day = 1  # Reset the day when a week is complete
            self.current_week += 1  # Move to the next week

        workout = self.program[self.current_day - 1]  # Fetch the workout for the day
        st.write(f"\nUpcoming workout - Week {self.current_week}, Day {self.current_day}:")
        for day_name, exercises in workout.items():
            st.write(f"\n{day_name}:")
            for exercise, details in exercises.items():
                # Check if there's an alternative exercise selected, if so replace it and recalculate the weight using new 1RM
                for category, alternatives in alternative_exercises.items():
                    if exercise in exercise_options[category]["primary"] and alternatives:
                        exercise = alternatives[0]
                        details['weight (kg)'] = self.calculate_weight(max_lifts.get(exercise, 0), 0.75)  # Example intensity (0.75)

                st.write(f"  {exercise}: {details['weight (kg)']} kg, {details['reps']} reps, {details['sets']} sets")
        
        # Update to the next day for the subsequent workout
        self.current_day += 1

    def add_abs_workout(self):
        """ Always include abs workout with 3 sets of 6-10 reps. """
        abs_exercise = random.choice(["leg raises", "ab roller"])
        reps = random.randint(6, 10)
        st.write(f"\nAbs Workout: {abs_exercise} - {reps} reps x 3 sets")

    def generate_full_program(self, selected_exercises, weeks, max_lifts):
        """ Generate a full program for a specified number of weeks. """
        self.adjust_volume()  # Adjust volume based on Fatigue-Fitness (Form) before generating the program
        for week in range(weeks):
            self.generate_program(selected_exercises, week, max_lifts)

    def print_full_month(self, selected_exercises, alternative_exercises, max_lifts):
        """ Print all workouts for the entire month (4 weeks), updating based on alternative exercises selected. """
        st.write("\nFull 4-Week Program:")
        day_counter = 1
        for week in range(1, 5):  # Assuming a month = 4 weeks
            st.write(f"\nWeek {week}:")
            for day in range(1, 4):
                workout = self.program[day_counter - 1]
                st.write(f"\nDay {day}:")
                for day_name, exercises in workout.items():
                    for exercise, details in exercises.items():
                        # Recalculate using the alternative exercises' 1RM if selected
                        for category, alternatives in alternative_exercises.items():
                            if exercise in exercise_options[category]["primary"] and alternatives:
                                exercise = alternatives[0]
                                details['weight (kg)'] = self.calculate_weight(max_lifts.get(exercise, 0), 0.75)  # Example intensity (0.75)
                        st.write(f"  {exercise}: {details['weight (kg)']} kg, {details['reps']} reps, {details['sets']} sets")
                day_counter += 1
        self.add_abs_workout()  # Always add abs workout to the end


# Streamlit app interface
st.title("Daily Customizable DUP Workout Program")

# 1. Allow user to choose exercises for today’s workout
st.write("**Choose exercises for today's workout (1-2 per body part):**")

# Leg exercises
legs_selected = st.multiselect(
    "Leg exercises", 
    options=exercise_options["legs"]["primary"], 
    default=["back squat"]
)

# Chest exercises
chest_selected = st.multiselect(
    "Chest exercises", 
    options=exercise_options["chest"]["primary"], 
    default=["bench press"]
)

# Upper back exercises
upper_back_selected = st.multiselect(
    "Upper back exercises", 
    options=exercise_options["upper_back"]["primary"], 
    default=["pull ups"]
)

# Lower back exercises
lower_back_selected = st.multiselect(
    "Lower back exercises", 
    options=exercise_options["lower_back"]["primary"], 
    default=["deadlift"]
)

# Shoulder exercises
shoulders_selected = st.multiselect(
    "Shoulder exercises", 
    options=exercise_options["shoulders"]["primary"], 
    default=["shoulder press"]
)

# Combine all selected exercises for today
selected_exercises = legs_selected + chest_selected + upper_back_selected + lower_back_selected + shoulders_selected

# 2. Inputs for max lifts (in kg)
st.write("**Enter your max lifts (in kg):**")
max_lifts = {
    "back squat": st.number_input("Max back squat (kg)", value=100),
    "front squat": st.number_input("Max front squat (kg)", value=90),
    "leg press": st.number_input("Max leg press (kg)", value=180),
    "bench press": st.number_input("Max bench press (kg)", value=80),
    "deadlift": st.number_input("Max deadlift (kg)", value=120),
    "pull ups": st.number_input("Max pull ups (reps)", value=10),
    "shoulder press": st.number_input("Max shoulder press (kg)", value=50)
}

# 3. Inputs for sets per week
st.write("**Enter the number of sets per week for each exercise:**")
sets_per_week = {
    "back squat": st.number_input("Sets per week (back squat)", value=9),
    "front squat": st.number_input("Sets per week (front squat)", value=6),
    "leg press": st.number_input("Sets per week (leg press)", value=6),
    "bench press": st.number_input("Sets per week (bench press)", value=9),
    "deadlift": st.number_input("Sets per week (deadlift)", value=6),
    "pull ups": st.number_input("Sets per week (pull ups)", value=9),
    "shoulder press": st.number_input("Sets per week (shoulder press)", value=6)
}

# 4. Inputs for fatigue and fitness levels
st.write("**Enter your current fatigue and fitness levels (scale 1-10):**")
fatigue = st.slider("Fatigue level", 1, 10, 5)
fitness = st.slider("Fitness level", 1, 10, 5)

# 5. Inputs for bodyweight exercise max reps
max_reps_bodyweight = st.number_input("Max reps for bodyweight exercises (e.g., pull ups)", value=10)

# 6. Alternative exercise options based on availability
st.write("**Alternative exercise options (choose if main exercise unavailable):**")

# Prompt the user to select if they want to use alternative exercises
use_alternatives = st.radio("Alternative options?", ["No", "Yes"])

alternative_exercises = {}
alternative_max_lifts = {}

if use_alternatives == "Yes":
    st.write("**Which lifts would you like to replace with alternatives?**")
    replace_exercises = st.multiselect(
        "Select main lifts to replace", 
        options=list(exercise_options.keys())
    )
    
    for exercise_group in replace_exercises:
        selected_alternatives = st.multiselect(
            f"Select alternative for {exercise_group.capitalize()}",
            options=exercise_options[exercise_group]["alternatives"]
        )
        alternative_exercises[exercise_group] = selected_alternatives
        
        # Ask for 1RM for alternative exercises
        st.write("**Enter your 1RM for the selected alternative exercises (in kg):**")
        for exercise in selected_alternatives:
            alternative_max_lifts[exercise] = st.number_input(f"Max {exercise} (kg)", value=0)

# Update the max_lifts dictionary with the alternative exercises' 1RM
max_lifts.update(alternative_max_lifts)

# 7. Generate the program dynamically for today
exercise_program = ExerciseProgram(max_lifts, sets_per_week, fatigue, fitness, max_reps_bodyweight)
exercise_program.generate_full_program(selected_exercises, weeks=4, max_lifts=max_lifts)

# Create tabs for today's workout and full program
tab1, tab2 = st.tabs(["Today's Workout", "Full Program"])

with tab1:
    exercise_program.get_upcoming_workout(selected_exercises, alternative_exercises, max_lifts)
    exercise_program.add_abs_workout()  # Add abs workout at the end of today's workout

with tab2:
    exercise_program.print_full_month(selected_exercises, alternative_exercises, max_lifts)

import streamlit as st

class ExerciseProgram:
    def __init__(self, max_lifts, sets_per_week, fatigue, fitness):
        self.max_lifts = max_lifts
        self.sets_per_week = sets_per_week
        self.program = []
        self.current_day = 1
        self.current_week = 1
        self.fatigue = fatigue
        self.fitness = fitness
        self.form = fatigue - fitness  # Calculate Form (Fatigue - Fitness)

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

    def generate_day(self, exercises, intensities, reps, sets_distribution, day):
        """ Generate a workout day with weight, reps, and sets for each exercise. """
        day_program = {}
        for exercise, intensity, rep_range, sets in zip(exercises, intensities, reps, sets_distribution):
            weight = self.calculate_weight(self.max_lifts[exercise], intensity)
            day_program[exercise] = {
                "weight (kg)": weight,
                "reps": rep_range,
                "sets": sets[day - 1]  # Get sets for the current day
            }
        self.program.append({f"Day {day}": day_program})

    def generate_program(self, week):
        """ Generate the full weekly DUP program with weekly undulation. """
        exercises = ["back squat", "front squat", "bench press", "pull ups", "deadlift", "shoulder press"]

        # Weekly undulation: intensity changes over different weeks
        base_intensities = [
            [0.75, 0.85, 0.65],  # Back squat
            [0.7, 0.8, 0.6],     # Front squat
            [0.75, 0.85, 0.65],  # Bench press
            [0.75, 0.85, 0.65],  # Pull ups
            [0.8, 0.9, 0.7],     # Deadlift
            [0.75, 0.85, 0.65]   # Shoulder press
        ]

        # Intensities vary between weeks (e.g., week 1 is baseline, week 2 has slightly higher intensity)
        intensity_multiplier = [1.0, 1.05, 0.95, 1.1]  # Week-to-week undulation multiplier
        intensities = [[round(base * intensity_multiplier[week % 4], 2) for base in week_set] for week_set in base_intensities]

        # Reps will vary over the week
        reps = [
            [5, 3, 8],   # Back squat
            [6, 4, 10],  # Front squat
            [5, 3, 8],   # Bench press
            [5, 3, 8],   # Pull ups
            [4, 2, 6],   # Deadlift
            [6, 4, 8]    # Shoulder press
        ]

        # Distribute sets per week across 3 days
        sets_distribution = {exercise: self.split_sets(self.sets_per_week[exercise]) for exercise in exercises}

        # Generate program for 3 days in a week
        for day in range(1, 4):
            day_intensities = [intensity[day - 1] for intensity in intensities]
            day_reps = [rep[day - 1] for rep in reps]
            day_sets = [sets_distribution[exercise] for exercise in exercises]
            self.generate_day(exercises, day_intensities, day_reps, day_sets, day)
        
    def get_upcoming_workout(self):
        """ Display the upcoming workout based on the current day and week. """
        if self.current_day > 3:
            self.current_day = 1  # Reset the day when a week is complete
            self.current_week += 1  # Move to the next week

        workout = self.program[self.current_day - 1]  # Fetch the workout for the day
        st.write(f"\nUpcoming workout - Week {self.current_week}, Day {self.current_day}:")
        for day_name, exercises in workout.items():
            st.write(f"\n{day_name}:")
            for exercise, details in exercises.items():
                st.write(f"  {exercise}: {details['weight (kg)']} kg, {details['reps']} reps, {details['sets']} sets")
        
        # Update to the next day for the subsequent workout
        self.current_day += 1

    def generate_full_program(self, weeks):
        """ Generate a full program for a specified number of weeks. """
        self.adjust_volume()  # Adjust volume based on Fatigue-Fitness (Form) before generating the program
        for week in range(weeks):
            self.generate_program(week)

    def print_full_month(self):
        """ Print all workouts for the entire month (4 weeks) """
        st.write("\nFull 4-Week Program:")
        day_counter = 1
        for week in range(1, 5):  # Assuming a month = 4 weeks
            st.write(f"\nWeek {week}:")
            for day in range(1, 4):
                workout = self.program[day_counter - 1]
                st.write(f"\nDay {day}:")
                for day_name, exercises in workout.items():
                    for exercise, details in exercises.items():
                        st.write(f"  {exercise}: {details['weight (kg)']} kg, {details['reps']} reps, {details['sets']} sets")
                day_counter += 1

# Streamlit app interface
st.title("DUP Workout Program with Tabs for Today's Workout and Full Program")

# Inputs for max lifts (in kg)
max_lifts = {
    "back squat": st.number_input("Max Back Squat (kg)", value=140),
    "front squat": st.number_input("Max Front Squat (kg)", value=100),
    "bench press": st.number_input("Max Bench Press (kg)", value=90),
    "pull ups": st.number_input("Max Pull Ups (kg)", value=90),  # Pull ups max (body weight + added load)
    "deadlift": st.number_input("Max Deadlift (kg)", value=180),
    "shoulder press": st.number_input("Max Shoulder Press (kg)", value=60)
}

# Inputs for sets per week for each exercise
sets_per_week = {
    "back squat": st.number_input("Back Squat Sets per Week", value=14),
    "front squat": st.number_input("Front Squat Sets per Week", value=9),
    "bench press": st.number_input("Bench Press Sets per Week", value=12),
    "pull ups": st.number_input("Pull-ups Sets per Week", value=9),
    "deadlift": st.number_input("Deadlift Sets per Week", value=6),
    "shoulder press": st.number_input("Shoulder Press Sets per Week", value=9)
}

# Dynamic input for Fatigue and Fitness
fatigue = st.slider("Fatigue", min_value=0, max_value=100, value=60)
fitness = st.slider("Fitness", min_value=0, max_value=100, value=50)

# Number of weeks for the program
weeks = st.number_input("Number of Weeks", value=4, step=1)

# Generate the program dynamically whenever fatigue or fitness values change
exercise_program = ExerciseProgram(max_lifts, sets_per_week, fatigue, fitness)
exercise_program.generate_full_program(weeks)

# Create tabs for today's workout and full program
tab1, tab2 = st.tabs(["Today's Workout", "Full Program"])

with tab1:
    exercise_program.get_upcoming_workout()

with tab2:
    exercise_program.print_full_month()

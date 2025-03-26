import ipywidgets as widgets
from IPython.display import display, clear_output
import time

def quiz1():
    # Sample questions and answers
    questions = [
        {"question": "The temperature recorded hourly throughout a day.", "answer": "Quantitative"},
        {"question": "Survey responses rating satisfaction with services on a scale from 1 to 5.", "answer": "Quantitative"},
        {"question": "Descriptions of the texture of a fabric.", "answer": "Qualitative"},
        {"question": "Colors observed in a sunset.", "answer": "Qualitative"},
        {"question": "Number of people who attended a concert.", "answer": "Quantitative"},
        {"question": "Opinions about a new product.", "answer": "Qualitative"}
    ]
    
    # Store total number of questions for display purposes
    total_questions = len(questions)

    # Create an Output widget to manage feedback messages
    feedback_output = widgets.Output()

    # Create buttons
    btn_quantitative = widgets.Button(description="Quantitative")
    btn_qualitative = widgets.Button(description="Qualitative")

    # Function to display the current question
    def display_question():
        if questions:
            question_number = total_questions - len(questions) + 1  # Calculate current question number
            with feedback_output:
                clear_output(wait=True)
                display(widgets.HTML(value=f"<b>Question {question_number} of {total_questions}:</b> <br>"
                                         f"<div style='font-size:16px'>{questions[0]['question']}</div>"))  # Display question with HTML formatting for size

    # Function to handle button clicks
    def on_button_clicked(b):
        correct = b.description == questions[0]['answer']
        with feedback_output:
            clear_output(wait=True)
            if correct:
                print("Correct! ✔️")
            else:
                print("Incorrect. ✖️")
        
        time.sleep(2)  # Pause for 2 seconds to let user read the feedback

        # Move to the next question
        questions.pop(0)
        if questions:
            display_question()
        else:
            with feedback_output:
                clear_output(wait=True)
                print("Quiz completed! 🎉")
                btn_quantitative.disabled = True
                btn_qualitative.disabled = True

    # Attach event handlers to buttons
    btn_quantitative.on_click(on_button_clicked)
    btn_qualitative.on_click(on_button_clicked)

    # Display the first question and buttons
    display_question()
    display(feedback_output, btn_quantitative, btn_qualitative)

# To launch the quiz, call quiz1()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from ipywidgets import interact, FloatSlider, Output
from IPython.display import display, HTML

def example1():
    # Set default font to Times New Roman, size 12
    rcParams['font.size'] = 12

    # Simulated vibration sensor data (in g-force)
    np.random.seed(0)
    time = np.linspace(0, 10, 500)  # 10 seconds of data
    base_vibration = np.sin(2 * np.pi * 2 * time)  # 2Hz vibration (normal machine operation)

    # Output widget for real-time conclusions
    output_text = Output()

    def analyze_vibration(noise_level=0.1):
        """Simulates vibration data with noise and evaluates its usability."""
        noise = np.random.normal(0, noise_level, size=base_vibration.shape)  # Add random noise
        measured_vibration = base_vibration + noise

        # Plot vibration data
        plt.figure(figsize=(6, 3))
        plt.plot(time, base_vibration, label="True Vibration", color="blue", alpha=0.6)
        plt.plot(time, measured_vibration, label="Measured Data", color="red", alpha=0.7)
        plt.xlabel("Time (s)")
        plt.ylabel("Vibration (g)")
        plt.title("Vibration Sensor Data with Noise")
        plt.legend()
        plt.grid(True)
        plt.xlim(0, 2)  # Show only first 2 seconds for clarity
        plt.show()

        # Evaluate the data quality based on noise level
        with output_text:
            output_text.clear_output()
            if noise_level < 0.05:
                message = "✅ <b>Data is clean:</b> Vibration readings are accurate and reliable."
            elif noise_level < 0.15:
                message = "⚠️ <b>Some noise present:</b> Still usable, but minor distortions may affect precision."
            elif noise_level < 0.25:
                message = "⚠️ <b>Significant noise:</b> Possible difficulty in detecting real anomalies."
            else:
                message = "❌ <b>Data unreliable:</b> Noise overwhelms the actual signal, making diagnosis impossible!"

            display(HTML(f"<p style='font-size:18px; color:black;'>{message}</p>"))

    # Interactive noise slider
    noise_slider = FloatSlider(value=0.0, min=0.0, max=0.3, step=0.05, description="Noise Level")

    # Display interactive plot and output text
    interact(analyze_vibration, noise_level=noise_slider)
    display(output_text)

# To run the example, simply call example1()

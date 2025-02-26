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
from ipywidgets import interact, FloatSlider

def example1():
    # Set default font to Times New Roman, size 12
    rcParams['font.family'] = 'serif'
    rcParams['font.serif'] = 'Times New Roman'
    rcParams['font.size'] = 12
    # Generate some clean data
    np.random.seed(0)
    x = np.linspace(0, 10, 50)
    y = np.sin(x)

    def plot_with_noise(noise_level=0.1):
        # Add noise
        noisy_y = y + np.random.normal(0, noise_level, size=y.shape)
        
        # Plotting
        plt.figure(figsize=(5, 3))
        plt.scatter(x, y, label='Data', color='blue', s=3)  # Original clean sine data
        plt.scatter(x, noisy_y, color='blue', label='Noisy Data', s=3, alpha=1)  # Noisy data
        plt.title('Effect of Noise on Data')
        plt.xlabel('X')
        plt.ylabel('Y')
        # plt.legend(loc='upper left')
        plt.grid(True)
        plt.ylim(-3, 3)
        plt.show()

    # Widget to control the noise level with adjusted layout
    interact(plot_with_noise, 
             noise_level=FloatSlider(value=0.1, min=0.0, max=1.0, step=0.1, description='Noise Level', style={'description_width': 'initial'}))

# To run the example, simply call example1()

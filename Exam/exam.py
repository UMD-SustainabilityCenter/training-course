# exam.py
import subprocess
import ipywidgets as widgets
from IPython.display import display, clear_output
import json
import requests
import time
import threading
from datetime import datetime

ADMIN_SERVER_URL = "http://141.215.12.38:8000"

def take_exam(exam_id: str):
    """Main function to launch the exam interface"""
    # Get student ID from hostname
    student_id = subprocess.run(
        "hostname | sed 's/^jupyter-//'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    # Create widgets
    output_widget = widgets.Output()
    full_name_input = widgets.Text(placeholder="Enter your full name (for certificate only)")
    exam_policy_agreement = widgets.Checkbox(value=False, description="I agree to the exam policy")
    submit_button = widgets.Button(description="Start Exam", button_style='success')

    def submit_details(btn):
        """Handle form submission"""
        student_name = full_name_input.value.strip()
        timestamp = datetime.now().isoformat()

        with output_widget:
            clear_output()
            if not student_name:
                display(widgets.HTML(value="<h4 style='color:red;'>❌ Full name is required</h4>"))
                return

            if not exam_policy_agreement.value:
                display(widgets.HTML(value="<h4 style='color:red;'>❌ Agree to exam policy</h4>"))
                return

            try:
                response = requests.post(
                    f"{ADMIN_SERVER_URL}/request_exam",
                    json={
                        "student_name": student_name,
                        "student_id": student_id,
                        "timestamp": timestamp,
                        "exam_id": exam_id
                    }
                )
                
                if response.status_code != 200:
                    display(widgets.HTML(value=f"<h4 style='color:red;'>❌ {response.json().get('detail', 'Unknown error')}</h4>"))
                    return

                exam_data = response.json()
                display(widgets.HTML(value=f"<h3>✅ Welcome {student_name}!</h3>"))
                _generate_exam_interface(exam_data["exam"])

            except Exception as e:
                display(widgets.HTML(value=f"<h4 style='color:red;'>❌ Connection error: {str(e)}</h4>"))

    def _generate_exam_interface(exam_data):
        """Create exam UI components"""
        with output_widget:
            clear_output()
            display(widgets.HTML(value=f"<h2>{exam_data['title']}</h2>"))
            
            question_widgets = []
            for i, q in enumerate(exam_data["questions"]):
                display(widgets.HTML(value=f"<b>Q{i+1}: {q['question']}</b>"))
                
                if q["type"] == "multiple_choice":
                    widget = widgets.RadioButtons(options=q["options"], layout={'width': 'max-content'})
                    display(widget)
                    question_widgets.append((i, widget))

                elif q["type"] == "true_false":
                    widget = widgets.RadioButtons(options=["True", "False"], layout={'width': 'max-content'})
                    display(widget)
                    question_widgets.append((i, widget))

                elif q["type"] == "multiple_select":
                    # Create checkboxes for multi-select
                    checkboxes = [widgets.Checkbox(value=False, description=opt) for opt in q["options"]]
                    container = widgets.VBox([
                        widgets.HTML(value="<i>Select all that apply:</i>"),
                        widgets.VBox(checkboxes)
                    ])
                    display(container)
                    question_widgets.append((i, checkboxes))

                elif q["type"] == "matching":
                    # Create matching table with dropdowns
                    prompts = list(q["options"].keys())
                    answers = list(set(q["options"].values()))  # Get unique answers
                    
                    # Create grid children list
                    children = []
                    
                    # Add headers
                    children.append(widgets.HTML(value="<b>Prompt</b>", layout=widgets.Layout(width='200px', padding='5px')))
                    children.append(widgets.HTML(value="<b>Match</b>", layout=widgets.Layout(width='300px', padding='5px')))
                    
                    # Create rows with prompts and dropdowns
                    dropdowns = []
                    for prompt in prompts:
                        # Prompt cell
                        children.append(widgets.Label(value=prompt, layout=widgets.Layout(width='200px', padding='5px')))
                        
                        # Dropdown cell
                        dropdown = widgets.Dropdown(options=answers, layout=widgets.Layout(width='300px'))
                        children.append(dropdown)
                        dropdowns.append(dropdown)
                    
                    # Create grid layout
                    grid = widgets.GridBox(
                        children=children,
                        layout=widgets.Layout(
                            grid_template_columns='200px 300px',
                            grid_auto_rows='40px',
                            grid_gap='5px 10px',
                            margin='10px 0',
                            border='1px solid #ddd',
                            padding='10px'
                        )
                    )
                    
                    display(widgets.VBox([
                        widgets.HTML(value="<i>Match each item with the correct description:</i>"),
                        grid
                    ]))
                    question_widgets.append((i, (prompts, dropdowns)))

                elif q["type"] in ["short_answer", "essay"]:
                    height = '150px' if q["type"] == "essay" else '100px'
                    widget = widgets.Textarea(layout={'width': '80%', 'height': height})
                    display(widget)
                    question_widgets.append((i, widget))

            # Timer and submission
            submit_btn = widgets.Button(description="Submit Exam", button_style='danger')
            submit_btn.on_click(lambda b: _submit_exam(question_widgets, exam_data))
            display(submit_btn)
            _start_timer(exam_data["duration_minutes"] * 60, question_widgets, exam_data)

    def _submit_exam(question_widgets, exam_data):
        """Handle exam submission"""
        responses = {}
        for idx, widget in question_widgets:
            q_type = exam_data["questions"][idx]["type"]
            
            if q_type == "multiple_select":
                # Get selected checkboxes
                responses[str(idx)] = [cb.description for cb in widget if cb.value]
                
            elif q_type == "matching":
                # Get prompt-dropdown pairs
                prompts, dropdowns = widget
                responses[str(idx)] = {prompt: dropdown.value for prompt, dropdown in zip(prompts, dropdowns)}
                
            else:
                # Standard widget value
                responses[str(idx)] = widget.value

        try:
            requests.post(
                f"{ADMIN_SERVER_URL}/submit_exam",
                json={
                    "student_name": full_name_input.value.strip(),
                    "student_id": student_id,
                    "exam_id": exam_id,
                    "responses": responses
                }
            )
            with output_widget:
                clear_output()
                display(widgets.HTML(value="<h3>✅ Exam submitted successfully!</h3>"))
        except Exception as e:
            display(widgets.HTML(value=f"<h4 style='color:red;'>❌ Submission failed: {str(e)}</h4>"))

    def _start_timer(duration, question_widgets, exam_data):
        """Initialize countdown timer"""
        timer_display = widgets.Label(value=f"Time Remaining: {duration // 60}:{duration % 60:02d}")
        display(timer_display)

        def countdown():
            nonlocal duration
            while duration > 0:
                time.sleep(1)
                duration -= 1
                timer_display.value = f"Time Remaining: {duration // 60}:{duration % 60:02d}"
            _submit_exam(question_widgets, exam_data)

        threading.Thread(target=countdown, daemon=True).start()

    # Initial UI setup
    display(widgets.HTML(value="<h2>Exam Registration</h2>"))
    display(widgets.HTML(value="<p>Enter your name to begin:</p>"))
    display(full_name_input, exam_policy_agreement, submit_button)
    submit_button.on_click(submit_details)
    display(output_widget)


def get_progress(belt_name: str):
    """Display student's progress for a specific belt level"""
    # Get student ID from hostname
    student_id = subprocess.run(
        "hostname | sed 's/^jupyter-//'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    # Create output widget
    output_widget = widgets.Output()
    
    def check_progress():
        with output_widget:
            clear_output()
            try:
                # Add timeout and explicit JSON headers
                response = requests.get(
                    f"{ADMIN_SERVER_URL}/progress/{student_id}/belt/{belt_name}",
                    headers={'Accept': 'application/json'},
                    timeout=10
                )
                
                # Check for HTTP errors first
                try:
                    response.raise_for_status()
                except requests.HTTPError as e:
                    display(widgets.HTML(
                        value=f"<h4 style='color:red;'>❌ Server Error: {e.response.status_code}</h4>"
                        f"<p>Response: {e.response.text[:200]}</p>"
                    ))
                    return

                # Attempt JSON parsing
                try:
                    progress = response.json()
                except json.JSONDecodeError:
                    display(widgets.HTML(
                        value=f"<h4 style='color:red;'>❌ Invalid JSON Response</h4>"
                        f"<pre>Raw response: {response.text[:200]}</pre>"
                    ))
                    return

                # Calculate progress based on passed exams
                passed_exams = sum(1 for exam in progress['exams'] if exam['passed'])
                total_required = len(progress['exams'])
                progress_percentage = (passed_exams / total_required) * 100 if total_required > 0 else 0
                
                # Create progress display
                display(widgets.HTML(value=f"<h2>{belt_name.replace('_', ' ').title()} Progress</h2>"))
                
                # Progress bar (now based on passed exams count)
                progress_html = f"""
                <div style="width: 100%; background-color: #ddd; border-radius: 5px; overflow: hidden;">
                    <div style="width: {progress_percentage}%; 
                                background-color: {'#4CAF50' if progress['completed'] else '#2196F3'}; 
                                height: 24px; 
                                border-radius: 5px;
                                text-align: center;
                                color: white;
                                line-height: 24px;">
                        {int(progress_percentage)}% Complete ({passed_exams}/{total_required} exams passed)
                    </div>
                </div>
                """
                display(widgets.HTML(value=progress_html))
                
                # Exams table (unchanged, shows individual grades)
                table_html = """
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 12px; text-align: left;">Exam</th>
                        <th style="padding: 12px; text-align: left;">Status</th>
                        <th style="padding: 12px; text-align: right;">Best Grade</th>
                        <th style="padding: 12px; text-align: right;">Attempts</th>
                    </tr>
                """
                
                for exam in progress['exams']:
                    if exam['attempts'] == 0:
                        status_color = "#777777"
                        status_icon = "➖"
                        status_text = "Not attempted"
                        grade_display = "—"
                    else:
                        status_color = "#4CAF50" if exam['passed'] else "#f44336"
                        status_icon = "✔️" if exam['passed'] else "❌"
                        status_text = "Passed" if exam['passed'] else "Not Passed"
                        grade_display = f"{exam['best_grade']}/{exam['max_points']}"
                    
                    table_html += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd;">{exam['title']}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; color: {status_color};">
                            {status_icon} {status_text}
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">
                            {grade_display}
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">
                            {exam['attempts']}
                        </td>
                    </tr>
                    """
                
                table_html += "</table>"
                display(widgets.HTML(value=table_html))
                
                # Overall status
                status_color = "#4CAF50" if progress['completed'] else "#777777"
                display(widgets.HTML(
                    value=f"<h3 style='margin-top: 20px; color: {status_color};'>"
                          f"{'Completed' if progress['completed'] else 'Not Completed'}</h3>"
                ))

            except Exception as e:
                display(widgets.HTML(
                    value=f"<h4 style='color:red;'>❌ Connection Error: {str(e)}</h4>"
                    f"<p>Verify:</p>"
                    "<ul>"
                    "<li>Server is running at " + ADMIN_SERVER_URL + "</li>"
                    "<li>Belt name exists in course structure</li>"
                    "<li>Network connectivity</li>"
                    "</ul>"
                ))

    # Initial display and trigger check
    display(output_widget)
    check_progress()

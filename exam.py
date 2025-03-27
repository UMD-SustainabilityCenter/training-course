# exam.py
import subprocess
import ipywidgets as widgets
from IPython.display import display, clear_output, Javascript
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
    
    output_widget = widgets.Output()
    
    try:
        meta_resp = requests.get(
            f"{ADMIN_SERVER_URL}/exam_metadata/{exam_id}",
            headers={"Accept": "application/json"},
            timeout=10
        )
        meta_resp.raise_for_status()
        meta = meta_resp.json()
    except Exception as e:
        meta = {}

    max_attempts = meta.get("max_attempts", 0)
    attempts = meta.get("attempts", [])
    if max_attempts and len(attempts) >= max_attempts:
        with output_widget:
            clear_output()
            display(
                widgets.HTML(
                    value="<h3 style='color:red;'>Maximum number attempted</h3>"
                )
            )
        display(output_widget)
        get_progress(exam_id)
        return

    time_limit = meta.get("duration_minutes")
    time_limit_label = widgets.HTML(
        value=(
            f"<p><strong>Exam Time Limit:</strong> {time_limit} minutes</p>"
            if time_limit is not None
            else "<p><strong>Exam Time Limit:</strong> (Unavailable)</p>"
        )
    )

    # Create widgets for exam registration if max_attempts not reached
    full_name_input = widgets.Text(
        placeholder="Enter your full name (for certificate only)"
    )
    exam_policy_agreement = widgets.Checkbox(
        value=False, description="I agree to the exam policy"
    )
    display(time_limit_label)
    submit_button = widgets.Button(
        description="Start Exam", button_style="success"
    )

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
                responses[str(idx)] = [cb.description for cb in widget if cb.value]
                
            elif q_type == "matching":
                prompts, dropdowns = widget
                responses[str(idx)] = {prompt: dropdown.value for prompt, dropdown in zip(prompts, dropdowns)}
                
            else:
                responses[str(idx)] = widget.value

        try:
            response = requests.post(
                f"{ADMIN_SERVER_URL}/submit_exam",
                json={
                    "student_name": full_name_input.value.strip(),
                    "student_id": student_id,
                    "exam_id": exam_id,
                    "responses": responses
                }
            )
            response.raise_for_status()
            
            with output_widget:
                clear_output()
                display(widgets.HTML(value="<h3>✅ Exam submitted successfully!</h3>"))
                # Show progress after submission
                get_progress(exam_id)  # Call progress function with exam_id

        except Exception as e:
            with output_widget:
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

def get_progress(exam_id: str):
    """Display student's progress for the selected exam."""
    # Get student ID from hostname
    student_id = subprocess.run(
        "hostname | sed 's/^jupyter-//'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    output_widget = widgets.Output()
    refresh_button = widgets.Button(description="Refresh Progress", icon='sync')
    
    def check_progress(_=None):
        with output_widget:
            clear_output()
            try:
                response = requests.get(
                    f"{ADMIN_SERVER_URL}/progress/{student_id}/exam/{exam_id}",
                    headers={'Accept': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()
                progress = response.json()
                exam_title = progress.get("title", "Exam Progress")
                attempts = progress.get("attempts", [])
                request_cert_flag = progress.get("request_certificate", False)
                
                display(widgets.HTML(value=f"<h2>{exam_title} - Attempts</h2>"))
                
                # Determine if any attempt is passing.
                passed = any(attempt.get("normalized_grade", 0) >= attempt.get("passing_threshold", 50)
                             for attempt in attempts)
                if passed:
                    passed_html = widgets.HTML(value="<h3 style='color: green;'>Exam Passed</h3>")
                    display(passed_html)
                    if request_cert_flag:
                        request_btn = widgets.Button(description="Request Certificate", button_style="info")
                        cert_status = widgets.HTML(value="")  # Status message placeholder.
                        def on_request_certificate(b):
                            try:
                                cert_res = requests.get(f"{ADMIN_SERVER_URL}/request_certificate/{student_id}/{exam_id}")
                                cert_res.raise_for_status()
                                msg = cert_res.json().get("message", "Certificate request successful.")
                                cert_status.value = f"<p style='color:green;'>{msg} (Under Development)</p>"
                            except Exception as e:
                                cert_status.value = f"<p style='color:red;'>Certificate request failed: {str(e)} (Under Development)</p>"
                        request_btn.on_click(on_request_certificate)
                        display(widgets.HBox([request_btn, cert_status]))
                
                if not attempts:
                    display(widgets.HTML(value="<p>No attempts yet.</p>"))
                else:
                    # Build the table header with the required columns
                    table_html = """
                    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                        <tr style="background-color: #f2f2f2;">
                            <th style="padding: 12px; text-align: left;">Attempt Number</th>
                            <th style="padding: 12px; text-align: left;">Date Taken</th>
                            <th style="padding: 12px; text-align: right;">Grade</th>
                            <th style="padding: 12px; text-align: right;">Duration (min)</th>
                        </tr>
                    """
                    total = len(attempts)
                    # Iterate through attempts in reverse order and assign sequential attempt numbers.
                    for i, attempt in enumerate(reversed(attempts), start=1):
                        attempt_number = total - i + 1
                        try:
                            # We assume the timestamp returned is in UTC.
                            dt = datetime.fromisoformat(attempt.get("timestamp", ""))
                            # Format as ISO string without timezone indicator.
                            date_taken = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            date_taken = attempt.get("timestamp", "")
                        raw_grade = attempt.get("raw_grade", 0)
                        max_points = attempt.get("max_points", 0)
                        rounded_norm = round(attempt.get("normalized_grade", 0), 2)
                        passing_threshold = attempt.get("passing_threshold", 50)
                        emoji = "✅" if rounded_norm >= passing_threshold else "❌"
                        grade_display = f"{raw_grade}/{max_points} ({rounded_norm}%) {emoji}"
                        duration_min = int(attempt.get("duration_seconds", 0) / 60)
                        
                        # Output the UTC timestamp in a span with class "localtime" and include the UTC string in a data attribute.
                        table_html += f"""
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #ddd;">Attempt {attempt_number}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                                <span class="localtime" data-utc="{date_taken}">{date_taken}</span>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{grade_display}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{duration_min} min</td>
                        </tr>
                        """
                    table_html += "</table>"
                    
                    display(widgets.HTML(value=table_html))
                    # Now, call a Javascript snippet to adjust any date in a span with class "localtime" to the browser's local time.
                    display(Javascript("""
                        var elems = document.querySelectorAll('.localtime');
                        elems.forEach(function(el){
                            var utcStr = el.getAttribute('data-utc');
                            // Append 'Z' so the string is treated as UTC.
                            if(utcStr && !utcStr.endsWith("Z")){
                                utcStr += "Z";
                            }
                            var d = new Date(utcStr);
                            if(!isNaN(d)){
                                el.innerText = d.toLocaleString();
                            }
                        });
                    """))
                    
            except Exception as e:
                display(widgets.HTML(
                    value=f"<h4 style='color:red;'>❌ Error: {str(e)}</h4>"
                ))
    
    refresh_button.on_click(check_progress)
    display(widgets.VBox([widgets.HBox([refresh_button]), output_widget]))
    check_progress()
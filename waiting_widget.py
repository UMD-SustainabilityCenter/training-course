# waiting_widget_module.py
import ipywidgets as widgets
from IPython.display import display
import time

class WaitingWidget:
    def __init__(
        self,
        running_text="🟧 Code Running Please Wait",
        success_text="✅ Code Successful",
        failure_text="❌ Code Crashed",
        animation_style="move_dots",  # Default animation style
    ):
        self.running_text = running_text
        self.success_text = success_text
        self.failure_text = failure_text
        self.animation_style = animation_style
        self.widget = widgets.HTML(value=self._generate_html())

    def _generate_html(self):
        if self.animation_style == "move_dots":
            animation_css = """
            .dots-container {
                display: inline-flex;
                align-items: center;
                justify-content: flex-start;
                margin-left: 5px;
            }

            .dot {
                width: 0.4em;
                height: 0.4em;
                background-color: orange;
                border-radius: 50%;
                margin: 0 0.1em;
                animation: moveDots 1.2s linear infinite;
            }

            .dot:nth-child(1) {
                animation-delay: 0s;
            }

            .dot:nth-child(2) {
                animation-delay: 0.4s;
            }

            .dot:nth-child(3) {
                animation-delay: 0.8s;
            }

            @keyframes moveDots {
                0%, 80%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-0.2em);
                }
            }
            """
            dots_html = """
            <div class="dots-container">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """
        elif self.animation_style == "rotate_circle":
            animation_css = """
            .dots-container {
                width: 20px; /* Adjusted container size */
                height: 20px; /* Adjusted container size */
                position: relative;
            }

            .dot {
                width: 6px;  /* Adjusted dot size */
                height: 6px; /* Adjusted dot size */
                background-color: orange;
                border-radius: 50%;
                position: absolute;
            }

            .dot:nth-child(1) { /* Top Dot */
                top: 0%;
                left: 50%;
                margin-left: -3px; /* Adjusted centering */
                animation: moveVertical 1.5s ease-in-out infinite;
            }

            .dot:nth-child(2) { /* Left Dot */
                top: 50%;
                left: 0%;
                margin-top: -3px; /* Adjusted centering */
                animation: moveHorizontal 1.5s ease-in-out infinite;
            }

            @keyframes moveVertical {
                0%, 100% {
                    transform: translateY(0);
                }
                50% {
                    transform: translateY(10px); /* Adjusted movement distance */
                }
            }

            @keyframes moveHorizontal {
                0%, 100% {
                    transform: translateX(0);
                }
                50% {
                    transform: translateX(10px); /* Adjusted movement distance */
                }
            }
            """
            dots_html = """
            <div class="dots-container">
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """
        else:
            raise ValueError(
                f"Invalid animation_style: {self.animation_style}.  Valid styles are 'move_dots' and 'rotate_circle'."
            )

        return f"""
        <style>
        {animation_css}
        </style>
        <span style='color: orange;'>{self.running_text} </span>
        {dots_html}
        """

    def display_widget(self):
        display(self.widget)

    def update_status(self, message, color):
        self.widget.value = f"<span style='color: {color};'>{message}</span>"

    def run_code(self, code_function):
        self.display_widget()
        try:
            code_function()
            self.update_status(self.success_text, "green")
        except Exception as e:
            self.update_status(f"{self.failure_text}: {e}", "red")


if __name__ == "__main__":

    def my_long_running_code():
        time.sleep(2)
        # raise ValueError("Simulated Crash!") #uncomment this line to test
        time.sleep(3)


    # Using default animation
    waiting_tool_default = WaitingWidget()
    waiting_tool_default.run_code(my_long_running_code)

    # Using rotate_circle animation
    waiting_tool_rotate = WaitingWidget(animation_style="rotate_circle")
    waiting_tool_rotate.run_code(my_long_running_code)

    # Using custom texts and animation
    waiting_tool_custom = WaitingWidget(
        running_text="⚙️ Processing...",
        success_text="✅ Task Completed!",
        failure_text="❌ Error Occurred",
        animation_style="rotate_circle",
    )
    waiting_tool_custom.run_code(my_long_running_code)

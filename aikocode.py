import ollama
import gradio as gr

# Set constants
OLLAMA_MODEL = "llama3.2"

# System messages
SYSTEM_MESSAGE = """
You are an assistant that analyzes input code from a user and adds
docstring and comments for all programming languages. If you don't know how
to comment the code say so. Do not add additional code unless the user asks. If 
the user asks for code include a brief summary after.
"""

UNIT_TEST_MESSAGE = """
You are an assistant that writes executable unit tests in the program language's framework for code.
Your task is to generate unit tests for the code provided by the user.

Requirements:
1. Detect the programming language from the code.
2. Write test functions that validate correct behavior of all functions and methods.
3. Include tests for default argument values and typical inputs.
4. Include tests for custom arguments where applicable.
5. Avoid tests that assume errors or exceptions for valid default behavior.
6. Include all necessary imports.
7. Use fixtures if appropriate to set up reusable objects.
8. Output only executable code. Do not include explanations or placeholders.
9. Use descriptive names for test functions and ensure they are ready to run.
10. For Python, generate pytests.
11. For C, generate a simple test harness with assert statements.
12. For Java, generate JUnit tests.

Example for Python with pytest:
import pytest
from employee import Employee

@pytest.fixture
def employee():
    return Employee('Alice', 'Brown', 50000)

def test_give_default_raise(employee):
    employee.give_raise()
    assert employee.salary == 55000

def test_give_custom_raise(employee):
    employee.give_raise(10000)
    assert employee.salary == 60000
"""

# Function to comment code
def comment_code(function_code):
    """Calls Ollama to comment user-provided code."""
    if not function_code.strip():
        return "Please provide code to comment."

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": function_code},
    ]

    response = ""
    chat_stream = ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True)
    for chunk in chat_stream:
        response += chunk.message.content or ""

    return response

# Function to generate unit test
def generate_unit_test(function_code):
    """Calls Ollama to generate a unit test for the provided code."""
    if not function_code.strip():
        return "Please provide code to generate a unit test."

    messages = [
        {"role": "system", "content": UNIT_TEST_MESSAGE},
        {"role": "user", "content": function_code},
    ]

    response = ""
    chat_stream = ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True)
    for chunk in chat_stream:
        response += chunk.message.content or ""

    return response

# Create Gradio UI
def gradio_interface(function_code, output_type):
    """Wrapper to select comment or unit test."""
    if output_type == "Add Comments":
        return comment_code(function_code)
    elif output_type == "Unit Test":
        return generate_unit_test(function_code)
    else:
        return "Invalid option selected."

with gr.Blocks(title="AikoCode", theme='NoCrypt/miku') as view:

    gr.Markdown(
        """
        # Hi! I'm Aiko, your friendly coding assistant.
        Enter your code below and choose whether you want comments or a unit test.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            code_input = gr.Textbox(
                label="Enter Your Code Here",
                placeholder="Let's get coding...",
                lines=15,
                elem_classes="input-box"
            )
            output_type = gr.Dropdown(
                label="What would you like me to do?",
                choices=["Add Comments", "Unit Test"],
                value="Add Comments",
                allow_custom_value=False,
                elem_classes="input-box"
            )
            run_button = gr.Button("Generate Code")

        with gr.Column(scale=3):
            code_output = gr.Markdown(
                "Your commented code or unit test will appear here!",
                elem_classes="output-box"
            )

    run_button.click(
        fn=gradio_interface,
        inputs=[code_input, output_type],
        outputs=[code_output]
    )

view.launch(share=True, inbrowser=True)
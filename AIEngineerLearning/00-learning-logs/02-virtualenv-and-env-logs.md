1. VENV

Why Do We Need a venv?
By default, when you install a Python package using pip install, your computer installs it globally—meaning it's shared across your entire machine. This leads to a massive headache called dependency hell.

Imagine you have two projects on your computer:

- Project A is an older website that relies on a package called LibraryX version 1.0.

- Project B is a brand new project that requires features only available in LibraryX version 3.0.

If you install version 3.0 globally, it will overwrite version 1.0, and Project A will instantly break.

The Solution: A venv is an isolated, self-contained digital sandbox for a specific project. It creates a private folder containing its own copy of Python and its own isolated set of packages. What you install inside Project A's sandbox stays there and never touches Project B.

2. How to Create and Use a venv
Creating and using a virtual environment takes three quick steps in your terminal.

Step 1: Create the environment
Open your terminal, navigate to your project directory (where your main.py is), and run the following command:

Bash
python -m venv .venv

What this does: It tells Python to run its built-in virtual environment module (-m venv) and create a folder named .venv inside your project directory. You can name the folder anything, but .venv or env are the industry standards.

Step 2: Activate the environment
Before you can use the sandbox, you have to "step inside" it. The command depends on your computer's operating system:

On Mac / Linux:
Bash
source .venv/bin/activate

On Windows (Command Prompt):
DOS
.venv\Scripts\activate.bat

On Windows (PowerShell):
PowerShell
.venv\Scripts\Activate.ps1

How do you know it worked? Your terminal prompt will change to show (.venv) at the very beginning of the line, like this:

(.venv) user@computer:~/my_project$

Step 3: Install your packages
Now that the environment is active, any package you install is completely isolated to this project:
pip install requests

How to leave (Deactivate)
When you are done working on this project and want to go back to your global computer settings, simply type:
deactivate

One Crucial Best Practice: .gitignore
Because the .venv folder contains a full copy of Python and all installed packages, it can easily grow to hundreds of megabytes.

Never commit your .venv folder to GitHub.

Instead, create a file named .gitignore in your root folder and add .venv/ to it, so Git knows to ignore it. To share your dependencies with other developers, use pip freeze > requirements.txt to save a tiny text list of your packages instead.
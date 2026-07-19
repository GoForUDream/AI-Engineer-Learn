# Virtual Environments and Environment Variables — Learning Log

## 1. Why Do We Need a Virtual Environment?

By default, installing a Python package globally makes it available across the machine. This can cause **dependency conflicts** when different projects require different versions of the same package.

For example:

- **Project A** depends on `LibraryX==1.0`.
- **Project B** needs features available only in `LibraryX==3.0`.

Installing version `3.0` globally could replace version `1.0` and break Project A.

### The Solution

A virtual environment, or **venv**, is an isolated environment for one project. It has its own Python installation context and package set, so packages installed for one project do not affect another.

## 2. How to Create and Use a Virtual Environment

### Step 1: Create the Environment

From the project directory, run:

```powershell
python -m venv .venv
```

This runs Python's built-in `venv` module and creates an environment in `.venv/`. The names `.venv` and `env` are common conventions.

### Step 2: Activate the Environment

Use the command for your operating system and shell.

**macOS or Linux:**

```bash
source .venv/bin/activate
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate.bat
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal prompt usually begins with `(.venv)`:

```text
(.venv) user@computer:~/my_project$
```

### Step 3: Install Packages

Packages installed while the environment is active remain isolated to the project:

```powershell
python -m pip install requests
```

### Deactivate the Environment

Run the following command when you want to leave the virtual environment:

```powershell
deactivate
```

## 3. Important Git Practice

The `.venv/` directory contains Python and installed packages, so it can become large. It should not be committed to Git.

Add it to `.gitignore`:

```gitignore
.venv/
```

To share project dependencies, save them to a small text file instead:

```powershell
python -m pip freeze > requirements.txt
```

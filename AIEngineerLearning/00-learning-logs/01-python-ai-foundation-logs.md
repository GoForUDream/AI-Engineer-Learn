1. How Python Code is Executed

Many people refer to Python as an interpreted language, but its execution process actually involves a hybrid approach of compilation and interpretation:
    [Source Code .py] ──(Auto-compiled)──> [Bytecode .pyc] ──(PVM Interpreted)──> [Machine Code 0101]

- Step 1: Compilation (To Bytecode)
Python first checks your syntax. If it looks good, the internal Python compiler translates your human-readable text (.py) into a low-level, platform-independent instruction set called Bytecode.

You might see these files stored in a folder named __pycache__ with a .pyc extension.

Why? Bytecode is much faster to load and run the next time you execute the script because Python doesn't have to re-parse your text file.

- Step 2: Interpretation (The PVM)
Next, the bytecode is sent to the Python Virtual Machine (PVM). The PVM is the runtime engine of Python—an interpreter that loops through your bytecode instructions one by one, converts them into binary machine code that your specific computer processor (Intel, AMD, Apple Silicon) understands, and executes them.

The Big Takeaway: Python compiles your code to bytecode automatically to save time, then interprets that bytecode on the fly. This is why Python is cross-platform; the same bytecode can run on Windows, Mac, or Linux as long as that system has a PVM installed.

2. What is __init__ in Python?
In Python, __init__ is a special method used in Object-Oriented Programming (OOP). It is often called the constructor, though technically it's an initializer.

When you create a blueprint for an object (a Class), __init__ is the method that automatically fires up the moment you instantiate (create) an individual object from that blueprint. Its main job is to set up the starting data—known as attributes—for your object.

A Simple Analogy
Think of a class as a factory blueprint for a car. The __init__ method is the setup line at the factory where you decide what color this specific car will be, how many seats it will have, and what its brand is before it hits the road.

Here is how it looks in code:

Python
class Car:
    # The initializer method
    def __init__(self, brand, color):
        self.brand = brand   # 'self' attaches the variable to the specific object
        self.color = color

# Creating two distinct objects (instances) from the Car blueprint
car1 = Car("Toyota", "Red")
car2 = Car("Tesla", "Electric Blue")

# Accessing their unique attributes
print(car1.color)  # Outputs: Red
print(car2.brand)  # Outputs: Tesla

Breaking Down the Syntax:
The Dunder (__): The double underscores mean this is a "magic" or "dunder" method built into Python's core. You don't call car1.__init__() manually; Python calls it implicitly when you run Car("Toyota", "Red").

self: This represents the specific object being created right now. When you type car1 = Car(...), Python translates self.brand = brand into car1.brand = "Toyota". You must always include self as the first parameter in __init__.

3. Why we need to have good structure in Python project:
- Maintainability: If your payment gateway changes from Stripe to PayPal, you only modify code inside the services/ folder. main.py stays exactly the same.

- Team Collaboration: Multiple developers can work on the project simultaneously without stepping on each other's toes. One person can tweak settings in config.py while another writes code in services/.

- Testing: It is significantly easier to write automated tests for a single, isolated function inside a service file than it is to test a giant, tangled main.py.
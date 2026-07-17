# Python AI Foundation — Learning Log

## 1. How Is Python Code Executed?

Python is often described as an interpreted language, but its execution process combines compilation and interpretation:

```text
Source code (.py) → Bytecode (.pyc) → Python Virtual Machine (PVM) → Machine instructions
```

### Step 1: Compile to Bytecode

Python first checks the syntax. If it is valid, Python's internal compiler translates the human-readable source code into a lower-level, platform-independent instruction set called **bytecode**.

Python may cache this bytecode in a `__pycache__/` directory using files with the `.pyc` extension. Loading cached bytecode can be faster because Python does not need to parse and compile unchanged source code again.

### Step 2: Execute with the PVM

The bytecode is then executed by the **Python Virtual Machine (PVM)**. The PVM is Python's runtime engine and processes the bytecode instructions on the current system.

### Key Takeaway

Python automatically compiles source code to bytecode and then executes that bytecode through the PVM. This runtime model helps Python programs work across Windows, macOS, and Linux when a compatible Python interpreter is installed.

## 2. What Is `__init__` in Python?

In object-oriented Python, `__init__` is a special method used to initialize a new object. It is often called a constructor, although technically it is an **initializer**.

When you instantiate a class, Python calls `__init__` automatically. Its main job is to set the object's initial data, known as **attributes**.

### Analogy

Think of a class as a factory blueprint for a car. The `__init__` method is the setup stage where you decide the color, brand, and other properties of each specific car before it leaves the factory.

### Example

```python
class Car:
    def __init__(self, brand, color):
        self.brand = brand
        self.color = color


car1 = Car("Toyota", "Red")
car2 = Car("Tesla", "Electric Blue")

print(car1.color)  # Red
print(car2.brand)  # Tesla
```

### Syntax Breakdown

- **`__init__`:** The double underscores identify it as a special, or *dunder*, method. Python calls it implicitly when you create an object with `Car(...)`.
- **`self`:** Represents the specific object being initialized. For `car1 = Car(...)`, assigning `self.brand` stores the value on `car1`.

## 3. Why Does a Python Project Need Good Structure?

- **Maintainability:** If a payment gateway changes from Stripe to PayPal, code isolated in a `services/` directory can change without requiring unrelated changes to `main.py`.
- **Team collaboration:** Developers can work in separate modules, such as `config.py` and `services/`, with fewer conflicts.
- **Testing:** Small, isolated functions are easier to test than one large, tightly coupled `main.py` file.

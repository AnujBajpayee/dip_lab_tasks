# Contributing to DIP Lab Tasks

Thank you for your interest in contributing to **DIP Lab Tasks**! We welcome bug fixes, documentation enhancements, and new image processing algorithms.

---

## 🛠️ Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/dip_lab_tasks.git
   cd dip_lab_tasks
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Testing Guidelines

Ensure all tests pass before submitting changes:

```bash
pytest task_1_tambola_ticket_generator/test_tambola.py -v
pytest task_2_rgb_to_greyscale_conversion/test_grayscale.py -v
```

---

## 📦 Code Style

- Follow **PEP 8**.
- Use type hints and clear docstrings.
- Keep commits descriptive following Conventional Commits.

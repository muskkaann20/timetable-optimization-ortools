# 🎓 University Timetable Optimization using Constraint Programming

An automated university timetable optimization system built using Google OR-Tools (CP-SAT).
This project formulates academic scheduling as a constraint optimization problem, ensuring feasibility while improving timetable quality.

Author: Muskaan Manwani

---

## 📌 Problem Statement

University timetable creation is a complex task due to:

- Course clashes
- Professor availability constraints
- Room capacity limitations
- Excessive idle gaps
- Frequent room changes

Manual scheduling is time-consuming and often produces suboptimal results.
This project automates timetable generation using constraint programming.

---

## 🧠 Why Constraint Programming?

This is not a machine learning problem.

- Rules must always be satisfied
- Feasibility is mandatory
- The goal is optimization, not prediction

Therefore, the problem is modeled using constraint satisfaction and optimization with Google OR-Tools.

---

## 🧩 Model Overview

### Decision Variable

For each course c, room r, and time slot t:

x[c, r, t] = 1 if course c is scheduled in room r at time t  
x[c, r, t] = 0 otherwise

---

### 🔒 Hard Constraints

- Each course is scheduled for the required number of sessions
- A room hosts at most one class per time slot
- A professor teaches at most one class per time slot
- Room capacity must be sufficient for enrolled students
- Classes are scheduled only during professor availability

These constraints ensure feasibility.

---

### ✨ Soft Constraints

- Prefer earlier time slots
- Minimize professor idle gaps
- Minimize room switches for each course

These constraints improve timetable quality.

---

### 🎯 Objective Function

The solver minimizes a weighted sum of:

- Time slot penalties
- Professor idle gaps
- Room switch penalties

This balances feasibility and optimization.

---

## 🛠️ Tech Stack

- Python
- Google OR-Tools (CP-SAT)
- Pandas
- Jupyter Notebook
- CSV / JSON

---

## 📊 Results

The optimized timetable achieves:

- Zero room conflicts
- Zero professor conflicts
- Zero idle gaps
- Minimal room switches

This demonstrates the effectiveness of constraint-based optimization.

---

## 🌐 Live Demo (Streamlit App)

An interactive web interface has been built using Streamlit to visualize the optimized timetable and metrics.

🔗 Live App: https://timetable-optimizer.streamlit.app

---

## ▶️ How to Run

1. Install dependencies  
   pip install ortools pandas

2. Run the optimizer  
   python src/model.py

3. View outputs in:
   - results/schedule.csv
   - results/metrics.json
   - notebooks/analysis.ipynb

---

## 🚀 Future Work

- Computer Vision
- Reinforcement Learning
- Optimization
- Human-Computer Interaction (HCI)

---

## 👤 Author

Muskaan Manwanii  
Undergraduate student with interest in optimization, AI, and real-world problem solving.

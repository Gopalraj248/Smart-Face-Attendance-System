# 📸 Smart Face Attendance System (with Anti-Spoofing & Unique ID)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

**An advanced AI-based desktop application for contactless biometric attendance. It features real-time liveness detection (Blink Check) and supports Unique IDs to handle duplicate names.**

---

## 📖 About The Project

This project is a robust Face Attendance System built using Python. It addresses two major issues in traditional face recognition systems:
1.  **Spoofing:** Prevents users from marking attendance using photos/videos by implementing **Liveness Detection (Eye Blink Verification)**.
2.  **Duplicate Names:** Uses a **Unique ID System** (Roll No. / Employee ID) to distinguish between different users with the same name.

The system automatically marks **Entry Time** and **Exit Time** and saves records in an Excel-compatible CSV file.

### Key Features ✨

* **🆔 Unique ID Support:** Register users with `Name` + `Unique ID` (e.g., Rahul-101) to prevent data overwriting.
* **🛡️ Anti-Spoofing Security:** Active Liveness Check using **Eye Aspect Ratio (EAR)**. Attendance is marked *only* after the user blinks.
* **🔄 Smart Entry/Exit Logic:**
    * **Entry:** Marked immediately upon verification.
    * **Exit:** Marked if the user appears again after a set time interval (e.g., 1 minute).
* **🖥️ Modern GUI:** built with **CustomTkinter** for a professional dark-mode look.
* **📊 Automatic Reporting:** Generates a `attendance.csv` file with columns: `Name`, `ID`, `Date`, `Entry_Time`, `Exit_Time`.
* **🔊 Audio Feedback:** Beep sounds for success and error alerts.

---

## ⚙️ Tech Stack

* **Language:** Python 3.x
* **GUI:** CustomTkinter
* **Core AI:** OpenCV, face_recognition (dlib), NumPy
* **Math/Logic:** Scipy (for Euclidean distance calculation)
* **Utils:** Winsound, Pillow (PIL)

---

## 📸 Screenshots

*(Place your screenshots in an 'assets' folder and link them here)*

| User Registration (with ID) | Blink Verification |
| :---: | :---: |
| ![Register](assets/register_screenshot.png) | ![Verify](assets/blink_screenshot.png) |

---

## 🚀 Getting Started

### Prerequisites
Ensure you have **Python 3.10+** installed. You also need C++ Build Tools (for dlib).

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Smart-Face-Attendance-System.git](https://github.com/YOUR_USERNAME/Smart-Face-Attendance-System.git)
    cd Smart-Face-Attendance-System
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💡 How to Use

1.  **Run the Application:**
    ```bash
    python main.py
    ```

2.  **Register a New User:**
    * Enter **Name** (e.g., Gopal).
    * Enter **Unique ID** (e.g., 101).
    * Click **"📸 Save Face"**.
    * *Note: This saves the file as `Gopal-101.jpg`.*

3.  **Mark Attendance:**
    * Look at the camera.
    * The system will show **"Waiting for Blink..."**.
    * **Blink your eyes** naturally.
    * Upon verification, the system will beep and mark **Entry (Green)**.
    * If you appear again after 1 minute, it will mark **Exit (Red)**.

4.  **View Records:**
    * Open `attendance.csv` in Excel to see the logs.
    * **⚠ Important:** Always close the Excel file before running the app to avoid permission errors.

---

## 📂 Project Structure

```text
├── images/                # Database of user faces (Name-ID.jpg)
├── main.py                # Main source code
├── attendance.csv         # Attendance Log (Auto-generated)
├── requirements.txt       # Python dependencies
└── README.md              # Project Documentation
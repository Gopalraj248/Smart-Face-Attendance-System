# 📸 Smart Face Attendance System with Anti-Spoofing

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

**An advanced AI-based desktop application for contactless biometric attendance, featuring real-time liveness detection to prevent spoofing attacks.**

---

## 📖 About The Project

This project is a robust Face Attendance System built using Python. Unlike traditional systems, it incorporates a security layer against "Replay Attacks" (using photos or videos) by implementing **Liveness Detection (Blink Check / Random Action Challenge)**.

The system automatically marks **Entry Time** and **Exit Time** for registered users and maintains records in an Excel-compatible CSV file. It features a modern, dark-mode GUI built with **CustomTkinter**.

### Key Features ✨

* **👤 Real-time Face Recognition:** High-accuracy recognition using the `dlib` library.
* **🛡️ Anti-Spoofing Security:** Prevents attendance via photos/videos using active liveness checks (e.g., Blink detection or random actions like "Smile").
* **🔄 Automatic Entry/Exit Logic:** Intelligently marks entry and exit times based on a time buffer (prevents duplicate entries).
* **🖥️ Modern GUI:** Clean and professional dark-mode interface using `CustomTkinter`.
* **🔊 Audio Feedback:** Sound alerts for successful attendance or errors.
* **📊 CSV Reporting:** Automatically generates and updates daily attendance logs in CSV format.

---

## ⚙️ Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** CustomTkinter
* **Core AI/ML:** OpenCV, face_recognition (dlib), NumPy
* **Utilities:** Pillow (PIL), Winsound

---

## 📸 Screenshots

*(Add your screenshots here. You can create a folder named 'assets' in your project, save images there, and link them below)*

| Login Screen | Liveness Check |
| :---: | :---: |
| ![Login](assets/login_screenshot.png) | ![Action](assets/action_screenshot.png) |

---

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites

* Python 3.10 or higher installed.
* **Visual Studio Build Tools** (C++ compiler) installed (Required for `dlib` on Windows).

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/](https://github.com/)[gopalraj248]/[REPO_NAMESmart-Face-Attendance-System].git
    cd [Smart-Face-Attendance-System]
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # Activate on Windows:
    venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💡 How to Use

1.  Run the main application file:
    ```bash
    python main.py
    ```

2.  **Register a New User:**
    * Go to the "Add New User" section in the right panel.
    * Enter the person's name.
    * Click **"📸 Save Face"**. The system will capture and save the encoding.

3.  **Mark Attendance (Automatic Mode):**
    * Just stand in front of the camera.
    * Follow the instructions on the screen (e.g., "Please Blink" or "Smile").
    * Once verified, the system will mark **Entry** (Green) or **Exit** (Red) automatically with a sound alert.

4.  **Check Logs:**
    * Attendance is shown in the live log box.
    * A permanent record is saved in `attendance.csv` in the project root.

---

## 📂 Project Structure

```text
├── images/                # Stores user face images for registration
├── main.py                # Main application script (GUI & Logic)
├── attendance.csv         # Daily attendance records (auto-generated)
├── requirements.txt       # List of python dependencies
└── README.md              # Project documentation
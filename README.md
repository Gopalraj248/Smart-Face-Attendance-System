# 📸 Smart Face Attendance System (Privacy-First V2.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

**An advanced AI-based desktop application for contactless biometric attendance. It features "Privacy Mode" (Hidden Identity), real-time Liveness Detection (Anti-Spoofing), and Unique ID support.**

---

## 📖 About The Project

This project resolves major security and privacy flaws found in traditional face recognition systems.
1.  **🔒 Privacy First:** User identity (Name/ID) remains **HIDDEN** (Red Box) until the user is verified.
2.  **🛡️ Anti-Spoofing:** Prevents attendance via photos/videos using **Eye Blink Verification**.
3.  **🆔 Unique IDs:** Handles duplicate names (e.g., `Rahul-101` vs `Rahul-102`) using a unique ID logic.

The system automatically logs **Entry & Exit Time** in an Excel-compatible CSV file and captures a screenshot upon successful verification.

---

## ✨ Key Features

* **Privacy Mode:** The interface shows "LOCKED" or no name until the user passes the liveness check.
* **Live Feedback Banner:** Displays `Name | ID | Time` on a green banner instantly after verification.
* **Auto-Screenshot:** Saves a proof-of-attendance image in the `screenshots` folder.
* **Smart Logging:** Prevents spam entries (minimum 1-minute interval between Entry/Exit).
* **Modern UI:** Built with **CustomTkinter** for a clean, dark-mode experience.

---

## 📸 Screenshots

| Privacy Mode (Locked) | Verified Mode (Unlocked) |
| :---: | :---: |
| ![Locked Mode](screenshots/locked.png) | ![Verified Mode](screenshots/verified.jpg) |

*(Note: Ensure you have `locked.png` and `verified.jpg` in your screenshots folder)*

---

## ⚙️ Tech Stack

* **Language:** Python 3.x
* **GUI:** CustomTkinter
* **Core AI:** OpenCV, face_recognition (dlib), NumPy
* **Math/Logic:** Scipy (Euclidean distance for Blink Detection)
* **Utilities:** Winsound (Audio feedback), Pillow (PIL)

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher.
* Visual Studio Build Tools (for dlib installation).

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Gopalraj248/Smart-Face-Attendance-System.git](https://github.com/Gopalraj248/Smart-Face-Attendance-System.git)
    cd Smart-Face-Attendance-System
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💡 How to Use

1.  **Run the App:**
    ```bash
    python main.py
    ```

2.  **Register User:**
    * Enter **Name** and **Unique ID** (e.g., 101).
    * Click **"📸 Save Face"**.

3.  **Mark Attendance:**
    * Stand in front of the camera. You will see a **RED BOX** (Locked).
    * **Blink your eyes** to verify liveness.
    * The box turns **GREEN**, and your Name/ID is revealed.
    * Attendance is marked in `attendance.csv`.

---

## 📂 Project Structure

```text
├── images/                # Database of registered faces
├── screenshots/           # Auto-saved proof of attendance
├── main.py                # Main application source code
├── attendance.csv         # Daily logs (Auto-generated)
├── requirements.txt       # Dependencies list
└── README.md              # Documentation
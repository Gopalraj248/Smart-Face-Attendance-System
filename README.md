![Gopal_101_11-36-59](https://github.com/user-attachments/assets/f8d447db-2d47-4c8f-baa8-0866c69acecf)
# 📸 Smart Face Attendance System (Privacy-First V2.1)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

**An advanced AI-based desktop application for contactless biometric attendance. It features "Privacy Mode" (Hidden Identity), real-time Liveness Detection (Anti-Spoofing), high-speed encoding cache, smooth 30+ FPS camera feed, and Unique ID support.**

---

## 📖 About The Project

This project resolves major security and privacy flaws found in traditional face recognition systems.
1.  **🔒 Privacy First:** User identity (Name/ID) remains **HIDDEN** (Red Box) until the user is verified.
2.  **🛡️ Anti-Spoofing (Per-User Isolation):** Prevents attendance via photos/videos using **Individual Eye Blink Verification** (eliminating multi-person spoofing flaws).
3.  **⚡ Instant Startup & High FPS:** Utilizes an intelligent pickle cache to launch instantly and 2-frame processing intervals for a smooth 30+ FPS webcam experience.
4.  **🆔 Unique IDs & Clean Names:** Seamlessly handles multi-word/hyphenated names (e.g., `Gopal Rajbhar-101`) with unique IDs.

The system automatically logs **Entry & Exit Time** in an Excel-compatible CSV file and captures a screenshot upon successful verification.

---

## ✨ Key Features

* **Privacy Mode:** The interface shows a red locked bounding box with no name until the user passes the eye-blink liveness check.
* **Per-Face Liveness Verification:** Isolated liveness tracking so static photos held alongside real people cannot trick the system.
* **Live Feedback Banner:** Displays `Name | ID | Time` on a green banner instantly after verification.
* **Auto-Screenshot Proof:** Saves a proof-of-attendance image with embedded timestamped banner in the `screenshots` folder.
* **Smart Logging & Cooldown:** Prevents spam entries (minimum 1-minute interval between Entry/Exit, with 8-second punch debouncing).
* **Admin PIN Security:** Protects user enrollment and full attendance records behind an Admin PIN (Default: `1234`), keeping the attendance screen secure for public kiosk use.
* **Modern UI:** Built with **CustomTkinter** with clean Tabview navigation and clean window exit handling.

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

4.  **Configure Environment (.env)**
    ```bash
    # Windows:
    copy .env.example .env
    ```
    *Open `.env` and configure your `ADMIN_PIN` (default: 1234), `CAMERA_INDEX` (default: 0), etc.*

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

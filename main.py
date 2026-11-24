import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime, timedelta
import pickle
import time
from scipy.spatial import distance as dist

# --- LOAD ENVIRONMENT VARIABLES (.env) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- SAFE AUDIO HELPER (Cross-Platform) ---
def play_beep(freq, duration):
    try:
        import winsound
        winsound.Beep(freq, duration)
    except Exception:
        pass

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- SETTINGS (Loaded dynamically from .env with safe defaults) ---
ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
MIN_MINUTES_BEFORE_EXIT = float(os.getenv("MIN_MINUTES_BEFORE_EXIT", "1"))
EYE_ASPECT_RATIO_THRESHOLD = float(os.getenv("EYE_ASPECT_RATIO_THRESHOLD", "0.30"))
EYE_ASPECT_RATIO_CONSEC_FRAMES = int(os.getenv("EYE_ASPECT_RATIO_CONSEC_FRAMES", "2"))
FEEDBACK_DURATION = int(os.getenv("FEEDBACK_DURATION", "40"))
FRAME_PROCESS_INTERVAL = int(os.getenv("FRAME_PROCESS_INTERVAL", "2"))
CACHE_FILE = os.getenv("CACHE_FILE", "encodings_cache.pkl")
PUNCH_COOLDOWN_SECONDS = int(os.getenv("PUNCH_COOLDOWN_SECONDS", "8"))

class FaceAttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Attendance System - Privacy & Liveness V2.1")
        self.geometry("1100x720")

        # Cleanly release camera and close window on [X] button click
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT FRAME: Camera ---
        self.camera_frame = ctk.CTkFrame(self, corner_radius=10)
        self.camera_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.cam_label = ctk.CTkLabel(self.camera_frame, text="")
        self.cam_label.pack(expand=True, fill="both", padx=10, pady=10)

        # --- RIGHT FRAME: Controls & Tabs ---
        self.control_frame = ctk.CTkFrame(self, width=350, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # --- TABVIEW (Separates Attendance Mode and Password-Protected Admin Panel) ---
        self.tabview = ctk.CTkTabview(self.control_frame, width=320, command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=(10, 5))

        self.tab_attendance = self.tabview.add("📌 Attendance")
        self.tab_admin = self.tabview.add("🔒 Admin Panel")
        self.tabview.set("📌 Attendance")

        # ==========================================
        # TAB 1: ATTENDANCE MODE (Public / Kiosk UI)
        # ==========================================
        self.lbl_title = ctk.CTkLabel(
            self.tab_attendance, 
            text="Secure Attendance", 
            font=("Roboto", 20, "bold"), 
            text_color="#00E676"
        )
        self.lbl_title.pack(pady=(12, 2))

        self.lbl_user_count = ctk.CTkLabel(
            self.tab_attendance, 
            text="👥 Registered: Loading...", 
            font=("Roboto", 13), 
            text_color="#90CAF9"
        )
        self.lbl_user_count.pack(pady=2)

        self.lbl_instruction = ctk.CTkLabel(
            self.tab_attendance, 
            text="ℹ Blink eyes to verify & mark attendance", 
            font=("Roboto", 12), 
            text_color="cyan"
        )
        self.lbl_instruction.pack(pady=4)

        self.divider = ctk.CTkFrame(self.tab_attendance, height=2, fg_color="gray")
        self.divider.pack(fill="x", padx=15, pady=8)

        self.status_label = ctk.CTkLabel(
            self.tab_attendance, 
            text="Scanning...", 
            font=("Roboto", 18, "bold"), 
            text_color="yellow"
        )
        self.status_label.pack(pady=4)

        # Spacious live punch log feed (Records cannot be opened from here)
        self.log_box = ctk.CTkTextbox(self.tab_attendance, width=280, height=270)
        self.log_box.pack(pady=8, padx=5)
        self.log_box.configure(state="disabled")

        # ==========================================
        # TAB 2: ADMIN PANEL (PIN-Protected)
        # ==========================================
        self.is_admin_authenticated = False

        # --- Sub-frame 1: Locked State (PIN Prompt) ---
        self.frame_admin_locked = ctk.CTkFrame(self.tab_admin, fg_color="transparent")
        self.frame_admin_locked.pack(fill="both", expand=True, padx=5, pady=25)

        self.lbl_lock_icon = ctk.CTkLabel(
            self.frame_admin_locked, 
            text="🔒", 
            font=("Roboto", 42)
        )
        self.lbl_lock_icon.pack(pady=(15, 5))

        self.lbl_admin_auth = ctk.CTkLabel(
            self.frame_admin_locked, 
            text="Admin Authorization", 
            font=("Roboto", 18, "bold"), 
            text_color="#64B5F6"
        )
        self.lbl_admin_auth.pack(pady=2)

        self.lbl_admin_desc = ctk.CTkLabel(
            self.frame_admin_locked, 
            text="Enter Admin PIN to manage users\nand access attendance records.", 
            font=("Roboto", 12), 
            text_color="#B0BEC5"
        )
        self.lbl_admin_desc.pack(pady=6)

        self.entry_pin = ctk.CTkEntry(
            self.frame_admin_locked, 
            placeholder_text="Enter PIN (Default: 1234)", 
            show="*", 
            width=220,
            justify="center",
            font=("Roboto", 14)
        )
        self.entry_pin.pack(pady=10)
        self.entry_pin.bind("<Return>", self.verify_admin_pin)

        self.btn_unlock = ctk.CTkButton(
            self.frame_admin_locked, 
            text="🔓 Unlock Admin Panel", 
            command=self.verify_admin_pin, 
            fg_color="#1976D2",
            hover_color="#1565C0",
            width=220,
            height=34,
            font=("Roboto", 13, "bold")
        )
        self.btn_unlock.pack(pady=5)

        self.lbl_pin_error = ctk.CTkLabel(
            self.frame_admin_locked, 
            text="", 
            text_color="#FF5252", 
            font=("Roboto", 13)
        )
        self.lbl_pin_error.pack(pady=5)

        # --- Sub-frame 2: Unlocked State (Admin Dashboard) ---
        self.frame_admin_unlocked = ctk.CTkFrame(self.tab_admin, fg_color="transparent")

        self.lbl_admin_title = ctk.CTkLabel(
            self.frame_admin_unlocked, 
            text="👑 Admin Dashboard", 
            font=("Roboto", 18, "bold"), 
            text_color="#00E676"
        )
        self.lbl_admin_title.pack(pady=(4, 1))

        self.lbl_reg_instruction = ctk.CTkLabel(
            self.frame_admin_unlocked, 
            text="Enroll new face or review records below.", 
            font=("Roboto", 11), 
            text_color="#B0BEC5"
        )
        self.lbl_reg_instruction.pack(pady=2)

        self.divider_reg = ctk.CTkFrame(self.frame_admin_unlocked, height=2, fg_color="gray")
        self.divider_reg.pack(fill="x", padx=10, pady=5)

        self.lbl_name_tag = ctk.CTkLabel(self.frame_admin_unlocked, text="Full Name:", font=("Roboto", 12, "bold"), anchor="w")
        self.lbl_name_tag.pack(fill="x", padx=20, pady=(2, 0))

        self.entry_name = ctk.CTkEntry(self.frame_admin_unlocked, placeholder_text="Enter Name (e.g. John Doe)", width=250)
        self.entry_name.pack(pady=(0, 4))

        self.lbl_id_tag = ctk.CTkLabel(self.frame_admin_unlocked, text="Unique ID (Auto-Generated):", font=("Roboto", 12, "bold"), anchor="w")
        self.lbl_id_tag.pack(fill="x", padx=20, pady=(2, 0))

        self.entry_id = ctk.CTkEntry(self.frame_admin_unlocked, placeholder_text="Unique ID", width=250)
        self.entry_id.pack(pady=(0, 6))

        self.btn_capture = ctk.CTkButton(
            self.frame_admin_unlocked, 
            text="📸 Save Face", 
            command=self.register_new_face, 
            fg_color="#388E3C",
            hover_color="#2E7D32",
            width=250,
            height=32,
            font=("Roboto", 13, "bold")
        )
        self.btn_capture.pack(pady=4)

        self.reg_status_label = ctk.CTkLabel(
            self.frame_admin_unlocked, 
            text="Ready to Enroll", 
            font=("Roboto", 12, "bold"), 
            text_color="gray"
        )
        self.reg_status_label.pack(pady=2)

        self.divider_admin2 = ctk.CTkFrame(self.frame_admin_unlocked, height=2, fg_color="gray")
        self.divider_admin2.pack(fill="x", padx=10, pady=5)

        # Protected View Attendance Records Button
        self.btn_open_csv = ctk.CTkButton(
            self.frame_admin_unlocked, 
            text="📋 View Attendance Records", 
            command=self.open_attendance_file, 
            fg_color="#1976D2",
            hover_color="#1565C0",
            width=250,
            height=32,
            font=("Roboto", 12, "bold")
        )
        self.btn_open_csv.pack(pady=4)

        # Lock & Return to Attendance
        self.btn_lock_admin = ctk.CTkButton(
            self.frame_admin_unlocked, 
            text="🔒 Lock & Back to Attendance", 
            command=self.lock_and_return_attendance, 
            fg_color="#455A64",
            hover_color="#37474F",
            width=250,
            height=30
        )
        self.btn_lock_admin.pack(pady=4)

        # Bottom Exit Button (Always accessible)
        self.btn_quit = ctk.CTkButton(
            self.control_frame, 
            text="Exit App", 
            command=self.close_app, 
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            width=220
        )
        self.btn_quit.pack(side="bottom", pady=10)

        # --- BACKEND STATE ---
        self.path = 'images'
        self.screenshot_path = 'screenshots'
        self.cache_file = CACHE_FILE
        self.knownEncodings = []
        self.classNames = []
        
        # Per-user liveness and cooldown tracking (Fixes multi-person spoofing flaw)
        self.user_blink_counter = {}
        self.user_liveness_verified = set()
        self.last_punch_time = {}

        # Rendering & performance optimization state
        self.frame_count = 0
        self.cached_face_data = []  # Stores (x1, y1, x2, y2, is_verified, disp_name)

        # Variables for Live Feedback Overlay
        self.feedback_text = ""      
        self.feedback_timer = 0      
        self.feedback_color = (0, 200, 0) 
        self.current_frame = None

        self.ensure_directory()
        self.load_existing_encodings()
        
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.update_camera()

    def ensure_directory(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)

    def parse_user_info(self, filename_base):
        """Clean helper to extract (Name, UID) handling spaces and hyphens."""
        if '-' in filename_base:
            name_raw, uid = filename_base.rsplit('-', 1)
            name = name_raw.replace('_', ' ').replace('-', ' ').strip()
            uid = uid.strip()
        else:
            name = filename_base.replace('_', ' ').strip()
            uid = "Unknown"
        return name, uid

    def get_next_unique_id(self):
        """Automatically find the next sequential unique ID based on registered users."""
        numeric_ids = []
        for class_name in self.classNames:
            _, uid = self.parse_user_info(class_name)
            digits = ''.join(filter(str.isdigit, uid))
            if digits:
                numeric_ids.append(int(digits))
        if numeric_ids:
            return max(numeric_ids) + 1
        return 101

    def auto_fill_next_id(self):
        """Pre-fill entry_id with next sequential ID."""
        next_id = self.get_next_unique_id()
        self.entry_id.delete(0, 'end')
        self.entry_id.insert(0, str(next_id))

    def on_tab_change(self):
        """Automatically lock admin panel when switching away to protect data."""
        current = self.tabview.get()
        if current == "📌 Attendance":
            self.lock_admin()

    def verify_admin_pin(self, event=None):
        """Verify the entered PIN and unlock the admin panel."""
        entered_pin = self.entry_pin.get().strip()
        if entered_pin == ADMIN_PIN:
            self.is_admin_authenticated = True
            self.lbl_pin_error.configure(text="")
            self.entry_pin.delete(0, 'end')
            self.frame_admin_locked.pack_forget()
            self.frame_admin_unlocked.pack(fill="both", expand=True, padx=5, pady=5)
            self.auto_fill_next_id()
            play_beep(1500, 150)
        else:
            self.lbl_pin_error.configure(text="⚠ Incorrect PIN! Access Denied")
            self.entry_pin.delete(0, 'end')
            play_beep(500, 300)

    def lock_admin(self):
        """Lock the admin panel and hide sensitive controls."""
        self.is_admin_authenticated = False
        self.frame_admin_unlocked.pack_forget()
        self.frame_admin_locked.pack(fill="both", expand=True, padx=5, pady=25)
        self.entry_pin.delete(0, 'end')
        self.lbl_pin_error.configure(text="")

    def lock_and_return_attendance(self):
        """Lock admin panel and switch back to attendance mode."""
        self.lock_admin()
        self.tabview.set("📌 Attendance")

    def load_existing_encodings(self):
        """Load face encodings using high-speed pickle cache for instantaneous startup."""
        self.status_label.configure(text="Loading DB...")
        self.update()

        cache_data = {}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
            except Exception:
                cache_data = {}

        updated = False
        if os.path.exists(self.path):
            images_list = os.listdir(self.path)
            current_files = set(images_list)
            
            # Prune deleted files from cache
            for cached_file in list(cache_data.keys()):
                if cached_file not in current_files:
                    del cache_data[cached_file]
                    updated = True

            for cl in images_list:
                file_path = os.path.join(self.path, cl)
                try:
                    mtime = os.path.getmtime(file_path)
                except OSError:
                    continue

                # Reuse cached encoding if file hasn't changed
                if cl in cache_data and cache_data[cl].get('mtime') == mtime:
                    encode = cache_data[cl].get('encoding')
                    if encode is not None:
                        self.knownEncodings.append(encode)
                        self.classNames.append(os.path.splitext(cl)[0])
                        continue

                # Compute encoding if new or modified
                curImg = cv2.imread(file_path)
                if curImg is not None:
                    img_rgb = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                    try:
                        encodes = face_recognition.face_encodings(img_rgb)
                        if len(encodes) > 0:
                            encode = encodes[0]
                            self.knownEncodings.append(encode)
                            self.classNames.append(os.path.splitext(cl)[0])
                            cache_data[cl] = {'mtime': mtime, 'encoding': encode}
                            updated = True
                    except Exception:
                        pass

        if updated:
            try:
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
            except Exception:
                pass

        self.status_label.configure(text="System Ready", text_color="cyan")
        self.lbl_user_count.configure(text=f"👥 Registered: {len(self.classNames)} Users")
        self.auto_fill_next_id()

    def register_new_face(self):
        if not self.is_admin_authenticated:
            messagebox.showerror("Access Denied", "Admin authorization required to enroll users!")
            return

        name = self.entry_name.get().strip()
        uid = self.entry_id.get().strip()

        if not name:
            self.reg_status_label.configure(text="⚠ Name is Required!", text_color="orange")
            return

        # If user left UID empty, auto-generate next sequential ID
        if not uid:
            uid = str(self.get_next_unique_id())

        if self.current_frame is None:
            self.reg_status_label.configure(text="⚠ Camera not ready!", text_color="red")
            return

        clean_name = name.replace(" ", "_")
        filename_base = f"{clean_name}-{uid}"
        file_path = f"{self.path}/{filename_base}.jpg"

        if os.path.exists(file_path):
            self.reg_status_label.configure(text="⚠ User Already Exists!", text_color="orange")
            return

        cv2.imwrite(file_path, self.current_frame)
        img_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        try:
            encodes = face_recognition.face_encodings(img_rgb)
            if len(encodes) == 0:
                raise IndexError("No face found")

            new_encode = encodes[0]
            self.knownEncodings.append(new_encode)
            self.classNames.append(filename_base)

            # Update cache file
            try:
                cache_data = {}
                if os.path.exists(self.cache_file):
                    with open(self.cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                cache_data[f"{filename_base}.jpg"] = {
                    'mtime': os.path.getmtime(file_path),
                    'encoding': new_encode
                }
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
            except Exception:
                pass

            self.reg_status_label.configure(text=f"✔ Saved: {name} ({uid})", text_color="#00E676")
            self.status_label.configure(text=f"✔ Enrolled: {name}", text_color="#00E676")
            self.lbl_user_count.configure(text=f"👥 Registered: {len(self.classNames)} Users")
            self.entry_name.delete(0, 'end')
            self.auto_fill_next_id()
            play_beep(2000, 200)
        except IndexError:
            if os.path.exists(file_path):
                os.remove(file_path)
            self.reg_status_label.configure(text="⚠ Face Not Clear", text_color="red")

    def process_attendance(self, filename_base, frame_to_save):
        name, uid = self.parse_user_info(filename_base)
        user_key = f"{name}_{uid}"

        # Cooldown check: ignore rapid repeated attempts within cooldown seconds
        now_time = time.time()
        last_punch = self.last_punch_time.get(user_key, 0)
        if now_time - last_punch < PUNCH_COOLDOWN_SECONDS:
            return

        filename = 'attendance.csv'
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        dString = now.strftime('%d-%m-%Y')

        try:
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write('Name,ID,Date,Entry_Time,Exit_Time\n')
            
            with open(filename, 'r') as f:
                lines = f.readlines()
        except PermissionError:
            self.status_label.configure(text="⚠ CLOSE EXCEL FILE!", text_color="red")
            return

        updated_lines = []
        found_entry_today = False
        action_taken = False
        status_msg = ""
        color = "white"
        sound_freq = 1000

        for line in lines:
            entry = line.strip().split(',')
            
            if len(entry) >= 3 and entry[0] == name and entry[1] == uid and entry[2] == dString:
                found_entry_today = True
                entry_time_str = entry[3]
                try:
                    entry_time_obj = datetime.strptime(entry_time_str, '%H:%M:%S')
                    time_diff = now - entry_time_obj.replace(year=now.year, month=now.month, day=now.day)
                    minutes_passed = time_diff.total_seconds() / 60
                except Exception:
                    minutes_passed = 0

                if minutes_passed >= MIN_MINUTES_BEFORE_EXIT:
                    has_exit = len(entry) >= 5 and entry[4].strip() != ""
                    if not has_exit:
                        new_line = f"{entry[0]},{entry[1]},{entry[2]},{entry[3]},{dtString}\n"
                        updated_lines.append(new_line)
                        action_taken = True
                        status_msg = f"Exit: {name} ({uid})"
                        color = "#FF5252"
                        self.feedback_color = (0, 0, 255)
                        sound_freq = 1000
                    else:
                        updated_lines.append(line)
                        self.status_label.configure(text=f"✔ Attendance Complete: {name}", text_color="cyan")
                        return
                else:
                    updated_lines.append(line)
                    self.status_label.configure(text=f"⚠ Just Entered: {name}", text_color="orange")
                    return 
            else:
                updated_lines.append(line)

        if not found_entry_today:
            new_line = f"{name},{uid},{dString},{dtString},\n"
            updated_lines.append(new_line)
            action_taken = True
            status_msg = f"Entry: {name} ({uid})"
            color = "#00E676"
            sound_freq = 1500
            self.feedback_color = (0, 200, 0) 

        if action_taken:
            try:
                with open(filename, 'w') as f:
                    f.writelines(updated_lines)
                
                self.last_punch_time[user_key] = now_time
                self.log_msg(f"{status_msg} ({dtString})")
                self.status_label.configure(text=status_msg, text_color=color)
                
                # --- LIVE FEEDBACK & SCREENSHOT PROOF ---
                self.feedback_text = f"NAME: {name} | ID: {uid} | TIME: {dtString}"
                self.feedback_timer = FEEDBACK_DURATION
                
                clean_name = name.replace(" ", "_")
                shot_name = f"{self.screenshot_path}/{clean_name}_{uid}_{dtString.replace(':','-')}.jpg"
                
                final_img = frame_to_save.copy()
                h, w, _ = final_img.shape
                cv2.rectangle(final_img, (0, h-60), (w, h), self.feedback_color, cv2.FILLED)
                cv2.putText(final_img, self.feedback_text, (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imwrite(shot_name, final_img)
                play_beep(sound_freq, 200)
            except PermissionError:
                self.status_label.configure(text="⚠ CLOSE EXCEL FILE!", text_color="red")

    def log_msg(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("0.0", msg + "\n")
        self.log_box.configure(state="disabled")

    def open_attendance_file(self):
        if not self.is_admin_authenticated:
            messagebox.showerror("Access Denied", "Admin authorization required to view records!")
            return

        filename = 'attendance.csv'
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write('Name,ID,Date,Entry_Time,Exit_Time\n')
        try:
            os.startfile(filename)
        except Exception as e:
            messagebox.showinfo("Attendance Log", f"Could not open file automatically: {e}")

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.frame_count += 1
            current_tab = self.tabview.get()

            # --- MODE 1: ADMIN PANEL TAB (Preview alignment only when authenticated) ---
            if current_tab == "🔒 Admin Panel" and self.is_admin_authenticated:
                if self.frame_count % FRAME_PROCESS_INTERVAL == 0:
                    imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                    facesCurFrame = face_recognition.face_locations(imgS)
                    new_cached_faces = []
                    for faceLoc in facesCurFrame:
                        y1, x2, y2, x1 = faceLoc
                        new_cached_faces.append((x1 * 4, y1 * 4, x2 * 4, y2 * 4, True, "Ready to Save"))
                    self.cached_face_data = new_cached_faces
                    if facesCurFrame:
                        self.reg_status_label.configure(text="✔ Face Detected - Click Save Face", text_color="#00E676")
                    else:
                        self.reg_status_label.configure(text="⚠ No Face Detected - Center Face", text_color="orange")

            # --- MODE 2: ATTENDANCE TAB (Privacy Mode + Liveness + Attendance) ---
            else:
                if self.frame_count % FRAME_PROCESS_INTERVAL == 0:
                    imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                    facesCurFrame = face_recognition.face_locations(imgS)
                    
                    if facesCurFrame:
                        face_landmarks_list = face_recognition.face_landmarks(imgS, face_locations=facesCurFrame)
                        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                        new_cached_faces = []

                        for i, (encodeFace, faceLoc) in enumerate(zip(encodesCurFrame, facesCurFrame)):
                            y1, x2, y2, x1 = faceLoc
                            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                            # Calculate EAR specifically for this individual face
                            face_landmarks = face_landmarks_list[i]
                            leftEye = face_landmarks['left_eye']
                            rightEye = face_landmarks['right_eye']
                            leftEAR = self.eye_aspect_ratio(leftEye)
                            rightEAR = self.eye_aspect_ratio(rightEye)
                            avgEAR = (leftEAR + rightEAR) / 2.0

                            matches = face_recognition.compare_faces(self.knownEncodings, encodeFace)
                            faceDis = face_recognition.face_distance(self.knownEncodings, encodeFace)

                            if len(faceDis) > 0 and matches:
                                matchIndex = np.argmin(faceDis)
                                if matches[matchIndex]:
                                    filename_base = self.classNames[matchIndex]
                                    name, uid = self.parse_user_info(filename_base)
                                    disp_name = f"{name.upper()} ({uid})"

                                    # Track blink per individual person (Anti-Spoofing fix)
                                    if avgEAR < EYE_ASPECT_RATIO_THRESHOLD:
                                        self.user_blink_counter[filename_base] = self.user_blink_counter.get(filename_base, 0) + 1
                                    else:
                                        if self.user_blink_counter.get(filename_base, 0) >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                                            self.user_liveness_verified.add(filename_base)
                                        self.user_blink_counter[filename_base] = 0

                                    # Verified Real Person
                                    if filename_base in self.user_liveness_verified:
                                        new_cached_faces.append((x1, y1, x2, y2, True, disp_name))
                                        self.process_attendance(filename_base, frame)
                                        self.user_liveness_verified.discard(filename_base)
                                    else:
                                        # Locked Privacy Mode: Red box, Name & ID hidden
                                        new_cached_faces.append((x1, y1, x2, y2, False, ""))
                                        self.status_label.configure(text=f"Waiting for Blink...", text_color="orange")
                                else:
                                    new_cached_faces.append((x1, y1, x2, y2, False, ""))
                            else:
                                new_cached_faces.append((x1, y1, x2, y2, False, ""))

                        self.cached_face_data = new_cached_faces
                    else:
                        self.cached_face_data = []
                        self.status_label.configure(text="Scanning...", text_color="yellow")

            # --- RENDER DETECTIONS ONTO FRAME ---
            for (x1, y1, x2, y2, is_verified, disp_name) in self.cached_face_data:
                if current_tab == "🔒 Admin Panel":
                    if self.is_admin_authenticated:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 230, 118), 2)
                        cv2.putText(frame, disp_name, (x1 + 6, y2 - 8), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
                else:
                    if is_verified:
                        # Verified: Green box + Name
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, disp_name, (x1 + 6, y2 - 8), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), 2)
                    else:
                        # Locked: Red box only, No text shown
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # --- RENDER FEEDBACK BANNER (IF ACTIVE) ---
            if self.feedback_timer > 0:
                h, w, _ = frame.shape
                cv2.rectangle(frame, (0, h-60), (w, h), self.feedback_color, cv2.FILLED)
                cv2.putText(frame, self.feedback_text, (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                self.feedback_timer -= 1

            # Convert OpenCV BGR to Tkinter Image
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img_pil = Image.fromarray(img)
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))
            self.cam_label.configure(image=ctk_img)
            self.cam_label.image = ctk_img

        self.after(10, self.update_camera)

    def close_app(self):
        """Safely release webcam and destroy window without hanging."""
        try:
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = FaceAttendanceApp()
    app.mainloop()

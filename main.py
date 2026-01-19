import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import winsound
from scipy.spatial import distance as dist

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- SETTINGS ---
MIN_MINUTES_BEFORE_EXIT = 1 
EYE_ASPECT_RATIO_THRESHOLD = 0.30 
EYE_ASPECT_RATIO_CONSEC_FRAMES = 2 

class FaceAttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Attendance System (With Unique ID)")
        self.geometry("1100x700") # Increased height for new input box

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT FRAME: Camera ---
        self.camera_frame = ctk.CTkFrame(self, corner_radius=10)
        self.camera_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.cam_label = ctk.CTkLabel(self.camera_frame, text="")
        self.cam_label.pack(expand=True, fill="both", padx=10, pady=10)

        # --- RIGHT FRAME: Controls ---
        self.control_frame = ctk.CTkFrame(self, width=350, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # Title
        self.lbl_title = ctk.CTkLabel(self.control_frame, text="Secure Attendance", font=("Roboto", 20, "bold"), text_color="#00E676")
        self.lbl_title.pack(pady=20)

        # Instructions
        self.lbl_instruction = ctk.CTkLabel(self.control_frame, text="ℹ Blink to Verify", font=("Roboto", 14), text_color="cyan")
        self.lbl_instruction.pack(pady=5)

        self.divider = ctk.CTkFrame(self.control_frame, height=2, fg_color="gray")
        self.divider.pack(fill="x", padx=20, pady=15)

        # --- REGISTRATION SECTION (UPDATED) ---
        self.lbl_register = ctk.CTkLabel(self.control_frame, text="Add New User", font=("Roboto", 16, "bold"))
        self.lbl_register.pack(pady=5)

        # Name Input
        self.entry_name = ctk.CTkEntry(self.control_frame, placeholder_text="Enter Name (e.g. Rahul)", width=250)
        self.entry_name.pack(pady=5)

        # ID Input (NEW)
        self.entry_id = ctk.CTkEntry(self.control_frame, placeholder_text="Enter Unique ID (e.g. 101)", width=250)
        self.entry_id.pack(pady=5)

        self.btn_capture = ctk.CTkButton(self.control_frame, text="📸 Save Face", command=self.register_new_face, fg_color="#388E3C")
        self.btn_capture.pack(pady=10)

        self.divider2 = ctk.CTkFrame(self.control_frame, height=2, fg_color="gray")
        self.divider2.pack(fill="x", padx=20, pady=15)

        # Logs
        self.status_label = ctk.CTkLabel(self.control_frame, text="Scanning...", font=("Roboto", 18), text_color="yellow")
        self.status_label.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.control_frame, width=280, height=180)
        self.log_box.pack(pady=5, padx=10)
        self.log_box.configure(state="disabled")

        self.btn_quit = ctk.CTkButton(self.control_frame, text="Exit App", command=self.close_app, fg_color="#D32F2F")
        self.btn_quit.pack(side="bottom", pady=20)

        # --- Backend ---
        self.path = 'images'
        self.knownEncodings = []
        self.classNames = []
        self.ensure_directory()
        self.load_existing_encodings()
        
        # --- Variables ---
        self.cap = cv2.VideoCapture(0)
        self.blink_counter = 0
        self.is_real_person = False
        
        self.current_frame = None
        self.update_camera()

    def ensure_directory(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def load_existing_encodings(self):
        self.status_label.configure(text="Loading DB...")
        self.update()
        if os.path.exists(self.path):
            images_list = os.listdir(self.path)
            for cl in images_list:
                curImg = cv2.imread(f'{self.path}/{cl}')
                if curImg is not None:
                    img_rgb = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                    try:
                        encode = face_recognition.face_encodings(img_rgb)[0]
                        self.knownEncodings.append(encode)
                        # Store the full filename base (e.g., "Rahul-101")
                        self.classNames.append(os.path.splitext(cl)[0])
                    except:
                        pass
        self.status_label.configure(text="System Ready", text_color="cyan")

    def register_new_face(self):
        name = self.entry_name.get()
        uid = self.entry_id.get() # Get ID

        if not name or not uid:
            self.status_label.configure(text="⚠ Name & ID Required!", text_color="orange")
            return
        if self.current_frame is None: return

        # Unique Filename: Name-ID.jpg
        filename_base = f"{name}-{uid}"
        file_path = f'{self.path}/{filename_base}.jpg'

        # Check if this exact Name-ID combination already exists
        if os.path.exists(file_path):
            self.status_label.configure(text="⚠ User Already Exists!", text_color="orange")
            return

        cv2.imwrite(file_path, self.current_frame)
        img_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        try:
            new_encode = face_recognition.face_encodings(img_rgb)[0]
            self.knownEncodings.append(new_encode)
            self.classNames.append(filename_base)
            
            self.status_label.configure(text=f"✔ Saved: {name} ({uid})", text_color="green")
            self.entry_name.delete(0, 'end')
            self.entry_id.delete(0, 'end')
            winsound.Beep(2000, 200)
        except IndexError:
            os.remove(file_path)
            self.status_label.configure(text="⚠ Face Not Clear", text_color="red")

    def process_attendance(self, filename_base):
        # Extract Name and ID from filename (e.g., "Rahul-101")
        try:
            name_parts = filename_base.split('-')
            name = name_parts[0]
            # Handle cases where ID might contain hyphens or strictly take the last part
            uid = name_parts[-1] if len(name_parts) > 1 else "Unknown"
        except ValueError:
            name = filename_base
            uid = "Unknown"

        filename = 'attendance.csv'
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        dString = now.strftime('%d-%m-%Y')

        try:
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    # Added ID to CSV Header
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
            
            # Match Logic: Must match Name, ID, and Date
            if len(entry) >= 3 and entry[0] == name and entry[1] == uid and entry[2] == dString:
                found_entry_today = True
                entry_time_str = entry[3]
                try:
                    entry_time_obj = datetime.strptime(entry_time_str, '%H:%M:%S')
                    time_diff = now - entry_time_obj.replace(year=now.year, month=now.month, day=now.day)
                    minutes_passed = time_diff.total_seconds() / 60
                except:
                    minutes_passed = 0

                if minutes_passed >= MIN_MINUTES_BEFORE_EXIT:
                    # Update Exit Time (Column 5)
                    new_line = f"{entry[0]},{entry[1]},{entry[2]},{entry[3]},{dtString}\n"
                    updated_lines.append(new_line)
                    # Check if exit time was already marked
                    if len(entry) < 5 or entry[4].strip() == "":
                        action_taken = True
                        status_msg = f"Exit: {name} ({uid})"
                        color = "#FF5252"
                else:
                    updated_lines.append(line)
                    self.status_label.configure(text=f"⚠ Just Entered: {name}", text_color="orange")
                    return 
            else:
                updated_lines.append(line)

        if not found_entry_today:
            # New Entry with ID
            new_line = f"{name},{uid},{dString},{dtString},\n"
            updated_lines.append(new_line)
            action_taken = True
            status_msg = f"Entry: {name} ({uid})"
            color = "#00E676"
            sound_freq = 1500

        if action_taken:
            try:
                with open(filename, 'w') as f:
                    f.writelines(updated_lines)
                self.log_msg(f"{status_msg} ({dtString})")
                self.status_label.configure(text=status_msg, text_color=color)
                winsound.Beep(sound_freq, 200)
                self.is_real_person = False 
                self.blink_counter = 0
            except PermissionError:
                 self.status_label.configure(text="⚠ CLOSE EXCEL FILE!", text_color="red")

    def log_msg(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("0.0", msg + "\n")
        self.log_box.configure(state="disabled")

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            face_landmarks_list = face_recognition.face_landmarks(imgS)
            liveness_status = "Waiting for Blink..."
            liveness_color = (0, 0, 255)

            for face_landmarks in face_landmarks_list:
                leftEye = face_landmarks['left_eye']
                rightEye = face_landmarks['right_eye']
                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)
                avgEAR = (leftEAR + rightEAR) / 2.0
                
                if avgEAR < EYE_ASPECT_RATIO_THRESHOLD:
                    self.blink_counter += 1
                else:
                    if self.blink_counter >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        self.is_real_person = True
                    self.blink_counter = 0 
            
            if self.is_real_person:
                liveness_status = "Verified!"
                liveness_color = (0, 255, 0)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            if not facesCurFrame:
                self.status_label.configure(text="Scanning...", text_color="yellow")
                self.is_real_person = False 

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                cv2.putText(frame, liveness_status, (x1, y1 - 35), cv2.FONT_HERSHEY_COMPLEX, 0.7, liveness_color, 2)

                matches = face_recognition.compare_faces(self.knownEncodings, encodeFace)
                faceDis = face_recognition.face_distance(self.knownEncodings, encodeFace)
                
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        # Here we get "Rahul-101"
                        filename_base = self.classNames[matchIndex]
                        
                        # Display only the Name part on screen
                        try:
                            disp_name = filename_base.split('-')[0].upper()
                        except:
                            disp_name = filename_base

                        box_color = (0, 255, 0) if self.is_real_person else (0, 0, 255)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                        cv2.putText(frame, disp_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        
                        if self.is_real_person:
                            self.process_attendance(filename_base)
                        else:
                            self.status_label.configure(text=f"Blink: {disp_name}", text_color="orange")
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img_pil = Image.fromarray(img)
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))
            self.cam_label.configure(image=ctk_img)
            self.cam_label.image = ctk_img

        self.after(10, self.update_camera)

    def close_app(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = FaceAttendanceApp()
    app.mainloop()
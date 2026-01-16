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
from scipy.spatial import distance as dist # Math ke liye (zaroori hai)

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- SETTINGS ---
MIN_MINUTES_BEFORE_EXIT = 1 
EYE_ASPECT_RATIO_THRESHOLD = 0.30 # Agar isse kam hua to aankh band hai
EYE_ASPECT_RATIO_CONSEC_FRAMES = 2 # Kitne frames tak aankh band honi chahiye

class FaceAttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anti-Spoofing Face Attendance (Stable Version)")
        self.geometry("1100x680")

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
        self.lbl_title = ctk.CTkLabel(self.control_frame, text="Secure Mode", font=("Roboto", 20, "bold"), text_color="#00E676")
        self.lbl_title.pack(pady=20)

        # Instructions
        self.lbl_instruction = ctk.CTkLabel(self.control_frame, text="ℹ Please Blink to Verify", font=("Roboto", 14), text_color="cyan")
        self.lbl_instruction.pack(pady=5)

        self.divider = ctk.CTkFrame(self.control_frame, height=2, fg_color="gray")
        self.divider.pack(fill="x", padx=20, pady=15)

        # Registration
        self.lbl_register = ctk.CTkLabel(self.control_frame, text="Add New User", font=("Roboto", 16, "bold"))
        self.lbl_register.pack(pady=5)
        self.entry_name = ctk.CTkEntry(self.control_frame, placeholder_text="Enter Name", width=250)
        self.entry_name.pack(pady=5)
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
        
        # --- Liveness Variables ---
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
                        self.classNames.append(os.path.splitext(cl)[0])
                    except:
                        pass
        self.status_label.configure(text="System Ready", text_color="cyan")

    def register_new_face(self):
        name = self.entry_name.get()
        if not name:
            self.status_label.configure(text="⚠ Name Required!", text_color="orange")
            return
        if self.current_frame is None: return

        file_path = f'{self.path}/{name}.jpg'
        if os.path.exists(file_path):
            self.status_label.configure(text="⚠ Already Exists!", text_color="orange")
            return

        cv2.imwrite(file_path, self.current_frame)
        img_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        try:
            new_encode = face_recognition.face_encodings(img_rgb)[0]
            self.knownEncodings.append(new_encode)
            self.classNames.append(name)
            self.status_label.configure(text=f"✔ Saved: {name}", text_color="green")
            self.entry_name.delete(0, 'end')
            winsound.Beep(2000, 200)
        except IndexError:
            os.remove(file_path)
            self.status_label.configure(text="⚠ Face Not Clear", text_color="red")

    def process_attendance(self, name):
        filename = 'attendance.csv'
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        dString = now.strftime('%d-%m-%Y')

        try:
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write('Name,Date,Entry_Time,Exit_Time\n')
            
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
            
            if len(entry) >= 2 and entry[0] == name and entry[1] == dString:
                found_entry_today = True
                entry_time_str = entry[2]
                try:
                    entry_time_obj = datetime.strptime(entry_time_str, '%H:%M:%S')
                    time_diff = now - entry_time_obj.replace(year=now.year, month=now.month, day=now.day)
                    minutes_passed = time_diff.total_seconds() / 60
                except:
                    minutes_passed = 0

                if minutes_passed >= MIN_MINUTES_BEFORE_EXIT:
                    new_line = f"{entry[0]},{entry[1]},{entry[2]},{dtString}\n"
                    updated_lines.append(new_line)
                    if len(entry) < 4 or entry[3] != dtString:
                        action_taken = True
                        status_msg = f"Exit Updated: {name}"
                        color = "#FF5252"
                else:
                    updated_lines.append(line)
                    self.status_label.configure(text=f"⚠ Just Entered: {name}", text_color="orange")
                    return 
            else:
                updated_lines.append(line)

        if not found_entry_today:
            new_line = f"{name},{dString},{dtString},\n"
            updated_lines.append(new_line)
            action_taken = True
            status_msg = f"Entry Marked: {name}"
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

    # --- EAR CALCULATION FUNCTION ---
    def eye_aspect_ratio(self, eye):
        # Vertical distance
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        # Horizontal distance
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB) # RGB for face_recognition
            
            # --- BLINK DETECTION LOGIC (Using face_recognition landmarks) ---
            face_landmarks_list = face_recognition.face_landmarks(imgS)
            
            liveness_status = "Waiting for Blink..."
            liveness_color = (0, 0, 255) # Red

            for face_landmarks in face_landmarks_list:
                leftEye = face_landmarks['left_eye']
                rightEye = face_landmarks['right_eye']
                
                # EAR Calculate karo
                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)
                
                # Average EAR
                avgEAR = (leftEAR + rightEAR) / 2.0
                
                # Agar EAR threshold se kam hai matlab aankh band hai
                if avgEAR < EYE_ASPECT_RATIO_THRESHOLD:
                    self.blink_counter += 1
                else:
                    # Agar blink counter sufficient hai to valid maano
                    if self.blink_counter >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        self.is_real_person = True
                    self.blink_counter = 0 # Reset agar aankh khuli hai
            
            if self.is_real_person:
                liveness_status = "Liveness Verified!"
                liveness_color = (0, 255, 0) # Green

            # --- FACE RECOGNITION START ---
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            if not facesCurFrame:
                self.status_label.configure(text="Scanning...", text_color="yellow")
                self.is_real_person = False # Reset if face lost

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                cv2.putText(frame, liveness_status, (x1, y1 - 35), cv2.FONT_HERSHEY_COMPLEX, 0.7, liveness_color, 2)

                matches = face_recognition.compare_faces(self.knownEncodings, encodeFace)
                faceDis = face_recognition.face_distance(self.knownEncodings, encodeFace)
                
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        name = self.classNames[matchIndex].upper()
                        
                        box_color = (0, 255, 0) if self.is_real_person else (0, 0, 255)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        
                        if self.is_real_person:
                            self.process_attendance(name)
                        else:
                            self.status_label.configure(text=f"Blink Eyes: {name}", text_color="orange")
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
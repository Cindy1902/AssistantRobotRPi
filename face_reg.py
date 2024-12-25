import cv2
import face_recognition
import numpy as np
import os
import pickle
from datetime import datetime
import time
import threading
from queue import Queue


class FaceTrainingSystem:
    def __init__(self):
        self.data_dir = "faceData"
        self.images_dir = os.path.join(self.data_dir, "images")
        self.encodings_file = os.path.join(self.data_dir, "encodings.pkl")

        os.makedirs(self.images_dir, exist_ok=True)

        self.known_face_encodings = []
        self.known_face_names = []
        self.load_encodings()

        self.cap = cv2.VideoCapture(0)

        self.frame_queue = Queue(maxsize=10)
        self.is_running = True
        self.current_mode = "recognition"

    def load_encodings(self):
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data["encodings"]
                self.known_face_names = data["names"]
                print(f"Loaded {len(self.known_face_names)} faces.")

    def save_encodings(self):
        with open(self.encodings_file, "wb") as f:
            pickle.dump({
                "encodings": self.known_face_encodings,
                "names": self.known_face_names
            }, f)

    def capture_frame_thread(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.01)

    def train_new_face(self):
        print("Begin new face training process...")
        name = input("Enter the name of the person: ")

        person_dir = os.path.join(self.images_dir, name)
        os.makedirs(person_dir, exist_ok=True)

        angles = ["Front View", "Left Side",
                  "Right Side", "Looking Up", "Looking Down"]
        images = []

        for i, angle in enumerate(angles):
            input(f"Preparing to capture {angle}. Press Enter when ready...")
            captured = False

            while not captured:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue

                face_locations = face_recognition.face_locations(frame)

                if len(face_locations) == 1:
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(frame, (left, top),
                                      (right, bottom), (0, 255, 0), 2)

                    cv2.imshow("Training", frame)
                    if cv2.waitKey() == ord("c"):
                        img_path = os.path.join(person_dir, f"{i+1}.jpg")
                        cv2.imwrite(img_path, frame)
                        images.append(frame)
                        print(f"Captured {angle}")
                        break
                    elif cv2.waitKey(1) == ord("q"):
                        return False

        new_encodings = []
        for img in images:
            face_encodings = face_recognition.face_encodings(img)
            if face_encodings:
                new_encodings.append(face_encodings[0])

        if new_encodings:
            self.known_face_encodings.extend(new_encodings)
            self.known_face_names.extend([name] * len(new_encodings))
            self.save_encodings()
            print(f"Successfully added {len(new_encodings)} images of {name}")
            return True

        print("Could not add new face. Please try again.")
        return False

    def recognize_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )

        face_names = []
        unknown_faces = []

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            if self.known_face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=0.6)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                else:
                    name = "Unknown"
                    unknown_faces.append(top*4, right*4, bottom*4, left*4)
            else:
                name = "Unknown"
                unknown_faces.append((top*4, right*4, bottom*4, left*4))

            face_names.append(name)

            cv2.rectangle(frame, (left*4, top*4),
                          (right*4, bottom*4), (0, 255, 0), 2)
            cv2.rectangle(frame, (left*4, bottom*4 - 35),
                          (right*4, bottom*4), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left*4 + 6, bottom*4 - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        return frame, unknown_faces

    def run(self):
        capture_thread = threading.Thread(target=self.capture_frame_thread)
        capture_thread.daemon = True
        capture_thread.start()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                continue

            if self.current_mode == "recognition":
                frame, unknown_faces = self.recognize_faces(frame)

                if unknown_faces:
                    cv2.imshow("Face Recognition", frame)
                    if cv2.waitKey(1) == ord("t"):
                        self.current_mode = "training"
                        cv2.destroyAllWindows()
                        self.train_new_face()
                        self.current_mode = "recognition"
                else:
                    cv2.imshow("Face Recognition", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        return False

            time.sleep(0.01)

        self.is_running = False
        capture_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    system = FaceTrainingSystem()
    system.run()

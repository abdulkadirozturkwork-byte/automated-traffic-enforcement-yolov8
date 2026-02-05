import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import os
import time
import pandas as pd
from datetime import datetime
import io 

# ==========================================
#        PROFESSIONAL CLASS STRUCTURE
# ==========================================

class ParkingViolationSystem:
    def __init__(self, model_path, evidence_folder="evidence"):
        """
        Constructor function that initializes system settings and loads the model.
        """
        self.model_path = model_path
        self.evidence_folder = evidence_folder
        self.excel_name = "Parking_Violation_Report.xlsx"
        
        # Default Settings
        self.tolerance = 5.0
        self.violation_threshold = 15
        self.min_box_height = 50
        
        # Create Folder
        os.makedirs(self.evidence_folder, exist_ok=True)
        
        # Memory (Session State Control)
        if 'violation_log' not in st.session_state:
            st.session_state.violation_log = []
        if 'penalized_ids' not in st.session_state:
            st.session_state.penalized_ids = set()
            
        # Load Model
        try:
            self.model = YOLO(self.model_path)
            # Get Class Names
            self.names = self.model.names
            self.road_ids = [k for k, v in self.names.items() if 'road' in v.lower() or 'yol' in v.lower()]
            self.vehicle_ids = [k for k, v in self.names.items() if 'car' in v.lower() or 'vehicle' in v.lower() or 'truck' in v.lower() or 'bus' in v.lower()]
            if not self.vehicle_ids: self.vehicle_ids = [0, 1, 2, 3] # Fallback
            
            st.sidebar.success("System Initialized: Model Loaded ✅")
        except Exception as e:
            st.error(f"Model could not be loaded: {e}")
            st.stop()

        # Trackers
        self.violation_tracker = {}

    def clear_system(self):
        """Resets memory and the report."""
        st.session_state.violation_log = []
        st.session_state.penalized_ids = set()
        st.rerun()

    def process_video(self, video_path, conf_curr, min_h_curr, stop_btn):
        """
        Main function processing video frames one by one.
        """
        cap = cv2.VideoCapture(video_path)
        stframe = st.empty()
        placeholder_evidence = st.sidebar.empty()

        while cap.isOpened():
            if stop_btn: break
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.resize(frame, (1280, 720))

            # --- TRACKING ALGORITHM ---
            try:
                results = self.model.track(frame, conf=conf_curr, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
            except:
                continue

            # 1. Draw Roads and Define Area
            road_polygons = []
            if results.masks is not None:
                for i, c in enumerate(results.boxes.cls):
                    if int(c) in self.road_ids:
                        pts = results.masks.xy[i].astype(np.int32)
                        road_polygons.append(pts)
                        cv2.polylines(frame, [pts], isClosed=True, color=(255, 0, 255), thickness=2)
                        overlay = frame.copy()
                        cv2.fillPoly(overlay, [pts], (255, 0, 255))
                        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

            # 2. Analyze Vehicles
            if results.boxes is not None and results.boxes.id is not None:
                boxes = results.boxes.xyxy.cpu().numpy().astype(int)
                ids = results.boxes.id.cpu().numpy().astype(int)
                clss = results.boxes.cls.cpu().numpy().astype(int)

                for box, track_id, cls_id in zip(boxes, ids, clss):
                    if cls_id in self.vehicle_ids:
                        self._check_vehicle(frame, box, track_id, cls_id, min_h_curr, road_polygons, placeholder_evidence)

            # Display on Screen
            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

        cap.release()

    def _check_vehicle(self, frame, box, track_id, cls_id, min_h, road_polygons, placeholder):
        """
        Internal function checking if a single vehicle is violating rules.
        """
        x1, y1, x2, y2 = box
        
        # Size Filter
        if (y2 - y1) < min_h: return

        center_x, center_y = int((x1+x2)/2), int(y2)
        vehicle_type = self.names[cls_id] # Vehicle Type (Car, Truck etc.)

        # Already Penalized?
        if track_id in st.session_state.penalized_ids:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"{vehicle_type} {track_id}: PENALIZED", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            return

        # Is on Road?
        on_road = False
        for poly in road_polygons:
            if cv2.pointPolygonTest(poly, (center_x, center_y), True) >= self.tolerance:
                on_road = True
                break
        
        # Counter Logic
        if track_id not in self.violation_tracker: self.violation_tracker[track_id] = 0

        if on_road:
            self.violation_tracker[track_id] = 0
            color = (0, 255, 0)
            label = f"{vehicle_type} {track_id}: Clean"
        else:
            self.violation_tracker[track_id] += 1
            
            # Violation Moment
            if self.violation_tracker[track_id] > self.violation_threshold:
                color = (255, 0, 0)
                label = f"{vehicle_type} {track_id}: VIOLATION!"
                
                # Save to Memory and Disk
                self._log_violation(frame, box, track_id, vehicle_type, placeholder)
            else:
                color = (0, 255, 255)
                remaining = self.violation_threshold - self.violation_tracker[track_id]
                label = f"{vehicle_type} {track_id}: Analyzing ({remaining})"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def _log_violation(self, frame, box, track_id, v_type, placeholder):
        """Captures evidence photo and saves it."""
        st.session_state.penalized_ids.add(track_id)
        x1, y1, x2, y2 = box
        
        crop = frame[max(0,y1):min(720,y2), max(0,x1):min(1280,x2)]
        if crop.size > 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img_name = f"{v_type}_{track_id}.jpg"
            full_path = f"{self.evidence_folder}/{img_name}"
            
            cv2.imwrite(full_path, crop)
            placeholder.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), caption=f"{v_type} {track_id} Violation")
            
            # Add to Log
            st.session_state.violation_log.append({
                "Vehicle ID": track_id,
                "Vehicle Type": v_type,
                "Timestamp": now,
                "Status": "ILLEGAL PARKING",
                "Evidence": img_name
            })
            st.toast(f"{v_type} {track_id} reported!", icon="🚨")

    def generate_report(self):
        """Generates Excel report and offers download button."""
        if not st.session_state.violation_log:
            st.warning("No violations recorded yet.")
            return

        df = pd.DataFrame(st.session_state.violation_log)
        
        # Column Ordering
        cols = ["Vehicle ID", "Vehicle Type", "Timestamp", "Status", "Evidence"]
        if all(c in df.columns for c in cols): df = df[cols]

        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Violations', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Violations']
                
                worksheet.set_column('A:B', 15)
                worksheet.set_column('C:C', 20)
                worksheet.set_column('E:E', 40)
                
                st.info("Embedding images into Excel...")
                
                for idx, row in df.iterrows():
                    img_path = os.path.abspath(os.path.join(self.evidence_folder, row['Evidence']))
                    if os.path.exists(img_path):
                        worksheet.set_row(idx+1, 100)
                        worksheet.insert_image(idx+1, 4, img_path, {'x_scale': 1.5, 'y_scale': 1.5, 'object_position': 1})

            buffer.seek(0)
            st.success(f"✅ Total {len(df)} violations reported.")
            st.download_button("📥 Download Report with Images", data=buffer, file_name=self.excel_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"Excel Error: {e}")

# ==========================================
#            APPLICATION UI (MAIN)
# ==========================================

st.set_page_config(page_title="Parking Violation System", layout="wide")
st.title("🚔 Autonomous Parking Violation Detection System (OOP Mode)")

# 1. Initialize Class (Create Instance)
system = ParkingViolationSystem(model_path='best.pt')

# 2. Sidebar Settings
st.sidebar.header("🔧 Control Panel")
conf_val = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)
min_h_val = st.sidebar.slider("Min Height Filter", 10, 200, 50, 10)

if st.sidebar.button("🧹 Reset System"):
    system.clear_system()

# 3. File Upload and Process
uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov'])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    tfile.close()
    
    stop_button = st.sidebar.button("Stop System and Get Report 🛑")
    
    # Call function inside the class
    system.process_video(tfile.name, conf_val, min_h_val, stop_button)
    
    # File cleanup
    time.sleep(0.1)
    try: os.unlink(tfile.name)
    except: pass
    
    # Show report
    system.generate_report()
# AI-Powered Dynamic Traffic Violation Detection System 🚗📹

## 📌 Project Overview
This project is an **automated traffic enforcement system** developed using **Python** and **YOLOv8**. Unlike static cameras, this system is designed to work on **moving vehicles** (e.g., patrol cars).

It analyzes real-time video feeds to identify vehicles traveling outside designated lanes. To ensure accuracy and eliminate false positives caused by camera vibrations or momentary tracking errors, the system implements a **Time-Based Verification Logic**.

## 🚀 Key Features

### 1. Dynamic Environment Analysis
* Capable of processing footage from a moving source.
* Simultaneous detection of **Road Lines** and **Vehicles**.
* Real-time analysis of vehicle position relative to the road boundaries.

### 2. False Positive Elimination (The "15-Frame" Rule) ⏱️
* **Problem:** Video vibrations or momentary object occlusion can cause flickering detections, leading to incorrect penalties.
* **Solution:** The system waits for a violation to persist for **15 consecutive frames** before confirming it.
* **Result:** Drastically reduces error rates and ensures only genuine violations are recorded.

### 3. Automated Evidence & Reporting 📊
* **Snapshot Capture:** Once a violation is confirmed, the system automatically crops and saves the vehicle's image.
* **Excel Integration:** Using `Pandas`, the system logs:
    * Unique Vehicle IDs
    * Violation Timestamp/Frame
    * Link to the saved evidence image.
* **User Control:** The "Download" command compiles all processed data into a structured Excel file for easy review.

## 🛠️ Tech Stack
* **Core:** Python 3.x
* **AI Model:** YOLOv8 (Ultralytics)
* **Computer Vision:** OpenCV (cv2)
* **Data Handling:** Pandas, NumPy

## 🏭 Potential Industrial Use Cases
While designed for traffic, this logic is directly applicable to **Industrial Engineering** contexts:
* **AGV Path Tracking:** Detecting if autonomous robots deviate from their magnetic/visual paths.
* **Safety Zone Monitoring:** Identifying unauthorized personnel or forklifts entering restricted dangerous zones for more than X seconds.
* **Quality Control:** Detecting defects on a conveyor belt that persist across multiple frames.

---
*Developed by [Adın Soyadın] - Industrial Engineering Student*

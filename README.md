# AI-Powered Dynamic Traffic Violation Detection System 🚗📹

## 🎥 Project Demo (Watch in Action)
[![Watch the video](https://img.youtube.com/vi/umTGWc5StwI)](https://www.youtube.com/watch?v=umTGWc5StwI)

> *Click the image above to watch the full demonstration on YouTube.*
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

  ## 🎥 System Demo
Check out the video above to see the system in action!
* **Real-time Tracking:** The system successfully identifies vehicles and filters false positives using the 15-frame rule.
* **Automated Logic:** Watch how the bounding boxes turn **RED** when a violation is confirmed.
* **Excel Export:** The end of the video demonstrates the auto-generated report with embedded evidence images.

* ## ⚖️ Data Source & Privacy Disclaimer
* **Source:** The video footage used in this demonstration is sourced from public domain content available on YouTube (Original Video Link: [Buraya YouTube Linkini Koy]).
* **Privacy Note:** No personal data (license plates) was stored, processed for identification, or used for commercial purposes. This project is strictly for **educational and research purposes**.
* **Compliance:** In a real-world deployment (e.g., Ford Otosan production line), a **real-time blurring algorithm** would be integrated to comply with KVKK/GDPR regulations.


## ⚠️ Current Limitations & Future Improvements
This project is currently a **Proof of Concept (PoC)** prototype.
* **Dataset Constraint:** The YOLOv8 model was trained on a limited dataset for demonstration purposes.
* **Performance:** Detection accuracy may vary in low-light conditions or with high-speed camera vibrations.
* **Next Steps:** To achieve industrial-level accuracy (99%+), the dataset will be expanded to 2,000+ labeled images, and the model will be retrained for better generalization.
---
*Developed by Abdulkadir Öztürk - Industrial Engineering Student*

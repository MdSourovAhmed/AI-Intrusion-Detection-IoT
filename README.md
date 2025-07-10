# 🛡️ AI-Based Intrusion Detection System for IoT Network

An AI-driven real-time intrusion detection system using **Raspberry Pi**, **ESP8266**, **MQTT**, **TON_IoT Dataset**, and **machine learning**, enhanced with **Node-RED**, **Prometheus**, and **Grafana** for visualization and alerts.

---

## 📸 Screenshots

> *(Add your own screenshots here)*
---

## 🚀 Project Overview

This system monitors IoT sensor data and network traffic on a Raspberry Pi, detects malicious behavior using a machine learning model trained on the TON_IoT dataset, and alerts users via **email** and **Grafana** dashboards in real-time.

---

## 🧹 System Architecture

```
ESP8266 + Sensors --> MQTT Broker (Mosquitto) --> Raspberry Pi (AI Detection)
         |                                 |
         --> Node-RED --> Prometheus <--> Grafana (Alerts)
```

---

## 🔧 Technologies Used

- **ESP8266** with Motion, Temperature, and Humidity sensors
- **Raspberry Pi** (Server + Sniffer + AI detection)
- **MQTT (Mosquitto)** for sensor communication
- **Node-RED** for message routing
- **Prometheus + Grafana** for real-time alerting
- **Scapy / Tcpdump / Tshark** for packet capture
- **Python (Scikit-learn, Pandas, Joblib)** for model training
- **TON_IoT Dataset** for supervised training

---

## 🧠 AI Model Details

- Dataset: Cleaned and merged `TON_IoT` + live captured MQTT packet data
- Selected Features:
  ```
  ['proto', 'src_pkts', 'dst_port', 'dst_pkts', 
   'src_port', 'packet_frequency', 'dst_bytes', 'src_bytes']
  ```
- Model: `RandomForestClassifier`
- Accuracy: `~100%` on test data
- Tools: Google Colab, matplotlib, seaborn

---

## 📦 Project Structure

```
🔹 ESP8266/
│   └── sensor_publisher.ino            # Code for ESP8266 sensors
🔹 pi-server/
│   ├── mqtt_sniffer.py                 # Captures packets from MQTT
│   ├── intrusion_detector.py           # Uses trained model to detect intrusion
│   ├── alert_emailer.py                # Sends email on detection
│   └── intrusion_log.csv               # CSV log of detections
🔹 model/
│   ├── ai_ids_model.pkl                # Trained model file
│   ├── scaler.pkl                      # Scaler used during training
│   └── training_notebook.ipynb         # Google Colab training notebook
🔹 dashboard/
│   ├── node_red_flow.json              # Node-RED flow
│   └── grafana_dashboard.json          # Prebuilt Grafana JSON
🔹 data/
│   ├── cleaned_ton_iot.csv             # Cleaned TON_IoT data
│   └── merged_dataset.csv              # Final dataset used to train
🔹 images/
│   ├── architecture.png                # System architecture diagram
│   └── grafana-alerts.png              # Grafana panel screenshot
🔹 README.md
🔹 requirements.txt
```

---

## ⚙️ How to Run

### 📍 On Raspberry Pi:

1. Install required packages:
   ```bash
   pip install scapy joblib pandas numpy prometheus_client
   ```
2. Start Prometheus metrics server + detection:
   ```bash
   python intrusion_detector.py
   ```

### 📍 On ESP8266:

- Upload `sensor_publisher.ino` using Arduino IDE
- Configure your Wi-Fi and MQTT broker address

### 📍 Node-RED + Grafana:

- Import provided Node-RED flow
- Set up Prometheus + Grafana dashboards using the JSON files

---

## 🔥 Simulating Attacks

To simulate attacks for testing:

- Use `hping3`, `nping`, or MQTT fuzzers from a Kali Linux VM
- Example:
  ```bash
  hping3 -S -p 1883 --flood <raspberry_pi_ip>
  ```

---

## 📈 Model Training Notebook

Model training was done in Google Colab using:

- TON_IoT network dataset
- Feature selection, encoding, and scaling
- Random Forest Classifier
- Evaluation using Confusion Matrix & ROC Curve

See: [`training_notebook.ipynb`](model/training_notebook.ipynb)

---

## 📬 Alerts and Logging

- 📧 Email notification upon attack detection
- 📊 Grafana alert triggered via Prometheus metric (`intrusion_alert`)
- 🗒️ CSV log: `intrusion_log.csv`

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License © 2025 Md. Sourov Ahmed

---

## 🤛 Author

**Md. Sourov Ahmed**Department of ICT, [Your University Name]Contact: [mdsourovahmedsamin@gmail.com](mailto:mdsourovahmedsamin@gmail.com)GitHub: [MdSourovAhmed](https://github.com/MdSourovAhmed)

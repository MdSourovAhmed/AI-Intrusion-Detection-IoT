
# 🛡️ AI-Based Real-Time Intrusion Detection System on Raspberry Pi

This project integrates **real-time IoT sensor data** with an **AI-based intrusion detection system (IDS)** running on a **Raspberry Pi**. It uses **MQTT**, **Node-RED**, **Prometheus**, and **Grafana** to monitor and detect cyberattacks such as DDoS and packet injection.

---

## ⚙️ Features

- Collect sensor data using ESP8266 over MQTT  
- Analyze network traffic on Raspberry Pi using Scapy  
- Detect DDoS and packet injection attacks via AI (Random Forest model)  
- Visualize live metrics in Grafana  
- Trigger alert emails and Grafana notifications  
- Support for `iptables` flood protection and Cloudflared tunnel  

---

## 📐 System Architecture

<table>
  <tr>
    <th>System Architecture</th>
    <th>Data Collection System Flowchart</th>
  </tr>
  <tr>
    <td><img src="screenshots/system_architecture.png" width="400"/></td>
    <td><img src="screenshots/Data_Collection_System_Flowchart.png" width="400"/></td>
  </tr>
</table>


```text
[ESP8266 Sensors] → MQTT → Mosquitto Broker (Raspberry Pi)
                                  ↓
                      [Node-RED] → Prometheus Exporter → Grafana Dashboard
                                  ↓
                   Live Packet Sniffer (Scapy) → AI Intrusion Detector → Alert (Email + Grafana)
```

---

## 🧪 Sensor Setup: DHT11 + PIR + ESP8266

<img src="screenshots/ESP8266_SetUp.png" alt="System Architecture" width="500" height="300"/>

---


### 📍 On ESP8266:

- Upload `sensor_publisher.ino` using Arduino IDE
- Configure your Wi-Fi and MQTT broker address
  
---


## 📦 Installation

### 🔧 Raspberry Pi Setup

```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-pip mosquitto mosquitto-clients
pip3 install scapy pandas joblib prometheus_client
```

---

## 🧰 Node-RED Setup

### Install Node-RED

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
sudo systemctl enable nodered.service
```

### Configure MQTT Node

- Access Node-RED at: `http://<RPI_IP>:1880`
- Install `node-red-contrib-mqtt-broker`
- Drag MQTT input node, parse the JSON, and connect it to Prometheus

#### Example Flow (Import This):

```json
[
  {
    "id": "mqtt_sensor",
    "type": "mqtt in",
    "z": "flow_id",
    "name": "",
    "topic": "sensor/data",
    "qos": "2",
    "datatype": "json",
    "broker": "mqtt_broker_id",
    "x": 100,
    "y": 100,
    "wires": [["function_to_metric"]]
  },
  {
    "id": "function_to_metric",
    "type": "function",
    "z": "flow_id",
    "name": "Format as metric",
    "func": "msg.payload = {
  temperature: msg.payload.temp,
  motion: msg.payload.motion
};
return msg;",
    "outputs": 1,
    "noerr": 0,
    "x": 300,
    "y": 100,
    "wires": [["prometheus_node"]]
  },
  {
    "id": "prometheus_node",
    "type": "prometheus-exporter",
    "z": "flow_id",
    "name": "Prometheus Metrics",
    "x": 500,
    "y": 100,
    "wires": []
  }
]
```

---

## 📊 Prometheus Setup

### Install

```bash
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-armv7.tar.gz
tar xvf prometheus-*.tar.gz
cd prometheus-*/
./prometheus --config.file=prometheus.yml
```

### `prometheus.yml` Configuration

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'node-red-sensors'
    static_configs:
      - targets: ['localhost:1880']

  - job_name: 'ai_intrusion_detector'
    static_configs:
      - targets: ['localhost:8000']
```

> Save as `prometheus.yml` and restart Prometheus.

---

## 📈 Grafana Setup

```bash
sudo apt install grafana
sudo systemctl enable --now grafana-server
```

- Access Grafana: `http://<RPI_IP>:3000`
- Add **Prometheus** as a data source
- Import dashboard JSON from: `dashboards/grafana_dashboard.json`

---

## 🌐 Cloudflared Tunnel (Optional)

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm
chmod +x cloudflared-linux-arm
sudo mv cloudflared-linux-arm /usr/local/bin/cloudflared
cloudflared tunnel login
cloudflared tunnel create ids-tunnel
```

---

## 🧠 AI Model: Intrusion Detection

### Selected Features

```text
['proto', 'src_pkts', 'dst_port', 'dst_pkts', 'src_port', 'packet_frequency', 'dst_bytes', 'src_bytes']
```

### Model Training

- Dataset: TON_IoT + live `tcpdump` merged
- Model: Random Forest  
- Accuracy: ~99.9%  
- Exported files: `ai_ids_model.pkl`, `scaler.pkl`

---

## 🔍 Live Detection + Email Alert

```bash
python3 scripts/intrusion_detection.py
```

- Captures packets using Scapy  
- Uses `ai_ids_model.pkl` for real-time prediction  
- On attack detection:
  - Sends email via `smtplib`
  - Logs entry to CSV
  - Exposes Prometheus metric (`intrusion_alert`)

---

## 🧪 Attack Simulation (Kali Linux)

### Simulate DDoS (TCP SYN Flood)

```bash
hping3 -S <RPI_IP> -p 1883 --flood
```

### MQTT Injection

```bash
mosquitto_pub -t sensor/data -m '{"temp":999,"motion":5}'
```

---

## 🧱 iptables Protection

```bash
sudo iptables -A INPUT -p tcp --syn -m limit --limit 15/second --limit-burst 20 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
```

---
## 🖼️ Sensor Data & Raspbarry Pi Health Visualization

| Grafana Dashboard |
|-------------------|
| ![](screenshots/grafana_view.png) |

---

## 🖼️ Attack, Logs & Alert Visualization

| Normal & Attack Situations |
|-------------------|
| ![](screenshots/Attack_view.png) |

---

## 📂 Folder Structure

```text
.
├── README.md
├── scripts/
│   ├── intrusion_detection.py
│   └── mqtt_simulator.py
├── models/
│   ├── ai_ids_model.pkl
│   └── scaler.pkl
├── dashboards/
│   └── grafana_dashboard.json
├── dataset/
│   └── cleaned_ton_iot.csv
├── screenshots/
│   ├── system_architecture.png
│   └── grafana_view.png
|   └── ---------
|   └── ---------
```

---

## ✅ TODO / Future Enhancements

- Integrate with **fail2ban** for IP banning  
- Explore deep learning models (LSTM, CNN)  
- Enable secure public dashboard hosting via tunneling  

---

## 🙋 Author

**Md. Sourov Ahmed**  
Department of ICT, [Mawlana Bhashani Science and Technology University]  
- GitHub: [@MdSourovAhmed](https://github.com/MdSourovAhmed)  
- LinkedIn: [LinkedIn Profile](https://www.linkedin.com/in/md-sourov-ahmed-661388334)

---

## 📄 License

MIT License — Free to use with attribution.

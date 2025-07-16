#!/usr/bin/env python3

from scapy.all import sniff, IP, TCP
import pandas as pd
import numpy as np
import time
import joblib
import paho.mqtt.client as mqtt
import warnings
import smtplib
from email.mime.text import MIMEText
import json

warnings.filterwarnings("ignore")  # Suppress sklearn warnings

# === EMAIL CONFIG ===
EMAIL_SENDER = "sender@gmail.com"
EMAIL_PASSWORD = "email app password"
EMAIL_RECEIVER = "receiver@email.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
ALERT_COOLDOWN = 60  # seconds between emails
last_alert_time = 0

# === MQTT CONFIG ===
MQTT_BROKER = "localhost"  # or Raspberry Pi IP
MQTT_PORT = 1883
MQTT_TOPIC = "ids/alert"

mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"[!] MQTT connection failed: {e}")

# === CONFIGURATION ===
MODEL_PATH = 'binary_ids_model.joblib' # use relative path
SCALER_PATH = 'binary_scaler.joblib' # use relative path
INTERFACE = 'wlan0'  # Change to your network interface (e.g., 'eth0', 'wlan0')
CONFIDENCE_THRESHOLD = 0.78

# === GLOBAL STATE ===
packet_window = []
window_start = time.time()


# === EMAIL ALERT ===
def send_email_alert(packet, confidence):
    global last_alert_time

    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN:
        return  # Skip sending if within cooldown

    subject = "🚨 Network Intrusion Detected"
    body = f"""
An intrusion was detected with high confidence.

Time: {time.strftime("%Y-%m-%d %H:%M:%S")}
Confidence: {confidence:.2%}
Source: {packet['src_ip']}:{packet['src_port']}
Destination: {packet['dst_ip']}:{packet['dst_port']}
Protocol: {packet['protocol']}
TCP Flags: {packet['flags']} ({decode_tcp_flags(packet['flags'])})
Length: {packet['length']} bytes
Packet Rate: {packet['packet_rate']:.1f}/s
Burst Score: {packet['burst_score']:.3f}
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("[+] Email alert sent.")
        last_alert_time = now
    except Exception as e:
        print(f"[!] Failed to send email: {e}")


# === FEATURE EXTRACTION ===
def extract_packet_features(pkt):
    return {
        'flags': int(pkt[TCP].flags) if TCP in pkt else 0,
        'packet_rate': 0,
        'burst_score': 0,
        'src_port': pkt[TCP].sport if TCP in pkt else 0,
        'dst_port': pkt[TCP].dport if TCP in pkt else 0,
        'protocol': pkt[IP].proto if IP in pkt else 0,
        'length': len(pkt),
        'timestamp': time.time(),
        'src_ip': pkt[IP].src if IP in pkt else "0.0.0.0",
        'dst_ip': pkt[IP].dst if IP in pkt else "0.0.0.0",
    }

# === TIME-BASED FEATURE CALCULATION ===
def update_time_features():
    global packet_window
    if len(packet_window) < 2:
        return

    timestamps = [p['timestamp'] for p in packet_window]
    deltas = np.diff(timestamps)
    duration = time.time() - window_start
    packet_rate = len(packet_window) / duration if duration > 0 else 0
    burst_score = np.sum(deltas < 0.001) / len(deltas)

    for p in packet_window:
        p['packet_rate'] = packet_rate
        p['burst_score'] = burst_score

# === TCP FLAG DECODER ===
def decode_tcp_flags(flag_int):
    flags_map = {
        0x01: 'FIN',
        0x02: 'SYN',
        0x04: 'RST',
        0x08: 'PSH',
        0x10: 'ACK',
        0x20: 'URG',
        0x40: 'ECE',
        0x80: 'CWR',
    }
    decoded = [name for bit, name in flags_map.items() if flag_int & bit]
    return ', '.join(decoded) if decoded else 'NONE'

# === ML INFERENCE ===
def predict_attack(packet_features):
    try:
        model_dict = joblib.load(MODEL_PATH)
        scaler_dict = joblib.load(SCALER_PATH)

        model = model_dict['model']
        feature_cols = model_dict['features']
        scaler = scaler_dict['scaler']

        features_df = pd.DataFrame(
            [[packet_features[col] for col in feature_cols]],
            columns=feature_cols
        )

        scaled = scaler.transform(features_df)
        pred = model.predict(scaled)[0]
        prob = model.predict_proba(scaled)[0][1]

        return int(pred), float(prob)

    except Exception as e:
        print(f"[!] Prediction error: {e}")
        return 0, 0.0

# === ALERT LOGGING ===
def print_alert(packet, confidence):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"""
🚨 INTRUSION DETECTED ({timestamp}) 🚨
    Confidence: {confidence:.2%}
    Source: {packet['src_ip']}:{packet['src_port']}
    Destination: {packet['dst_ip']}:{packet['dst_port']}
    Protocol: {packet['protocol']}
    TCP Flags: {packet['flags']} ({decode_tcp_flags(packet['flags'])})
    Length: {packet['length']} bytes
    Packet Rate: {packet['packet_rate']:.1f}/s
    Burst Score: {packet['burst_score']:.3f}
"""
    print(msg)
    with open("/var/log/ids_alerts.log", "a") as f:
        f.write(msg + "\n")
    send_email_alert(packet, confidence)

# === PACKET HANDLER ===
def process_packet(pkt):
    global packet_window, window_start

    if IP not in pkt:
        return

    feat = extract_packet_features(pkt)
    packet_window.append(feat)

    if time.time() - window_start >= 1.0:
        update_time_features()

        for pf in packet_window:
            is_attack, prob = predict_attack(pf)

            pf["attack"] = bool(is_attack == 1 and prob >= CONFIDENCE_THRESHOLD)
            pf["confidence"] = float(prob)

            if pf["attack"]:
                print_alert(pf, prob)
            else:
                print("Normal Traffic...")

            mqtt_payload = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "confidence": pf["confidence"],
                "attack": pf["attack"],
                "src_ip": pf["src_ip"],
                "dst_ip": pf["dst_ip"],
                "flags": int(pf["flags"]),
                "protocol": int(pf["protocol"]),
                "length": int(pf["length"]),
            }

            try:
                mqtt_client.publish(MQTT_TOPIC, json.dumps(mqtt_payload))
            except Exception as e:
                print(f"[!] MQTT publish failed: {e}")

        packet_window = []
        window_start = time.time()

# === MAIN ===
if __name__ == "__main__":
    print(f"[+] Starting Real-Time IDS on {INTERFACE}")
    print(f"[+] Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print("[+] Press Ctrl+C to stop\n")

    try:
        sniff(iface=INTERFACE, filter="port 1883", prn=process_packet, store=0)
    except KeyboardInterrupt:
        print("\n[+] IDS stopped.")
    except PermissionError:
        print("[!] Must run as root (use sudo)")

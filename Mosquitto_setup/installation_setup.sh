sudo apt install -y mosquitto mosquitto-clients;
mosquitto -v;
sudo systemctl enable mosquitto.service;
sudo systemctl start mosquitto.service;
sudo systemctl status mosquitto.service;
# To create a new user and follow up the process
sudo mosquitto_passwd -c /etc/mosquitto/passwd your_username;
# For additional users:
sudo mosquitto_passwd /etc/mosquitto/passwd another_username;
# To see all users:
sudo cat /etc/mosquitto/passwd;
# Type the following command and add appropriate contents;
# The contents are given in a separate mosquitto.conf file
cat /etc/mosquitto/mosquitto.conf;
sudo systemctl restart mosquitto.service;
# Publish contents as follows: 
# Terminal 1 (subscribe to a topic):
mosquitto_sub -h localhost -t "test" -u "your_username" -P "your_password";

# Terminal 2 (publish a message):
mosquitto_pub -h localhost -t "test" -m "Hello MQTT" -u "your_username" -P "your_password";


# Debugging:
echo "log_dest file /var/log/mosquitto/mosquitto.log" | sudo tee -a /etc/mosquitto/mosquitto.conf;
echo "log_type all" | sudo tee -a /etc/mosquitto/mosquitto.conf;
sudo systemctl restart mosquitto;

#Advanced debugging:
journalctl -u mosquitto -f;  # Live logs

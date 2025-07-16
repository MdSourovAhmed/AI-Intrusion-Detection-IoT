sudo systemctl enable grafana-server;
sudo systemctl enable mosquitto.service;
sudo systemctl enable nodered.service;
sudo systemctl enable prometheus;

sudo systemctl start grafana-server;
sudo systemctl start mosquitto.service;
node-red-start;
sudo systemctl start prometheus;

# 1. Add Grafana's GPG key (correct as you have it)
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# 2. Add the Grafana repository (correct as you have it)
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# 3. Update your package lists
sudo apt update

# 4. Install Grafana
sudo apt install grafana

# 5. Start and enable the service (systemd systems)
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# 6. Verify installation (check version)
grafana-server -v

# 7. Check service status
sudo systemctl status grafana-server

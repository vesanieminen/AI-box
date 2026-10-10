# LAN access to vLLM

vLLM uses host networking and listens on `0.0.0.0:8000`. The current LAN address
is `192.168.0.181/24`; the OpenAI API base URL is
`http://192.168.0.181:8000/v1`. Model discovery is `/v1/models`.

Omarchy's existing UFW firewall remains enabled. Add only this application
profile and local-subnet rule; do not replace the existing firewall rules:

```bash
sudo install -Dm644 system/firewall/etc/ufw/applications.d/local-vllm /etc/ufw/applications.d/local-vllm
sudo ufw allow from 192.168.0.0/24 to any app 'Local vLLM' comment 'vLLM API from LAN'
sudo ufw status verbose
```

UFW persists the rule across boot. On another network, replace the source subnet
with that LAN's CIDR. The rule covers TCP port 8000 and does not open unrelated
ports. IPv6 access is not added by this IPv4-subnet rule.

From another device on the LAN:

```bash
curl http://192.168.0.181:8000/v1/models
```

The current API retains the SSD's configuration without an API key. Full remote
reachability requires checking from another device; a host-local request to its
LAN address alone does not exercise the incoming firewall path.

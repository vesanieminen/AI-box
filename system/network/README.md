# Persistent network wake

The SSD stored wake settings in NetworkManager connection profiles, not a
separate ethtool boot service: Ethernet `wake-on-lan=64` and Wi-Fi
`wake-on-wlan=8`, both magic-packet wake. The profiles contain credentials and
are not copied into Git. This file reproduces those values as global defaults,
loaded at NetworkManager startup and used when profiles select `default`.

```bash
sudo install -Dm644 system/network/etc/NetworkManager/conf.d/90-wake-on-network.conf /etc/NetworkManager/conf.d/90-wake-on-network.conf
sudo nmcli general reload conf
# For existing profiles, explicitly preserve the same wake behavior:
sudo nmcli connection modify "UniFi" wifi.wake-on-wlan magic
sudo nmcli connection modify "Wired connection 1" ethernet.wake-on-lan magic
sudo nmcli connection modify "Wired connection 2" ethernet.wake-on-lan magic
# Apply Wi-Fi wake immediately without disconnecting ongoing transfers:
sudo iw phy phy0 wowlan enable magic-packet
```

On another machine, use its profile and radio names. NetworkManager reload and
profile edits do not require restarting the network or disconnecting downloads.
The settings persist across boot and connection activation; NetworkManager also
uses wake triggers when preparing Wi-Fi for suspend. `ethtool` is retained for
Ethernet diagnosis/configuration, while Wi-Fi wake is handled by NetworkManager
and `iw`.

```bash
nmcli -g 802-11-wireless.wake-on-wlan connection show "UniFi"
iw phy phy0 wowlan show
ethtool enp5s0 | sed -n '/Wake-on/p'
ethtool enp6s0 | sed -n '/Wake-on/p'
```

The current Wi-Fi adapter advertises magic-packet wake support. A remote wake
from actual suspend needs a separate end-to-end test; the box was not suspended
while downloads and model setup were running.

References: [NetworkManager wake flags](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html),
[connection defaults](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/NetworkManager.conf.html).

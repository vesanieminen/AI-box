# Additional NVMe storage

The additional Samsung SSD 970 EVO Plus 2TB (serial `S4J4NX0RA13684E`)
has one Btrfs partition labeled `data`, UUID
`efc1934f-e063-455a-97ce-298270e8867f`. The OS is on the other SSD,
serial `S4J4NX0R861213X`. Device numbering may change; use UUIDs or serials.
Formatting and the single-partition layout were verified on 2026-10-25.

The retained fstab fragment configures `/mnt/data` at boot. `nofail` allows
boot to continue if the drive is absent; device discovery waits at most ten
seconds. Default Btrfs options are used, without explicitly enabling compression.
The mounted filesystem root should be owned by the desktop user (currently
UID/GID 1000:1000), mode 0755. This is a separate, unencrypted filesystem.
Existing model paths and AI services are unchanged.

## Apply or restore

Run from the repository root after checking `lsblk -o NAME,SERIAL,FSTYPE,LABEL,UUID,MOUNTPOINTS`.
On a reformatted or replacement drive, update the fragment with its new UUID.
Do not format again during restoration. If mounted elsewhere, unmount it first.
Review any existing entry for this UUID or `/mnt/data` before replacing it.

```bash
sudo cp -a /etc/fstab "/etc/fstab.backup.$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p /mnt/data
# Only append if neither this UUID nor mount point is already configured:
if ! grep -Eq '^[[:space:]]*[^#].*(efc1934f-e063-455a-97ce-298270e8867f|/mnt/data)' /etc/fstab; then
  cat system/storage/fstab.data | sudo tee -a /etc/fstab >/dev/null
fi
sudo findmnt --verify
sudo systemctl daemon-reload
sudo systemctl start mnt-data.mount
# Verify the mounted UUID before setting ownership:
findmnt --mountpoint /mnt/data
if [ "$(findmnt -n -o UUID --mountpoint /mnt/data)" = efc1934f-e063-455a-97ce-298270e8867f ]; then
  sudo chown "$(id -u):$(id -g)" /mnt/data
  sudo chmod 0755 /mnt/data
fi
```

Verify user write access with `touch /mnt/data/.write-test && rm /mnt/data/.write-test`.
`systemctl cat mnt-data.mount` should show the generated unit referencing the
UUID and mount options. A reboot is the final check of boot-time mounting.

Installation is pending administrator authentication: the fstab fragment has
not been applied. Mounting, user write access, generated-unit validation and
fresh-boot verification remain outstanding.

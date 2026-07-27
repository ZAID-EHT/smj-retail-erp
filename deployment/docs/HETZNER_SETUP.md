# Hetzner Setup (external — requires Hetzner credentials)

1. **Provision** a Hetzner Cloud server (CX22+ / CPX21+ recommended for ERPNext),
   Ubuntu LTS. **External: Hetzner account + API/console credentials.**
2. **Harden**: create a non-root sudo user, SSH keys only, disable password login.
3. **Install** Docker Engine + compose plugin.
4. **Firewall** (Hetzner Cloud Firewall + host ufw):
   - allow 22 (SSH, from trusted IPs), 80, 443
   - **deny** 3306, 6379, 8000, 8080, 9000 and all worker/internal ports
5. **Registry**: `docker login` to your private registry (external credentials).
6. **Deploy**: clone this app (or copy `deployment/`), set `.env`, run
   `scripts/preflight.sh` then `scripts/deploy.sh`.
7. **Storage Box / snapshots**: attach a Hetzner Storage Box for offsite backups and
   enable server snapshots (external).

Everything above needs Hetzner/registry credentials and is therefore external to this
repository.

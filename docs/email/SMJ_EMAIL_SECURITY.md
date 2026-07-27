# SMJ Email Security

- **Manager-only.** Every email-admin endpoint re-checks System Manager server-side.
- **No credential exposure.** The overview never returns a password, SMTP host,
  username, API key or token — asserted by `test_email_admin`
  (`test_overview_never_returns_a_credential`).
- **No credential logging.** Nothing in this module logs credentials.
- **Queue privacy.** Email Queue is summarised as counts by status only — no
  recipient addresses, no message bodies.
- **Password reset / welcome.** Where email cannot send, the system directs
  administrators to set a temporary password (see access model), rather than silently
  failing to deliver a reset link.

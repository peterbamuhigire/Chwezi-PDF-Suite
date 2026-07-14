# Secure Deployment

## Supported initial profile

The initial supported profile is a single-user local installation. The future web adapter must bind `127.0.0.1` by default. The current `web_interface.py` is a development prototype and must not be exposed to a LAN or the internet.

## Local controls

- install into an isolated environment or signed desktop bundle;
- keep application, parser and system-tool updates current;
- use a private temporary directory with restrictive permissions;
- configure storage and job retention; clear failed-job data when no longer required;
- supply remote-provider keys through environment/keyring references;
- disable remote AI unless the user has reviewed the data sent;
- process suspicious documents in an OS/container sandbox where available.

## Server mode status

Server mode is not production-ready. Before that label is used, implement authentication, authorisation, CSRF/cookie controls, TLS guidance, per-user isolation, quotas, upload/rate limits, worker isolation, audit logs, malware hooks and scheduled cleanup. A deployment review must test those controls; documentation alone is not acceptance evidence.

## Diagnostics

Diagnostic bundles exclude documents, extracted text, credentials and raw private paths. Include version, OS/Python, capability versions, configuration locations, storage availability and sanitised recent errors.


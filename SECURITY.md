# Security policy

## Credential handling

This repository must never contain API keys, access tokens, passwords, cookies, or exported n8n credentials.

- Store OpenRouter and Meta secrets in n8n credentials.
- Keep local secret files outside the repository with owner-only permissions.
- Rotate a secret immediately if it appears in an exported workflow, screenshot, terminal log, issue, commit, or shared document.
- Treat Git history as public even after deleting a secret from the latest revision.

## Reporting

If you find a credential or security issue, contact the repository owner privately. Do not open a public issue containing the secret.

## Current release-stage status

The workflow export contains no embedded token. The live n8n workflow uses an encrypted Meta Query Auth credential for the AZAR Page; the portable export deliberately omits that credential.

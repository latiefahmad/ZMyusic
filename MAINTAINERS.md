# Maintainers

This document lists the maintainers responsible for ZMyusic.

| Maintainer | GitHub | Responsibilities |
|---|---|---|
| latiefahmad | [@latiefahmad](https://github.com/latiefahmad) | Project maintainer, core architecture, release management, and PR reviews |

## Responsibilities

Maintainers oversee project direction, repository maintenance, review and merging of contributions, and release management.

## Release signing

The Android builds are signed by CI. `Android Release APK` reads four repository secrets — `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS` and `KEY_PASSWORD` — and skips the signed job while any of them is missing. The keystore itself is deliberately not in this repository, and GitHub never shows a secret back: losing the file means installed copies can never be updated in place again, only replaced with a new install.

Desktop builds are unsigned unless `MACOS_CERTIFICATE`, `MACOS_CERTIFICATE_PASSWORD` and `MACOS_SIGNING_IDENTITY` are set. The iOS IPA is never signed at build time: AltStore, SideStore or an Ad Hoc profile signs it with the installer's own certificate.

## Contributors

This list is automatically generated from GitHub repository contributor data.

<!-- BEGIN CONTRIBUTORS -->
- [@latiefahmad](https://github.com/latiefahmad)
<!-- END CONTRIBUTORS -->

# Security Policy

## Supported Versions

The following versions of MISP CLI are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of MISP CLI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **GitHub Security Advisories** (Preferred): Use the [GitHub Security Advisory](https://github.com/StevePearson-github/misp-cli/security/advisories/new) feature to privately report a vulnerability.

2. **Email**: Send a detailed report to the maintainers. You can find contact information in the commit history or repository settings.

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What kind of vulnerability is it? (e.g., credential exposure, injection, etc.)
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Proof of Concept**: If available, provide a minimal example
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have ideas for how to fix the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 5 business days
- **Updates**: We will keep you informed of progress

### What to Expect

1. We will acknowledge receipt of your report
2. We will investigate and confirm the vulnerability
3. We will work on a fix and coordinate disclosure with you
4. We will release a patch and publish a security advisory
5. We will credit you in the advisory (unless you prefer to remain anonymous)

### Disclosure Policy

- Please give us reasonable time to investigate and fix the issue before public disclosure
- We follow [Coordinated Vulnerability Disclosure (CVD)](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure)
- We will publish a GitHub Security Advisory once a fix is available

## Security Considerations

### API Key Handling

MISP CLI handles sensitive credentials (API keys). Please be aware of the following:

- **Configuration Files**: API keys are stored in configuration files (`.misp-cli.conf`). Ensure these files have appropriate permissions (`chmod 600`).
- **Environment Variables**: API keys can be provided via environment variables. Be cautious about logging and shell history.
- **Logging**: MISP CLI does not log API keys, but be careful when sharing debug output.

### Best Practices

1. **Never commit configuration files** containing real API keys to version control
2. **Use environment variables** or secure secret management in CI/CD environments
3. **Rotate API keys** periodically and after any suspected compromise
4. **Use the principle of least privilege** when creating MISP API keys
5. **Verify SSL certificates** in production environments (the default)

### Reporting Security Issues in Dependencies

If you discover a security vulnerability in one of our dependencies:

1. Check if the vulnerability has been reported to the dependency maintainers
2. Report it to us so we can assess the impact and update dependencies
3. We will work to update vulnerable dependencies promptly

## Security Updates

Security updates will be announced via:

- GitHub Security Advisories
- GitHub Releases
- The release notes will include CVE identifiers where applicable

## Comments on this Policy

If you have suggestions on how this policy could be improved, please open an issue or submit a pull request.

---

Thank you for helping keep MISP CLI and its users safe! 🔐

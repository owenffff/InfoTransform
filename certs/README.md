# Corporate CA Certificates

This directory is for storing corporate CA certificates when running InfoTransform in Docker within a corporate network.

## Usage

If your organization uses a corporate proxy or internal CA:

1. Place your corporate CA certificate in this directory
2. Name it `corporate-ca.crt`
3. The Dockerfile will automatically trust this certificate

## Certificate Format

- The certificate must be in PEM format (`.crt` or `.pem`)
- If you have a DER format certificate, convert it first:
  ```bash
  openssl x509 -inform der -in certificate.der -out corporate-ca.crt
  ```

## Example

```
certs/
  ├── README.md
  └── corporate-ca.crt  # Your corporate CA certificate
```

## Note

If you don't have a corporate CA certificate, the Docker build will skip this step gracefully. This is optional for most users.

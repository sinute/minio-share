---
name: minio-share
description: Upload files to MinIO object storage and generate shareable links. Use when users ask to send files, share files, upload files, or get a download link for files. Requires MINIO_API_URL, MINIO_CONSOLE_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_BUCKET environment variables.
---

# MinIO Share

Upload files to MinIO and generate shareable links for users.

## Requirements

Ensure these environment variables are set:
- `MINIO_API_URL` - MinIO S3 API endpoint (e.g., `https://minio-api.example.com`)
- `MINIO_CONSOLE_URL` - MinIO Web Console URL (e.g., `https://minio.example.com`)
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET` - Default bucket name for uploads

## Installation

Install the minio Python package if not already available:
```bash
pip install minio
```

## Usage

### Basic Upload

Upload a file and get a shareable link:
```bash
python3 scripts/minio_upload.py /path/to/file.txt
```

### Custom Object Name

Specify a custom name for the uploaded object:
```bash
python3 scripts/minio_upload.py /path/to/file.txt --name custom-name.pdf
```

### Adjust Link Expiry

Change the presigned URL expiry time (default: 7 days):
```bash
python3 scripts/minio_upload.py /path/to/file.txt --expiry 30
```

### JSON Output

Get structured output with both presigned URL and console URL:
```bash
python3 scripts/minio_upload.py /path/to/file.txt --json
```

## Workflow

When a user asks to send/share/upload a file:

1. **Check environment variables** - Verify MINIO_* variables are set
2. **Upload the file** using `scripts/minio_upload.py`
3. **Provide links to user**:
   - **Presigned URL** - Direct download link (expires in N days)
4. **Inform user of expiry** - Let them know when the link will expire
5. **Human-readable format** - Use appropriate Markdown tags to display links

## Example Response

```
文件已上传到 MinIO！

📥 下载链接（7天后过期）：
[file.txt](https://minio-api.example.com/bucket/file.txt?AWSAccessKeyId=...)

```

## Error Handling

Common issues:
- Missing environment variables - Check all MINIO_* vars are set
- Bucket doesn't exist - Ensure MINIO_BUCKET exists or create it first
- File not found - Verify the file path is correct
- Connection error - Check MINIO_API_URL is accessible

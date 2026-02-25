#!/usr/bin/env python3
"""
MinIO 文件上传脚本
从环境变量读取配置，上传文件到 MinIO 并生成分享链接
"""

import os
import sys
import argparse
from datetime import timedelta
from urllib.parse import urljoin

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:
    print("Error: minio Python package not installed.", file=sys.stderr)
    print("Install with: pip install minio", file=sys.stderr)
    sys.exit(1)


def get_env_config():
    """从环境变量读取 MinIO 配置"""
    config = {
        'api_url': os.getenv('MINIO_API_URL'),
        'console_url': os.getenv('MINIO_CONSOLE_URL'),
        'access_key': os.getenv('MINIO_ACCESS_KEY'),
        'secret_key': os.getenv('MINIO_SECRET_KEY'),
        'bucket': os.getenv('MINIO_BUCKET'),
    }
    
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    
    return config


def parse_endpoint(api_url):
    """解析 API URL 获取 endpoint 和 secure 标志"""
    api_url = api_url.rstrip('/')
    if api_url.startswith('https://'):
        secure = True
        endpoint = api_url.replace('https://', '', 1)
    elif api_url.startswith('http://'):
        secure = False
        endpoint = api_url.replace('http://', '', 1)
    else:
        # 默认 https
        secure = True
        endpoint = api_url
    
    return endpoint, secure


def upload_file(client, bucket, file_path, object_name=None, expiry_days=7):
    """上传文件到 MinIO"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not object_name:
        object_name = os.path.basename(file_path)
    
    # 确保 bucket 存在
    if not client.bucket_exists(bucket):
        print(f"Error: Bucket '{bucket}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # 上传文件
    try:
        client.fput_object(bucket, object_name, file_path)
        print(f"Uploaded: {file_path} -> {bucket}/{object_name}", file=sys.stderr)
    except S3Error as e:
        print(f"Error uploading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return object_name


def generate_presigned_url(client, bucket, object_name, expiry_days=7):
    """生成预签名 URL"""
    try:
        url = client.presigned_get_object(
            bucket, 
            object_name,
            expires=timedelta(days=expiry_days)
        )
        return url
    except S3Error as e:
        print(f"Error generating URL: {e}", file=sys.stderr)
        sys.exit(1)


def generate_console_url(console_url, bucket, object_name):
    """生成 Console 预览 URL"""
    # MinIO Console 的 object 预览路径
    return f"{console_url.rstrip('/')}/browser/{bucket}/{object_name}"


def main():
    parser = argparse.ArgumentParser(description='Upload file to MinIO and generate shareable link')
    parser.add_argument('file_path', help='Path to the file to upload')
    parser.add_argument('--name', '-n', help='Object name in MinIO (default: filename)')
    parser.add_argument('--expiry', '-e', type=int, default=7, help='Link expiry in days (default: 7)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # 读取配置
    config = get_env_config()
    endpoint, secure = parse_endpoint(config['api_url'])
    
    # 创建 MinIO 客户端
    client = Minio(
        endpoint,
        access_key=config['access_key'],
        secret_key=config['secret_key'],
        secure=secure
    )
    
    # 上传文件
    object_name = upload_file(
        client, 
        config['bucket'], 
        args.file_path, 
        args.name,
        args.expiry
    )
    
    # 生成链接
    presigned_url = generate_presigned_url(client, config['bucket'], object_name, args.expiry)
    console_url = generate_console_url(config['console_url'], config['bucket'], object_name)
    
    # 输出结果
    if args.json:
        import json
        result = {
            'success': True,
            'object_name': object_name,
            'bucket': config['bucket'],
            'presigned_url': presigned_url,
            'console_url': console_url,
            'expiry_days': args.expiry
        }
        print(json.dumps(result, indent=2))
    else:
        print(presigned_url)


if __name__ == '__main__':
    main()

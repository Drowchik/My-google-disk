import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException


class S3Service:
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str, endpoint_url: str):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            endpoint_url=endpoint_url,
            verify=False
        )
        self.bucket_name = bucket_name

    def get_user_folder(self, user_id: int) -> str:
        return f"users/{user_id}"

    def create_user_folder(self, user_id: int):
        folder_name = self.get_user_folder(user_id)
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=(folder_name + "/"))
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create folder: {e}")

    def upload_file(self, user_id: int, file_name: str, file_data: bytes):
        folder_name = self.get_user_folder(user_id)
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"{folder_name}/{file_name}",
                Body=file_data
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {e}")

    def list_files(self, user_id: int):
        folder_name = self.get_user_folder(user_id)
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=f"{folder_name}/"
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to list files: {e}")

    def delete_file(self, user_id: int, file_name: str):
        folder_name = self.get_user_folder(user_id)
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=f"{folder_name}/{file_name}"
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete file: {e}")

    def rename_file(self, user_id: int, old_file_name: str, new_file_name: str):
        folder_name = self.get_user_folder(user_id)
        old_key = f"{folder_name}/{old_file_name}"
        new_key = f"{folder_name}/{new_file_name}"
        try:
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource={"Bucket": self.bucket_name, "Key": old_key},
                Key=new_key,
            )
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=old_key)
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to rename file: {e}")

    def download_file(self, user_id: int, file_name: str) -> bytes:
        try:
            folder_name = self.get_user_folder(user_id)
            key = f"{folder_name}/{file_name}"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Ошибка при скачивании файла: {str(e)}")

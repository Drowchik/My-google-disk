import React from "react";
import { Upload, message } from "antd";
import { InboxOutlined } from "@ant-design/icons";

const FileUploader = ({ onUploadSuccess, currentPath }) => {
    const customUpload = async ({ file, onSuccess, onError }) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("folder_path", currentPath); // Используем переданный путь

        try {
            const response = await fetch("http://localhost:8000/mydisk/files/upload", {
                method: "POST",
                credentials: "include",
                body: formData,
            });

            if (response.ok) {
                message.success(`${file.name} успешно загружен!`);
                onSuccess(response, file); // Уведомляем Ant Design о завершении загрузки

                if (onUploadSuccess) {
                    onUploadSuccess(); // Вызываем callback для обновления списка файлов
                }
            } else {
                message.error(`${file.name} ошибка загрузки: ${response.statusText}`);
                onError(new Error(`Ошибка загрузки: ${response.statusText}`));
            }
        } catch (error) {
            message.error(`${file.name} ошибка загрузки.`);
            onError(error);
        }
    };

    return (
        <Upload.Dragger customRequest={customUpload} multiple={true}>
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <p className="ant-upload-text">Перетащите файл сюда или нажмите для выбора</p>
            <p className="ant-upload-hint">Вы можете загрузить файлы в директорию: {currentPath || "/"}</p>
        </Upload.Dragger>
    );
};

export default FileUploader;

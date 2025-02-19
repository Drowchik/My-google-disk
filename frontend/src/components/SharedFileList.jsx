import React from "react";
import { List, Button, message } from "antd";
import { FileOutlined, FolderOutlined } from "@ant-design/icons";

const SharedFileList = ({ files }) => {
    // Функция для извлечения имени файла или папки
    const extractFileName = (fullPath) => {
        const sanitizedPath = fullPath.endsWith("/") ? fullPath.slice(0, -1) : fullPath;
        return sanitizedPath.split("/").pop();
    };

    // Проверка: это файл или папка?
    const isFolder = (path) => path.endsWith("/");

    // Логика скачивания файла
    const handleDownload = (filePath) => {
        fetch(`http://localhost:8000/mydisk/files/download?path=${encodeURIComponent(filePath)}`, {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.blob())
            .then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = extractFileName(filePath);
                document.body.appendChild(link);
                link.click();
                link.remove();
            })
            .catch((error) => {
                console.error("Ошибка при скачивании файла:", error);
                message.error("Не удалось скачать файл.");
            });
    };

    return (
        <List
            bordered
            dataSource={files}
            renderItem={(filePath) => (
                <List.Item
                    actions={
                        isFolder(filePath)
                            ? null // Для папок действия не нужны
                            : [
                                <Button
                                    type="text"
                                    icon={<FileOutlined />}
                                    onClick={() => handleDownload(filePath)}
                                >
                                    Скачать
                                </Button>,
                            ]
                    }
                >
                    {isFolder(filePath) ? (
                        <FolderOutlined style={{ marginRight: "8px" }} />
                    ) : (
                        <FileOutlined style={{ marginRight: "8px" }} />
                    )}
                    {extractFileName(filePath)}
                </List.Item>
            )}
        />
    );
};

export default SharedFileList;

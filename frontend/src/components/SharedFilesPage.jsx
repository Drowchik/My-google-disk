import React, { useState, useEffect } from "react";
import { Breadcrumb, List, Button, message } from "antd";

const SharedFilesPage = () => {
    const [currentPath, setCurrentPath] = useState("/"); // Полный путь
    const [sharedFiles, setSharedFiles] = useState([]);
    const [isRoot, setIsRoot] = useState(true);

    useEffect(() => {
        if (isRoot) {
            fetchSharedFolders();
        } else {
            fetchFolderContents(currentPath);
        }
    }, [currentPath, isRoot]);

    const fetchSharedFolders = () => {
        fetch("http://localhost:8000/mydisk/folders/shared", {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => setSharedFiles(data))
            .catch((error) =>
                message.error("Ошибка при получении расшаренных папок: " + error)
            );
    };

    const fetchFolderContents = (path) => {
        fetch(`http://localhost:8000/mydisk/files/shared?path=${encodeURIComponent(path)}`, {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => setSharedFiles(data))
            .catch((error) =>
                message.error("Ошибка при получении содержимого папки: " + error)
            );
    };

    const extractFileName = (fullPath) => {
        const sanitizedPath = fullPath.endsWith("/") ? fullPath.slice(0, -1) : fullPath;
        return sanitizedPath.split("/").pop();
    };

    const handleFolderClick = (folderName) => {
        setCurrentPath((prevPath) => `${prevPath}${folderName}/`);
        setIsRoot(false);
    };

    const handleDownload = (filePath, fileName) => {
        fetch(
            `http://localhost:8000/mydisk/files/download?path=${encodeURIComponent(filePath)}&file_name=${encodeURIComponent(fileName)}`,
            {
                method: "GET",
                credentials: "include",
            }
        )
            .then((response) => response.blob())
            .then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = fileName;
                document.body.appendChild(link);
                link.click();
                link.remove();
            })
            .catch((error) => {
                console.error("Ошибка при скачивании файла:", error);
                message.error("Не удалось скачать файл.");
            });
    };

    const handleGoBack = () => {
        if (isRoot) {
            return;
        }

        setCurrentPath((prevPath) => {
            const parts = prevPath.split("/").filter(Boolean);
            parts.pop();
            const newPath = parts.length > 0 ? `/${parts.join("/")}/` : "/";

            if (newPath === "/") {
                setIsRoot(true);
                fetchSharedFolders();
            }

            return newPath;
        });
    };

    return (
        <div style={{ padding: "20px" }}>
            <h1>Расшаренные файлы</h1>
            <Breadcrumb style={{ marginBottom: "20px" }}>
                <Breadcrumb.Item
                    onClick={() => {
                        setCurrentPath("/");
                        setIsRoot(true);
                    }}
                    style={{ cursor: "pointer" }}
                >
                    Главная
                </Breadcrumb.Item>
                {!isRoot &&
                    currentPath
                        .split("/")
                        .filter(Boolean)
                        .map((folder, index, arr) => (
                            <Breadcrumb.Item
                                key={index}
                                onClick={() => {
                                    const newPath = `/${arr.slice(0, index + 1).join("/")}/`;
                                    setCurrentPath(newPath);
                                }}
                                style={{ cursor: "pointer" }}
                            >
                                {folder}
                            </Breadcrumb.Item>
                        ))}
            </Breadcrumb>

            {currentPath !== "/" && (
                <Button onClick={handleGoBack} style={{ marginBottom: "20px" }}>
                    Назад
                </Button>
            )}

            <List
                bordered
                dataSource={sharedFiles.map((item) => ({
                    fullPath: item,
                    displayName: extractFileName(item),
                    isFolder: item.endsWith("/"),
                }))}
                renderItem={(item) => (
                    <List.Item
                        actions={
                            item.isFolder
                                ? [
                                    <Button
                                        type="link"
                                        onClick={() => handleFolderClick(item.fullPath)}
                                    >
                                        Открыть
                                    </Button>,
                                ]
                                : [
                                    <Button
                                        type="link"
                                        onClick={() =>
                                            handleDownload(item.fullPath, item.displayName)
                                        }
                                    >
                                        Скачать
                                    </Button>,
                                ]
                        }
                    >
                        {item.displayName}
                    </List.Item>
                )}
            />
        </div>
    );
};

export default SharedFilesPage;


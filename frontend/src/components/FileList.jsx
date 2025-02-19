import React, { useState, useEffect } from "react";
import { List, Dropdown, Menu, Button, message, Modal, Input } from "antd";
import { FolderOutlined, FileOutlined, EllipsisOutlined } from "@ant-design/icons";

const FileList = ({ files, currentPath, setCurrentPath, fetchFiles }) => {
    const [isShareModalVisible, setShareModalVisible] = useState(false);
    const [shareEmail, setShareEmail] = useState("");
    const [shareFolderPath, setShareFolderPath] = useState("");


    const handleDelete = (fileName) => {
        fetch(`http://localhost:8000/mydisk/files?path=${encodeURIComponent(currentPath)}&file_name=${encodeURIComponent(fileName)}`, {
            method: "DELETE",
            credentials: "include",
        })
            .then(() => {
                message.success("Файл успешно удалён!");
                fetchFiles();
            })
            .catch((error) => {
                console.error("Ошибка при удалении файла:", error);
                message.error("Не удалось удалить файл.");
            });
    };

    const handleDeleteFolder = async (folderPath) => {
        try {
            await fetch(`http://localhost:8000/mydisk/folders?path=${encodeURIComponent(folderPath)}`, {
                method: "DELETE",
                credentials: "include",
            });
            message.success("Папка успешно удалена!");
            fetchFiles();
        } catch (error) {
            console.error("Ошибка при удалении папки:", error);
            message.error("Не удалось удалить папку.");
        }
    };


    const handleShareFolder = async () => {
        try {
            const response = await fetch(`http://localhost:8000/mydisk/folders/share`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    folder_path: shareFolderPath,
                    user_email: shareEmail,
                }),
            });

            if (response.ok) {
                message.success("Доступ успешно предоставлен!");
            } else {
                const errorData = await response.json();
                message.error(`Ошибка: ${errorData.detail || "Не удалось предоставить доступ"}`);
            }
        } catch (error) {
            console.error("Ошибка при предоставлении доступа:", error);
            message.error("Не удалось предоставить доступ.");
        } finally {
            setShareModalVisible(false);
            setShareEmail("");
            setShareFolderPath("");
        }
    };

    const showShareModal = (folderPath) => {
        setShareFolderPath(folderPath);
        setShareModalVisible(true);
    };

    const handleDownload = (fileName) => {
        fetch(`http://localhost:8000/mydisk/files/download?path=${encodeURIComponent(currentPath)}&file_name=${encodeURIComponent(fileName)}`, {
            method: "GET",
            credentials: "include",
        })
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

    const handleRename = (fileName) => {
        const newName = prompt(`Введите новое имя для ${fileName}`);
        if (newName) {
            fetch(`http://localhost:8000/mydisk/files/rename`, {
                method: "PUT",
                credentials: "include",
                body: JSON.stringify({ path: currentPath, old_name: fileName, new_name: newName }),
                headers: { "Content-Type": "application/json" },
            })
                .then(() => {
                    message.success("Файл успешно переименован!");
                    fetchFiles();
                })
                .catch((error) => {
                    console.error("Ошибка при переименовании файла:", error);
                    message.error("Не удалось переименовать файл.");
                });
        }
    };

    const navigateToFolder = (folderName) => {
        setCurrentPath(`${currentPath}${folderName}`);
    };

    const navigateBack = () => {
        const newPath = currentPath.split("/").slice(0, -2).join("/") + "/";
        const finalPath = newPath === "/" ? "" : newPath;
        setCurrentPath(finalPath || "");
    };

    return (
        <div>
            {currentPath && (
                <Button style={{ marginBottom: "10px" }} onClick={navigateBack}>
                    Назад
                </Button>
            )}
            <List
                bordered
                dataSource={files}
                renderItem={(fileName) => (
                    <List.Item
                        actions={[
                            <Dropdown
                                overlay={
                                    <Menu
                                        items={
                                            String(fileName).includes("/") // Проверяем, что это папка
                                                ? [
                                                    {
                                                        key: "delete-folder",
                                                        label: "Удалить папку",
                                                        onClick: () => handleDeleteFolder(`${currentPath}${fileName}`),
                                                    },
                                                    {
                                                        key: "share-folder",
                                                        label: "Поделиться",
                                                        onClick: () => showShareModal(`${currentPath}${fileName}`),
                                                    },
                                                ]
                                                : [
                                                    {
                                                        key: "delete-file",
                                                        label: "Удалить файл",
                                                        onClick: () => handleDelete(fileName),
                                                    },
                                                    {
                                                        key: "download",
                                                        label: "Скачать",
                                                        onClick: () => handleDownload(fileName),
                                                    },
                                                    {
                                                        key: "rename",
                                                        label: "Переименовать",
                                                        onClick: () => handleRename(fileName),
                                                    },
                                                ]
                                        }
                                    />
                                }
                                trigger={["click"]}
                            >
                                <Button
                                    type="text"
                                    icon={<EllipsisOutlined />}
                                    onClick={(e) => e.stopPropagation()} // Останавливаем всплытие события
                                />
                            </Dropdown>,
                        ]}
                        onClick={(e) => {
                            // Избегаем перехода внутрь папки, если кликнули на меню
                            if (e.target.closest("button")) return;

                            // Если это папка, позволяем переход
                            if (String(fileName).includes("/")) {
                                navigateToFolder(fileName);
                            }
                        }}
                    >
                        {String(fileName).includes("/") ? (
                            <FolderOutlined style={{ marginRight: "8px" }} />
                        ) : (
                            <FileOutlined style={{ marginRight: "8px" }} />
                        )}
                        {fileName}
                    </List.Item>

                )}
            />
            <Modal
                title="Поделиться папкой"
                visible={isShareModalVisible}
                onOk={handleShareFolder}
                onCancel={() => setShareModalVisible(false)}
                okText="Поделиться"
                cancelText="Отмена"
            >
                <Input
                    placeholder="Введите email пользователя"
                    value={shareEmail}
                    onChange={(e) => setShareEmail(e.target.value)}
                />
            </Modal>
        </div >
    );
};

export default FileList;

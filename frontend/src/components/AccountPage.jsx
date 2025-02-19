import React, { useState, useEffect } from "react";
import { Button, Avatar, message, Input } from "antd";
import { useNavigate } from "react-router-dom";
import { UserOutlined } from "@ant-design/icons";
import FileList from "./FileList";
import FileUploader from "./FileUploader";
import SharedFileList from './SharedFileList';

const AccountPage = () => {
    const [userData, setUserData] = useState(null);
    const [files, setFiles] = useState([]);
    const [sharedFiles, setSharedFiles] = useState([]);
    const [currentPath, setCurrentPath] = useState(""); // Хранит текущий путь
    const [folderName, setFolderName] = useState(""); // Для ввода имени папки
    const navigate = useNavigate();

    useEffect(() => {
        fetchFiles();
        fetchSharedFiles();
        fetchUserData();
    }, [currentPath]); // Обновление файлов при изменении пути

    const fetchSharedFiles = () => {
        fetch("http://localhost:8000/mydisk/folders/shared", {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => setSharedFiles(data))
            .catch((error) => console.error("Ошибка при получении расшаренных файлов:", error));
    };

    const fetchUserData = () => {
        fetch("http://localhost:8000/auth/me", {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => setUserData(data))
            .catch((error) => console.error("Ошибка при получении данных:", error));
    };

    const fetchFiles = () => {
        fetch(`http://localhost:8000/mydisk/files?path=${encodeURIComponent(currentPath)}`, {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => setFiles(data.files))
            .catch((error) => console.error("Ошибка при получении файлов:", error));
    };

    const createFolder = () => {
        if (!folderName.trim()) {
            message.warning("Введите имя папки");
            return;
        }
        fetch("http://localhost:8000/mydisk/folders", {
            method: "POST",
            credentials: "include",
            body: JSON.stringify({ name: folderName, path: currentPath }),
            headers: { "Content-Type": "application/json" },
        })
            .then(() => {
                setFolderName(""); // Очистка ввода
                fetchFiles(); // Обновление списка файлов
            })
            .catch((error) => console.error("Ошибка при создании папки:", error));
    };

    const handleLogout = async () => {
        try {
            await fetch("http://localhost:8000/auth/logout", {
                method: "POST",
                credentials: "include",
            });
            navigate("/login");
        } catch (error) {
            message.error("Ошибка при выходе");
        }
    };

    return (
        <div style={{ padding: "20px" }}>
            {/* Шапка пользователя */}
            <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
                <Avatar icon={<UserOutlined />} size={64} />
                <Button type="primary" onClick={handleLogout}>
                    Выйти
                </Button>
            </div>
            <h1 style={{ marginTop: "20px" }}>Добро пожаловать, {userData?.name}</h1>

            {/* Текущий путь */}
            <p>Текущий путь: {currentPath || "/"}</p>

            {/* Создание папки */}
            <div style={{ marginBottom: "20px" }}>
                <Input
                    value={folderName}
                    onChange={(e) => setFolderName(e.target.value)}
                    placeholder="Имя папки"
                    style={{ width: "200px", marginRight: "10px" }}
                />
                <Button type="primary" onClick={createFolder}>
                    Создать папку
                </Button>
            </div>

            {/* Загрузка файлов */}
            <h3>Загрузите файл:</h3>
            <FileUploader
                onUploadSuccess={fetchFiles}
                currentPath={currentPath}
            />

            {/* Список файлов */}
            <h3 style={{ marginTop: "20px" }}>Ваши файлы:</h3>
            <FileList
                files={files}
                currentPath={currentPath}
                setCurrentPath={setCurrentPath}
                fetchFiles={fetchFiles}
            />
        </div>
    );
};

export default AccountPage;

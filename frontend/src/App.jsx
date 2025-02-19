import React, { useState, useEffect } from "react";
import { Layout, Typography, Button, message } from "antd";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import RegistrationForm from "./components/RegistrationForm";
import LoginForm from "./components/LoginForm";
import AccountPage from "./components/AccountPage";
import HeaderComponent from "./components/Header";
import SharedFilesPage from "./components/SharedFilesPage";

const { Title } = Typography;
const { Content } = Layout;

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Проверка на авторизован ли пользователь
    fetch("http://localhost:8000/auth/me", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data?.name) {
          setIsAuthenticated(true);
        }
      })
      .catch((error) => {
        console.error("Ошибка проверки авторизации:", error);
      });
  }, []);

  // Функция выхода
  const handleLogout = async () => {
    try {
      await fetch("http://localhost:8000/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      setIsAuthenticated(false); // Сбрасываем состояние авторизации
      message.success("Вы вышли из системы!");
    } catch (error) {
      message.error("Ошибка при выходе");
    }
  };

  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        {/* Хэдер с кнопкой выхода */}
        <HeaderComponent isAuthenticated={isAuthenticated} onLogout={handleLogout} />
        <Content
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: "20px",
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: "600px",
              backgroundColor: "#fff",
              padding: "20px",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
            }}
          >
            <Routes>
              {/* Путь для логина */}
              <Route path="/login" element={<LoginForm />} />
              {/* Путь для регистрации */}
              <Route path="/register" element={<RegistrationForm />} />
              {/* Путь для страницы пользователя */}
              <Route path="/account" element={isAuthenticated ? <AccountPage /> : <LoginForm />} />
              <Route
                path="/shared"
                element={isAuthenticated ? <SharedFilesPage /> : <LoginForm />}
              />
              {/* Главная страница */}
              <Route
                path="/"
                element={
                  isAuthenticated ? (
                    <AccountPage />
                  ) : (
                    <div style={{ textAlign: "center" }}>
                      <Title level={3}>Пожалуйста, войдите в систему</Title>
                      <Button type="primary" onClick={() => window.location.href = "/login"}>
                        Войти
                      </Button>
                      <Button
                        type="link"
                        style={{ marginLeft: "10px" }}
                        onClick={() => window.location.href = "/register"}
                      >
                        Зарегистрироваться
                      </Button>
                    </div>
                  )
                }
              />
            </Routes>
          </div>
        </Content>
      </Layout>
    </Router>
  );
};

export default App;

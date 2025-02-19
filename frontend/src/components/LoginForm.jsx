import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import { useNavigate } from "react-router-dom";

const LoginForm = () => {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const onFinish = async (values) => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:8000/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(values),
                credentials: "include",
            });
            if (response.ok) {
                message.success("Авторизация успешна!");
                navigate("/account");
            } else {
                message.error("Ошибка авторизации!");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            message.error("Произошла ошибка");
        }
        setLoading(false);
    };

    return (
        <Form name="login" onFinish={onFinish} layout="vertical">
            <Form.Item
                name="email"
                label="Email"
                rules={[{ required: true, type: "email", message: "Введите правильный email" }]}
            >
                <Input />
            </Form.Item>
            <Form.Item
                name="password"
                label="Пароль"
                rules={[{ required: true, message: "Введите пароль" }]}
            >
                <Input.Password />
            </Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
                Войти
            </Button>
        </Form>
    );
};

export default LoginForm;

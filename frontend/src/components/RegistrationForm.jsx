import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import { useNavigate } from "react-router-dom";

const RegistrationForm = () => {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Состояние для полей формы
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:8000/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                message.success("Вы успешно зарегистрированы!");
                navigate("/login"); // После успешной регистрации переходим на страницу логина
            } else {
                message.error("Ошибка при регистрации!");
            }
        } catch (error) {
            message.error("Ошибка при регистрации!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: "400px", margin: "0 auto" }}>
            <Form onFinish={handleSubmit}>
                <Form.Item
                    label="Имя"
                    name="name"
                    rules={[{ required: true, message: "Пожалуйста, введите ваше имя!" }]}
                >
                    <Input
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Введите ваше имя"
                    />
                </Form.Item>

                <Form.Item
                    label="Email"
                    name="email"
                    rules={[{ required: true, message: "Пожалуйста, введите ваш email!" }]}
                >
                    <Input
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Введите ваш email"
                    />
                </Form.Item>

                <Form.Item
                    label="Пароль"
                    name="password"
                    rules={[{ required: true, message: "Пожалуйста, введите ваш пароль!" }]}
                >
                    <Input.Password
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Введите ваш пароль"
                    />
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading} block>
                        Зарегистрироваться
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default RegistrationForm;

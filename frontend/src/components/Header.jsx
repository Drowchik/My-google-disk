import React from "react";
import { Layout, Dropdown, Menu } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const HeaderComponent = ({ isAuthenticated, onLogout }) => {
    const navigate = useNavigate();

    const menu = (
        <Menu>
            <Menu.Item onClick={() => navigate("/account")}>Мои файлы</Menu.Item>
            <Menu.Item onClick={() => navigate("/shared")}>Расшаренные файлы</Menu.Item>
            <Menu.Item onClick={onLogout}>Выйти</Menu.Item>
        </Menu>
    );

    return (
        <Layout.Header style={{ backgroundColor: "#001529", padding: "10px" }}>
            {isAuthenticated && (
                <Dropdown overlay={menu} trigger={['click']}>
                    <UserOutlined style={{ color: "#fff", fontSize: "24px" }} />
                </Dropdown>
            )}
        </Layout.Header>
    );
};

export default HeaderComponent;

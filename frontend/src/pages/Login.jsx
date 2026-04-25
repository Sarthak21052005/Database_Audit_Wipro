import { useState } from "react";
import { TextField, Button, Card, CardContent, Typography } from "@mui/material";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const navigate = useNavigate();

const handleLogin = async () => {
  try {
    const params = new URLSearchParams();
    params.append("username", form.username);
    params.append("password", form.password);

    const res = await API.post("/auth/login", params);

    localStorage.setItem("token", res.data.access_token);

    const payload = JSON.parse(
  decodeURIComponent(
    atob(res.data.access_token.split(".")[1])
      .split("")
      .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  )
);

    if (payload.role === "admin") navigate("/admin");
    else navigate("/user");

  } catch (err) {
    console.error(err);
    alert(err.response?.data?.detail || "Login failed");
  }
};
  return (
    <div style={{ display: "flex", justifyContent: "center", marginTop: "100px" }}>
      <Card sx={{ width: 400, padding: 2 }}>
        <CardContent>
          <Typography variant="h5" align="center" gutterBottom>
            Login
          </Typography>

          <TextField
            fullWidth
            label="Username"
            margin="normal"
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />

          <TextField
            fullWidth
            type="password"
            label="Password"
            margin="normal"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

            <Button
            fullWidth
            variant="contained"
            sx={{ marginTop: 2 }}
            onClick={handleLogin}
            disabled={!form.username || !form.password}
            >
            Login
            </Button>
        </CardContent>
      </Card>
    </div>
  );
}
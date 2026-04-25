import { useState } from "react";
import { Button, Container, Typography, TextField } from "@mui/material";
import Navbar from "../components/Navbar";
import API from "../services/api";

export default function UserDashboard() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const updateUser = async () => {
    try {
      await API.put("/user/update-user", {
        username: username || null,
        password: password || null,
      });

      alert("User Updated Successfully!");
      setUsername("");
      setPassword("");
    } catch (err) {
      console.error(err);
      alert("Update failed");
    }
  };

  return (
    <>
      <Navbar />
      <Container sx={{ marginTop: 4 }}>
        <Typography variant="h5" gutterBottom>
          User Dashboard
        </Typography>

        {/* Username Input */}
        <TextField
          fullWidth
          label="New Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          sx={{ marginBottom: 2 }}
        />

        {/* Password Input */}
        <TextField
          fullWidth
          label="New Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{ marginBottom: 2 }}
        />

        <Button variant="contained" color="success" onClick={updateUser}>
          Update User
        </Button>
      </Container>
    </>
  );
}
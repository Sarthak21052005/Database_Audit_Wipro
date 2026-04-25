import { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
  Paper,
} from "@mui/material";
import Navbar from "../components/Navbar";
import API from "../services/api";

export default function AdminDashboard() {
  const [logs, setLogs] = useState([]);

  const fetchLogs = async () => {
    const res = await API.get("/admin/logs");
    setLogs(res.data);
  };

  const rollback = async (id) => {
    await API.post(`/admin/rollback/${id}`);
    fetchLogs();
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <>
      <Navbar />
      <Container sx={{ marginTop: 4 }}>
        <Typography variant="h5" gutterBottom>
          Admin Dashboard
        </Typography>

        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Table</TableCell>
                <TableCell>Operation</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>{log.id}</TableCell>
                  <TableCell>{log.table_name}</TableCell>
                  <TableCell>{log.operation}</TableCell>
                  <TableCell>{log.user_name}</TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      color="error"
                      onClick={() => rollback(log.id)}
                    >
                      Rollback
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </Container>
    </>
  );
}
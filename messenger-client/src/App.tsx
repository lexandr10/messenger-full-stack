import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import RequireAuth from "./components/RequireAuth";
import ConversationsPage from "./pages/Conversations";
import AuthLayout from "./layouts/AuthLayout";
import RedirectIfAuth from "./components/RedirectIfAuth"; 

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route element={<RequireAuth />}>
          <Route index element={<ConversationsPage />} />
          <Route path="c/:id" element={<Chat />} />
        </Route>
      </Route>

      <Route element={<AuthLayout />}>
        <Route element={<RedirectIfAuth />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>
      </Route>
    </Routes>
  );
}

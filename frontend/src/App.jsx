import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/auth';
import { UserProvider } from './context/user';
import TopNav from './components/TopNav';
import Home from './components/Home';
import Profile from './components/Profile';
import Login from './components/Login';
import Register from './components/Register';
import ChatsPage from './components/ChatsPage';
import './App.css';
import ChatDetails from './components/ChatDetails';
import CreateChat from './components/CreateChat';

const queryClient = new QueryClient();

function AuthenticatedRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/chats" element={<ChatsPage />} />
      <Route path="/chats/new" element={<CreateChat />} />
      <Route path="/chats/:chatID" element={<ChatsPage />} />
      <Route path="/chats/:chatID/details" element={<ChatDetails />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/error" element={<h1>Error</h1>} />
      <Route path="/error/404" element={<h1>404: not found</h1>} />
    </Routes>
  );
}

function UnauthenticatedRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

function Header() {
  return (
    <header>
      <TopNav />
    </header>
  );
}

function Main() {
  const { isLoggedIn } = useAuth();

  return (
    <>
      {isLoggedIn ?
        <AuthenticatedRoutes /> :
        <UnauthenticatedRoutes />
      }
    </>
  );
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <UserProvider>
            <Header />
            <Main />
          </UserProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';

const Login: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    // Navigate to dashboard after successful magic link request
    setTimeout(() => {
      navigate('/app/dashboard');
    }, 2000);
  };

  return <LoginForm onSuccess={handleLoginSuccess} />;
};

export default Login;
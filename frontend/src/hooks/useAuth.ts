import { useState, useEffect } from 'react';
import { authAPI, type User } from '../services/api';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      setUser(null);
      localStorage.removeItem('authToken');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password?: string) => {
    try {
      const response = await authAPI.login(email, password);
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        await checkAuth();
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const sendMagicLink = async (email: string) => {
    try {
      const response = await authAPI.magicLink(email);
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('authToken');
      setUser(null);
    }
  };

  return {
    user,
    isLoading,
    login,
    logout,
    sendMagicLink,
    checkAuth,
  };
}
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Base URL configuration for different environments
const getBaseURL = () => {
  // For Android emulator, use 10.0.2.2
  // For iOS simulator, use localhost
  // For physical devices with Expo Go, use your computer's IP address
  if (__DEV__) {
    // For Expo Go on physical devices, use your computer's IP address
    return 'http://192.168.1.27:8000'; // Your computer's IP address
    // return 'http://10.0.2.2:8000'; // Android emulator
    // return 'http://localhost:8000'; // iOS simulator
  }
  return 'http://127.0.0.1:8000'; // Production
};

const API_BASE_URL = getBaseURL();

export const loginUser = async (acc_username: string, acc_password: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/token/`, {
    acc_username,
    acc_password,
  });
    const data = response.data;
    if (data.access && data.refresh) {
      await SecureStore.setItemAsync('accessToken', data.access);
      await SecureStore.setItemAsync('refreshToken', data.refresh);
      await SecureStore.setItemAsync('user', JSON.stringify(data.user));
    }
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getAccessToken = async () => {
  return await SecureStore.getItemAsync('accessToken');
};

export const getRefreshToken = async () => {
  return await SecureStore.getItemAsync('refreshToken');
};

export const getUserInfo = async () => {
  const user = await SecureStore.getItemAsync('user');
  return user ? JSON.parse(user) : null;
};

export const logoutUser = async () => {
  await SecureStore.deleteItemAsync('accessToken');
  await SecureStore.deleteItemAsync('refreshToken');
  await SecureStore.deleteItemAsync('user');
}; 
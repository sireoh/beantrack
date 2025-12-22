// src/api/axiosInstance.ts
import axios, { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
	baseURL: 'http://localhost:5483/api/v1',
	withCredentials: true,
});

export default api;
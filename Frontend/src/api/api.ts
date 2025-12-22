import api from './axiosInstance';
import {
	AddMovieRequest,
	UpdateMovieStatusRequest,
	AddTVShowRequest,
	UpdateStatusRequest,
	UpdateProgressRequest,
	UpdateProgressByIndexRequest,
} from '../models';

// Auth endpoints
export const login = async (data: { username: string; password: string }) => {
	const response = await api.post('/login', data);
	return response.data;
};

export const getAuth = async () => {
	const response = await api.get('/auth');
	return response.data;
};

export const signup = async (data: { username: string; password: string }) => {
	const response = await api.post('/signup', data);
	return response.data;
};

// Movie endpoints
export const getUserMovieList = async (status?: string) => {
	const params = status ? { status } : {};
	const response = await api.get('/movielist', { params });
	return response.data;
};

export const addMovie = async (data: AddMovieRequest) => {
	const response = await api.post('/movielist/add', data);
	return response.data;
};

export const deleteMovie = async (imdb: string) => {
	const response = await api.delete(`/movielist/${imdb}`);
	return response.data;
};

export const updateMovieStatus = async (data: UpdateMovieStatusRequest) => {
	const response = await api.patch('/movielist/edit', data);
	return response.data;
};

// TV endpoints
export const getUserTVList = async (status?: string) => {
	const params = status ? { status } : {};
	const response = await api.get('/tvlist', { params });
	return response.data;
};

export const addTVShow = async (data: AddTVShowRequest) => {
	const response = await api.post('/tvlist/add', data);
	return response.data;
};

export const deleteTVShow = async (imdb: string) => {
	const response = await api.delete(`/tvlist/${imdb}`);
	return response.data;
};

export const updateTVShowStatus = async (data: UpdateStatusRequest) => {
	const response = await api.patch('/tvlist/edit', data);
	return response.data;
};

export const incrementTVProgress = async (data: UpdateProgressRequest) => {
	const response = await api.patch('/tvlist/progress/increment', data);
	return response.data;
};

export const decrementTVProgress = async (data: UpdateProgressRequest) => {
	const response = await api.patch('/tvlist/progress/decrement', data);
	return response.data;
};

export const updateTVProgressByIndex = async (data: UpdateProgressByIndexRequest) => {
	const response = await api.patch('/tvlist/progress/index', data);
	return response.data;
};

// Search endpoints
export const searchMovies = async (query: string) => {
	const response = await api.get('/search/movie', { params: { q: query } });
	return response.data;
};

export const searchTVShows = async (query: string) => {
	const response = await api.get('/search/tv_show', { params: { q: query } });
	return response.data;
};
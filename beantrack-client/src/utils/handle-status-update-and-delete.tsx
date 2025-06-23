import { WatchlistItem } from "@/models";
import axios from "axios";
import { toast } from "sonner";

export const handleStatusUpdateAndDelete = async (
  action: string,
  type: string,
  item: WatchlistItem
) => {
  if (action === "delete") {
    return handleDelete(type, item);
  }

  return type == "tv"
    ? handleTVShowSelect(action, type, item)
    : handleMovieSelect(action, type, item);
};

const handleTVShowSelect = async (
  action: string,
  type: string,
  item: WatchlistItem
) => {
  if (action === "delete") {
    return handleDelete(type, item);
  }

  try {
    const url = `/api/${item.imdb}/edit/tv_show/status/${action}`;
    await axios.patch(url);
    toast.success(`Updated to "${action}"`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to update tv show.");
  }
};

const handleMovieSelect = async (
  action: string,
  type: string,
  item: WatchlistItem
) => {
  if (action === "delete") {
    return handleDelete(type, item);
  }

  try {
    const url = `/api/${item.imdb}/edit/movie/status/${action}`;
    await axios.patch(url);
    toast.success(`Updated to "${action}"`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to update movie.");
  }
};

const handleDelete = async (type: string, item: WatchlistItem) => {
  return type == "tv" ? handleTVShowDelete(item) : handleMovieDelete(item);
};

const handleTVShowDelete = async (item: WatchlistItem) => {
  try {
    const url = `/api/delete/${item.imdb}/tv_show`;
    await axios.delete(url);
    toast.success("TV show deleted.");
    // Optionally trigger a refresh or remove item from local state
  } catch (error) {
    console.error(error);
    toast.error("Failed to delete tv show.");
  }
};

const handleMovieDelete = async (item: WatchlistItem) => {
  try {
    const url = `/api/delete/${item.imdb}/movie`;
    await axios.delete(url);
    toast.success("TV show deleted.");
    // Optionally trigger a refresh or remove item from local state
  } catch (error) {
    console.error(error);
    toast.error("Failed to delete movie.");
  }
};

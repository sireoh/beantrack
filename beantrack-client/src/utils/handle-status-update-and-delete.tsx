import { ItemCardDataModel } from "@/components/app/item-card/item-card";
import { WatchlistItem } from "@/models";
import axios from "axios";
import { toast } from "sonner";

const notifs: Record<string, string> = {
  watching: "Currently Watching",
  completed: "Completed",
  on_hold: "On Hold",
  dropped: "Dropped",
  plan_to_watch: "Plan to Watch",
};

export const handleStatusUpdateAndDelete = async (
  action: string,
  type: string,
  item: WatchlistItem | ItemCardDataModel
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
  item: WatchlistItem | ItemCardDataModel
) => {
  if (action === "delete") {
    return handleDelete(type, item);
  }

  try {
    const url = `/api/${item.imdb}/edit/tv_show/status/${action}`;
    await axios.patch(url);
    toast.success(action != "delete" ? `Updated to: ${notifs[action]}` : "");
  } catch (error) {
    console.error(error);
    toast.error("Failed to update tv show.");
  }
};

const handleMovieSelect = async (
  action: string,
  type: string,
  item: WatchlistItem | ItemCardDataModel
) => {
  if (action === "delete") {
    return handleDelete(type, item);
  }

  try {
    const url = `/api/${item.imdb}/edit/movie/status/${action}`;
    await axios.patch(url);
    toast.success(action != "delete" ? `Updated to: ${notifs[action]}` : "");
  } catch (error) {
    console.error(error);
    toast.error("Failed to update movie.");
  }
};

const handleDelete = async (
  type: string,
  item: WatchlistItem | ItemCardDataModel
) => {
  return type == "tv" ? handleTVShowDelete(item) : handleMovieDelete(item);
};

const handleTVShowDelete = async (item: WatchlistItem | ItemCardDataModel) => {
  try {
    const url = `/api/delete/${item.imdb}/tv_show`;
    await axios.delete(url);
    toast.success(`${item.title} removed from library.`);
    // Optionally trigger a refresh or remove item from local state
  } catch (error) {
    console.error(error);
    toast.error(`Failed to remove ${item.title}.`);
  }
};

const handleMovieDelete = async (item: WatchlistItem | ItemCardDataModel) => {
  try {
    const url = `/api/delete/${item.imdb}/movie`;
    await axios.delete(url);
    toast.success(`${item.title} removed from library.`);
    // Optionally trigger a refresh or remove item from local state
  } catch (error) {
    console.error(error);
    toast.error(`Failed to remove ${item.title}.`);
  }
};

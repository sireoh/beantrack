import { ItemCardDataModel } from "@/components/app/item-card/item-card";
import { WatchlistItem } from "@/models";
import { deleteDataModel } from "@/store/slices/dialog-slice";
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
  item: WatchlistItem | ItemCardDataModel,
  toggleDialog: () => void,
  setDeleteData: (data: deleteDataModel | undefined) => void
) => {
  // Set the deleteData to the State.
  setDeleteData({ type, item });

  if (action === "delete") {
    return toggleDialog();
  }

  return type == "tv"
    ? handleTVShowSelect(action, item)
    : handleMovieSelect(action, item);
};

const handleTVShowSelect = async (
  action: string,
  item: WatchlistItem | ItemCardDataModel
) => {
  try {
    const url = `/api/${item.imdb}/edit/tv_show/status/${action}`;
    await axios.patch(url);
    toast.success(`Updated to: ${notifs[action]}`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to update tv show.");
  }
};

const handleMovieSelect = async (
  action: string,
  item: WatchlistItem | ItemCardDataModel
) => {
  try {
    const url = `/api/${item.imdb}/edit/movie/status/${action}`;
    await axios.patch(url);
    toast.success(`Updated to: ${notifs[action]}`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to update movie.");
  }
};

export const handleDelete = async (deleteData: deleteDataModel) => {
  console.log("deleteData", deleteData);

  const { type, item } = deleteData;
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

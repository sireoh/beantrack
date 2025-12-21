import { WatchlistItem } from "@/models";
import axios from "axios";
import { Dispatch, SetStateAction } from "react";
import { toast } from "sonner";

export async function handleChangeProgress(
  item: WatchlistItem,
  index: number,
  setCurrentProgress: Dispatch<SetStateAction<number>>
) {
  // BACKEND
  try {
    const url = `/api/${item.imdb}/edit/tv_show/progress/by_index/${index}`;
    await axios.patch(url);
  } catch (error) {
    console.error(error);
    toast.error("Failed to update item.");
  }

  // FRONTEND
  setCurrentProgress(index);

  // Toast Validation
  const episode = item.episodes[index];
  const code = episode.code;
  const name = episode.name;
  toast.success(`Changed to: ${code} ${name}`);
}

import { WatchlistItem } from "@/models";
import { updateTVProgressByIndex } from "@/api/api";
import { Dispatch, SetStateAction } from "react";
import { toast } from "sonner";

export async function handleChangeProgress(
  item: WatchlistItem,
  index: number,
  setCurrentProgress: Dispatch<SetStateAction<number>>
) {
  // BACKEND
  try {
    await updateTVProgressByIndex({
      imdb: item.imdb,
      index: index,
    });
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

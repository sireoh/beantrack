import { WatchlistItem } from "@/models";
import { Dispatch, SetStateAction } from "react";
import { toast } from "sonner";

export function handleChangeProgress(
  item: WatchlistItem,
  index: number,
  setCurrentProgress: Dispatch<SetStateAction<number>>
) {
  // FRONTEND
  setCurrentProgress(index);

  // Toast Validation
  const episode = item.episodes[index];
  const code = episode.code;
  const name = episode.name;
  toast.success(`Changed to: ${code} ${name}`);
}

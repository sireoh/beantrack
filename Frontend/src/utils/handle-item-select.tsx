import { addTVShow, addMovie } from "@/api/api";
import { toast } from "sonner";

export async function handleTVSelect(
  tvMazeId: number,
  status: string
) {

  try {
    await addTVShow({
      "tvmaze_id": tvMazeId,
      "status": status
    });
    toast.success(`Added TV Show #${tvMazeId} to the database.`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to add TV Show.");
  }
}

export async function handleMovieSelect(
  imdb: string,
  status: string
) {

  try {
    await addMovie({
      "imdb": imdb,
      "status": status
    });
    toast.success(`Added Movie #${imdb} to the database.`);
  } catch (error) {
    console.error(error);
    toast.error("Failed to add Movie.");
  }
}

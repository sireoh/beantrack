import { ItemCardDataModel } from "@/components/app/item-card/item-card";
import { TVMazeEpisodeModel } from "@/models";
import axios from "axios";
import { toast } from "sonner";

export async function handleTVSelect(
  itemCardData: ItemCardDataModel,
  action: string,
  results: TVMazeEpisodeModel[]
) {
  const truncatedImage =
    itemCardData.image.match(/original_untouched\/(.*?)\.jpg/)?.[1] ??
    itemCardData.image;

  const tvShowData = {
    status: action,
    image: truncatedImage,
    title: itemCardData.title,
    imdb: itemCardData.imdb,
    score: itemCardData.score,
    currentEpisodeIndex: 0,
    episodes: __handleResultsFormat(results),
  };

  console.log("[id]:", itemCardData.id, tvShowData);

  try {
    const res = await axios.post("/api/add/tv_show", tvShowData, {
      withCredentials: true,
    });
    toast.success(`Added TV Show "${itemCardData.title}" to the database.`);
    console.log(res.data);
  } catch (error) {
    console.error(error);
    toast.error("Failed to add TV Show.");
  }
}

function __handleResultsFormat(results: TVMazeEpisodeModel[]) {
  return results.map(({ season, number, name }) => ({
    code: `${season}x${String(number).padStart(2, "0")}`,
    name,
  }));
}

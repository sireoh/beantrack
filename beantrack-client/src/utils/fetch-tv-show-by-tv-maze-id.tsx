import { TVMazeEpisodeModel } from "@/models";

export async function fetchTVShowByTVMazeID(
  id: number
): Promise<TVMazeEpisodeModel[]> {
  const TV_SHOW_BY_TV_MAZE_ID_API_ENDPOINT =
    process.env.NEXT_PUBLIC_TV_SHOW_BY_TV_MAZE_ID_API_ENDPOINT;

  if (!TV_SHOW_BY_TV_MAZE_ID_API_ENDPOINT) {
    throw new Error(
      "TV Maze API endpoint is not defined in environment variables"
    );
  }

  const url = TV_SHOW_BY_TV_MAZE_ID_API_ENDPOINT.replace(":id", id.toString());

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch TV show by TVMaze ID");

  return await res.json();
}

import { TVMazeEpisodeModel } from "@/models";

export async function fetchTVShowByTVMazeID(
  id: number
): Promise<TVMazeEpisodeModel[]> {
  const res = await fetch(
    `/api/search_by_tvmaze_id/tv_show?id=${encodeURIComponent(id)}`,
    {
      method: "POST",
      credentials: "include", // optional if using cookies/auth
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch TV show by TVMaze ID: ${res.statusText}`);
  }

  const data = await res.json();
  return data.results;
}

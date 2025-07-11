import { OMDBResultsByIMDB } from "@/models";

export async function fetchMovieByIMDB(
  imdb: string
): Promise<OMDBResultsByIMDB> {
  const res = await fetch(
    `/api/search_by_imdb/movie?i=${encodeURIComponent(imdb)}`,
    {
      method: "POST",
      credentials: "include", // optional if using cookies/sessions
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch movie by IMDB: ${res.statusText}`);
  }

  return await res.json().then((data) => data.results);
}

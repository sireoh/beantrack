import { OMDBResultsByIMDB } from "@/models";

export async function fetchMovieByIMDB(
  imdb: string
): Promise<OMDBResultsByIMDB> {
  const MOVIE_BY_IMDB_API_ENDPOINT =
    process.env.NEXT_PUBLIC_MOVIE_BY_IMDB_API_ENDPOINT;

  const res = await fetch(`${MOVIE_BY_IMDB_API_ENDPOINT}${imdb}`);
  if (!res.ok) throw new Error("Failed to fetch movie by IMDB");
  return await res.json();
}

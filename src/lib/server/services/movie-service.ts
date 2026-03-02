import { db } from '$lib/server/db';
import { movie } from '$lib/server/db/schema';
import { OMDB_API_KEY } from '$env/static/private';
import { eq } from 'drizzle-orm';

export const movieService = {
	addByImdbId: async (imdbId: string) => {
		const response = await fetch(`https://www.omdbapi.com/?i=${imdbId}&apikey=${OMDB_API_KEY}`);
		const data = await response.json();

		if (data.Response === 'False') throw new Error(data.Error);

		return await db.insert(movie).values({
			imdb: data.imdbID,
			title: data.Title,
			image: data.Poster,
			score: parseFloat(data.imdbRating)
		}).onConflictDoUpdate({
			target: movie.imdb,
			set: { score: parseFloat(data.imdbRating) }
		}).returning();
	},

	remove: async (imdbId: string) => {
		return await db.delete(movie).where(eq(movie.imdb, imdbId));
	},
};
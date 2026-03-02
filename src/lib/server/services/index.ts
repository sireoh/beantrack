import { tvshowService } from "./tvshow-service";
import { movieService } from "./movie-service";

export const beantrackService = {
	movies: movieService,
	tvshows: tvshowService
};
export interface WatchlistItem {
  id: string;
  status: string;
  image: string;
  title: string;
  imdb: string;
  score: number;
  type: string;
  currentEpisode: number;
  totalEpisodes: number;
}

export interface CollectionModel {
  _id: {
    data: WatchlistItem[];
  };
}

export interface SearchResult<T> {
  results: T;
  error: string | null;
  loading: boolean;
}

export interface TVMazeTVShowModel {
  externals: { imdb: string };
  name: string;
  image: { original: string };
  rating: { average: number };
  summary: string;
}

export interface TVMazeResultEntryModel {
  show: TVMazeTVShowModel;
}

interface OMDBMovieModel {
  Title: string;
  Year: string;
  imdbID: string;
  Type: string;
  Poster: string;
}

export interface OMDBResults {
  Search?: OMDBMovieModel[];
  totalResults?: string;
  Response: string;
}

export type TVMazeResults = TVMazeResultEntryModel[];

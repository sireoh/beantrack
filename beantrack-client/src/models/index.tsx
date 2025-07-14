export interface Episode {
  code: string;
  name: string;
}

export interface WatchlistItem {
  id: string;
  status: string;
  image: string;
  title: string;
  imdb: string;
  score: number;
  currentEpisodeIndex: number;
  episodes: Episode[];
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
  id: number;
  externals: { imdb: string };
  name: string;
  image: { original: string };
  rating: { average: number };
  summary: string;
  premiered: string;
  ended: string;
  isAdded?: boolean;
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
  isAdded?: boolean;
}

export interface OMDBResults {
  Search?: OMDBMovieModel[];
  totalResults?: string;
  Response: string;
}

export interface OMDBResultsByIMDB {
  imdbRating?: string;
  Response: string;
}

export type TVMazeResults = TVMazeResultEntryModel[];

export type TVMazeEpisodeModel = {
  season: number;
  number: number;
  name: string;
};

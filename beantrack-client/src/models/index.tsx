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

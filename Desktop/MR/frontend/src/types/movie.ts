export interface StreamingPlatform {
  name: string;
  color: string;
  link?: string;
}

export interface Movie {
  id: number;
  title: string;
  poster: string;
  backdrop?: string;
  rating: number;
  genres: string[];
  year: number;
  platforms: StreamingPlatform[];
  overview?: string;
  runtime?: number;
  director?: string;
  cast?: string[];
  trailer?: string;
}

import poster1 from "@/assets/movie-poster-1.jpg";
import poster2 from "@/assets/movie-poster-2.jpg";
import poster3 from "@/assets/movie-poster-3.jpg";
import poster4 from "@/assets/movie-poster-4.jpg";
import poster5 from "@/assets/movie-poster-5.jpg";
import poster6 from "@/assets/movie-poster-6.jpg";
import type { Movie } from "@/types/movie";

export const mockMovies: Movie[] = [
  {
    id: 1,
    title: "Cosmic Odyssey",
    poster: poster1,
    backdrop: poster1,
    rating: 8.7,
    genres: ["Sci-Fi", "Adventure", "Drama"],
    year: 2024,
    platforms: [
      { name: "Netflix", color: "#E50914" },
      { name: "Prime", color: "#00A8E1" },
    ],
    overview: "A breathtaking journey through the cosmos as humanity's last hope embarks on an interstellar mission to find a new home. When a mysterious signal from a distant galaxy offers hope, a crew of unlikely heroes must navigate treacherous space anomalies and confront their deepest fears.",
    runtime: 148,
    director: "Christopher Nolan",
    cast: ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
  },
  {
    id: 2,
    title: "Nightfall Protocol",
    poster: poster2,
    backdrop: poster2,
    rating: 7.9,
    genres: ["Action", "Thriller"],
    year: 2024,
    platforms: [
      { name: "HBO Max", color: "#5822B4" },
    ],
    overview: "When a covert operative discovers a government conspiracy that threatens millions of lives, she must go rogue to expose the truth. With time running out and enemies closing in, she'll need to use every skill she has to survive.",
    runtime: 127,
    director: "David Fincher",
    cast: ["Charlize Theron", "Idris Elba", "Oscar Isaac"],
  },
  {
    id: 3,
    title: "Sunset in Paris",
    poster: poster3,
    backdrop: poster3,
    rating: 8.2,
    genres: ["Romance", "Comedy", "Drama"],
    year: 2023,
    platforms: [
      { name: "Disney+", color: "#113CCF" },
      { name: "Hulu", color: "#1CE783" },
    ],
    overview: "A chance encounter at a Parisian café sparks an unexpected romance between a struggling artist and a bestselling author. As they explore the city of lights together, they discover that love often finds you when you least expect it.",
    runtime: 115,
    director: "Richard Linklater",
    cast: ["Timothée Chalamet", "Florence Pugh", "Marion Cotillard"],
  },
  {
    id: 4,
    title: "The Hollow Manor",
    poster: poster4,
    backdrop: poster4,
    rating: 7.5,
    genres: ["Horror", "Mystery", "Thriller"],
    year: 2024,
    platforms: [
      { name: "Netflix", color: "#E50914" },
    ],
    overview: "A family inherits an ancient manor with a dark past. As strange occurrences begin to unfold, they must uncover the sinister secrets buried within its walls before they become the next victims of the curse that haunts the estate.",
    runtime: 109,
    director: "Mike Flanagan",
    cast: ["Carla Gugino", "Henry Thomas", "Victoria Pedretti"],
  },
  {
    id: 5,
    title: "Skyward Dreams",
    poster: poster5,
    backdrop: poster5,
    rating: 9.1,
    genres: ["Animation", "Adventure", "Family"],
    year: 2024,
    platforms: [
      { name: "Disney+", color: "#113CCF" },
    ],
    overview: "A young girl discovers she has the ability to bring her drawings to life. Together with her magical creations, she embarks on an epic adventure to save her kingdom from an ancient darkness that threatens to consume all creativity.",
    runtime: 102,
    director: "Hayao Miyazaki",
    cast: ["Elle Fanning", "Keanu Reeves", "Meryl Streep"],
  },
  {
    id: 6,
    title: "Shadows of the City",
    poster: poster6,
    backdrop: poster6,
    rating: 8.4,
    genres: ["Crime", "Drama", "Noir"],
    year: 2023,
    platforms: [
      { name: "Prime", color: "#00A8E1" },
      { name: "Apple TV", color: "#555555" },
    ],
    overview: "In a city where corruption runs deep, a detective with a troubled past takes on a case that will force him to confront the demons he's been running from. The line between justice and vengeance blurs as he digs deeper into the criminal underworld.",
    runtime: 135,
    director: "Denis Villeneuve",
    cast: ["Jake Gyllenhaal", "Viola Davis", "Mahershala Ali"],
  },
];

export const suggestions = [
  { label: "Trending Now", icon: "TrendingUp" },
  { label: "Action Movies", icon: "Flame" },
  { label: "Romantic Comedies", icon: "Heart" },
  { label: "Family Friendly", icon: "Popcorn" },
  { label: "Award Winners", icon: "Clapperboard" },
] as const;

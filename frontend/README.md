# BeanTrack frontend

SvelteKit (Svelte 5) + TypeScript + Tailwind CSS 4 + daisyUI 5, icons from `lucide-svelte`.
It is a single-page app (`ssr = false`, `adapter-static` with an `index.html` fallback) that talks
to the FastAPI backend in `../backend` with the session cookie.

## Run it

Needs Node 20+. From `frontend/`:

```bash
npm install
```

```bash
cp .env.example .env
```

```bash
npm run dev
```

Open the site on **the same hostname as `PUBLIC_API_URL`**, e.g. http://127.0.0.1:5173 for
`PUBLIC_API_URL=http://127.0.0.1:8000`. The dev server binds to that hostname automatically.
The login cookie is `SameSite=Lax`, and browsers treat `localhost` and `127.0.0.1` as different
sites, so mixing them makes you look logged out.

The backend's `.env` must match for local development:

```
DISCORD_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback   # also registered in the Discord app
FRONTEND_URL=http://127.0.0.1:5173/                             # where Discord login lands
CORS_ORIGINS=["http://127.0.0.1:5173"]                          # (this is the default)
COOKIE_SECURE=false                                             # plain http locally
```

Other scripts: `npm run check` (svelte-check + TypeScript), `npm run build` (static site in
`build/`), `npm run preview`.

## Configuration (`.env`)

| Variable | Meaning |
|---|---|
| `PUBLIC_API_URL` | API origin, e.g. `http://127.0.0.1:8000` (empty = same origin as the site) |
| `PUBLIC_DAISYUI_THEME` | Default daisyUI theme; empty or missing means `dark`. A user's dark/light choice (saved in `localStorage`) overrides it |

## Structure

```
src/
├── app.html                  # applies the saved/default theme before first paint
├── app.css                   # Tailwind + daisyUI (all themes enabled)
├── lib/
│   ├── api/
│   │   ├── types.ts          # API shapes, mirroring backend/app/schemas
│   │   └── client.ts         # typed fetch wrapper (credentials: 'include', ApiError, 401 hook)
│   ├── status.ts             # WatchStatus enum + STATUS_COLORS (theme variables) + labels
│   ├── config.ts             # PUBLIC_* env, login URL, IMDb links
│   ├── list-edit.ts          # shared edit logic: episodes, +/- (delta), jump (set_to), status, episode search
│   ├── list-view.ts          # filter / sort helpers for the list tables
│   ├── stores/               # user, searchMode, searchResults, tvList, movieList, episodes, theme, toasts
│   └── components/           # Navbar, SearchBar, SearchFilter, SearchTVCard/SearchMovieCard,
│                             # TVListTable, MovieListTable, EpisodeEditDropdown, EditMobileModal,
│                             # StatusPicker, ThemeController, LandingPage (+ small shared pieces)
└── routes/                   # /, /login, /search, /tvlist, /movielist
```

- **Stores own the data.** `tvList` / `movieList` are fetched once (`ensureTvList()`), then patched
  with the server's response after every add, progress or status change, so pages never refetch on
  navigation. `episodes` caches each show's episode list the first time its edit menu opens.
- **Edit logic is written once.** `EpisodeEditDropdown` (desktop) and `EditMobileModal`
  (mobile/tablet) both render `TvEditPanel`, which calls `$lib/list-edit`.
- **Breakpoints:** "desktop" is Tailwind's `lg` (≥1024px). Below that the list pages use the slim
  table, the status dropdown and the edit modal.

## Notes on the API

- `current_episode` is a 0-based index into `GET /api/tvlist/{imdb}/episodes`. The Progress column
  shows `current_episode + 1 / episodes_count` once an episode has been chosen, and `0 / N` before.
- Progress changes use `PATCH /api/tvlist/{imdb}/progress`; status changes use
  `PATCH /api/tvlist/{imdb}/status` and `PATCH /api/movielist/{imdb}/status`.
- `GET /api/search` requires login, so logged-out visitors to `/search` see the login landing page.
- Search results added from `/search` start with status `planned`.

# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
npx sv@0.12.4 create --template minimal --types ts --add tailwindcss="plugins:forms" drizzle="database:postgresql+postgresql:postgres.js+docker:no" better-auth="demo:password" --install npm beantrack
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

🧩 Add-on steps
drizzle:
- Check DATABASE_URL in .env and adjust it to your needs
- Run npm run db:push to update your database schema
better-auth:
- Run npm run auth:schema to generate the auth schema
- Run npm run db:push to update your database
- Check ORIGIN & BETTER_AUTH_SECRET in .env and adjust it to your needs                                                        
- Visit /demo/better-auth route to view the demo 
shadcn-svelte:
- npx shadcn-svelte@latest add button

# Tips
Find a specific route / Search through nested:
- <name_of_route>+
	- To search for nested routes

Show all server routes:
- routes+page.server.ts

# Fetch Data (Drizzle ORM) like:
```ts
// Fetch a show and include all its episodes
const showWithEpisodes = await db.query.tvshow.findFirst({
  where: (tvshow, { eq }) => eq(tvshow.imdb, 12345),
  with: {
    episodes: true,
  },
});

// Fetch an episode and include the parent show's details
const episodeWithShow = await db.query.episode.findFirst({
  with: {
    show: true, 
  },
});
```
import { pgTable, real, integer, text } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { user } from '$lib/server/db/auth.schema'

// ========================================
// ============= Watchlists ===============
// ========================================
export const tvlist = pgTable('watchlists', {
	id: text('id').primaryKey(),
	userId: text('user_id').references(() => user.id, {
		onDelete: 'cascade',
		onUpdate: 'cascade'
	})
})

// ========================================
// =========== Watchlist Items ============
// ========================================

export const tvshow = pgTable('tvshows', {
	imdb: text('imdb').primaryKey(),
	title: text('title').notNull(),
	image: text('image'),
	score: real('score').notNull().default(0.0),
})

export const movie = pgTable('movies', {
	imdb: text('imdb').primaryKey(),
	title: text('title').notNull(),
	image: text('image'),
	score: real('score').notNull().default(0.0),
})

export const episode = pgTable('episodes', {
	imdb: text('imdb').primaryKey(),
	season: integer('season').notNull(),
	episode: integer('episode').notNull(),
	title: text('title').notNull(),

	// Foreign Keys
	tvshowImdb: text('tvshow_imdb').references(() => tvshow.imdb, {
		onDelete: 'cascade',
		onUpdate: 'cascade'
	})
})

export const progress = pgTable('progress', {
	id: text('id').primaryKey(),
	status: text('status').notNull(),
	current_episode: integer('current_episode').notNull().default(0) // The index of the current episode in the season
})

// ========================================
// ============ Relationships =============
// ========================================
export const tvshowRelations = relations(tvshow, ({ many }) => ({
	episodes: many(episode),
}));

export const episodeRelations = relations(episode, ({ one }) => ({
	show: one(tvshow, {
		fields: [episode.tvshowImdb],
		references: [tvshow.imdb],
	}),
}));

export * from './auth.schema';

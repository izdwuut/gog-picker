import { RedditProfile } from './reddit-profile.model';
import { SteamProfile } from './steam-profile.model';

export class RedditComment {
    constructor(
        public body: String,
        public commentId: String,
        public entering: Boolean,
        public author?: RedditProfile,
        public steamProfile?: SteamProfile
    ) {}
}

export class SteamProfile {
    constructor(
        public steamId: String,
        public existent: Boolean,
        public gamesCount: Number,
        public gamesVisible: Boolean,
        public level: Number,
        public publicProfile: Boolean,
        public notScrapped: Boolean,
        public url: String
    ) { }
}

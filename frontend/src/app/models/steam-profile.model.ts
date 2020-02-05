export class SteamProfile {
    constructor(
        public existent: Boolean,
        public gamesCount: Number,
        public gamesVisible: Boolean,
        public level: Number,
        public publicProfile: Boolean
    ) { }
}

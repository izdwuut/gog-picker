export class Results {
    constructor(
        public eligible: Array<String>,
        public hash: String,
        public winners: Array<String>,
        public violators: Array<String>,
        public notEntering: Array<String>,
        public thread: String,
        public title: String
    ) {}
}

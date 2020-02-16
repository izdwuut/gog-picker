import { ResultsComment } from './results-comment.model';

export class Results {
    constructor(
        public eligible: Array<ResultsComment>,
        public hash: String,
        public winners: Array<ResultsComment>,
        public violators: Array<String>,
        public notEntering: Array<String>,
        public thread: String,
        public title: String
    ) {}
}

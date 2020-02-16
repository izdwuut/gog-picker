import { ResultsComment } from './results-comment.model';

export class Results {
    constructor(
        public eligible: Array<ResultsComment>,
        public hash: String,
        public winners: Array<ResultsComment>,
        public violators: Array<ResultsComment>,
        public notEntering: Array<ResultsComment>,
        public thread: String,
        public title: String
    ) {}
}

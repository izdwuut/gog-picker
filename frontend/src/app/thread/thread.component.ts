import { Component, OnInit } from '@angular/core';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { RestService } from '../services/rest.service';
import { RedditComment } from '../models/reddit-comment.model';

@Component({
  selector: 'app-cached',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit {
  thread: String = ''
  n: Number = 0
  comments: RedditComment[]

  constructor(private rest: RestService, private threadSubject: ThreadSubjectService) { }

  ngOnInit() {
    this.threadSubject.thread.subscribe(thread => {
      this.thread = thread
      if (!this.comments) {
        this.rest.getCachedComments(thread).subscribe(results => this.comments = results)
      }
    })
    this.threadSubject.n.subscribe(n => this.n = n)
  }

}

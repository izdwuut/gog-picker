import { Component, OnInit } from '@angular/core';
import { ThreadSubjectService } from '../services/thread-subject.service';

@Component({
  selector: 'app-cached',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit {
  thread: String = ''
  n: Number = 0

  constructor(private threadSubject: ThreadSubjectService) { }

  ngOnInit() {
    this.threadSubject.thread.subscribe(thread => this.thread = thread)
    this.threadSubject.n.subscribe(n => this.n = n)
  }

}

import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest.service'
import { Router } from '@angular/router';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { Location } from '@angular/common';
import { ThreadGuard } from '../guards/thread.guard';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  thread: string = ''
  threadInputHint: String = ''
  hasThreadErrors: Boolean = true

  n: number = 1
  nInputHint: String = ''
  hasNErrors: Boolean = false

  constructor(private rest: RestService, private router: Router,
    private threadSubject: ThreadSubjectService,
    private guard: ThreadGuard) { }

  ngOnInit() {
  }

  onThreadChange(): void {
    this.rest.isUrlValid(this.thread).subscribe(data => {
      this.hasThreadErrors = false
      this.threadInputHint = data['success']
    },
      error => {
        this.hasThreadErrors = true
        if (this.thread === '') {
          this.threadInputHint = ''
        } else {
          this.threadInputHint = error['error']['error']
        }
      })
  }

  onNChange(): void {
    if (this.n < 1) {
      if (!this.n) {
        this.nInputHint = 'Required.'
      } else {
        this.nInputHint = 'N must be positive.'
      }
      this.hasNErrors = true
    } else {
      this.nInputHint = ''
      this.hasNErrors = false
    }
  }

  send(): void {
    if (this.hasThreadErrors || this.hasNErrors) {
      if (!this.thread) {
        this.threadInputHint = 'No URL.'
      }
      return
    }
    this.threadSubject.changeThread(this.thread)
    this.threadSubject.changeN(this.n)
    this.guard.allow = true
    this.router.navigate(['/thread'])
  }
}

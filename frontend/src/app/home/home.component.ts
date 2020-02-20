import { Component, OnInit, OnDestroy } from '@angular/core';
import { RestService } from '../services/rest.service'
import { Router } from '@angular/router';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { ThreadGuard } from '../guards/thread.guard';
import { Subscription } from "rxjs";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {
  thread: string = ''
  threadInputHint: String = ''
  hasThreadErrors: Boolean = true
  isLoading = false

  n: number = 1
  nInputHint: String = ''
  hasNErrors: Boolean = false
  isUrlVaidSubscription: Subscription

  constructor(private rest: RestService, private router: Router,
    private threadSubject: ThreadSubjectService,
    private guard: ThreadGuard) { }

  ngOnInit() {
  }

  onThreadChange(): void {
    this.isLoading = true
    this.isUrlVaidSubscription = this.rest.isUrlValid(this.thread).subscribe(data => {
      this.hasThreadErrors = false
      this.threadInputHint = data['success']
      this.isLoading = false
    },
      error => {
        this.hasThreadErrors = true
        if (this.thread === '') {
          this.threadInputHint = ''
        } else {
          this.threadInputHint = error['error']['error']
        }
        this.isLoading = false
      })
  }

  onNChange(): void {
    if (this.n < 1) {
      if (this.n === null) {
        this.nInputHint = 'Required.'
      } else {
        this.nInputHint = 'Must be positive.'
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
    sessionStorage.clear()
    this.threadSubject.changeThread(this.thread)
    this.threadSubject.changeN(this.n)
    this.guard.allow = true
    this.router.navigate(['/thread'])
  }

  ngOnDestroy() {
    if(this.isUrlVaidSubscription) {
      this.isUrlVaidSubscription.unsubscribe()
    }
  }
}

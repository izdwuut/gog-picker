import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest.service'
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  thread = ''
  threadInputHint = ''
  hasThreadErrors = true

  n = 1

  constructor(private rest: RestService, private router: Router) { }

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

  send(): void {
    if (this.hasThreadErrors) {
      if(!this.thread) {
        this.threadInputHint = 'No URL.'
      }
      return
    }
    this.router.navigate(['/thread'])
  }
}

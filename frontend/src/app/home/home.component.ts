import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest.service'
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  thread = ''
  inputHint = ''
  hasErrors = false
  
  constructor(private rest: RestService) { }

  ngOnInit() {
  }

  onSearchChange(): void {  
    this.rest.isUrlValid(this.thread).subscribe(data => {
      this.hasErrors = false
      this.inputHint = data['success']
    },
    error => {
      this.hasErrors = true
      if(this.thread === '') {
        this.inputHint = ''
      } else {
        this.inputHint = error['error']['error']
      }
    })
  }

}

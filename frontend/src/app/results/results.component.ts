import { Component, OnInit } from '@angular/core';
import { RestService } from '../services/rest.service';
import { ActivatedRoute } from '@angular/router';
import { Results } from '../models/results.model';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss']
})
export class ResultsComponent implements OnInit {
  hash: String
  results: Results

  constructor(private rest: RestService, private route: ActivatedRoute) { }

  ngOnInit() {
    this.hash = this.route.snapshot.paramMap.get('hash')
    this.rest.getResults(this.hash).subscribe(results => {
      console.log(results)
      this.results = results
    })
  }

  getLinks(users: String[]): String {
    if(!users) {
      return
    }
    let links = Array<String>()
    users.forEach(item => {
      const link = `<a href="https://reddit.com/u/${item}">${item}</a>`
      links.push(link)
    })
    return links.join(', ')
  }
}

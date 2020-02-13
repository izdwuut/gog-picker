import { Component, OnInit, OnDestroy } from '@angular/core';
import { RestService } from '../services/rest.service';
import { ActivatedRoute } from '@angular/router';
import { Results } from '../models/results.model';
import { Subscription } from "rxjs";

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss']
})
export class ResultsComponent implements OnInit, OnDestroy {
  hash: String
  results: Results
  resultsSubscription: Subscription

  constructor(private rest: RestService, private route: ActivatedRoute) { }

  ngOnInit() {
    this.hash = this.route.snapshot.paramMap.get('hash')
    this.resultsSubscription = this.rest.getResults(this.hash).subscribe(results => {
      this.results = results
    })
  }

  getLinks(users: String[]): String {
    if(!users) {
      return
    }
    let links = Array<String>()
    users.forEach(item => {
      const link = `<a href="https://reddit.com/u/${item}" target="_blank">${item}</a>`
      links.push(link)
    })
    return links.join(', ')
  }

  ngOnDestroy() {
    this.resultsSubscription.unsubscribe()
  }
}

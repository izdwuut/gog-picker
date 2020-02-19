import { Component, OnInit, OnDestroy } from '@angular/core';
import { RestService } from '../services/rest.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Results } from '../models/results.model';
import { Subscription } from "rxjs";
import { ResultsComment } from '../models/results-comment.model';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss']
})
export class ResultsComponent implements OnInit, OnDestroy {
  hash: String
  results: Results
  resultsSubscription: Subscription

  constructor(private rest: RestService, private route: ActivatedRoute,
    private router: Router) { }

  ngOnInit() {
    this.hash = this.route.snapshot.paramMap.get('hash')
    this.resultsSubscription = this.rest.getResults(this.hash).subscribe(results => {
      this.results = results
      console.log(results)
    },
    error => {
      if(error.status === 404) {
        this.router.navigate(['404'])
      }
    })
  }

  getLinks(comments: ResultsComment[], thread: String): String {
    if(!comments) {
      return
    }
    let links = Array<String>()
    comments.forEach(item => {
      let link = `<a href="https://reddit.com/u/${item.author}" target="_blank">${item.author}</a>
<a href="${thread}${item.commentId}" target="_blank"><span class="material-icons">comment</span></a>`
      links.push(link)
    })
    return links.join(', ')
  }

  ngOnDestroy() {
    this.resultsSubscription.unsubscribe()
  }
}

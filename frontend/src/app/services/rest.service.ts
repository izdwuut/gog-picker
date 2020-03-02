import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'
import { RedditProfile } from '../models/reddit-profile.model';
import { SteamProfile } from '../models/steam-profile.model';
import { Results } from '../models/results.model';
import { ResultsComment } from '../models/results-comment.model';

@Injectable({
  providedIn: 'root'
})
export class RestService {
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type':  'application/json'
    })
  };

  apiUrl = environment.apiUrl;

  constructor(private http: HttpClient ) { }

  getCachedComments(url): Observable<RedditComment[]> {
    const payload = {'url': url}
    return this.http.post<any[]>(this.apiUrl + 'cache', payload).pipe(map(results => {
      let comments = new Array<RedditComment>()
      results.forEach(record => {
        let age = null
        if(record.author.age) {
          age = new Date(record.author.age)
        }
        const redditProfile = new RedditProfile(record.author.karma, record.author.name, age)
        let steamProfile
        if(record.steam_profile) {
          steamProfile = new SteamProfile(record.steam_profile.steam_id, 
            record.steam_profile.existent, record.steam_profile.games_count,
            record.steam_profile.games_visible, record.steam_profile.level, 
            record.steam_profile.public_profile, record.steam_profile.not_scrapped,
            record.steam_profile.url)
        }
        let comment = new RedditComment(record.body, record.comment_id, record.entering, redditProfile, steamProfile)
        comments.push(comment)
      })
      return comments
    }))
  }

  getBackendResultsComments(comments: Array<ResultsComment>): any[] {
    let resultsComments: any[] = Array<any>()
    comments.forEach((comment: ResultsComment) => {
      resultsComments.push({'author': comment.author, 'comment_id': comment.commentId})
    })
    return resultsComments
  }

  pickWinners(users: Array<ResultsComment>, n: Number, violators: Array<ResultsComment>, notEntering: Array<ResultsComment>, thread: String): Observable<any> {
    const payload = {'usernames': this.getBackendResultsComments(users), "n": n, "violators": this.getBackendResultsComments(violators), 
    "not_entering": this.getBackendResultsComments(notEntering), "thread": thread}
    console.log(payload)
    return this.http.post(this.apiUrl + 'picker/pick', payload)
  }

  isUrlValid(url: String): Observable<any> {
    const payload = {'url': url}
    return this.http.post(this.apiUrl + 'picker/url/valid', payload)
  }

  sendMessage(username: String, subject: String, body: String): Observable<any> {
    const payload = {'username': username, 'subject': subject, 'body': body}
    return this.http.post(this.apiUrl + 'mailer/send', payload)
  }

  getResultsComments(comments: any[]): ResultsComment[] {
    let resultsComments: ResultsComment[] = new Array<ResultsComment>()
    comments.forEach(comment => {
      resultsComments.push(new ResultsComment(comment.author, comment.comment_id))
    })
    return resultsComments
  }

  getResults(hash: String): Observable<Results> {
    return this.http.get<any>(this.apiUrl + 'picker/results/' + hash).pipe(map(results => {
      return new Results(this.getResultsComments(results.eligible), results.hash, this.getResultsComments(results.winners), 
      this.getResultsComments(results.violators), this.getResultsComments(results.not_entering),
        results.thread, results.title)
      }))
  }
}

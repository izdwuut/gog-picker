import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'
import { RedditProfile } from '../models/reddit-profile.model';
import { SteamProfile } from '../models/steam-profile.model';
import { Results } from '../models/results.model';

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
        console.log(record)
        const redditProfile = new RedditProfile(record.author.karma, record.author.name)
        let steamProfile
        if(record.steam_profile) {
          steamProfile = new SteamProfile(record.steam_profile.steam_id, record.steam_profile.existent, record.steam_profile.games_count,
            record.steam_profile.games_visible, record.steam_profile.level, record.steam_profile.public_profile)
        }
        let comment = new RedditComment(record.body, record.comment_id, record.entering, redditProfile, steamProfile)
        comments.push(comment)
      })
      return comments
    }))
  }

  pickWinners(users: Array<String>, n: Number, violators: Array<String>, notEntering: Array<String>, thread: String): Observable<any> {
    const payload = {'usernames': users, "n": n, "violators": violators, "not_entering": notEntering, "thread": thread}
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

  getResults(hash: String): Observable<Results> {
    return this.http.get<any>(this.apiUrl + 'picker/results/' + hash).pipe(map(results => {
      return new Results(results.eligible, results.hash, results.winners, results.violators, results.not_entering,
        results.thread)
      }))
  }
}

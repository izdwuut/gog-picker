import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'

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

  getCachedComments(url): Observable<any> {
    const payload = {'url': url}
    return this.http.post(this.apiUrl + 'cache', payload)
  }

  pickWinners(users: Array<String>, n: Number): Observable<any> {
    const payload = {'usernames': users, "n": n}
    return this.http.post(this.apiUrl + 'picker/pick', payload)
  }

  isUrlValid(url: String): Observable<any> {
    const payload = {'url': url}
    return this.http.post(this.apiUrl + 'url/valid', payload)
  }

  sendMessage(username: String, subject: String, body: String): Observable<any> {
    const payload = {'username': username, 'subject': subject, 'body': body}
    return this.http.post(this.apiUrl + 'mailer/send', payload)
  }
}

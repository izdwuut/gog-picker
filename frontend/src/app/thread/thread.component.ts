import { Component, OnInit } from '@angular/core';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { RestService } from '../services/rest.service';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'

@Component({
  selector: 'app-cached',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit {
  thread: String = ''
  n: Number = 1
  comments: RedditComment[]

  constructor(private rest: RestService, private threadSubject: ThreadSubjectService) { }

  ngOnInit() {
    // this.threadSubject.thread.subscribe(thread => {
    //   this.thread = thread
    //   if (!this.comments) {
    //     this.rest.getCachedComments(thread).subscribe(results => this.comments = results)
    //   }
    // })
    // this.threadSubject.n.subscribe(n => this.n = n)
    this.rest.getCachedComments('https://www.reddit.com/r/GiftofGames/comments/eltt4p/offersteam_bad_north_jotunn_edition/').subscribe(results => this.comments = results)
  }

  unescapeQuotes(s: String): String {
    return s.replace(/\\"/g, '"');
  }

  isWarning(comment: RedditComment): Boolean {
    return comment.steamProfile == null || !comment.steamProfile.existent || comment.steamProfile.gamesCount >= environment.hoarderNumber
  }

  isError(comment: RedditComment): Boolean {
    if(comment.steamProfile) {
      return comment.author.karma < environment.minKarma ||
      !comment.steamProfile.existent || 
      comment.steamProfile.level < environment.minLevel ||
      !comment.steamProfile.gamesVisible ||
      !comment.steamProfile.publicProfile
    }
    return comment.author.karma < environment.minKarma
  }

  getErrors(comment: RedditComment): String[] {
    let errors = Array<String>()
    if(comment.entering) {
      if(comment.author.karma < environment.minKarma) {
        errors.push('not enough karma')
      }
      if(comment.steamProfile == null) {
        errors.push('no Steam profile')
      } else {
        if(comment.steamProfile.publicProfile) {
          if(comment.steamProfile.gamesCount >= environment.hoarderNumber) {
            errors.push('potential hoarder (' + comment.steamProfile.gamesCount + ' games)')
          }
          if(comment.steamProfile.level < environment.minLevel) {
            errors.push('Steam level too low')
          }
          if(!comment.steamProfile.gamesVisible) {
            errors.push('Steam games not visible')
          }
        } else {
          if(!comment.steamProfile.existent) {
            errors.push('nonexistent Steam profile')
          } else {
            errors.push('non public Steam profile')
          }
        }
      }
    }
    return errors
  }

  hasErrors(comment: RedditComment): Boolean {
    return this.getErrors(comment).length > 0
  }

  getSteamProfile(comment: RedditComment): String {
    let profile = Array<String>()
    if(comment.steamProfile == null) {
      return ''
    }
    if(comment.steamProfile.existent) {
      if(comment.steamProfile.publicProfile) {
        profile.push('level ' + comment.steamProfile.level) 
        if(comment.steamProfile.gamesVisible) {
          profile.push('Steam games visible')
        } else {
          profile.push('Steam games not visible')
        }
      } else {
        profile.push('non public')
      }
    } else {
      profile.push('nonexistent')
    }
    return profile.join(', ')
  }
}

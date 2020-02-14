import { Component, OnInit, ViewChild, ElementRef, ViewChildren, QueryList, AfterViewInit, AfterContentInit, OnChanges, OnDestroy } from '@angular/core';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { RestService } from '../services/rest.service';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'
import { MatCheckbox } from '@angular/material';
import { Router } from '@angular/router';
import { Subscription } from "rxjs";

@Component({
  selector: 'app-cached',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit, OnDestroy {
  thread: String = ''
  n: Number = 1
  comments: RedditComment[]
  @ViewChildren(MatCheckbox) results: QueryList<MatCheckbox>;
  isAllToggled = false
  isEmptySelect = false
  threadSubscription: Subscription
  commentsSubscription: Subscription
  nSubscription: Subscription
  pickWinnersSubscription: Subscription

  constructor(private rest: RestService, private threadSubject: ThreadSubjectService,
    private router: Router) { }

  ngOnInit() {
    if (sessionStorage.getItem('comments') === null || sessionStorage.getItem('n') === null ||
      sessionStorage.getItem('thread') === null) {
      this.threadSubscription = this.threadSubject.thread.subscribe(thread => {
        this.thread = thread
        sessionStorage.setItem('thread', JSON.stringify(thread))
        if (!this.comments) {
          this.commentsSubscription = this.rest.getCachedComments(thread).subscribe(results => {
            this.comments = results
            sessionStorage.setItem('comments', JSON.stringify(results))
          })
        }
      })
      this.nSubscription = this.threadSubject.n.subscribe(n => {
        this.n = n
        sessionStorage.setItem('n', JSON.stringify(n))
      })
    } else {
      this.thread = JSON.parse(sessionStorage.getItem('thread'))
      this.comments = JSON.parse(sessionStorage.getItem('comments'))
      this.n = JSON.parse(sessionStorage.getItem('n'))
    }

    // this.rest.getCachedComments('https://www.reddit.com/r/GiftofGames/comments/eltt4p/offersteam_bad_north_jotunn_edition/')
    // .subscribe(results => {
    //   this.comments = results
    // })
  }

  unescapeQuotes(s: String): String {
    return s.replace(/\\"/g, '"');
  }

  isWarning(comment: RedditComment): Boolean {
    return comment.steamProfile == null || !comment.steamProfile.existent || comment.steamProfile.gamesCount >= environment.hoarderNumber
  }

  isError(comment: RedditComment): Boolean {
    if (comment.steamProfile) {
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
    if (comment.entering) {
      if (comment.author.karma < environment.minKarma) {
        errors.push('not enough karma')
      }
      if (comment.steamProfile == null) {
        errors.push('no Steam profile')
      } else {
        if (comment.steamProfile.publicProfile) {
          if (comment.steamProfile.level < environment.minLevel) {
            errors.push('Steam level too low')
          }
          if (!comment.steamProfile.gamesVisible) {
            errors.push('Steam games not visible')
          }
        }
      }
      if(!this.isAgeValid(comment.author.age)) {
        errors.push('age too low')
      }
    }
    return errors
  }

  hasErrors(comment: RedditComment): Boolean {
    return this.getErrors(comment).length > 0
  }

  getSteamProfile(comment: RedditComment): String {
    let profile = Array<String>()
    if (comment.steamProfile == null) {
      return ''
    }
    if (comment.steamProfile.existent) {
      if (comment.steamProfile.publicProfile) {
        profile.push('level ' + comment.steamProfile.level)
        if (comment.steamProfile.gamesVisible) {
          profile.push('games visible')
          profile.push(comment.steamProfile.gamesCount + ' games')
        } else {
          profile.push('games not visible')
        }
      } else {
        profile.push('non public')
      }
    } else {
      profile.push('nonexistent')
    }
    return profile.join(', ')
  }

  isParticipating(comment: RedditComment): Boolean {
    return !this.hasErrors(comment) && comment.entering && !this.hasWarnings(comment)
  }

  getWarnings(comment: RedditComment): String[] {
    let warnings = Array<String>()
    if (comment.steamProfile && comment.steamProfile.steamId == null) {
      warnings.push('no Steam profile detected')
    }
    if (comment.steamProfile && comment.steamProfile.gamesCount >= environment.hoarderNumber) {
      warnings.push('potential hoarder (' + comment.steamProfile.gamesCount + ' games)')
    }
    return warnings
  }

  hasWarnings(comment: RedditComment): Boolean {
    return this.getWarnings(comment).length > 0
  }

  pickWinners() {
    let winners = Array<String>()
    this.results.forEach(item => {
      if (item.checked) {
        winners.push(item.value)
      }
    })
    let violators = Array<String>()
    let notEntering = Array<String>()
    this.comments.forEach(comment => {
      const author = comment.author.name
      if (comment.entering) {
        if (this.hasErrors(comment)) {
          violators.push(author)
        }
      } else {
        notEntering.push(author)
      }
    })
    if (winners.length === 0) {
      this.isEmptySelect = true
    } else {
      this.pickWinnersSubscription = this.rest.pickWinners(winners, this.n, violators, notEntering, this.thread).subscribe(results => {
        this.router.navigate(['results', results['results_hash']])
      })
    }
  }

  toggleAll(): void {
    this.isAllToggled = !this.isAllToggled
    this.results.forEach(item => {
      item.checked = this.isAllToggled
    })
  }

  isAgeValid(age: Date) {
    if (new Date().getTime() - age.getTime() >= 1000/*ms*/ * 60/*s*/ * 60/*min*/ * 24/*h*/ * 30/*days*/ * environment.minAgeInMonths/*months*/) {
      return true
    }
    return false
  }

  getAge(age: Date) {
    if(age === null) {
      return ''
    }
    let dateFrom = age
    let dateTo = new Date();

    let months = dateTo.getMonth() - dateFrom.getMonth() + (12 * (dateTo.getFullYear() - dateFrom.getFullYear()));
    let s = ''
    if (months >= 12) {
      s += (months - (months % 12)) / 12 + 'y '
    } else {
      s += months + 'm'
    }
    return s
  }

  ngOnDestroy() {
    if (this.threadSubscription) {
      this.threadSubscription.unsubscribe()
    }
    if (this.commentsSubscription) {
      this.commentsSubscription.unsubscribe()
    }
    if (this.nSubscription) {
      this.nSubscription.unsubscribe()
    }
    if (this.pickWinnersSubscription) {
      this.pickWinnersSubscription.unsubscribe()
    }
  }
}

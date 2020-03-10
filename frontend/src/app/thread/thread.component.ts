import { Component, OnInit, ViewChild, ElementRef, ViewChildren, QueryList, AfterViewInit, AfterContentInit, OnChanges, OnDestroy, AfterViewChecked, ChangeDetectorRef } from '@angular/core';
import { ThreadSubjectService } from '../services/thread-subject.service';
import { RestService } from '../services/rest.service';
import { RedditComment } from '../models/reddit-comment.model';
import { environment } from '../../environments/environment'
import { MatCheckbox } from '@angular/material';
import { Router } from '@angular/router';
import { Subscription } from "rxjs";
import { ResultsComment } from '../models/results-comment.model';

@Component({
  selector: 'app-cached',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit, OnDestroy, AfterViewInit {
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
  selection: Array<String> = []
  isHttpError: Boolean = false

  constructor(private rest: RestService, private threadSubject: ThreadSubjectService,
    private router: Router, private cdRef: ChangeDetectorRef) { }

  ngOnInit() {
    if (sessionStorage.getItem('comments') === null || sessionStorage.getItem('n') === null ||
      sessionStorage.getItem('thread') === null || sessionStorage.getItem('selection') === null) {
      this.threadSubscription = this.threadSubject.thread.subscribe(thread => {
        this.thread = thread
        sessionStorage.setItem('thread', JSON.stringify(thread))
        if (!this.comments) {
          this.commentsSubscription = this.rest.getCachedComments(thread).subscribe(results => {
            this.comments = results
            sessionStorage.setItem('comments', JSON.stringify(results))
            this.initSelected()
          },
            error => {
              this.isHttpError = true
            })
        } else {
          this.initSelected()
        }
      })
      this.nSubscription = this.threadSubject.n.subscribe(n => {
        this.n = n
        sessionStorage.setItem('n', JSON.stringify(n))
      })
    }
  }

  ngAfterViewInit() {
    this.results.changes.subscribe(() => {
      setTimeout(() => {
        this.setSelected()
      });
    })
    setTimeout(() => {
      if (sessionStorage.getItem('comments') && sessionStorage.getItem('n') &&
        sessionStorage.getItem('thread') && sessionStorage.getItem('selection')) {
        this.thread = JSON.parse(sessionStorage.getItem('thread'))
        this.comments = JSON.parse(sessionStorage.getItem('comments'))
        this.n = JSON.parse(sessionStorage.getItem('n'))
      }
    });
  }

  initSelected() {
    this.comments.forEach((comment: RedditComment) => {
      if (this.isParticipating(comment)) {
        this.selection.push(comment.commentId)
      }
    })
    sessionStorage.setItem('selection', JSON.stringify(this.selection))
  }

  setSelected() {
    this.selection = JSON.parse(sessionStorage.getItem('selection'))
    this.results.forEach(item => {
      const commentId = item._elementRef.nativeElement.getAttribute('data-comment-id')
      if (this.selection.includes(commentId)) {
        item.checked = true
      } else {
        item.checked = false
      }
    })
  }

  saveSelection(commentId: String, $event) {
    const index = this.selection.indexOf(commentId)
    if ($event.checked && index == -1) {
      this.selection.push(commentId)
    } else {
      this.selection.splice(index, 1)
    }
    sessionStorage.setItem('selection', JSON.stringify(this.selection))
  }

  unescapeQuotes(s: String): String {
    return s.replace(/\\"/g, '"');
  }

  isWarning(comment: RedditComment): Boolean {
    return comment.steamProfile == null || !comment.steamProfile.existent || comment.steamProfile.gamesCount >= environment.hoarderNumber
  }

  getErrors(comment: RedditComment): String[] {
    let errors = Array<String>()
    if (comment.entering) {
      if (comment.author.karma < environment.minKarma) {
        errors.push('not enough karma')
      }
      if (comment.steamProfile) {
        if (comment.steamProfile.url) {
          if (comment.steamProfile.steamId) {
            if (comment.steamProfile.existent) {
              if (comment.steamProfile.publicProfile) {
                if (comment.steamProfile.level < environment.minLevel) {
                  errors.push('Steam level too low')
                }
                if (!comment.steamProfile.gamesVisible) {
                  errors.push('Steam games not visible')
                }
              } else {
                errors.push('private Steam profile')
              }
            } else {
              errors.push('nonexistent Steam profile')
            }
          }
        } else {
          errors.push('no Steam profile link')
        }
      }

      if (comment.author.age) {
        if (!this.isAgeValid(comment.author.age)) {
          errors.push('age too low')
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
    if (comment.steamProfile == null) {
      return ''
    }
    if (comment.steamProfile.notScrapped || !comment.steamProfile.url) {
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
        profile.push('private')
      }
    } else {
      profile.push('nonexistent')
    }
    return profile.join(', ')
  }

  isParticipating(comment: RedditComment): Boolean {
    return !this.hasErrors(comment) && comment.entering && !this.hasWarnings(comment)
  }

  canScrapSteamProfile(comment: RedditComment): Boolean {
    return comment.steamProfile && !comment.steamProfile.notScrapped
  }

  getWarnings(comment: RedditComment): String[] {
    let warnings = Array<String>()
    if (comment.steamProfile && !comment.steamProfile.url) {
      return warnings
    }
    if (!this.canScrapSteamProfile(comment) || !comment.steamProfile.steamId) {
      warnings.push("couldn't scrap Steam profile. Please check it manually.")
      return warnings
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
    let winners = Array<any>()
    let violators = Array<ResultsComment>()
    this.results.forEach(item => {
      if (item.checked) {
        winners.push(new ResultsComment(item.value, item._elementRef.nativeElement.getAttribute('data-comment-id')))
      } else {
        if (item._elementRef.nativeElement.getAttribute('data-has-warnings')) {
          violators.push(new ResultsComment(item.value, item._elementRef.nativeElement.getAttribute('data-comment-id')))
        }
      }
    })
    let notEntering = Array<ResultsComment>()
    this.comments.forEach(comment => {
      const author = comment.author.name
      if (comment.entering) {
        if (this.hasErrors(comment)) {
          violators.push(new ResultsComment(author, comment.commentId))
        }
      } else {
        notEntering.push(new ResultsComment(author, comment.commentId))
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
    this.selection = []
    this.results.forEach(item => {
      item.checked = this.isAllToggled
      if (this.isAllToggled) {
        this.selection.push(item._elementRef.nativeElement.getAttribute('data-comment-id'))
      }
    })
    sessionStorage.setItem('selection', JSON.stringify(this.selection))
  }

  isAgeValid(age: Date) {
    if (new Date().getTime() - new Date(age).getTime() >= 1000/*ms*/ * 60/*s*/ * 60/*min*/ * 24/*h*/ * 30/*days*/ * environment.minAgeInMonths/*months*/) {
      return true
    }
    return false
  }

  getAge(age) {
    if (age === null) {
      return ''
    }
    let dateFrom = new Date(age)
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

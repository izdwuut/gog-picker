import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThreadSubjectService {
  private threadSource = new BehaviorSubject('');
  thread = this.threadSource.asObservable();

  private nSource = new BehaviorSubject(1);
  n = this.nSource.asObservable();

  constructor() { }

  changeThread(thread: string) {
    this.threadSource.next(thread)
  }

  changeN(n: number) {
    this.nSource.next(n)
  }
}

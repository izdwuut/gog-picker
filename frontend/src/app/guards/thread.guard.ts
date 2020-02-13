import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThreadGuard implements CanActivate {
  allow = false;

  constructor(private router: Router) {}

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    if (sessionStorage.getItem('comments') !== null && sessionStorage.getItem('n') !== null && 
    sessionStorage.getItem('thread') !== null) {
      return true;
    }
    if (this.allow) {
      this.allow = false;
      return true;
    }
    this.router.navigate([''])
    return false;
  }

}

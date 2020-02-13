import { Component, OnDestroy, OnInit } from '@angular/core';
import { LoadingScreenSubjectService } from "../services/loading-screen-subject.service";
import { Subscription } from "rxjs";
import { HttpRequest } from "@angular/common/http";
import { Router } from '@angular/router';

@Component({
  selector: 'app-loading-screen',
  templateUrl: './loading-screen.component.html',
  styleUrls: ['./loading-screen.component.scss']
})
export class LoadingScreenComponent implements OnInit, OnDestroy {

  loading: boolean = false;
  loadingSubscription: Subscription;

  constructor(private loadingScreenSubjectService: LoadingScreenSubjectService, private router: Router) {
  }

  ngOnInit() {
    this.loadingSubscription = this.loadingScreenSubjectService.loadingStatus.subscribe((value) => {
      this.loading = value;
    });
  }

  ngOnDestroy() {
    this.loadingSubscription.unsubscribe();
  }
}
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule, routes } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule, HttpRequest } from '@angular/common/http';
import { HomeComponent } from './home/home.component';
import { ThreadComponent } from './thread/thread.component';
import { MailerComponent } from './mailer/mailer.component';
import { RouterModule } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  MatFormFieldModule, MatIconModule, MatInputModule,
  MatButtonModule, MatCardModule, MatCheckboxModule,
  MatProgressSpinnerModule
} from '@angular/material'
import { FormsModule } from '@angular/forms';
import { ResultsComponent } from './results/results.component';
import { LoadingScreenComponent } from './loading-screen/loading-screen.component';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { LoadingScreenInterceptor } from './loading-screen/loading.interceptor';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ThreadComponent,
    MailerComponent,
    ResultsComponent,
    LoadingScreenComponent,
    PageNotFoundComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    RouterModule.forRoot(
      routes
    ),
    BrowserAnimationsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
  ],
  providers: [
    HomeComponent,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoadingScreenInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule, routes } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { HomeComponent } from './home/home.component';
import { ThreadComponent } from './thread/thread.component';
import { MailerComponent } from './mailer/mailer.component';
import { RouterModule, Routes } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatFormFieldModule, MatIconModule, MatInputModule, 
  MatButtonModule, MatCardModule, MatCheckboxModule, } from '@angular/material'
import { FormsModule } from '@angular/forms';
import { ResultsComponent } from './results/results.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ThreadComponent,
    MailerComponent,
    ResultsComponent
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
    MatCheckboxModule
  ],
  providers: [HomeComponent],
  bootstrap: [AppComponent]
})
export class AppModule { }

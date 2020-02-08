import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
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
import { ThreadGuard } from './guards/thread.guard';

const appRoutes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'thread', component: ThreadComponent,
canActivate: [ThreadGuard] },
  { path: 'mailer', component: MailerComponent },
  { path: 'results/:hash', component: ResultsComponent },
];

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
      appRoutes
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

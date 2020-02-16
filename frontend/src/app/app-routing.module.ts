import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { ThreadComponent } from './thread/thread.component';
import { MailerComponent } from './mailer/mailer.component';
import { ResultsComponent } from './results/results.component';
import { ThreadGuard } from './guards/thread.guard';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  {
    path: 'thread', component: ThreadComponent,
    canActivate: [ThreadGuard]
  },
  { path: 'mailer', component: MailerComponent },
  { path: 'results/:hash', component: ResultsComponent },
  { path: '404', component: PageNotFoundComponent },
  { path: '**', redirectTo: '/404' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

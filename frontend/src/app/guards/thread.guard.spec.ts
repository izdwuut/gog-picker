import { TestBed, async, inject } from '@angular/core/testing';

import { ThreadGuard } from './thread.guard';

describe('ThreadGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ThreadGuard]
    });
  });

  it('should ...', inject([ThreadGuard], (guard: ThreadGuard) => {
    expect(guard).toBeTruthy();
  }));
});

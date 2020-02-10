import { TestBed } from '@angular/core/testing';

import { LoadingScreenSubjectService } from './loading-screen-subject.service';

describe('LoadingScreenSubjectService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: LoadingScreenSubjectService = TestBed.get(LoadingScreenSubjectService);
    expect(service).toBeTruthy();
  });
});

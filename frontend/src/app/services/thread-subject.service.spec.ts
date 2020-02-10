import { TestBed } from '@angular/core/testing';

import { ThreadSubjectService } from './thread-subject.service';

describe('ThreadSubjectService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ThreadSubjectService = TestBed.get(ThreadSubjectService);
    expect(service).toBeTruthy();
  });
});

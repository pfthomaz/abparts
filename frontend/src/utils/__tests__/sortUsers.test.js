// frontend/src/utils/__tests__/sortUsers.test.js

import { sortUsersByName } from '../sortUsers';

describe('sortUsers', () => {
  describe('sortUsersByName', () => {
    test('sorts by name, case-insensitively', () => {
      const users = [{ name: 'charlie' }, { name: 'Alice' }, { name: 'bob' }];
      expect(sortUsersByName(users).map((u) => u.name)).toEqual(['Alice', 'bob', 'charlie']);
    });

    test('falls back to username when name is missing', () => {
      const users = [{ name: 'Zed' }, { username: 'amy' }, { name: 'Mona' }];
      expect(sortUsersByName(users).map((u) => u.name || u.username)).toEqual(['amy', 'Mona', 'Zed']);
    });

    test('does not mutate the input array', () => {
      const users = [{ name: 'b' }, { name: 'a' }];
      const result = sortUsersByName(users);
      expect(users.map((u) => u.name)).toEqual(['b', 'a']);
      expect(result).not.toBe(users);
    });

    test('returns empty/non-array input as-is', () => {
      expect(sortUsersByName([])).toEqual([]);
      expect(sortUsersByName(null)).toBeNull();
      expect(sortUsersByName(undefined)).toBeUndefined();
    });
  });
});

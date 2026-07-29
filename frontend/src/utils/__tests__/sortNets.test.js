// frontend/src/utils/__tests__/sortNets.test.js

import { sortByName, sortNetsByName } from '../sortNets';

describe('sortNets', () => {
  describe('sortNetsByName', () => {
    test('sorts purely numeric names numerically, not lexicographically', () => {
      const nets = [{ name: '10' }, { name: '2' }, { name: '1' }];
      expect(sortNetsByName(nets).map((n) => n.name)).toEqual(['1', '2', '10']);
    });

    test('sorts alphanumeric names alphabetically', () => {
      const nets = [{ name: 'Cage 12' }, { name: 'Cage 2' }, { name: 'Cage 1' }];
      expect(sortNetsByName(nets).map((n) => n.name)).toEqual(['Cage 1', 'Cage 12', 'Cage 2']);
    });

    test('sorts letters-only names alphabetically, case-insensitively', () => {
      const nets = [{ name: 'pen c' }, { name: 'Pen A' }, { name: 'pen B' }];
      expect(sortNetsByName(nets).map((n) => n.name)).toEqual(['Pen A', 'pen B', 'pen c']);
    });

    test('falls back to alphabetical when names are a mix of numeric-only and alphanumeric', () => {
      const nets = [{ name: '10' }, { name: 'Pen A' }, { name: '2' }];
      expect(sortNetsByName(nets).map((n) => n.name)).toEqual(['10', '2', 'Pen A']);
    });

    test('does not mutate the input array', () => {
      const nets = [{ name: '2' }, { name: '1' }];
      const result = sortNetsByName(nets);
      expect(nets.map((n) => n.name)).toEqual(['2', '1']);
      expect(result).not.toBe(nets);
    });

    test('returns empty/non-array input as-is', () => {
      expect(sortNetsByName([])).toEqual([]);
      expect(sortNetsByName(null)).toBeNull();
      expect(sortNetsByName(undefined)).toBeUndefined();
    });
  });

  describe('sortByName', () => {
    test('supports a custom name getter', () => {
      const items = [{ label: '10' }, { label: '2' }];
      expect(sortByName(items, (item) => item.label).map((i) => i.label)).toEqual(['2', '10']);
    });
  });
});

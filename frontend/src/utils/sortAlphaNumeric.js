// frontend/src/utils/sortAlphaNumeric.js

const isNumericName = (name) => /^\d+$/.test(String(name ?? '').trim());

/**
 * Sorts items by name: numerically (ascending) when every name in the list
 * consists only of digits, otherwise alphabetically (case-insensitive).
 */
export const sortByName = (items, getName = (item) => item.name) => {
  if (!Array.isArray(items) || items.length === 0) {
    return items;
  }

  const allNumeric = items.every((item) => isNumericName(getName(item)));
  const sorted = [...items];

  if (allNumeric) {
    sorted.sort((a, b) => parseInt(getName(a), 10) - parseInt(getName(b), 10));
  } else {
    sorted.sort((a, b) =>
      String(getName(a) ?? '').localeCompare(String(getName(b) ?? ''), undefined, { sensitivity: 'base' })
    );
  }

  return sorted;
};

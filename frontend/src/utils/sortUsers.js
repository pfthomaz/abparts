// frontend/src/utils/sortUsers.js

const getDisplayName = (user) => user?.name || user?.username || '';

/** Sorts users alphabetically (case-insensitive) by display name (name, falling back to username). */
export const sortUsersByName = (users) => {
  if (!Array.isArray(users) || users.length === 0) {
    return users;
  }

  return [...users].sort((a, b) =>
    getDisplayName(a).localeCompare(getDisplayName(b), undefined, { sensitivity: 'base' })
  );
};

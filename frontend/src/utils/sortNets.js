// frontend/src/utils/sortNets.js

import { sortByName } from './sortAlphaNumeric';

export { sortByName };

export const sortNetsByName = (nets) => sortByName(nets, (net) => net.name);

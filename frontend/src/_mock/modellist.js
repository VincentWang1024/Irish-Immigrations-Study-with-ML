import { faker } from '@faker-js/faker';
import { sample } from 'lodash';

// ----------------------------------------------------------------------

const modellist = [...Array(5)].map((_, index) => ({
  id: faker.datatype.uuid(),
  name: sample(['CNN', 'LSTM','NB']),
  accuracy: faker.random.numeric(2),
  recall: faker.random.numeric(2),
  f1score: faker.random.numeric(2),
  enable: sample(['YES', 'NO']),
}));

export default modellist;

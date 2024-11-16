import os
import json
from app.common.preprocess import preprocess_default
from app.common.postprocess import postprocess_default
import pandas as pd


#CONFIG = json.load(open('config.json'))

comps = {'99993-04923-492040': ('99993-04923-492040', '9990487238074', 'Elegant Flowers Company'),
         '88893-04923-493041': ('88893-04923-493041', '8880487238084', 'Perfectly Organized Systems Inc.'),
         '77793-04923-493142': ('77793-04923-493142', '7770487238094', 'Sparkling Stars Corporation'),
         '66693-04923-493243': ('66693-04923-493243', '6660487238104', 'Diamonds and Pearls Trading Company'),
         '55593-04923-493344': ('55593-04923-493344', '5550487238114', 'Green Energy Solutions'),
         '44493-04923-493445': ('44493-04923-493445', '4440487238124', 'Global Business Services LLC'),
}
df_comps = pd.DataFrame.from_dict(comps, orient='index', columns=['OGRN', 'INN', 'Name'])

d = {'99993-04923-492040': {('9990487238074', 'Alexei Viktorovich Petrov'):0.1,
    ('8880487238084', 'Eugene Nikolaevich Orlov'):0.5,
    ('7770487238094', 'Viktor Mikhailovich Kuznetsov'):0.25},
    '88893-04923-493041': {('6660487238104', 'Anastasia Nikolaevna Lebedeva'):0.03,
    ('5550487238114', 'Mikhail Ivanovich Petrov'):0.82,
    ('4440487238124', 'Olga Viktorovna Nikolaeva'):0.15},
    '77793-04923-493142': {('3330487238134', 'Pavel Andreevich Smirnov'):0.41,
    ('2220487238144', 'Dmitrii Aleksandrovich Kuznetsov'):0.18,
    ('1110487238154', 'Sergei Petrovich Mikhailov'):0.41},
    '66693-04923-493243': {('8880487238084', 'Eugene Nikolaevich Orlov'):0.35,
    ('7770487238094', 'Viktor Mikhailovich Kuznetsov'):0.25,
    ('6660487238104', 'Anastasia Nikolaevna Lebedeva'):0.4},
    '55593-04923-493344': {('5550487238114', 'Mikhail Ivanovich Petrov'):0.15,
    ('4440487238124', 'Olga Viktorovna Nikolaeva'):0.3,
    ('3330487238134', 'Pavel Andreevich Smirnov'):0.55},
    '44493-04923-493445': {('2220487238144', 'Dmitrii Aleksandrovich Kuznetsov'):0.4,
    ('1110487238154', 'Sergei Petrovich Mikhailov'):0.3,
    ('9990487238074', 'Alexei Viktorovich Petrov'):0.3},
}



postprocess_default(d, comps)

os.makedirs('environment', exist_ok=True)

with open('environment/results.tsv', 'w', encoding='utf-8') as f:
    f.write('test')


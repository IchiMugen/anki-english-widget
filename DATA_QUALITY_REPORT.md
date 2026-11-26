# Отчёт о качестве данных — English Trainer

Создаётся `tests/check_units.py` из `deck/words.csv` + `deck/units.jsonl`. Руками не править.

Статусы: **rich** — значения, 5+ примеров (6+ для фразовых глаголов и многозначных) с переводом, формы; **migrated** — только старые данные (один пример, одно значение), ещё не обработано.
Все примеры написаны для колоды (сгенерированы, это не цитаты) и проверены автоматически: целевая форма есть в предложении, пропуск не оставляет подсказку, есть перевод, нет повторов. **Ни один пример не помечен как проверенный человеком**; сомнительное — в разделе ниже.

## Итог

| | |
|---|---|
| Учебных единиц (слова и выражения) | 1261 |
| Обработано (rich) | 79 (6%) |
| Ещё не обработано (migrated) | 1182 |
| Примеров в карточках | 1640 (с переводом: 457) |
| Многозначных единиц | 15 |
| Примеров отложено на проверку | 1 |
| Ошибок | 0 |
| Предупреждений | 15 |

## Нужно посмотреть человеку

- «other»: сомнение — «the other day» обычно значит «на днях» (в прошлом), а не «в другой раз» — пример нужно заменить
- одно предложение у разных слов (friend, to be): she is my best friend
- одно предложение у разных слов (lunch, to have): let's have lunch together
- одно предложение у разных слов (between, difference): what's the difference between them
- одно предложение у разных слов (next, week): see you next week
- одно предложение у разных слов (many, people): many people work from home now
- одно предложение у разных слов (before, to wash): wash your hands before dinner
- одно предложение у разных слов (great, idea): that's a great idea
- одно предложение у разных слов (early, to get up): i get up early on weekdays
- одно предложение у разных слов (form, to fill in): please fill in this form
- одно предложение у разных слов (date, today): what's the date today
- одно предложение у разных слов (nice, to meet): nice to meet you
- одно предложение у разных слов (key, to find): i can't find my keys
- одно предложение у разных слов (light, to turn on): turn on the light please
- одно предложение у разных слов (glass, water): can i have a glass of water

## По каждой единице

| # | English | Уровень | Статус | Значений | Примеров | С переводом | Заметки |
|---|---|---|---|---|---|---|---|
| 1 | to borrow | A1-A2 | migrated | 1 | 1 | 0 |  |
| 2 | to undermine | B2-C1 | migrated | 1 | 1 | 0 |  |
| 3 | approach | B1-B2 | rich | 1 | 6 | 6 |  |
| 4 | issue | B1-B2 | rich | 1 | 6 | 6 |  |
| 5 | outcome | B1-B2 | rich | 1 | 6 | 6 |  |
| 6 | to improve | B1-B2 | rich | 1 | 6 | 6 |  |
| 7 | to persuade | B1-B2 | rich | 1 | 6 | 6 |  |
| 8 | requirement | B1-B2 | rich | 1 | 6 | 6 |  |
| 9 | capable | B1-B2 | rich | 1 | 6 | 6 |  |
| 10 | purpose | B1-B2 | rich | 1 | 6 | 6 |  |
| 11 | consistent | B1-B2 | rich | 1 | 6 | 6 |  |
| 12 | trade-off | Pro | rich | 1 | 6 | 6 |  |
| 13 | repetitive | B1-B2 | rich | 1 | 5 | 5 |  |
| 14 | arrogant | B1-B2 | rich | 1 | 5 | 5 |  |
| 15 | constraint | B2-C1 | rich | 1 | 5 | 5 |  |
| 16 | pacing | B2-C1 | rich | 1 | 5 | 5 |  |
| 17 | reunion | B1-B2 | rich | 1 | 5 | 5 |  |
| 18 | consumer | B1-B2 | rich | 1 | 5 | 5 |  |
| 19 | to edit | B1-B2 | rich | 1 | 6 | 6 |  |
| 20 | reluctant | B1-B2 | rich | 1 | 6 | 6 |  |
| 21 | to come across | B2-C1 | rich | 2 | 7 | 7 |  |
| 22 | to come up with | B1-B2 | rich | 1 | 6 | 6 |  |
| 23 | to come down with | B2-C1 | rich | 1 | 6 | 6 |  |
| 24 | to be | A1-A2 | rich | 1 | 6 | 6 |  |
| 25 | to clarify | B1-B2 | rich | 1 | 6 | 6 |  |
| 26 | to take for granted | B1-B2 | rich | 1 | 7 | 6 |  |
| 27 | to bring about | B2-C1 | rich | 1 | 6 | 6 |  |
| 28 | eventually | B1-B2 | rich | 1 | 6 | 6 |  |
| 29 | to cut down on | B2-C1 | rich | 1 | 6 | 6 |  |
| 30 | to have | A1-A2 | rich | 2 | 7 | 7 |  |
| 31 | to get rid of | B1-B2 | rich | 1 | 6 | 6 |  |
| 32 | to assign | B1-B2 | rich | 1 | 6 | 6 |  |
| 33 | to back up | B2-C1 | rich | 2 | 6 | 6 |  |
| 34 | thorough | B1-B2 | rich | 1 | 6 | 6 |  |
| 35 | to back out | B2-C1 | rich | 1 | 6 | 6 |  |
| 36 | to do | A1-A2 | rich | 1 | 6 | 6 |  |
| 37 | to figure out | B1-B2 | rich | 1 | 6 | 6 |  |
| 38 | to stand out | B2-C1 | rich | 1 | 6 | 6 |  |
| 39 | feedback | B1-B2 | rich | 1 | 6 | 6 |  |
| 40 | affordable | B1-B2 | rich | 1 | 5 | 5 |  |
| 41 | to stand up for | B2-C1 | rich | 1 | 6 | 6 |  |
| 42 | to make | A1-A2 | rich | 2 | 7 | 7 |  |
| 43 | to make sense | B1-B2 | rich | 1 | 6 | 6 |  |
| 44 | to look up to | B2-C1 | rich | 1 | 6 | 6 |  |
| 45 | other | A1-A2 | rich | 1 | 5 | 5 | «the other day» обычно значит «на днях» (в прошлом), а не «в другой раз» — пример нужно заменить; 1 пример(ов) на проверке |
| 46 | nevertheless | B1-B2 | rich | 1 | 5 | 5 |  |
| 47 | to adjust | B1-B2 | rich | 2 | 6 | 6 |  |
| 48 | well | A1-A2 | rich | 2 | 6 | 6 |  |
| 49 | to look down on | B2-C1 | migrated | 1 | 1 | 0 |  |
| 50 | to go | A1-A2 | rich | 1 | 6 | 6 |  |
| 51 | because | A1-A2 | rich | 1 | 5 | 5 |  |
| 52 | to give up | B1-B2 | rich | 2 | 6 | 6 |  |
| 53 | to let down | B2-C1 | migrated | 1 | 1 | 0 |  |
| 54 | just | A1-A2 | rich | 2 | 6 | 6 |  |
| 55 | to put off | B1-B2 | rich | 1 | 6 | 6 |  |
| 56 | to get away with | B2-C1 | migrated | 1 | 1 | 0 |  |
| 57 | also | A1-A2 | rich | 1 | 5 | 5 |  |
| 58 | to align | Pro | rich | 2 | 6 | 6 |  |
| 59 | to come | A1-A2 | rich | 1 | 6 | 6 |  |
| 60 | only | A1-A2 | rich | 1 | 5 | 5 |  |
| 61 | to call off | B1-B2 | rich | 1 | 6 | 6 |  |
| 62 | to get on with | B2-C1 | migrated | 1 | 1 | 0 |  |
| 63 | most | A1-A2 | rich | 1 | 5 | 5 |  |
| 64 | to turn down | B1-B2 | rich | 2 | 6 | 6 |  |
| 65 | to get by | B2-C1 | migrated | 1 | 1 | 0 |  |
| 66 | to mean | A1-A2 | rich | 2 | 6 | 6 |  |
| 67 | to get | A1-A2 | rich | 3 | 7 | 7 |  |
| 68 | flexible | B1-B2 | rich | 1 | 5 | 5 |  |
| 69 | even | A1-A2 | rich | 1 | 5 | 5 |  |
| 70 | to look forward to | B1-B2 | rich | 1 | 6 | 6 |  |
| 71 | to go through | B2-C1 | migrated | 1 | 1 | 0 |  |
| 72 | such | B1-B2 | rich | 1 | 5 | 5 |  |
| 73 | to look after | B1-B2 | rich | 1 | 6 | 6 |  |
| 74 | to turn out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 75 | last | A1-A2 | rich | 2 | 6 | 6 |  |
| 76 | to take | A1-A2 | rich | 3 | 7 | 7 |  |
| 77 | to find out | B1-B2 | rich | 1 | 6 | 6 |  |
| 78 | really | A1-A2 | rich | 1 | 5 | 5 |  |
| 79 | to meet a deadline | Pro | rich | 1 | 5 | 5 |  |
| 80 | to keep up with | B2-C1 | migrated | 1 | 1 | 0 |  |
| 81 | between | A1-A2 | rich | 1 | 5 | 5 |  |
| 82 | to run out of | B1-B2 | rich | 1 | 6 | 6 |  |
| 83 | to make up for | B2-C1 | migrated | 1 | 1 | 0 |  |
| 84 | a lot of | A1-A2 | rich | 1 | 5 | 5 |  |
| 85 | to give | A1-A2 | rich | 1 | 6 | 6 |  |
| 86 | to get along with | B1-B2 | rich | 1 | 6 | 6 |  |
| 87 | own | A1-A2 | rich | 1 | 5 | 5 |  |
| 88 | to rule out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 89 | draft | B1-B2 | rich | 1 | 5 | 5 |  |
| 90 | little | A1-A2 | rich | 2 | 6 | 6 |  |
| 91 | to get over | B1-B2 | rich | 1 | 6 | 6 |  |
| 92 | to sort out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 93 | to know | A1-A2 | migrated | 1 | 1 | 0 |  |
| 94 | another | A1-A2 | migrated | 1 | 1 | 0 |  |
| 95 | to set up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 96 | to take over | B2-C1 | migrated | 1 | 1 | 0 |  |
| 97 | to become | A1-A2 | migrated | 1 | 1 | 0 |  |
| 98 | to evaluate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 99 | to take up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 100 | interest | B1-B2 | migrated | 1 | 1 | 0 |  |
| 101 | to take after | B2-C1 | migrated | 1 | 1 | 0 |  |
| 102 | to think | A1-A2 | migrated | 1 | 1 | 0 |  |
| 103 | next | A1-A2 | migrated | 1 | 1 | 0 |  |
| 104 | first | A1-A2 | migrated | 1 | 1 | 0 |  |
| 105 | to take off | B1-B2 | migrated | 1 | 1 | 0 |  |
| 106 | to wear off | B2-C1 | migrated | 1 | 1 | 0 |  |
| 107 | where | A1-A2 | migrated | 1 | 1 | 0 |  |
| 108 | while | B1-B2 | migrated | 1 | 1 | 0 |  |
| 109 | to bring up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 110 | much | A1-A2 | migrated | 1 | 1 | 0 |  |
| 111 | to reach out | Pro | migrated | 1 | 1 | 0 |  |
| 112 | to include | B1-B2 | migrated | 1 | 1 | 0 |  |
| 113 | many | A1-A2 | migrated | 1 | 1 | 0 |  |
| 114 | to put forward | B2-C1 | migrated | 1 | 1 | 0 |  |
| 115 | to see | A1-A2 | migrated | 1 | 1 | 0 |  |
| 116 | before | A1-A2 | migrated | 1 | 1 | 0 |  |
| 117 | report | B1-B2 | migrated | 1 | 1 | 0 |  |
| 118 | to grow up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 119 | great | A1-A2 | migrated | 1 | 1 | 0 |  |
| 120 | to give in | B2-C1 | migrated | 1 | 1 | 0 |  |
| 121 | around | A1-A2 | migrated | 1 | 1 | 0 |  |
| 122 | number | A1-A2 | migrated | 1 | 1 | 0 |  |
| 123 | to show up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 124 | to hold on | B2-C1 | migrated | 1 | 1 | 0 |  |
| 125 | school | A1-A2 | migrated | 1 | 1 | 0 |  |
| 126 | to seem | B1-B2 | migrated | 1 | 1 | 0 |  |
| 127 | accurate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 128 | high | A1-A2 | migrated | 1 | 1 | 0 |  |
| 129 | to look | A1-A2 | migrated | 1 | 1 | 0 |  |
| 130 | kind | A1-A2 | migrated | 1 | 1 | 0 |  |
| 131 | why | A1-A2 | migrated | 1 | 1 | 0 |  |
| 132 | to deal with | B1-B2 | migrated | 1 | 1 | 0 |  |
| 133 | to hang out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 134 | book | A1-A2 | migrated | 1 | 1 | 0 |  |
| 135 | every | A1-A2 | migrated | 1 | 1 | 0 |  |
| 136 | to put up with | B1-B2 | migrated | 1 | 1 | 0 |  |
| 137 | month | A1-A2 | migrated | 1 | 1 | 0 |  |
| 138 | to drop by | B2-C1 | migrated | 1 | 1 | 0 |  |
| 139 | during | B1-B2 | migrated | 1 | 1 | 0 |  |
| 140 | business | A1-A2 | migrated | 1 | 1 | 0 |  |
| 141 | to watch | A1-A2 | migrated | 1 | 1 | 0 |  |
| 142 | to get stuck | B1-B2 | migrated | 1 | 1 | 0 |  |
| 143 | word | A1-A2 | migrated | 1 | 1 | 0 |  |
| 144 | to begin | A1-A2 | migrated | 1 | 1 | 0 |  |
| 145 | to carry on | B1-B2 | migrated | 1 | 1 | 0 |  |
| 146 | to build | A1-A2 | migrated | 1 | 1 | 0 |  |
| 147 | to drop out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 148 | since | B1-B2 | migrated | 1 | 1 | 0 |  |
| 149 | plan | A1-A2 | migrated | 1 | 1 | 0 |  |
| 150 | to work out | B1-B2 | migrated | 1 | 1 | 0 |  |
| 151 | to fall out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 152 | hour | A1-A2 | migrated | 1 | 1 | 0 |  |
| 153 | few | A1-A2 | migrated | 1 | 1 | 0 |  |
| 154 | to want | A1-A2 | migrated | 1 | 1 | 0 |  |
| 155 | student | A1-A2 | migrated | 1 | 1 | 0 |  |
| 156 | to point out | B1-B2 | migrated | 1 | 1 | 0 |  |
| 157 | early | A1-A2 | migrated | 1 | 1 | 0 |  |
| 158 | head | A1-A2 | migrated | 1 | 1 | 0 |  |
| 159 | to resolve | B1-B2 | migrated | 1 | 1 | 0 |  |
| 160 | person | A1-A2 | migrated | 1 | 1 | 0 |  |
| 161 | state | B1-B2 | migrated | 1 | 1 | 0 |  |
| 162 | to fall behind | B2-C1 | migrated | 1 | 1 | 0 |  |
| 163 | night | A1-A2 | migrated | 1 | 1 | 0 |  |
| 164 | to look up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 165 | area | A1-A2 | migrated | 1 | 1 | 0 |  |
| 166 | force | B1-B2 | migrated | 1 | 1 | 0 |  |
| 167 | to fall through | B2-C1 | migrated | 1 | 1 | 0 |  |
| 168 | to need | A1-A2 | migrated | 1 | 1 | 0 |  |
| 169 | bit | A1-A2 | migrated | 1 | 1 | 0 |  |
| 170 | large | A1-A2 | migrated | 1 | 1 | 0 |  |
| 171 | to run into | B1-B2 | migrated | 1 | 1 | 0 |  |
| 172 | language | A1-A2 | migrated | 1 | 1 | 0 |  |
| 173 | burnout | B1-B2 | migrated | 1 | 1 | 0 |  |
| 174 | without | A1-A2 | migrated | 1 | 1 | 0 |  |
| 175 | town | A1-A2 | migrated | 1 | 1 | 0 |  |
| 176 | to put up | B2-C1 | migrated | 1 | 1 | 0 |  |
| 177 | top | A1-A2 | migrated | 1 | 1 | 0 |  |
| 178 | order | B1-B2 | migrated | 1 | 1 | 0 |  |
| 179 | to catch up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 180 | colour | A1-A2 | migrated | 1 | 1 | 0 |  |
| 181 | market | A1-A2 | migrated | 1 | 1 | 0 |  |
| 182 | note | A1-A2 | migrated | 1 | 1 | 0 |  |
| 183 | to pick up | B2-C1 | migrated | 1 | 1 | 0 |  |
| 184 | to like | A1-A2 | migrated | 1 | 1 | 0 |  |
| 185 | to create | B1-B2 | migrated | 1 | 1 | 0 |  |
| 186 | service | B1-B2 | migrated | 1 | 1 | 0 |  |
| 187 | to address | B2-C1 | migrated | 1 | 1 | 0 |  |
| 188 | game | A1-A2 | migrated | 1 | 1 | 0 |  |
| 189 | to check in | B1-B2 | migrated | 1 | 1 | 0 |  |
| 190 | against | B1-B2 | migrated | 1 | 1 | 0 |  |
| 191 | to receive | B1-B2 | migrated | 1 | 1 | 0 |  |
| 192 | to show off | B2-C1 | migrated | 1 | 1 | 0 |  |
| 193 | body | A1-A2 | migrated | 1 | 1 | 0 |  |
| 194 | second | A1-A2 | migrated | 1 | 1 | 0 |  |
| 195 | to sign up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 196 | team | A1-A2 | migrated | 1 | 1 | 0 |  |
| 197 | to talk into | B2-C1 | migrated | 1 | 1 | 0 |  |
| 198 | though | B1-B2 | migrated | 1 | 1 | 0 |  |
| 199 | black | A1-A2 | migrated | 1 | 1 | 0 |  |
| 200 | to bear | B1-B2 | migrated | 1 | 1 | 0 |  |
| 201 | to love | A1-A2 | migrated | 1 | 1 | 0 |  |
| 202 | downside | B1-B2 | migrated | 1 | 1 | 0 |  |
| 203 | to regard | B2-C1 | migrated | 1 | 1 | 0 |  |
| 204 | research | B1-B2 | migrated | 1 | 1 | 0 |  |
| 205 | result | B1-B2 | migrated | 1 | 1 | 0 |  |
| 206 | foot | A1-A2 | migrated | 1 | 1 | 0 |  |
| 207 | to fill in | B1-B2 | migrated | 1 | 1 | 0 |  |
| 208 | war | A1-A2 | migrated | 1 | 1 | 0 |  |
| 209 | current | B1-B2 | migrated | 1 | 1 | 0 |  |
| 210 | to think over | B2-C1 | migrated | 1 | 1 | 0 |  |
| 211 | example | A1-A2 | migrated | 1 | 1 | 0 |  |
| 212 | century | B1-B2 | migrated | 1 | 1 | 0 |  |
| 213 | account | B1-B2 | migrated | 1 | 1 | 0 |  |
| 214 | to break down | B1-B2 | migrated | 1 | 1 | 0 |  |
| 215 | particularly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 216 | to make out | B2-C1 | migrated | 1 | 1 | 0 |  |
| 217 | major | B1-B2 | migrated | 1 | 1 | 0 |  |
| 218 | cell | B1-B2 | migrated | 1 | 1 | 0 |  |
| 219 | to offer | B1-B2 | migrated | 1 | 1 | 0 |  |
| 220 | to say | A1-A2 | migrated | 1 | 1 | 0 |  |
| 221 | art | A1-A2 | migrated | 1 | 1 | 0 |  |
| 222 | above | A1-A2 | migrated | 1 | 1 | 0 |  |
| 223 | to break up | B1-B2 | migrated | 1 | 1 | 0 |  |
| 224 | plant | A1-A2 | migrated | 1 | 1 | 0 |  |
| 225 | to lead | B1-B2 | migrated | 1 | 1 | 0 |  |
| 226 | condition | B1-B2 | migrated | 1 | 1 | 0 |  |
| 227 | to paint | A1-A2 | migrated | 1 | 1 | 0 |  |
| 228 | to hand over | B1-B2 | migrated | 1 | 1 | 0 |  |
| 229 | to set off | B2-C1 | migrated | 1 | 1 | 0 |  |
| 230 | to press | A1-A2 | migrated | 1 | 1 | 0 |  |
| 231 | certain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 232 | far | A1-A2 | migrated | 1 | 1 | 0 |  |
| 233 | to fit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 234 | to achieve | B1-B2 | migrated | 1 | 1 | 0 |  |
| 235 | main | A1-A2 | migrated | 1 | 1 | 0 |  |
| 236 | guy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 237 | to acknowledge | B2-C1 | migrated | 1 | 1 | 0 |  |
| 238 | face | A1-A2 | migrated | 1 | 1 | 0 |  |
| 239 | wall | A1-A2 | migrated | 1 | 1 | 0 |  |
| 240 | to die | A1-A2 | migrated | 1 | 1 | 0 |  |
| 241 | to tell | A1-A2 | migrated | 1 | 1 | 0 |  |
| 242 | direct | B1-B2 | migrated | 1 | 1 | 0 |  |
| 243 | to accomplish | B2-C1 | migrated | 1 | 1 | 0 |  |
| 244 | to describe | B1-B2 | migrated | 1 | 1 | 0 |  |
| 245 | success | B1-B2 | migrated | 1 | 1 | 0 |  |
| 246 | less | A1-A2 | migrated | 1 | 1 | 0 |  |
| 247 | to avoid | B1-B2 | migrated | 1 | 1 | 0 |  |
| 248 | clearly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 249 | especially | B1-B2 | migrated | 1 | 1 | 0 |  |
| 250 | scope | Pro | migrated | 1 | 1 | 0 |  |
| 251 | lack | B1-B2 | migrated | 1 | 1 | 0 |  |
| 252 | until | B1-B2 | migrated | 1 | 1 | 0 |  |
| 253 | strong | A1-A2 | migrated | 1 | 1 | 0 |  |
| 254 | review | B1-B2 | migrated | 1 | 1 | 0 |  |
| 255 | to anticipate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 256 | to speak | A1-A2 | migrated | 1 | 1 | 0 |  |
| 257 | to depend | B1-B2 | migrated | 1 | 1 | 0 |  |
| 258 | to rise | B1-B2 | migrated | 1 | 1 | 0 |  |
| 259 | form | A1-A2 | migrated | 1 | 1 | 0 |  |
| 260 | race | A1-A2 | migrated | 1 | 1 | 0 |  |
| 261 | to afford | B1-B2 | migrated | 1 | 1 | 0 |  |
| 262 | girl | A1-A2 | migrated | 1 | 1 | 0 |  |
| 263 | to recognize | B1-B2 | migrated | 1 | 1 | 0 |  |
| 264 | to assume | B2-C1 | migrated | 1 | 1 | 0 |  |
| 265 | level | A1-A2 | migrated | 1 | 1 | 0 |  |
| 266 | to gain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 267 | community | B1-B2 | migrated | 1 | 1 | 0 |  |
| 268 | to allow | B1-B2 | migrated | 1 | 1 | 0 |  |
| 269 | tree | A1-A2 | migrated | 1 | 1 | 0 |  |
| 270 | to ensure | B2-C1 | migrated | 1 | 1 | 0 |  |
| 271 | else | A1-A2 | migrated | 1 | 1 | 0 |  |
| 272 | to argue | B1-B2 | migrated | 1 | 1 | 0 |  |
| 273 | member | B1-B2 | migrated | 1 | 1 | 0 |  |
| 274 | to implement | B2-C1 | migrated | 1 | 1 | 0 |  |
| 275 | board | B1-B2 | migrated | 1 | 1 | 0 |  |
| 276 | particular | B1-B2 | migrated | 1 | 1 | 0 |  |
| 277 | to ask | A1-A2 | migrated | 1 | 1 | 0 |  |
| 278 | mark | A1-A2 | migrated | 1 | 1 | 0 |  |
| 279 | able | B1-B2 | migrated | 1 | 1 | 0 |  |
| 280 | to join | A1-A2 | migrated | 1 | 1 | 0 |  |
| 281 | church | A1-A2 | migrated | 1 | 1 | 0 |  |
| 282 | to admit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 283 | to emphasize | B2-C1 | migrated | 1 | 1 | 0 |  |
| 284 | item | B1-B2 | migrated | 1 | 1 | 0 |  |
| 285 | detail | B1-B2 | migrated | 1 | 1 | 0 |  |
| 286 | support | B1-B2 | migrated | 1 | 1 | 0 |  |
| 287 | to prove | B1-B2 | migrated | 1 | 1 | 0 |  |
| 288 | to suggest | B1-B2 | migrated | 1 | 1 | 0 |  |
| 289 | difference | B1-B2 | migrated | 1 | 1 | 0 |  |
| 290 | season | A1-A2 | migrated | 1 | 1 | 0 |  |
| 291 | to hesitate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 292 | whether | B1-B2 | migrated | 1 | 1 | 0 |  |
| 293 | floor | A1-A2 | migrated | 1 | 1 | 0 |  |
| 294 | step | A1-A2 | migrated | 1 | 1 | 0 |  |
| 295 | to answer | A1-A2 | migrated | 1 | 1 | 0 |  |
| 296 | stuff | A1-A2 | migrated | 1 | 1 | 0 |  |
| 297 | to maintain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 298 | true | A1-A2 | migrated | 1 | 1 | 0 |  |
| 299 | wide | A1-A2 | migrated | 1 | 1 | 0 |  |
| 300 | to refer | B2-C1 | migrated | 1 | 1 | 0 |  |
| 301 | present | A1-A2 | migrated | 1 | 1 | 0 |  |
| 302 | to expect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 303 | unclear | B1-B2 | migrated | 1 | 1 | 0 |  |
| 304 | anyone | A1-A2 | migrated | 1 | 1 | 0 |  |
| 305 | to draw | A1-A2 | migrated | 1 | 1 | 0 |  |
| 306 | directly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 307 | to struggle | B2-C1 | migrated | 1 | 1 | 0 |  |
| 308 | below | A1-A2 | migrated | 1 | 1 | 0 |  |
| 309 | heavy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 310 | quite | B1-B2 | migrated | 1 | 1 | 0 |  |
| 311 | white | A1-A2 | migrated | 1 | 1 | 0 |  |
| 312 | to remove | B1-B2 | migrated | 1 | 1 | 0 |  |
| 313 | doctor | A1-A2 | migrated | 1 | 1 | 0 |  |
| 314 | to accept | B1-B2 | migrated | 1 | 1 | 0 |  |
| 315 | to conduct | B2-C1 | migrated | 1 | 1 | 0 |  |
| 316 | to cope with | B2-C1 | migrated | 1 | 1 | 0 |  |
| 317 | statement | B1-B2 | migrated | 1 | 1 | 0 |  |
| 318 | equipment | B1-B2 | migrated | 1 | 1 | 0 |  |
| 319 | date | A1-A2 | migrated | 1 | 1 | 0 |  |
| 320 | term | B1-B2 | migrated | 1 | 1 | 0 |  |
| 321 | title | B1-B2 | migrated | 1 | 1 | 0 |  |
| 322 | link | A1-A2 | migrated | 1 | 1 | 0 |  |
| 323 | to work | A1-A2 | migrated | 1 | 1 | 0 |  |
| 324 | extra | A1-A2 | migrated | 1 | 1 | 0 |  |
| 325 | customer | B1-B2 | migrated | 1 | 1 | 0 |  |
| 326 | to introduce | B1-B2 | migrated | 1 | 1 | 0 |  |
| 327 | chair | A1-A2 | migrated | 1 | 1 | 0 |  |
| 328 | to refuse | B1-B2 | migrated | 1 | 1 | 0 |  |
| 329 | least | B1-B2 | migrated | 1 | 1 | 0 |  |
| 330 | sample | B1-B2 | migrated | 1 | 1 | 0 |  |
| 331 | to marry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 332 | front | A1-A2 | migrated | 1 | 1 | 0 |  |
| 333 | to deliver | B1-B2 | migrated | 1 | 1 | 0 |  |
| 334 | to follow through | Pro | migrated | 1 | 1 | 0 |  |
| 335 | strike | B1-B2 | migrated | 1 | 1 | 0 |  |
| 336 | connection | B1-B2 | migrated | 1 | 1 | 0 |  |
| 337 | to postpone | B2-C1 | migrated | 1 | 1 | 0 |  |
| 338 | to explain | A1-A2 | migrated | 1 | 1 | 0 |  |
| 339 | to collect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 340 | to seek | B2-C1 | migrated | 1 | 1 | 0 |  |
| 341 | age | A1-A2 | migrated | 1 | 1 | 0 |  |
| 342 | to inform | B1-B2 | migrated | 1 | 1 | 0 |  |
| 343 | to reduce | B1-B2 | migrated | 1 | 1 | 0 |  |
| 344 | ability | B1-B2 | migrated | 1 | 1 | 0 |  |
| 345 | straight | A1-A2 | migrated | 1 | 1 | 0 |  |
| 346 | outside | A1-A2 | migrated | 1 | 1 | 0 |  |
| 347 | to overcome | B2-C1 | migrated | 1 | 1 | 0 |  |
| 348 | appeal | B2-C1 | migrated | 1 | 1 | 0 |  |
| 349 | hospital | A1-A2 | migrated | 1 | 1 | 0 |  |
| 350 | low | A1-A2 | migrated | 1 | 1 | 0 |  |
| 351 | highly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 352 | teacher | A1-A2 | migrated | 1 | 1 | 0 |  |
| 353 | quickly | A1-A2 | migrated | 1 | 1 | 0 |  |
| 354 | to trust | A1-A2 | migrated | 1 | 1 | 0 |  |
| 355 | to live | A1-A2 | migrated | 1 | 1 | 0 |  |
| 356 | to increase | B1-B2 | migrated | 1 | 1 | 0 |  |
| 357 | wonderful | A1-A2 | migrated | 1 | 1 | 0 |  |
| 358 | agreement | B1-B2 | migrated | 1 | 1 | 0 |  |
| 359 | land | B1-B2 | migrated | 1 | 1 | 0 |  |
| 360 | flat | A1-A2 | migrated | 1 | 1 | 0 |  |
| 361 | within | B1-B2 | migrated | 1 | 1 | 0 |  |
| 362 | to release | B1-B2 | migrated | 1 | 1 | 0 |  |
| 363 | absolutely | B1-B2 | migrated | 1 | 1 | 0 |  |
| 364 | to overlook | B2-C1 | migrated | 1 | 1 | 0 |  |
| 365 | charge | B1-B2 | migrated | 1 | 1 | 0 |  |
| 366 | flow | B1-B2 | migrated | 1 | 1 | 0 |  |
| 367 | solution | B1-B2 | migrated | 1 | 1 | 0 |  |
| 368 | to outline | B2-C1 | migrated | 1 | 1 | 0 |  |
| 369 | additional | B1-B2 | migrated | 1 | 1 | 0 |  |
| 370 | public | B1-B2 | migrated | 1 | 1 | 0 |  |
| 371 | popular | A1-A2 | migrated | 1 | 1 | 0 |  |
| 372 | farm | A1-A2 | migrated | 1 | 1 | 0 |  |
| 373 | finally | A1-A2 | migrated | 1 | 1 | 0 |  |
| 374 | to require | B1-B2 | migrated | 1 | 1 | 0 |  |
| 375 | negative | B1-B2 | migrated | 1 | 1 | 0 |  |
| 376 | fear | B1-B2 | migrated | 1 | 1 | 0 |  |
| 377 | to tend to | B2-C1 | migrated | 1 | 1 | 0 |  |
| 378 | relative | B1-B2 | migrated | 1 | 1 | 0 |  |
| 379 | to enjoy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 380 | to aim | B1-B2 | migrated | 1 | 1 | 0 |  |
| 381 | pair | A1-A2 | migrated | 1 | 1 | 0 |  |
| 382 | possible | A1-A2 | migrated | 1 | 1 | 0 |  |
| 383 | to eat | A1-A2 | migrated | 1 | 1 | 0 |  |
| 384 | double | A1-A2 | migrated | 1 | 1 | 0 |  |
| 385 | serious | A1-A2 | migrated | 1 | 1 | 0 |  |
| 386 | death | B1-B2 | migrated | 1 | 1 | 0 |  |
| 387 | leg | A1-A2 | migrated | 1 | 1 | 0 |  |
| 388 | to manage | B1-B2 | migrated | 1 | 1 | 0 |  |
| 389 | target | B1-B2 | migrated | 1 | 1 | 0 |  |
| 390 | to observe | B2-C1 | migrated | 1 | 1 | 0 |  |
| 391 | rather | B1-B2 | migrated | 1 | 1 | 0 |  |
| 392 | nice | A1-A2 | migrated | 1 | 1 | 0 |  |
| 393 | sentence | A1-A2 | migrated | 1 | 1 | 0 |  |
| 394 | degree | B1-B2 | migrated | 1 | 1 | 0 |  |
| 395 | to deserve | B2-C1 | migrated | 1 | 1 | 0 |  |
| 396 | truth | A1-A2 | migrated | 1 | 1 | 0 |  |
| 397 | to mention | B1-B2 | migrated | 1 | 1 | 0 |  |
| 398 | to pull | A1-A2 | migrated | 1 | 1 | 0 |  |
| 399 | nobody | A1-A2 | migrated | 1 | 1 | 0 |  |
| 400 | amount | B1-B2 | migrated | 1 | 1 | 0 |  |
| 401 | view | B1-B2 | migrated | 1 | 1 | 0 |  |
| 402 | to examine | B1-B2 | migrated | 1 | 1 | 0 |  |
| 403 | red | A1-A2 | migrated | 1 | 1 | 0 |  |
| 404 | to provide | B1-B2 | migrated | 1 | 1 | 0 |  |
| 405 | to lay | B2-C1 | migrated | 1 | 1 | 0 |  |
| 406 | picture | A1-A2 | migrated | 1 | 1 | 0 |  |
| 407 | husband | A1-A2 | migrated | 1 | 1 | 0 |  |
| 408 | to reply | B1-B2 | migrated | 1 | 1 | 0 |  |
| 409 | parent | A1-A2 | migrated | 1 | 1 | 0 |  |
| 410 | to display | B1-B2 | migrated | 1 | 1 | 0 |  |
| 411 | access | B1-B2 | migrated | 1 | 1 | 0 |  |
| 412 | boy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 413 | perfect | A1-A2 | migrated | 1 | 1 | 0 |  |
| 414 | to consider | B2-C1 | migrated | 1 | 1 | 0 |  |
| 415 | movement | B1-B2 | migrated | 1 | 1 | 0 |  |
| 416 | slightly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 417 | to drink | A1-A2 | migrated | 1 | 1 | 0 |  |
| 418 | couple | A1-A2 | migrated | 1 | 1 | 0 |  |
| 419 | overall | B1-B2 | migrated | 1 | 1 | 0 |  |
| 420 | to treat | B1-B2 | migrated | 1 | 1 | 0 |  |
| 421 | hard | A1-A2 | migrated | 1 | 1 | 0 |  |
| 422 | to intend | B2-C1 | migrated | 1 | 1 | 0 |  |
| 423 | to remind | B1-B2 | migrated | 1 | 1 | 0 |  |
| 424 | loss | B1-B2 | migrated | 1 | 1 | 0 |  |
| 425 | to respond | B1-B2 | migrated | 1 | 1 | 0 |  |
| 426 | to act | B1-B2 | migrated | 1 | 1 | 0 |  |
| 427 | to confirm | B2-C1 | migrated | 1 | 1 | 0 |  |
| 428 | slow | A1-A2 | migrated | 1 | 1 | 0 |  |
| 429 | modern | A1-A2 | migrated | 1 | 1 | 0 |  |
| 430 | party | A1-A2 | migrated | 1 | 1 | 0 |  |
| 431 | regular | B1-B2 | migrated | 1 | 1 | 0 |  |
| 432 | quality | B1-B2 | migrated | 1 | 1 | 0 |  |
| 433 | treatment | B1-B2 | migrated | 1 | 1 | 0 |  |
| 434 | physical | B1-B2 | migrated | 1 | 1 | 0 |  |
| 435 | to rely on | B1-B2 | migrated | 1 | 1 | 0 |  |
| 436 | stakeholder | Pro | migrated | 1 | 1 | 0 |  |
| 437 | apart | B1-B2 | migrated | 1 | 1 | 0 |  |
| 438 | supply | B1-B2 | migrated | 1 | 1 | 0 |  |
| 439 | round | A1-A2 | migrated | 1 | 1 | 0 |  |
| 440 | to suit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 441 | local | B1-B2 | migrated | 1 | 1 | 0 |  |
| 442 | village | A1-A2 | migrated | 1 | 1 | 0 |  |
| 443 | to reveal | B2-C1 | migrated | 1 | 1 | 0 |  |
| 444 | to convince | B2-C1 | migrated | 1 | 1 | 0 |  |
| 445 | road | A1-A2 | migrated | 1 | 1 | 0 |  |
| 446 | peace | A1-A2 | migrated | 1 | 1 | 0 |  |
| 447 | natural | B1-B2 | migrated | 1 | 1 | 0 |  |
| 448 | to sleep | A1-A2 | migrated | 1 | 1 | 0 |  |
| 449 | to decline | B2-C1 | migrated | 1 | 1 | 0 |  |
| 450 | story | A1-A2 | migrated | 1 | 1 | 0 |  |
| 451 | to express | B1-B2 | migrated | 1 | 1 | 0 |  |
| 452 | decade | B1-B2 | migrated | 1 | 1 | 0 |  |
| 453 | list | A1-A2 | migrated | 1 | 1 | 0 |  |
| 454 | to complain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 455 | to launch | B1-B2 | migrated | 1 | 1 | 0 |  |
| 456 | to indicate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 457 | to blame | B2-C1 | migrated | 1 | 1 | 0 |  |
| 458 | to warn | B1-B2 | migrated | 1 | 1 | 0 |  |
| 459 | to wish | A1-A2 | migrated | 1 | 1 | 0 |  |
| 460 | to attend | B1-B2 | migrated | 1 | 1 | 0 |  |
| 461 | favour | B1-B2 | migrated | 1 | 1 | 0 |  |
| 462 | almost | A1-A2 | migrated | 1 | 1 | 0 |  |
| 463 | to apologize | B1-B2 | migrated | 1 | 1 | 0 |  |
| 464 | dry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 465 | brother | A1-A2 | migrated | 1 | 1 | 0 |  |
| 466 | kid | A1-A2 | migrated | 1 | 1 | 0 |  |
| 467 | spot | B1-B2 | migrated | 1 | 1 | 0 |  |
| 468 | to claim | B2-C1 | migrated | 1 | 1 | 0 |  |
| 469 | score | B1-B2 | migrated | 1 | 1 | 0 |  |
| 470 | horse | A1-A2 | migrated | 1 | 1 | 0 |  |
| 471 | to continue | B1-B2 | migrated | 1 | 1 | 0 |  |
| 472 | education | B1-B2 | migrated | 1 | 1 | 0 |  |
| 473 | heat | A1-A2 | migrated | 1 | 1 | 0 |  |
| 474 | beyond | B2-C1 | migrated | 1 | 1 | 0 |  |
| 475 | feasible | B2-C1 | migrated | 1 | 1 | 0 |  |
| 476 | excited | A1-A2 | migrated | 1 | 1 | 0 |  |
| 477 | to buy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 478 | fish | A1-A2 | migrated | 1 | 1 | 0 |  |
| 479 | reader | A1-A2 | migrated | 1 | 1 | 0 |  |
| 480 | to measure | B1-B2 | migrated | 1 | 1 | 0 |  |
| 481 | whole | B1-B2 | migrated | 1 | 1 | 0 |  |
| 482 | importance | B1-B2 | migrated | 1 | 1 | 0 |  |
| 483 | to promise | A1-A2 | migrated | 1 | 1 | 0 |  |
| 484 | to appreciate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 485 | distance | A1-A2 | migrated | 1 | 1 | 0 |  |
| 486 | to kill | A1-A2 | migrated | 1 | 1 | 0 |  |
| 487 | trouble | B1-B2 | migrated | 1 | 1 | 0 |  |
| 488 | guide | B1-B2 | migrated | 1 | 1 | 0 |  |
| 489 | to estimate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 490 | yet | B1-B2 | migrated | 1 | 1 | 0 |  |
| 491 | to grant | B2-C1 | migrated | 1 | 1 | 0 |  |
| 492 | middle | A1-A2 | migrated | 1 | 1 | 0 |  |
| 493 | to serve | B1-B2 | migrated | 1 | 1 | 0 |  |
| 494 | to feed | A1-A2 | migrated | 1 | 1 | 0 |  |
| 495 | to commit | B2-C1 | migrated | 1 | 1 | 0 |  |
| 496 | to suffer | B1-B2 | migrated | 1 | 1 | 0 |  |
| 497 | mistake | A1-A2 | migrated | 1 | 1 | 0 |  |
| 498 | to pay | A1-A2 | migrated | 1 | 1 | 0 |  |
| 499 | certainly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 500 | to satisfy | B1-B2 | migrated | 1 | 1 | 0 |  |
| 501 | deep | A1-A2 | migrated | 1 | 1 | 0 |  |
| 502 | rate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 503 | chief | B1-B2 | migrated | 1 | 1 | 0 |  |
| 504 | to prevent | B1-B2 | migrated | 1 | 1 | 0 |  |
| 505 | except | B1-B2 | migrated | 1 | 1 | 0 |  |
| 506 | cool | A1-A2 | migrated | 1 | 1 | 0 |  |
| 507 | field | B1-B2 | migrated | 1 | 1 | 0 |  |
| 508 | to put together | B1-B2 | migrated | 1 | 1 | 0 |  |
| 509 | wave | A1-A2 | migrated | 1 | 1 | 0 |  |
| 510 | star | A1-A2 | migrated | 1 | 1 | 0 |  |
| 511 | to care | B1-B2 | migrated | 1 | 1 | 0 |  |
| 512 | south | A1-A2 | migrated | 1 | 1 | 0 |  |
| 513 | security | B1-B2 | migrated | 1 | 1 | 0 |  |
| 514 | generally | B1-B2 | migrated | 1 | 1 | 0 |  |
| 515 | surface | B1-B2 | migrated | 1 | 1 | 0 |  |
| 516 | to encourage | B2-C1 | migrated | 1 | 1 | 0 |  |
| 517 | to pretend | B1-B2 | migrated | 1 | 1 | 0 |  |
| 518 | library | A1-A2 | migrated | 1 | 1 | 0 |  |
| 519 | seat | A1-A2 | migrated | 1 | 1 | 0 |  |
| 520 | air | A1-A2 | migrated | 1 | 1 | 0 |  |
| 521 | excellent | A1-A2 | migrated | 1 | 1 | 0 |  |
| 522 | effect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 523 | to throw | A1-A2 | migrated | 1 | 1 | 0 |  |
| 524 | lift | A1-A2 | migrated | 1 | 1 | 0 |  |
| 525 | to settle | B2-C1 | migrated | 1 | 1 | 0 |  |
| 526 | trade | B1-B2 | migrated | 1 | 1 | 0 |  |
| 527 | to advertise | B1-B2 | migrated | 1 | 1 | 0 |  |
| 528 | task | B1-B2 | migrated | 1 | 1 | 0 |  |
| 529 | to open | A1-A2 | migrated | 1 | 1 | 0 |  |
| 530 | to select | B1-B2 | migrated | 1 | 1 | 0 |  |
| 531 | ever | A1-A2 | migrated | 1 | 1 | 0 |  |
| 532 | positive | B1-B2 | migrated | 1 | 1 | 0 |  |
| 533 | to surround | B1-B2 | migrated | 1 | 1 | 0 |  |
| 534 | news | A1-A2 | migrated | 1 | 1 | 0 |  |
| 535 | to waste | B1-B2 | migrated | 1 | 1 | 0 |  |
| 536 | extent | B2-C1 | migrated | 1 | 1 | 0 |  |
| 537 | option | B1-B2 | migrated | 1 | 1 | 0 |  |
| 538 | experience | B1-B2 | migrated | 1 | 1 | 0 |  |
| 539 | river | A1-A2 | migrated | 1 | 1 | 0 |  |
| 540 | to vote | B1-B2 | migrated | 1 | 1 | 0 |  |
| 541 | box | A1-A2 | migrated | 1 | 1 | 0 |  |
| 542 | annual | B1-B2 | migrated | 1 | 1 | 0 |  |
| 543 | anything | A1-A2 | migrated | 1 | 1 | 0 |  |
| 544 | to streamline | Pro | migrated | 1 | 1 | 0 |  |
| 545 | fully | B1-B2 | migrated | 1 | 1 | 0 |  |
| 546 | huge | A1-A2 | migrated | 1 | 1 | 0 |  |
| 547 | stage | B1-B2 | migrated | 1 | 1 | 0 |  |
| 548 | entire | B1-B2 | migrated | 1 | 1 | 0 |  |
| 549 | to close | A1-A2 | migrated | 1 | 1 | 0 |  |
| 550 | message | A1-A2 | migrated | 1 | 1 | 0 |  |
| 551 | crowd | A1-A2 | migrated | 1 | 1 | 0 |  |
| 552 | cause | B1-B2 | migrated | 1 | 1 | 0 |  |
| 553 | space | B1-B2 | migrated | 1 | 1 | 0 |  |
| 554 | corner | A1-A2 | migrated | 1 | 1 | 0 |  |
| 555 | quarter | A1-A2 | migrated | 1 | 1 | 0 |  |
| 556 | opportunity | B1-B2 | migrated | 1 | 1 | 0 |  |
| 557 | shift | B1-B2 | migrated | 1 | 1 | 0 |  |
| 558 | awareness | B2-C1 | migrated | 1 | 1 | 0 |  |
| 559 | baby | A1-A2 | migrated | 1 | 1 | 0 |  |
| 560 | quick | A1-A2 | migrated | 1 | 1 | 0 |  |
| 561 | to realize | B1-B2 | migrated | 1 | 1 | 0 |  |
| 562 | past | A1-A2 | migrated | 1 | 1 | 0 |  |
| 563 | to spread | B1-B2 | migrated | 1 | 1 | 0 |  |
| 564 | successful | B1-B2 | migrated | 1 | 1 | 0 |  |
| 565 | opinion | B1-B2 | migrated | 1 | 1 | 0 |  |
| 566 | driver | A1-A2 | migrated | 1 | 1 | 0 |  |
| 567 | single | B1-B2 | migrated | 1 | 1 | 0 |  |
| 568 | to sing | A1-A2 | migrated | 1 | 1 | 0 |  |
| 569 | ball | A1-A2 | migrated | 1 | 1 | 0 |  |
| 570 | benefit | B2-C1 | migrated | 1 | 1 | 0 |  |
| 571 | power | B1-B2 | migrated | 1 | 1 | 0 |  |
| 572 | to cry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 573 | doubt | B1-B2 | migrated | 1 | 1 | 0 |  |
| 574 | society | B1-B2 | migrated | 1 | 1 | 0 |  |
| 575 | introduction | B1-B2 | migrated | 1 | 1 | 0 |  |
| 576 | to help | A1-A2 | migrated | 1 | 1 | 0 |  |
| 577 | to propose | B2-C1 | migrated | 1 | 1 | 0 |  |
| 578 | north | A1-A2 | migrated | 1 | 1 | 0 |  |
| 579 | robust | B2-C1 | migrated | 1 | 1 | 0 |  |
| 580 | choice | B1-B2 | migrated | 1 | 1 | 0 |  |
| 581 | senior | B1-B2 | migrated | 1 | 1 | 0 |  |
| 582 | argument | B1-B2 | migrated | 1 | 1 | 0 |  |
| 583 | nothing | A1-A2 | migrated | 1 | 1 | 0 |  |
| 584 | to emerge | B2-C1 | migrated | 1 | 1 | 0 |  |
| 585 | decision | B1-B2 | migrated | 1 | 1 | 0 |  |
| 586 | adult | A1-A2 | migrated | 1 | 1 | 0 |  |
| 587 | map | A1-A2 | migrated | 1 | 1 | 0 |  |
| 588 | to save | A1-A2 | migrated | 1 | 1 | 0 |  |
| 589 | burden | B2-C1 | migrated | 1 | 1 | 0 |  |
| 590 | island | A1-A2 | migrated | 1 | 1 | 0 |  |
| 591 | to fly | A1-A2 | migrated | 1 | 1 | 0 |  |
| 592 | to return | B1-B2 | migrated | 1 | 1 | 0 |  |
| 593 | to survive | B1-B2 | migrated | 1 | 1 | 0 |  |
| 594 | common | B1-B2 | migrated | 1 | 1 | 0 |  |
| 595 | obviously | B1-B2 | migrated | 1 | 1 | 0 |  |
| 596 | flight | A1-A2 | migrated | 1 | 1 | 0 |  |
| 597 | advice | B1-B2 | migrated | 1 | 1 | 0 |  |
| 598 | concern | B2-C1 | migrated | 1 | 1 | 0 |  |
| 599 | left | A1-A2 | migrated | 1 | 1 | 0 |  |
| 600 | bill | A1-A2 | migrated | 1 | 1 | 0 |  |
| 601 | demand | B1-B2 | migrated | 1 | 1 | 0 |  |
| 602 | to solve | B1-B2 | migrated | 1 | 1 | 0 |  |
| 603 | matter | B1-B2 | migrated | 1 | 1 | 0 |  |
| 604 | to search | B1-B2 | migrated | 1 | 1 | 0 |  |
| 605 | neighbour | A1-A2 | migrated | 1 | 1 | 0 |  |
| 606 | to wait | A1-A2 | migrated | 1 | 1 | 0 |  |
| 607 | due | B1-B2 | migrated | 1 | 1 | 0 |  |
| 608 | background | B1-B2 | migrated | 1 | 1 | 0 |  |
| 609 | separate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 610 | knowledge | B1-B2 | migrated | 1 | 1 | 0 |  |
| 611 | traffic | A1-A2 | migrated | 1 | 1 | 0 |  |
| 612 | value | B1-B2 | migrated | 1 | 1 | 0 |  |
| 613 | speech | B1-B2 | migrated | 1 | 1 | 0 |  |
| 614 | tool | B1-B2 | migrated | 1 | 1 | 0 |  |
| 615 | to complete | B1-B2 | migrated | 1 | 1 | 0 |  |
| 616 | willing | B1-B2 | migrated | 1 | 1 | 0 |  |
| 617 | improvement | B1-B2 | migrated | 1 | 1 | 0 |  |
| 618 | dog | A1-A2 | migrated | 1 | 1 | 0 |  |
| 619 | contribution | B2-C1 | migrated | 1 | 1 | 0 |  |
| 620 | circumstance | B2-C1 | migrated | 1 | 1 | 0 |  |
| 621 | to lie | B1-B2 | migrated | 1 | 1 | 0 |  |
| 622 | throughout | B2-C1 | migrated | 1 | 1 | 0 |  |
| 623 | smoke | A1-A2 | migrated | 1 | 1 | 0 |  |
| 624 | to record | B1-B2 | migrated | 1 | 1 | 0 |  |
| 625 | skill | B1-B2 | migrated | 1 | 1 | 0 |  |
| 626 | rain | A1-A2 | migrated | 1 | 1 | 0 |  |
| 627 | to dress | A1-A2 | migrated | 1 | 1 | 0 |  |
| 628 | ground | B1-B2 | migrated | 1 | 1 | 0 |  |
| 629 | lesson | A1-A2 | migrated | 1 | 1 | 0 |  |
| 630 | profit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 631 | brain | A1-A2 | migrated | 1 | 1 | 0 |  |
| 632 | to stay | A1-A2 | migrated | 1 | 1 | 0 |  |
| 633 | animal | A1-A2 | migrated | 1 | 1 | 0 |  |
| 634 | funny | A1-A2 | migrated | 1 | 1 | 0 |  |
| 635 | to guess | A1-A2 | migrated | 1 | 1 | 0 |  |
| 636 | evidence | B2-C1 | migrated | 1 | 1 | 0 |  |
| 637 | to contribute | B2-C1 | migrated | 1 | 1 | 0 |  |
| 638 | to find | A1-A2 | migrated | 1 | 1 | 0 |  |
| 639 | fun | A1-A2 | migrated | 1 | 1 | 0 |  |
| 640 | failure | B1-B2 | migrated | 1 | 1 | 0 |  |
| 641 | to exist | B1-B2 | migrated | 1 | 1 | 0 |  |
| 642 | several | B1-B2 | migrated | 1 | 1 | 0 |  |
| 643 | schedule | B1-B2 | migrated | 1 | 1 | 0 |  |
| 644 | to protect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 645 | goal | B1-B2 | migrated | 1 | 1 | 0 |  |
| 646 | speaker | B1-B2 | migrated | 1 | 1 | 0 |  |
| 647 | similar | B1-B2 | migrated | 1 | 1 | 0 |  |
| 648 | disease | B1-B2 | migrated | 1 | 1 | 0 |  |
| 649 | to adopt | B2-C1 | migrated | 1 | 1 | 0 |  |
| 650 | to be swamped | Pro | migrated | 1 | 1 | 0 |  |
| 651 | light | A1-A2 | migrated | 1 | 1 | 0 |  |
| 652 | to combine | B1-B2 | migrated | 1 | 1 | 0 |  |
| 653 | balance | B1-B2 | migrated | 1 | 1 | 0 |  |
| 654 | to fight | A1-A2 | migrated | 1 | 1 | 0 |  |
| 655 | mountain | A1-A2 | migrated | 1 | 1 | 0 |  |
| 656 | damage | B1-B2 | migrated | 1 | 1 | 0 |  |
| 657 | to hide | A1-A2 | migrated | 1 | 1 | 0 |  |
| 658 | feature | B2-C1 | migrated | 1 | 1 | 0 |  |
| 659 | fine | A1-A2 | migrated | 1 | 1 | 0 |  |
| 660 | marriage | B1-B2 | migrated | 1 | 1 | 0 |  |
| 661 | hair | A1-A2 | migrated | 1 | 1 | 0 |  |
| 662 | to develop | B1-B2 | migrated | 1 | 1 | 0 |  |
| 663 | meal | A1-A2 | migrated | 1 | 1 | 0 |  |
| 664 | reason | B1-B2 | migrated | 1 | 1 | 0 |  |
| 665 | to reflect | B2-C1 | migrated | 1 | 1 | 0 |  |
| 666 | colleague | B1-B2 | migrated | 1 | 1 | 0 |  |
| 667 | former | B1-B2 | migrated | 1 | 1 | 0 |  |
| 668 | bag | A1-A2 | migrated | 1 | 1 | 0 |  |
| 669 | exercise | A1-A2 | migrated | 1 | 1 | 0 |  |
| 670 | to share | B1-B2 | migrated | 1 | 1 | 0 |  |
| 671 | to repeat | A1-A2 | migrated | 1 | 1 | 0 |  |
| 672 | wife | A1-A2 | migrated | 1 | 1 | 0 |  |
| 673 | useful | A1-A2 | migrated | 1 | 1 | 0 |  |
| 674 | equal | B1-B2 | migrated | 1 | 1 | 0 |  |
| 675 | impact | B2-C1 | migrated | 1 | 1 | 0 |  |
| 676 | to lose | A1-A2 | migrated | 1 | 1 | 0 |  |
| 677 | expression | B1-B2 | migrated | 1 | 1 | 0 |  |
| 678 | income | B1-B2 | migrated | 1 | 1 | 0 |  |
| 679 | to prepare | B1-B2 | migrated | 1 | 1 | 0 |  |
| 680 | plus | A1-A2 | migrated | 1 | 1 | 0 |  |
| 681 | real | A1-A2 | migrated | 1 | 1 | 0 |  |
| 682 | property | B1-B2 | migrated | 1 | 1 | 0 |  |
| 683 | extremely | B1-B2 | migrated | 1 | 1 | 0 |  |
| 684 | redundant | B2-C1 | migrated | 1 | 1 | 0 |  |
| 685 | to discuss | B1-B2 | migrated | 1 | 1 | 0 |  |
| 686 | owner | B1-B2 | migrated | 1 | 1 | 0 |  |
| 687 | previous | B1-B2 | migrated | 1 | 1 | 0 |  |
| 688 | challenge | B1-B2 | migrated | 1 | 1 | 0 |  |
| 689 | plane | A1-A2 | migrated | 1 | 1 | 0 |  |
| 690 | letter | A1-A2 | migrated | 1 | 1 | 0 |  |
| 691 | dark | A1-A2 | migrated | 1 | 1 | 0 |  |
| 692 | lady | A1-A2 | migrated | 1 | 1 | 0 |  |
| 693 | response | B1-B2 | migrated | 1 | 1 | 0 |  |
| 694 | insight | B2-C1 | migrated | 1 | 1 | 0 |  |
| 695 | duty | B1-B2 | migrated | 1 | 1 | 0 |  |
| 696 | to imagine | B1-B2 | migrated | 1 | 1 | 0 |  |
| 697 | attitude | B1-B2 | migrated | 1 | 1 | 0 |  |
| 698 | strength | B1-B2 | migrated | 1 | 1 | 0 |  |
| 699 | voice | A1-A2 | migrated | 1 | 1 | 0 |  |
| 700 | to earn | B1-B2 | migrated | 1 | 1 | 0 |  |
| 701 | to connect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 702 | subject | B1-B2 | migrated | 1 | 1 | 0 |  |
| 703 | to remember | A1-A2 | migrated | 1 | 1 | 0 |  |
| 704 | to arrange | B1-B2 | migrated | 1 | 1 | 0 |  |
| 705 | daughter | A1-A2 | migrated | 1 | 1 | 0 |  |
| 706 | to suppose | B1-B2 | migrated | 1 | 1 | 0 |  |
| 707 | payment | B1-B2 | migrated | 1 | 1 | 0 |  |
| 708 | behaviour | B1-B2 | migrated | 1 | 1 | 0 |  |
| 709 | post | B1-B2 | migrated | 1 | 1 | 0 |  |
| 710 | unfortunately | A1-A2 | migrated | 1 | 1 | 0 |  |
| 711 | half | A1-A2 | migrated | 1 | 1 | 0 |  |
| 712 | to apply | B1-B2 | migrated | 1 | 1 | 0 |  |
| 713 | brief | B1-B2 | migrated | 1 | 1 | 0 |  |
| 714 | newspaper | A1-A2 | migrated | 1 | 1 | 0 |  |
| 715 | bird | A1-A2 | migrated | 1 | 1 | 0 |  |
| 716 | to bring sb up to speed | Pro | migrated | 1 | 1 | 0 |  |
| 717 | to define | B2-C1 | migrated | 1 | 1 | 0 |  |
| 718 | to demonstrate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 719 | fire | A1-A2 | migrated | 1 | 1 | 0 |  |
| 720 | clear | B1-B2 | migrated | 1 | 1 | 0 |  |
| 721 | chapter | B1-B2 | migrated | 1 | 1 | 0 |  |
| 722 | conclusion | B1-B2 | migrated | 1 | 1 | 0 |  |
| 723 | priority | B2-C1 | migrated | 1 | 1 | 0 |  |
| 724 | secret | A1-A2 | migrated | 1 | 1 | 0 |  |
| 725 | to compare | B1-B2 | migrated | 1 | 1 | 0 |  |
| 726 | clock | A1-A2 | migrated | 1 | 1 | 0 |  |
| 727 | novel | B1-B2 | migrated | 1 | 1 | 0 |  |
| 728 | habit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 729 | future | A1-A2 | migrated | 1 | 1 | 0 |  |
| 730 | to burn | A1-A2 | migrated | 1 | 1 | 0 |  |
| 731 | everybody | A1-A2 | migrated | 1 | 1 | 0 |  |
| 732 | court | B1-B2 | migrated | 1 | 1 | 0 |  |
| 733 | pleasure | A1-A2 | migrated | 1 | 1 | 0 |  |
| 734 | to perform | B1-B2 | migrated | 1 | 1 | 0 |  |
| 735 | suggestion | B1-B2 | migrated | 1 | 1 | 0 |  |
| 736 | to forget | A1-A2 | migrated | 1 | 1 | 0 |  |
| 737 | store | A1-A2 | migrated | 1 | 1 | 0 |  |
| 738 | to gather | B1-B2 | migrated | 1 | 1 | 0 |  |
| 739 | memory | B1-B2 | migrated | 1 | 1 | 0 |  |
| 740 | ago | A1-A2 | migrated | 1 | 1 | 0 |  |
| 741 | mostly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 742 | relationship | B1-B2 | migrated | 1 | 1 | 0 |  |
| 743 | green | A1-A2 | migrated | 1 | 1 | 0 |  |
| 744 | earth | A1-A2 | migrated | 1 | 1 | 0 |  |
| 745 | poor | A1-A2 | migrated | 1 | 1 | 0 |  |
| 746 | desire | B1-B2 | migrated | 1 | 1 | 0 |  |
| 747 | song | A1-A2 | migrated | 1 | 1 | 0 |  |
| 748 | to remain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 749 | to promote | B1-B2 | migrated | 1 | 1 | 0 |  |
| 750 | to laugh | A1-A2 | migrated | 1 | 1 | 0 |  |
| 751 | object | B1-B2 | migrated | 1 | 1 | 0 |  |
| 752 | currently | B1-B2 | migrated | 1 | 1 | 0 |  |
| 753 | to reassure | B2-C1 | migrated | 1 | 1 | 0 |  |
| 754 | range | B2-C1 | migrated | 1 | 1 | 0 |  |
| 755 | to employ | B1-B2 | migrated | 1 | 1 | 0 |  |
| 756 | ring | A1-A2 | migrated | 1 | 1 | 0 |  |
| 757 | arm | A1-A2 | migrated | 1 | 1 | 0 |  |
| 758 | path | A1-A2 | migrated | 1 | 1 | 0 |  |
| 759 | among | B1-B2 | migrated | 1 | 1 | 0 |  |
| 760 | to discover | B1-B2 | migrated | 1 | 1 | 0 |  |
| 761 | topic | B1-B2 | migrated | 1 | 1 | 0 |  |
| 762 | environment | B1-B2 | migrated | 1 | 1 | 0 |  |
| 763 | heart | A1-A2 | migrated | 1 | 1 | 0 |  |
| 764 | beach | A1-A2 | migrated | 1 | 1 | 0 |  |
| 765 | dead | A1-A2 | migrated | 1 | 1 | 0 |  |
| 766 | to attract | B1-B2 | migrated | 1 | 1 | 0 |  |
| 767 | to win | A1-A2 | migrated | 1 | 1 | 0 |  |
| 768 | afternoon | A1-A2 | migrated | 1 | 1 | 0 |  |
| 769 | to engage | B2-C1 | migrated | 1 | 1 | 0 |  |
| 770 | source | B1-B2 | migrated | 1 | 1 | 0 |  |
| 771 | to understand | A1-A2 | migrated | 1 | 1 | 0 |  |
| 772 | powerful | B1-B2 | migrated | 1 | 1 | 0 |  |
| 773 | to prefer | B1-B2 | migrated | 1 | 1 | 0 |  |
| 774 | advantage | B1-B2 | migrated | 1 | 1 | 0 |  |
| 775 | flower | A1-A2 | migrated | 1 | 1 | 0 |  |
| 776 | employee | B1-B2 | migrated | 1 | 1 | 0 |  |
| 777 | to extend | B1-B2 | migrated | 1 | 1 | 0 |  |
| 778 | aid | B1-B2 | migrated | 1 | 1 | 0 |  |
| 779 | to involve | B1-B2 | migrated | 1 | 1 | 0 |  |
| 780 | shortage | B2-C1 | migrated | 1 | 1 | 0 |  |
| 781 | twice | A1-A2 | migrated | 1 | 1 | 0 |  |
| 782 | possibility | B1-B2 | migrated | 1 | 1 | 0 |  |
| 783 | simply | B1-B2 | migrated | 1 | 1 | 0 |  |
| 784 | fresh | A1-A2 | migrated | 1 | 1 | 0 |  |
| 785 | bottom line | Pro | migrated | 1 | 1 | 0 |  |
| 786 | direction | B1-B2 | migrated | 1 | 1 | 0 |  |
| 787 | delay | B1-B2 | migrated | 1 | 1 | 0 |  |
| 788 | period | B1-B2 | migrated | 1 | 1 | 0 |  |
| 789 | fast | A1-A2 | migrated | 1 | 1 | 0 |  |
| 790 | safety | B1-B2 | migrated | 1 | 1 | 0 |  |
| 791 | variety | B1-B2 | migrated | 1 | 1 | 0 |  |
| 792 | salary | B1-B2 | migrated | 1 | 1 | 0 |  |
| 793 | quiet | A1-A2 | migrated | 1 | 1 | 0 |  |
| 794 | daily | B1-B2 | migrated | 1 | 1 | 0 |  |
| 795 | insurance | B1-B2 | migrated | 1 | 1 | 0 |  |
| 796 | foreign | A1-A2 | migrated | 1 | 1 | 0 |  |
| 797 | type | A1-A2 | migrated | 1 | 1 | 0 |  |
| 798 | nurse | A1-A2 | migrated | 1 | 1 | 0 |  |
| 799 | clothes | A1-A2 | migrated | 1 | 1 | 0 |  |
| 800 | threat | B2-C1 | migrated | 1 | 1 | 0 |  |
| 801 | to divide | B1-B2 | migrated | 1 | 1 | 0 |  |
| 802 | surprise | A1-A2 | migrated | 1 | 1 | 0 |  |
| 803 | screen | A1-A2 | migrated | 1 | 1 | 0 |  |
| 804 | length | B1-B2 | migrated | 1 | 1 | 0 |  |
| 805 | to learn | A1-A2 | migrated | 1 | 1 | 0 |  |
| 806 | sound | A1-A2 | migrated | 1 | 1 | 0 |  |
| 807 | investigation | B2-C1 | migrated | 1 | 1 | 0 |  |
| 808 | to dance | A1-A2 | migrated | 1 | 1 | 0 |  |
| 809 | pretty | A1-A2 | migrated | 1 | 1 | 0 |  |
| 810 | package | B1-B2 | migrated | 1 | 1 | 0 |  |
| 811 | deadline | B1-B2 | migrated | 1 | 1 | 0 |  |
| 812 | completely | B1-B2 | migrated | 1 | 1 | 0 |  |
| 813 | somewhere | A1-A2 | migrated | 1 | 1 | 0 |  |
| 814 | recently | B1-B2 | migrated | 1 | 1 | 0 |  |
| 815 | to expand | B1-B2 | migrated | 1 | 1 | 0 |  |
| 816 | responsibility | B1-B2 | migrated | 1 | 1 | 0 |  |
| 817 | moment | A1-A2 | migrated | 1 | 1 | 0 |  |
| 818 | to jump | A1-A2 | migrated | 1 | 1 | 0 |  |
| 819 | to procrastinate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 820 | sister | A1-A2 | migrated | 1 | 1 | 0 |  |
| 821 | weapon | B1-B2 | migrated | 1 | 1 | 0 |  |
| 822 | to affect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 823 | trend | B2-C1 | migrated | 1 | 1 | 0 |  |
| 824 | relatively | B1-B2 | migrated | 1 | 1 | 0 |  |
| 825 | rock | A1-A2 | migrated | 1 | 1 | 0 |  |
| 826 | sale | B1-B2 | migrated | 1 | 1 | 0 |  |
| 827 | host | B1-B2 | migrated | 1 | 1 | 0 |  |
| 828 | recent | B1-B2 | migrated | 1 | 1 | 0 |  |
| 829 | dream | A1-A2 | migrated | 1 | 1 | 0 |  |
| 830 | winter | A1-A2 | migrated | 1 | 1 | 0 |  |
| 831 | effort | B1-B2 | migrated | 1 | 1 | 0 |  |
| 832 | wealth | B2-C1 | migrated | 1 | 1 | 0 |  |
| 833 | broad | B1-B2 | migrated | 1 | 1 | 0 |  |
| 834 | nor | B2-C1 | migrated | 1 | 1 | 0 |  |
| 835 | to relate | B1-B2 | migrated | 1 | 1 | 0 |  |
| 836 | to tire | B1-B2 | migrated | 1 | 1 | 0 |  |
| 837 | further | B1-B2 | migrated | 1 | 1 | 0 |  |
| 838 | easily | A1-A2 | migrated | 1 | 1 | 0 |  |
| 839 | spring | A1-A2 | migrated | 1 | 1 | 0 |  |
| 840 | to teach | A1-A2 | migrated | 1 | 1 | 0 |  |
| 841 | to miss | A1-A2 | migrated | 1 | 1 | 0 |  |
| 842 | spirit | B1-B2 | migrated | 1 | 1 | 0 |  |
| 843 | garden | A1-A2 | migrated | 1 | 1 | 0 |  |
| 844 | consequence | B1-B2 | migrated | 1 | 1 | 0 |  |
| 845 | lunch | A1-A2 | migrated | 1 | 1 | 0 |  |
| 846 | general | B1-B2 | migrated | 1 | 1 | 0 |  |
| 847 | ahead | B1-B2 | migrated | 1 | 1 | 0 |  |
| 848 | actual | B1-B2 | migrated | 1 | 1 | 0 |  |
| 849 | private | B1-B2 | migrated | 1 | 1 | 0 |  |
| 850 | pool | A1-A2 | migrated | 1 | 1 | 0 |  |
| 851 | to cross | A1-A2 | migrated | 1 | 1 | 0 |  |
| 852 | hands-on | Pro | migrated | 1 | 1 | 0 |  |
| 853 | battle | B1-B2 | migrated | 1 | 1 | 0 |  |
| 854 | everyone | A1-A2 | migrated | 1 | 1 | 0 |  |
| 855 | weight | A1-A2 | migrated | 1 | 1 | 0 |  |
| 856 | cash | A1-A2 | migrated | 1 | 1 | 0 |  |
| 857 | to appear | B1-B2 | migrated | 1 | 1 | 0 |  |
| 858 | mood | B2-C1 | migrated | 1 | 1 | 0 |  |
| 859 | award | B1-B2 | migrated | 1 | 1 | 0 |  |
| 860 | proposal | B1-B2 | migrated | 1 | 1 | 0 |  |
| 861 | to worry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 862 | coach | B1-B2 | migrated | 1 | 1 | 0 |  |
| 863 | available | B1-B2 | migrated | 1 | 1 | 0 |  |
| 864 | conversation | A1-A2 | migrated | 1 | 1 | 0 |  |
| 865 | strange | A1-A2 | migrated | 1 | 1 | 0 |  |
| 866 | full | A1-A2 | migrated | 1 | 1 | 0 |  |
| 867 | summer | A1-A2 | migrated | 1 | 1 | 0 |  |
| 868 | possibly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 869 | shape | B1-B2 | migrated | 1 | 1 | 0 |  |
| 870 | guilt | B2-C1 | migrated | 1 | 1 | 0 |  |
| 871 | accident | A1-A2 | migrated | 1 | 1 | 0 |  |
| 872 | to study | A1-A2 | migrated | 1 | 1 | 0 |  |
| 873 | sea | A1-A2 | migrated | 1 | 1 | 0 |  |
| 874 | to represent | B1-B2 | migrated | 1 | 1 | 0 |  |
| 875 | perhaps | B1-B2 | migrated | 1 | 1 | 0 |  |
| 876 | immediately | B1-B2 | migrated | 1 | 1 | 0 |  |
| 877 | reliable | B1-B2 | migrated | 1 | 1 | 0 |  |
| 878 | key | A1-A2 | migrated | 1 | 1 | 0 |  |
| 879 | to smile | A1-A2 | migrated | 1 | 1 | 0 |  |
| 880 | pressure | B2-C1 | migrated | 1 | 1 | 0 |  |
| 881 | to add | A1-A2 | migrated | 1 | 1 | 0 |  |
| 882 | to replace | B1-B2 | migrated | 1 | 1 | 0 |  |
| 883 | inside | A1-A2 | migrated | 1 | 1 | 0 |  |
| 884 | accountable | B2-C1 | migrated | 1 | 1 | 0 |  |
| 885 | judge | B1-B2 | migrated | 1 | 1 | 0 |  |
| 886 | responsible | B1-B2 | migrated | 1 | 1 | 0 |  |
| 887 | to contain | B1-B2 | migrated | 1 | 1 | 0 |  |
| 888 | suddenly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 889 | to pass | A1-A2 | migrated | 1 | 1 | 0 |  |
| 890 | patience | B2-C1 | migrated | 1 | 1 | 0 |  |
| 891 | favourite | A1-A2 | migrated | 1 | 1 | 0 |  |
| 892 | to notice | B1-B2 | migrated | 1 | 1 | 0 |  |
| 893 | to read | A1-A2 | migrated | 1 | 1 | 0 |  |
| 894 | difficulty | B1-B2 | migrated | 1 | 1 | 0 |  |
| 895 | to produce | B1-B2 | migrated | 1 | 1 | 0 |  |
| 896 | nature | A1-A2 | migrated | 1 | 1 | 0 |  |
| 897 | purchase | B1-B2 | migrated | 1 | 1 | 0 |  |
| 898 | reasonable | B1-B2 | migrated | 1 | 1 | 0 |  |
| 899 | significant | B2-C1 | migrated | 1 | 1 | 0 |  |
| 900 | to shoot | B1-B2 | migrated | 1 | 1 | 0 |  |
| 901 | exactly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 902 | to sell | A1-A2 | migrated | 1 | 1 | 0 |  |
| 903 | to announce | B1-B2 | migrated | 1 | 1 | 0 |  |
| 904 | suitable | B1-B2 | migrated | 1 | 1 | 0 |  |
| 905 | worker | A1-A2 | migrated | 1 | 1 | 0 |  |
| 906 | independent | B1-B2 | migrated | 1 | 1 | 0 |  |
| 907 | to fine-tune | Pro | migrated | 1 | 1 | 0 |  |
| 908 | law | B1-B2 | migrated | 1 | 1 | 0 |  |
| 909 | to recommend | B1-B2 | migrated | 1 | 1 | 0 |  |
| 910 | whatever | B1-B2 | migrated | 1 | 1 | 0 |  |
| 911 | sufficient | B2-C1 | migrated | 1 | 1 | 0 |  |
| 912 | survey | B1-B2 | migrated | 1 | 1 | 0 |  |
| 913 | to write | A1-A2 | migrated | 1 | 1 | 0 |  |
| 914 | necessary | B1-B2 | migrated | 1 | 1 | 0 |  |
| 915 | to stick | B1-B2 | migrated | 1 | 1 | 0 |  |
| 916 | everything | A1-A2 | migrated | 1 | 1 | 0 |  |
| 917 | aware | B1-B2 | migrated | 1 | 1 | 0 |  |
| 918 | request | B1-B2 | migrated | 1 | 1 | 0 |  |
| 919 | growth | B1-B2 | migrated | 1 | 1 | 0 |  |
| 920 | efficient | B2-C1 | migrated | 1 | 1 | 0 |  |
| 921 | rich | A1-A2 | migrated | 1 | 1 | 0 |  |
| 922 | to cover | B1-B2 | migrated | 1 | 1 | 0 |  |
| 923 | influence | B1-B2 | migrated | 1 | 1 | 0 |  |
| 924 | wind | A1-A2 | migrated | 1 | 1 | 0 |  |
| 925 | confident | B1-B2 | migrated | 1 | 1 | 0 |  |
| 926 | relevant | B2-C1 | migrated | 1 | 1 | 0 |  |
| 927 | none | B1-B2 | migrated | 1 | 1 | 0 |  |
| 928 | respect | B1-B2 | migrated | 1 | 1 | 0 |  |
| 929 | paper | A1-A2 | migrated | 1 | 1 | 0 |  |
| 930 | exchange | B1-B2 | migrated | 1 | 1 | 0 |  |
| 931 | to overthink | B2-C1 | migrated | 1 | 1 | 0 |  |
| 932 | various | B1-B2 | migrated | 1 | 1 | 0 |  |
| 933 | famous | A1-A2 | migrated | 1 | 1 | 0 |  |
| 934 | to listen | A1-A2 | migrated | 1 | 1 | 0 |  |
| 935 | position | B1-B2 | migrated | 1 | 1 | 0 |  |
| 936 | blood | A1-A2 | migrated | 1 | 1 | 0 |  |
| 937 | attempt | B1-B2 | migrated | 1 | 1 | 0 |  |
| 938 | comfortable | B1-B2 | migrated | 1 | 1 | 0 |  |
| 939 | appropriate | B2-C1 | migrated | 1 | 1 | 0 |  |
| 940 | relieved | B2-C1 | migrated | 1 | 1 | 0 |  |
| 941 | son | A1-A2 | migrated | 1 | 1 | 0 |  |
| 942 | to count | A1-A2 | migrated | 1 | 1 | 0 |  |
| 943 | near | A1-A2 | migrated | 1 | 1 | 0 |  |
| 944 | convenient | B1-B2 | migrated | 1 | 1 | 0 |  |
| 945 | writer | A1-A2 | migrated | 1 | 1 | 0 |  |
| 946 | simple | A1-A2 | migrated | 1 | 1 | 0 |  |
| 947 | grateful | B2-C1 | migrated | 1 | 1 | 0 |  |
| 948 | to invite | A1-A2 | migrated | 1 | 1 | 0 |  |
| 949 | human | B1-B2 | migrated | 1 | 1 | 0 |  |
| 950 | bed | A1-A2 | migrated | 1 | 1 | 0 |  |
| 951 | to mix | A1-A2 | migrated | 1 | 1 | 0 |  |
| 952 | to hear | A1-A2 | migrated | 1 | 1 | 0 |  |
| 953 | to sign off on | Pro | migrated | 1 | 1 | 0 |  |
| 954 | correct | A1-A2 | migrated | 1 | 1 | 0 |  |
| 955 | to hit | A1-A2 | migrated | 1 | 1 | 0 |  |
| 956 | situation | B1-B2 | migrated | 1 | 1 | 0 |  |
| 957 | to beat | B1-B2 | migrated | 1 | 1 | 0 |  |
| 958 | obvious | B1-B2 | migrated | 1 | 1 | 0 |  |
| 959 | to establish | B2-C1 | migrated | 1 | 1 | 0 |  |
| 960 | to copy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 961 | anxious | B2-C1 | migrated | 1 | 1 | 0 |  |
| 962 | staff | B1-B2 | migrated | 1 | 1 | 0 |  |
| 963 | to handle | B1-B2 | migrated | 1 | 1 | 0 |  |
| 964 | indeed | B2-C1 | migrated | 1 | 1 | 0 |  |
| 965 | curious | B1-B2 | migrated | 1 | 1 | 0 |  |
| 966 | glass | A1-A2 | migrated | 1 | 1 | 0 |  |
| 967 | size | A1-A2 | migrated | 1 | 1 | 0 |  |
| 968 | trial | B1-B2 | migrated | 1 | 1 | 0 |  |
| 969 | activity | B1-B2 | migrated | 1 | 1 | 0 |  |
| 970 | cautious | B2-C1 | migrated | 1 | 1 | 0 |  |
| 971 | to ride | A1-A2 | migrated | 1 | 1 | 0 |  |
| 972 | addition | B1-B2 | migrated | 1 | 1 | 0 |  |
| 973 | to call | A1-A2 | migrated | 1 | 1 | 0 |  |
| 974 | event | B1-B2 | migrated | 1 | 1 | 0 |  |
| 975 | to determine | B2-C1 | migrated | 1 | 1 | 0 |  |
| 976 | self-conscious | B2-C1 | migrated | 1 | 1 | 0 |  |
| 977 | likely | B1-B2 | migrated | 1 | 1 | 0 |  |
| 978 | to fail | B1-B2 | migrated | 1 | 1 | 0 |  |
| 979 | special | A1-A2 | migrated | 1 | 1 | 0 |  |
| 980 | player | A1-A2 | migrated | 1 | 1 | 0 |  |
| 981 | challenging | B2-C1 | migrated | 1 | 1 | 0 |  |
| 982 | average | B1-B2 | migrated | 1 | 1 | 0 |  |
| 983 | to enter | B1-B2 | migrated | 1 | 1 | 0 |  |
| 984 | demanding | B2-C1 | migrated | 1 | 1 | 0 |  |
| 985 | to send | A1-A2 | migrated | 1 | 1 | 0 |  |
| 986 | to occur | B2-C1 | migrated | 1 | 1 | 0 |  |
| 987 | to pitch | Pro | migrated | 1 | 1 | 0 |  |
| 988 | essential | B1-B2 | migrated | 1 | 1 | 0 |  |
| 989 | alone | A1-A2 | migrated | 1 | 1 | 0 |  |
| 990 | overwhelmed | B2-C1 | migrated | 1 | 1 | 0 |  |
| 991 | disappointed | B1-B2 | migrated | 1 | 1 | 0 |  |
| 992 | straightforward | B2-C1 | migrated | 1 | 1 | 0 |  |
| 993 | to bring | A1-A2 | migrated | 1 | 1 | 0 |  |
| 994 | embarrassed | B1-B2 | migrated | 1 | 1 | 0 |  |
| 995 | versatile | B2-C1 | migrated | 1 | 1 | 0 |  |
| 996 | sophisticated | B2-C1 | migrated | 1 | 1 | 0 |  |
| 997 | exhausted | B1-B2 | migrated | 1 | 1 | 0 |  |
| 998 | specific | B2-C1 | migrated | 1 | 1 | 0 |  |
| 999 | to put | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1000 | upset | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1001 | vague | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1002 | to justify | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1003 | rude | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1004 | valid | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1005 | to start | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1006 | polite | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1007 | vivid | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1008 | tedious | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1009 | patient | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1010 | workload | Pro | migrated | 1 | 1 | 0 |  |
| 1011 | tough | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1012 | to finish | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1013 | however | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1014 | to sync up | Pro | migrated | 1 | 1 | 0 |  |
| 1015 | to proceed | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1016 | genuine | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1017 | therefore | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1018 | to follow up | Pro | migrated | 1 | 1 | 0 |  |
| 1019 | generous | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1020 | to stop | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1021 | otherwise | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1022 | to touch base | Pro | migrated | 1 | 1 | 0 |  |
| 1023 | inevitable | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1024 | although | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1025 | to loop in | Pro | migrated | 1 | 1 | 0 |  |
| 1026 | to try | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1027 | unless | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1028 | to push back | Pro | migrated | 1 | 1 | 0 |  |
| 1029 | eager | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1030 | actually | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1031 | to wrap up | Pro | migrated | 1 | 1 | 0 |  |
| 1032 | fluent | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1033 | to use | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1034 | probably | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1035 | to walk sb through | Pro | migrated | 1 | 1 | 0 |  |
| 1036 | awkward | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1037 | nearly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1038 | to run late | Pro | migrated | 1 | 1 | 0 |  |
| 1039 | complicated | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1040 | to feel | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1041 | hardly | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1042 | to be on track | Pro | migrated | 1 | 1 | 0 |  |
| 1043 | lately | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1044 | to be on hold | Pro | migrated | 1 | 1 | 0 |  |
| 1045 | moreover | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1046 | to leave | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1047 | instead | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1048 | heads-up | Pro | migrated | 1 | 1 | 0 |  |
| 1049 | whereas | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1050 | anyway | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1051 | ASAP | Pro | migrated | 1 | 1 | 0 |  |
| 1052 | despite | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1053 | to arrive | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1054 | according to | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1055 | FYI | Pro | migrated | 1 | 1 | 0 |  |
| 1056 | meanwhile | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1057 | to make a decision | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1058 | ETA | Pro | migrated | 1 | 1 | 0 |  |
| 1059 | apparently | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1060 | to meet | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1061 | to pay attention | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1062 | bandwidth | Pro | migrated | 1 | 1 | 0 |  |
| 1063 | approximately | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1064 | to take part in | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1065 | to take ownership | Pro | migrated | 1 | 1 | 0 |  |
| 1066 | gradually | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1067 | to visit | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1068 | to take place | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1069 | to raise a concern | Pro | migrated | 1 | 1 | 0 |  |
| 1070 | thoroughly | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1071 | to keep in touch | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1072 | to get back to sb | Pro | migrated | 1 | 1 | 0 |  |
| 1073 | definitely | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1074 | to travel | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1075 | to be about to | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1076 | to be up for | Pro | migrated | 1 | 1 | 0 |  |
| 1077 | deliberately | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1078 | to be used to | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1079 | on my end | Pro | migrated | 1 | 1 | 0 |  |
| 1080 | regardless | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1081 | to walk | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1082 | worth it | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1083 | it's a known issue | Pro | migrated | 1 | 1 | 0 |  |
| 1084 | as long as | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1085 | it depends | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1086 | good catch | Pro | migrated | 1 | 1 | 0 |  |
| 1087 | as soon as | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1088 | to run | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1089 | no wonder | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1090 | good call | Pro | migrated | 1 | 1 | 0 |  |
| 1091 | to make ends meet | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1092 | by the way | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1093 | to make a point | Pro | migrated | 1 | 1 | 0 |  |
| 1094 | to keep an eye on | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1095 | to drive | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1096 | on purpose | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1097 | to get the hang of | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1098 | in advance | B1-B2 | migrated | 1 | 1 | 0 |  |
| 1099 | to prioritize | Pro | migrated | 1 | 1 | 0 |  |
| 1100 | to break the ice | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1101 | to play | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1102 | to delegate | Pro | migrated | 1 | 1 | 0 |  |
| 1103 | to be on the same page | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1104 | to negotiate | Pro | migrated | 1 | 1 | 0 |  |
| 1105 | to be on the safe side | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1106 | to cook | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1107 | to keep sb posted | Pro | migrated | 1 | 1 | 0 |  |
| 1108 | to cut corners | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1109 | no worries | Pro | migrated | 1 | 1 | 0 |  |
| 1110 | to call it a day | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1111 | to clean | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1112 | to brainstorm | Pro | migrated | 1 | 1 | 0 |  |
| 1113 | under the weather | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1114 | deliverable | Pro | migrated | 1 | 1 | 0 |  |
| 1115 | over the moon | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1116 | to wash | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1117 | milestone | Pro | migrated | 1 | 1 | 0 |  |
| 1118 | out of the blue | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1119 | once in a blue moon | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1120 | to sit | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1121 | to ship | Pro | migrated | 1 | 1 | 0 |  |
| 1122 | a piece of cake | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1123 | a pain in the neck | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1124 | to stand | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1125 | no big deal | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1126 | to be up to | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1127 | to wake up | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1128 | to be fed up with | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1129 | to be keen on | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1130 | to get up | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1131 | it's on me | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1132 | fair enough | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1133 | to turn on | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1134 | that makes two of us | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1135 | not my cup of tea | B2-C1 | migrated | 1 | 1 | 0 |  |
| 1136 | to turn off | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1137 | to look for | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1138 | to show | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1139 | to change | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1140 | to choose | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1141 | to decide | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1142 | to move | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1143 | to cost | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1144 | to spend | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1145 | to rest | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1146 | to hope | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1147 | to believe | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1148 | to happen | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1149 | to agree | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1150 | time | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1151 | day | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1152 | week | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1153 | year | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1154 | morning | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1155 | evening | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1156 | weekend | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1157 | people | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1158 | man | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1159 | woman | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1160 | child | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1161 | friend | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1162 | family | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1163 | mother | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1164 | father | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1165 | home | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1166 | house | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1167 | room | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1168 | kitchen | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1169 | door | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1170 | window | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1171 | table | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1172 | car | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1173 | bus | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1174 | train | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1175 | street | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1176 | city | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1177 | country | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1178 | money | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1179 | price | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1180 | shop | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1181 | job | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1182 | food | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1183 | water | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1184 | breakfast | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1185 | dinner | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1186 | question | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1187 | problem | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1188 | idea | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1189 | phone | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1190 | name | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1191 | weather | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1192 | holiday | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1193 | trip | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1194 | ticket | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1195 | place | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1196 | way | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1197 | thing | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1198 | life | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1199 | world | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1200 | health | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1201 | good | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1202 | bad | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1203 | big | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1204 | small | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1205 | new | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1206 | old | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1207 | young | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1208 | long | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1209 | short | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1210 | easy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1211 | difficult | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1212 | hot | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1213 | cold | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1214 | warm | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1215 | cheap | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1216 | expensive | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1217 | free | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1218 | busy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1219 | tired | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1220 | hungry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1221 | happy | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1222 | sad | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1223 | beautiful | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1224 | interesting | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1225 | important | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1226 | ready | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1227 | sure | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1228 | right | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1229 | wrong | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1230 | different | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1231 | same | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1232 | always | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1233 | never | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1234 | often | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1235 | sometimes | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1236 | usually | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1237 | already | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1238 | still | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1239 | again | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1240 | soon | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1241 | now | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1242 | today | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1243 | tomorrow | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1244 | yesterday | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1245 | here | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1246 | there | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1247 | very | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1248 | too | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1249 | maybe | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1250 | together | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1251 | thank you | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1252 | please | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1253 | you're welcome | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1254 | excuse me | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1255 | sorry | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1256 | of course | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1257 | see you | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1258 | good luck | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1259 | never mind | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1260 | How are you? | A1-A2 | migrated | 1 | 1 | 0 |  |
| 1261 | What time is it? | A1-A2 | migrated | 1 | 1 | 0 |  |

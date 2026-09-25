| Run | race vs/s (x) | n | GameThread % | GsWorker % | main % | other % | latch ms/frame | upload ms/frame | present/readback/copy ms (backend avg) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-1x | 14.16 (0.236x) | 9 | 90 | 11 | 5 | 9 | 5.40 | 0.24 | 4.15258/3.30219/0.0643583 |
| B-4xhr-sync | 13.24 (0.221x) | 10 | 89 | 12 | 6 | 10 | 7.74 | 0.62 | 6.29906/5.02246/0.245718 |
| C-4xhr-zc-sync | 13.33 (0.222x) | 9 | 81 | 9 | 3 | 5 | 13.93 | 0.18 | 7.58612/0/0 |

# What an SSX 3 location holds besides terrain

Date: 2026-09-10. Output of `tools/location_inventory.py ... inventory ERA5 A
A_ARA1` (a race, a hub, a connector). Kind names are SSX-Library's labels and
are unverified in play. `n` is resources per group, `memsize` the SDB group
memsize word (kinds 0–12), so `bytes-memsize` is what kinds 13+ add.

Reading for "replace a run's terrain": a race location is nine groups of which
eight hold only textures and lightmaps (kinds 9 and 10, track 255) and one
holds everything else. Replacing terrain means regenerating kinds 1 (patches)
and 12 (collision) and, for a playable race, 8 (splines: rails and paths), 14
(AI paths), 3 (instances of models) and whatever kinds 13–18 script the start,
finish and cameras. Textures and lightmaps can stay as they are, which is what
gari-003 already relies on.


## ERA5: groups 140..148, spatial 155..169, tail words [0, 0, 0, 0]
| group | n    | bytes   | memsize | bytes-memsize | tracks | kinds                                                                                                         |
|-------|------|---------|---------|---------------|--------|---------------------------------------------------------------------------------------------------------------|
| 140   | 81   | 740392  | 740392  | 0             | [255]  | 9:74 10:7                                                                                                     |
| 141   | 56   | 728400  | 728400  | 0             | [255]  | 9:50 10:6                                                                                                     |
| 142   | 67   | 743160  | 743160  | 0             | [255]  | 9:64 10:3                                                                                                     |
| 143   | 65   | 746280  | 746280  | 0             | [255]  | 9:59 10:6                                                                                                     |
| 144   | 67   | 780776  | 780776  | 0             | [255]  | 9:65 10:2                                                                                                     |
| 145   | 64   | 769728  | 769728  | 0             | [255]  | 9:61 10:3                                                                                                     |
| 146   | 53   | 729832  | 729832  | 0             | [255]  | 9:48 10:5                                                                                                     |
| 147   | 63   | 726280  | 726280  | 0             | [255]  | 9:60 10:3                                                                                                     |
| 148   | 6175 | 4365701 | 3921076 | 444625        | [45]   | 0:128 1:1739 2:757 3:2803 4:7 5:7 6:241 7:131 8:138 11:12 12:200 13:1 14:3 15:1 16:1 17:1 18:1 20:2 21:1 22:1 |
| kind | name              | count | bytes(+hdr) | sdb loc count |
|------|-------------------|-------|-------------|---------------|
| 0    | material          | 128   | 3596        | 128           |
| 1    | patch             | 1739  | 765160      | 1739          |
| 2    | model(MDR)        | 757   | 1340712     | 757           |
| 3    | instance          | 2803  | 1423704     | 2803          |
| 4    | particle model    | 7     | 2408        | 7             |
| 5    | particle instance | 7     | 1064        | 7             |
| 6    | light             | 241   | 28920       | 241           |
| 7    | halo              | 131   | 11528       | 131           |
| 8    | spline            | 138   | 126384      | 138           |
| 9    | texture(SSH)      | 481   | 4354456     | 0             |
| 10   | lightmap(SSH)     | 35    | 1610392     | 0             |
| 11   | vis curtain       | 12    | 2592        | 12            |
| 12   | collision         | 200   | 215008      | 200           |
| 13   | sound trigger?    | 1     | 34329       | 1             |
| 14   | AI paths(AIP)     | 3     | 66840       | 3             |
| 15   | world painter?    | 1     | 14920       | 1             |
| 16   | scripts?          | 1     | 116196      | 1             |
| 17   | camera trigger?   | 1     | 7776        | 1             |
| 18   | NIS table         | 1     | 80          | 1             |
| 20   | audio bank        | 2     | 187472      | 2             |
| 21   | radar?            | 1     | 7084        | 1             |
| 22   | avalanche anim    | 1     | 9928        | 1             |

## A: groups 1..2, spatial 1..1, tail words [0, 0, 0, 0]
| group | n    | bytes   | memsize | bytes-memsize | tracks | kinds                                                                              |
|-------|------|---------|---------|---------------|--------|------------------------------------------------------------------------------------|
| 1     | 66   | 769280  | 769280  | 0             | [255]  | 9:62 10:4                                                                          |
| 2     | 1209 | 1338393 | 1103788 | 234605        | [1]    | 0:57 1:291 2:166 3:566 6:8 8:29 11:4 12:77 13:1 14:3 15:1 16:1 17:1 18:1 20:2 22:1 |
| kind | name            | count | bytes(+hdr) | sdb loc count |
|------|-----------------|-------|-------------|---------------|
| 0    | material        | 57    | 1596        | 57            |
| 1    | patch           | 291   | 128040      | 291           |
| 2    | model(MDR)      | 166   | 475344      | 166           |
| 3    | instance        | 566   | 366752      | 566           |
| 6    | light           | 8     | 960         | 8             |
| 8    | spline          | 29    | 23080       | 29            |
| 9    | texture(SSH)    | 62    | 506592      | 0             |
| 10   | lightmap(SSH)   | 4     | 262688      | 0             |
| 11   | vis curtain     | 4     | 864         | 4             |
| 12   | collision       | 77    | 107152      | 77            |
| 13   | sound trigger?  | 1     | 11313       | 1             |
| 14   | AI paths(AIP)   | 3     | 22640       | 3             |
| 15   | world painter?  | 1     | 4364        | 1             |
| 16   | scripts?        | 1     | 17404       | 1             |
| 17   | camera trigger? | 1     | 108         | 1             |
| 18   | NIS table       | 1     | 80          | 1             |
| 20   | audio bank      | 2     | 178688      | 2             |
| 22   | avalanche anim  | 1     | 8           | 1             |

## A_ARA1: groups 5..6, spatial 3..3, tail words [0, 0, 0, 0]
| group | n   | bytes  | memsize | bytes-memsize | tracks | kinds                                                                  |
|-------|-----|--------|---------|---------------|--------|------------------------------------------------------------------------|
| 5     | 37  | 338072 | 338072  | 0             | [255]  | 9:34 10:3                                                              |
| 6     | 530 | 524633 | 510260  | 14373         | [3]    | 0:26 1:132 2:66 3:240 6:2 8:7 12:47 13:1 14:3 15:1 16:1 18:1 20:2 22:1 |
| kind | name           | count | bytes(+hdr) | sdb loc count |
|------|----------------|-------|-------------|---------------|
| 0    | material       | 26    | 728         | 26            |
| 1    | patch          | 132   | 58080       | 132           |
| 2    | model(MDR)     | 66    | 222624      | 66            |
| 3    | instance       | 240   | 156848      | 240           |
| 6    | light          | 2     | 240         | 2             |
| 8    | spline         | 7     | 5000        | 7             |
| 9    | texture(SSH)   | 34    | 300800      | 0             |
| 10   | lightmap(SSH)  | 3     | 37272       | 0             |
| 12   | collision      | 47    | 66740       | 47            |
| 13   | sound trigger? | 1     | 4389        | 1             |
| 14   | AI paths(AIP)  | 3     | 1256        | 3             |
| 15   | world painter? | 1     | 3040        | 1             |
| 16   | scripts?       | 1     | 5584        | 1             |
| 18   | NIS table      | 1     | 80          | 1             |
| 20   | audio bank     | 2     | 16          | 2             |
| 22   | avalanche anim | 1     | 8           | 1             |

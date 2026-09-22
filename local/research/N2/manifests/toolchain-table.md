# N2 toolchain table (bytesize WSL Ubuntu 24.04.1, ~/n2, user-local, no sudo)

WSL baseline: Ubuntu 24.04.1 LTS, 20 cores, 896 GB free, 9 GB RAM,
cmake 3.28.3 (host), ninja 1.11.1, git 2.43.0, python 3.12.3, no Java, no unzip
(python3 zipfile used for all unzips; exec bits re-applied after unzip).

## Direct downloads (URL + sha256, all verified at fetch)

| # | Component | Version | URL | sha256 | Bytes |
|---|---|---|---|---|---|
| T1 | Eclipse Temurin JDK 17 | jdk-17.0.20.1+1 | https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.20.1%2B1/OpenJDK17U-jdk_x64_linux_hotspot_17.0.20.1_1.tar.gz | `3808d1d15e3ec6bd5b84057fb5d84c33d8a1536a258146bcea2e603fc726e08e` | 193252603 |
| T2 | Android cmdline-tools (linux) | 13114758 | https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip | `7ec965280a073311c339e571cd5de778b9975026cfcbe79f2b1cdcb1e15317ee` | (zip) |
| T3 | Gradle distribution | 8.9 | https://services.gradle.org/distributions/gradle-8.9-bin.zip | `d725d707bfabd4dfdc958c624003b3c80accc03f7037b5122c4b1d0ef15cecab` | 136114148 |

Notes:
- T1 URL + sha came from `api.adoptium.net/v3/assets/latest/17/hotspot`
  metadata (`~/n2/logs/temurin-17-meta.json`), verified with `sha256sum -c`.
  `java -version`: 17.0.20.1 Temurin-17.0.20.1+1.
- T2: first candidate 13114758 accepted (fallback 11076708 unused); zip
  integrity via python zipfile `testzip`; unpacked to
  `android-sdk/cmdline-tools/latest/` (proper nested layout).
- T3: published `.sha256` sidecar is a bare hash (no filename), verified by
  manual compare + `sha256sum -c` on a reconstructed line. `gradle --version`:
  8.9 (revision d536ef3). Wrapper generated per fork README Option B
  (`gradle wrapper --gradle-version 8.9`, BUILD SUCCESSFUL), wrapper's own
  8.9 re-download went to `~/n2/gradle-home`.

## sdkmanager packages (sdkmanager 19.0, licenses accepted)

| Package | Version | Location |
|---|---|---|
| platforms;android-34 | 3 (platform-34-ext7_r03) | platforms/android-34 |
| build-tools;34.0.0 | 34.0.0 | build-tools/34.0.0 |
| ndk;28.2.13676358 | r28c, clang 19.0.1 (r530567e) | ndk/28.2.13676358 |
| cmake;3.22.1 | 3.22.1-g37088a8 | cmake/3.22.1 |

SDK total on disk: 2.7 GB. No platform-tools (no adb: no device in N2).

## Fork checkout (Mission 1)

- Clone: `https://github.com/brad-richardson/PS2Recomp.git` branch `ssx3`
- Branch HEAD at clone == pin `3adc0478b6d2260acdd28a249466f2eef9a20176`
  (2026-09-21 15:33:21 -0400, "[E18] Deliver non-stream MPEG input callbacks")
- Checked out detached at the pin; `git status` clean at checkout
  (later: only generated `android/gradlew*` + `gradle-wrapper.jar` untracked).

# ProductivityApp

This is for people who need an app to monitor whenever they `alt + tab` or just look at other _distracting_ windows.

## Preview

Below are previews of some of the functionality the app offers:

### Animated Loading Screen

![productivity app opening](https://github.com/user-attachments/assets/622f8a56-645a-43c5-8e84-6d1d5228056b)

### Testing

![productivity app testing 1](https://github.com/user-attachments/assets/29d7f768-3d58-4d63-b29f-3c473d68bbdb)

![productivity app testing 2](https://github.com/user-attachments/assets/419b1d1d-b4de-4277-8d25-144040242a52)

## Features

| Feature | Description | Implementation |
| -------- | -------- | -------- |
| **Window Check** | The app will check if look at "distracting" apps by checking the name of the executable. | Since version `0.1.1` |
| **Distraction Timer** | Everytime you look at "distracting" apps, it will increment this timer. | Since version `0.1.1` |
| **Customizable Keyword List** | You can add your own custom keywords to detect when using the app. | Since version `0.2.0` |
| **Additional Menu Settings** | App behavior is now also customizable. | Since version `0.3.0` |
| **Enhanced Keyword Matching System** | The config file that is used by the app to check for "productive" and "distracting" apps are now overhauled. It can fuzzy match, partial match, and more! | Since version `0.3.0` |
| **Productivity Timer** | Everytime you look at "productive" apps, it will increment this timer. | Since version `0.3.0` |

## Installation

### Step 1

Go to the releases tab to the right, and download the latest version, and follow the instructions written there.

### Step 2

Simply open the executable, and the app will immediately check if you're _slacking off_. Specific app behavior can be modified within the app's popup menu.

> If it doesn't detect anything (including itself), run the executable as **administrator**.

**That's it.**

## Setting Up as Dev

If you wish to run the files yourself, you can just clone the repository, then use a package manager like `uv`.

### Requirements

- `uv` package manager (download in your global environment).

### Setup

If you have `uv` then, you can just let `uv` handle the project dependencies. If you don't know how to use `uv`, you can do this command:

```bash
uv sync
uv lock
uv run flet run
```

It will automatically download the missing dependencies. If it doesn't download properly, add an additional flag; `--prerelease=allow` just like this:

```bash
uv sync --prerelease=allow
```

Then check if you have `flet` with:

```bash
uv flet --version
```

Then do the first 3 commands again.

## Safety Concerns

**Yes, this app is safe**.

> "Are you sure?"

If you're doubting me, you can take a look at the source code, which is literally in this repository. The only things that this app may tamper with your files, is where the config files will be stored. By default, this will be stored in the `./AppData/Roaming/MetaDusk/` directory. If you can't locate it, you can open this folder by doing `win + r` then typing `%appdata%` which will bring you to this exact directory, where you will now just search for the `MetaDusk` directory, which is where the config files will be stored.

The other concern you might have, would be:

> "How does this app detect what app you're looking at?"

Basically, this app works by using a library that only provides the window's names, process ids, and such, which are easily locatable manually as well (mostly for the names). And that's the system that this app uses; it simply checks the currently focused window's name against a list of keywords.

## Known Issues and Fixes

| No. | Issue | Description | Solution | Severity |
| -------- | -------- | -------- | -------- | -------- |
| 1. | Stuck on Loading Screen. | This could be because your device is struggling to run the app. | Simply close then open the executable again. | Easily fixed. |
| 2. | App Window Appears Stretched | This could be a `flet` rendering issue. | Click the fullscreen button, then exit fullscreen; any form of page resizing will fix this issue. | Easily fixed. |
| 3. | After long usage of the app, it will just suddenly refuse to detect anything. |  Hopefully this issue has been fixed in `v0.3.1`. | Restart the app. | Easily fixed. |
| 4. | The app enters an indefinite loading screen post-startup. | This could be an issue originating from the new window data detection libraries. | End task the application. | This issue is quite concerning, and it looks like I haven't fixed this yet. |

### Issue Previews

Below is what **Issue No. 4** looks like:

![productivity app bug](https://github.com/user-attachments/assets/7f0568ba-5bf7-48c0-9f25-7d10b28e4006)

Attempting to recreate **Issue No. 4**:

![productivity app stress test](https://github.com/user-attachments/assets/f8ac8ada-1e4c-4dae-9e81-273ca9feb719)

> Based from testing, this issue is reproducible if you stress-test the application. For some reason, spamming interactions with it, will eventually enter this _zombie loading_ state. However, this usually doesn't happen, if you decide to **NOT** stress-test the application. _Stress-test on your own risk!_
> This is also apparently easily reproducible if you open the config files whilst the app is open. For some reason, after some time has passed, the app will enter this _zombie loading_ state. This issue is not yet fixed in `v0.3.1`.

## Future Additions

| Feature | Description | Progress |
| -------- | -------- | -------- |
| **Customizable List for Used Keywords in Detection** | The user can edit a file to add their own keywords that they wish to detect. | 100% |
| **Sound Effects** | A sound effect will play everytime the app catches the user _slacking off_. | 0% |
| **Overhaul Keyword Matching System** | Rework the entire system to support multiple keyword checking systems, including the config file for it. | 100% |

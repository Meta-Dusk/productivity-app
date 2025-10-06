# ProductivityApp

This is for people who need an app to monitor whenever they `alt + tab` or just look at other _distracting_ windows.

## Preview

Below is what you'd expect from the app:

![productivity app preview](https://github.com/user-attachments/assets/bbb32838-1ad1-43ff-a99e-27c6270f4ebe)

## Features

| Feature | Description | Implementation |
| -------- | -------- | -------- |
| **Window Check** | The app will check if look at "distracting" apps by checking the name of the executable. | Since version `0.1.1` |
| **Times Distracted Counter** | Everytime you look at "distracting" apps, it will increment this counter. | Since version `0.1.1` |
| **Customizable Keyword List** | You can add your own custom keywords to detect when using the app. | Since version `0.2.0` |

## Installation

**Step 1**

Go to the releases tab to the right, and download the latest version, and follow the instructions written there.

**Step 2**

Simply open the executable, and the app will immediately check if you're *slacking off*. If it detects that you're not being productive, it will be sent to the front, if it's being hidden behind other windows.

> If it doesn't detect anything (including itself), run the executable as **administrator**.

**That's it.**

## Setting Up as Dev

If you wish to run the files yourself, you can just clone the repository, then us a package manager like `uv`.

**Requirements**:

- `uv` package manager (download in your global environment)

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
| 2. | App Window Appears Stretched | This could be a `flet` rendering issue. | Simply restart the app. | Easily fixed. |

## Future Additions

| Feature | Description | Progress |
| -------- | -------- | -------- |
| **Customizable List for Used Keywords in Detection** | The user can edit a file to add their own keywords that they wish to detect. | 100% |
| **Sound Effects** | A sound effect will play everytime the app catches the user *slacking off*. | 0% |

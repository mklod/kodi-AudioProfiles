# Audio Profiles (Patched)

A patched fork of the Kodi [Audio Profiles](https://kodi.wiki/view/Add-on:Audio_Profiles) addon with additional features for multi-output setups (e.g. AVR + Bluetooth speaker).

Based on v2.1.2 by pkscout / notoco / CtrlGy / Regss.

## New Features (vs. vanilla addon)

### Per-Profile Audio Delay
Each profile now saves and restores its own audio delay value. This is essential for setups where different outputs have different latencies (e.g. HDMI to AVR = 0 ms, Bluetooth speaker = 275 ms).

- When saving a profile, the addon prompts you to enter the delay in seconds (e.g. `0.275` or `-0.1`), since Kodi resets audiodelay to 0 whenever playback stops.
- On profile switch, the saved delay is restored — during playback it uses `Player.SetAudioDelay` (the only method Kodi respects mid-playback), otherwise `Settings.SetSettingValue`.
- On every `Player.OnPlay` event, the delay is automatically re-applied after a short settle period, because Kodi resets it to 0 at the start of each playback.

### Unity Volume Mode
A per-profile toggle that forces Kodi's volume to 100 (0 dB). Intended for passthrough / bitstream profiles where the AVR controls volume and Kodi's volume slider should not attenuate the signal.

- When enabled, the addon also sets a skin boolean (`unity_volume_active`) and a window property so your skin can optionally hide the volume OSD.

### Default Profile Seeding
On first run, the addon seeds two starter profiles if no profile files exist yet:
- **Profile 1 (AVR)**: audio delay = 0.0 s
- **Profile 2 (BLE)**: audio delay = 0.275 s

## Original Features
- Save up to 10 profiles covering System/Audio, System/Display, Player/Videos, and Kodi volume settings
- Send HDMI-CEC commands (Toggle, Standby, Wakeup) per profile
- Switch profiles via keymaps, rotation, or popup dialog
- Auto-switch profiles based on media type, audio codec, or channel count
- Load a default profile on Kodi startup or wake

## Setup Guide
See [`audio-profiles-setup-guide.pdf`](audio-profiles-setup-guide.pdf) for installation and configuration instructions.

## License
GPL-3.0 — see [LICENSE.txt](LICENSE.txt).

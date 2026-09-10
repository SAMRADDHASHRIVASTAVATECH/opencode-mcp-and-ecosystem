# Storage
Set `AUDIO_WORKSTATION_DATA`. The server creates `config`, `logs`, `voices/references`, `voices/profiles`, `models`, `sounds/imported`, `sounds/generated`, `music`, `presets`, and `cache`. State and libraries persist atomically. Models/cache are external data and are not packaged. Back them up separately; deletion tools are consequential.
